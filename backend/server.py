import os
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

import httpx
from lxml import etree
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "boardgame_collection")
BGG_API_URL = "https://boardgamegeek.com/xmlapi2"

# Cache for BGG API responses (24 hour TTL)
game_cache = TTLCache(maxsize=1000, ttl=86400)

# MongoDB client
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]

# Pydantic models
class GameSearch(BaseModel):
    id: str
    name: str
    year: Optional[str] = None

class GameDetails(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bgg_id: str
    title: str
    title_hu: Optional[str] = None  # Magyar cím
    authors: List[str] = []
    cover_image: Optional[str] = None
    min_players: int = 1
    max_players: int = 1
    play_time: int = 0
    complexity_rating: float = 0.0
    bgg_rating: float = 0.0  # BGG átlagos értékelés
    min_age: int = 0  # Minimális életkor
    rules_link: str = ""
    release_year: int = 0
    categories: List[str] = []
    description: str = ""  # Hosszú leírás
    description_short: str = ""  # Rövid leírás (1 mondatos)
    description_hu: Optional[str] = None  # Magyar hosszú leírás
    description_short_hu: Optional[str] = None  # Magyar rövid leírás
    personal_notes: Optional[str] = None  # Saját megjegyzések
    language: str = "en"  # Játék nyelve: hu, en, multilang
    status: str = "available"  # available, borrowed
    borrowed_by: Optional[str] = None
    borrowed_date: Optional[datetime] = None
    return_date: Optional[datetime] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    games: List[str] = []  # List of game IDs owned by user

class BorrowRequest(BaseModel):
    game_id: str
    borrower_name: str
    return_date: str

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Board Game Collection API")
    # Create indexes
    await db.games.create_index("bgg_id", unique=True)
    await db.users.create_index("email", unique=True)
    yield
    # Shutdown
    logger.info("Shutting down Board Game Collection API")

app = FastAPI(
    title="Board Game Collection API",
    description="Manage your board game collection with automatic data from BoardGameGeek",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    if not text:
        return ""
    # Simple HTML tag removal
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

async def fetch_bgg_data(endpoint: str, retries: int = 3) -> bytes:
    """Fetch data from BGG API with retries"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(retries):
            try:
                response = await client.get(f"{BGG_API_URL}{endpoint}")
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 202:
                    # BGG API returns 202 when processing, wait and retry
                    await asyncio.sleep(2)
                    continue
                else:
                    logger.warning(f"BGG API returned {response.status_code}")
            except httpx.TimeoutException:
                logger.warning(f"BGG API timeout, attempt {attempt + 1}")
                if attempt == retries - 1:
                    raise HTTPException(status_code=503, detail="BoardGameGeek API unavailable")
                await asyncio.sleep(1)
        
        raise HTTPException(status_code=503, detail="BoardGameGeek API unavailable")

# API endpoints
@app.get("/")
async def root():
    return {"message": "Board Game Collection API", "version": "1.0.0"}

@app.get("/api/games/search/{query}", response_model=List[GameSearch])
async def search_games(query: str):
    """Search for games on BoardGameGeek"""
    if len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    try:
        xml_content = await fetch_bgg_data(f"/search?query={query}&type=boardgame")
        root = etree.fromstring(xml_content)
        
        games = []
        for item in root.xpath("//item"):
            name_elem = item.find("name")
            year_elem = item.find("yearpublished")
            
            games.append(GameSearch(
                id=item.get("id"),
                name=name_elem.get("value") if name_elem is not None else "Unknown",
                year=year_elem.get("value") if year_elem is not None else None
            ))
        
        return games[:10]  # Return top 10 matches
        
    except etree.XMLSyntaxError:
        logger.error("Invalid XML from BGG search API")
        raise HTTPException(status_code=502, detail="Invalid response from BoardGameGeek")

@app.get("/api/games/details/{bgg_id}", response_model=GameDetails)
async def get_game_details(bgg_id: str):
    """Get detailed information about a game from BoardGameGeek"""
    
    # Check cache first
    if bgg_id in game_cache:
        return game_cache[bgg_id]
    
    try:
        xml_content = await fetch_bgg_data(f"/thing?id={bgg_id}&stats=1")
        root = etree.fromstring(xml_content)
        
        item = root.find(".//item")
        if item is None:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Extract game data
        name_elem = item.find(".//name[@type='primary']")
        year_elem = item.find(".//yearpublished")
        desc_elem = item.find(".//description")
        image_elem = item.find(".//image")
        thumbnail_elem = item.find(".//thumbnail")
        minplayers_elem = item.find(".//minplayers")
        maxplayers_elem = item.find(".//maxplayers")
        playtime_elem = item.find(".//playingtime")
        weight_elem = item.find(".//statistics/ratings/averageweight")
        
        # Get designers (authors)
        authors = []
        for designer in item.xpath(".//link[@type='boardgamedesigner']"):
            authors.append(designer.get("value", "Unknown"))
        
        # Get categories
        categories = []
        for category in item.xpath(".//link[@type='boardgamecategory']"):
            categories.append(category.get("value", ""))
        
        game_details = GameDetails(
            bgg_id=bgg_id,
            title=name_elem.get("value") if name_elem is not None else "Unknown Game",
            authors=authors[:3],  # Limit to 3 authors
            cover_image=image_elem.text if image_elem is not None else (thumbnail_elem.text if thumbnail_elem is not None else None),
            min_players=int(minplayers_elem.get("value", 1)) if minplayers_elem is not None else 1,
            max_players=int(maxplayers_elem.get("value", 1)) if maxplayers_elem is not None else 1,
            play_time=int(playtime_elem.get("value", 0)) if playtime_elem is not None else 0,
            complexity_rating=float(weight_elem.get("value", 0)) if weight_elem is not None else 0.0,
            rules_link=f"https://boardgamegeek.com/boardgame/{bgg_id}/rules",
            release_year=int(year_elem.get("value", 0)) if year_elem is not None else 0,
            categories=categories[:5],  # Limit to 5 categories
            description=clean_html(desc_elem.text if desc_elem is not None else ""),
        )
        
        # Cache the result
        game_cache[bgg_id] = game_details
        
        return game_details
        
    except etree.XMLSyntaxError:
        logger.error("Invalid XML from BGG thing API")
        raise HTTPException(status_code=502, detail="Invalid response from BoardGameGeek")

@app.post("/api/games", response_model=GameDetails)
async def add_game_to_collection(game_data: GameDetails):
    """Add a game to the collection"""
    try:
        # Check if game already exists
        existing = await db.games.find_one({"bgg_id": game_data.bgg_id})
        if existing:
            raise HTTPException(status_code=409, detail="Game already in collection")
        
        # Save to database
        game_dict = game_data.dict()
        await db.games.insert_one(game_dict)
        
        logger.info(f"Added game: {game_data.title}")
        return game_data
        
    except Exception as e:
        logger.error(f"Error adding game: {e}")
        raise HTTPException(status_code=500, detail="Failed to add game to collection")

@app.get("/api/games", response_model=List[GameDetails])
async def get_collection(
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get user's game collection with optional filtering"""
    
    query = {}
    if status:
        query["status"] = status
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"authors": {"$regex": search, "$options": "i"}},
            {"categories": {"$regex": search, "$options": "i"}}
        ]
    
    try:
        cursor = db.games.find(query)
        games = []
        async for game in cursor:
            game["id"] = str(game.get("_id", game.get("id", "")))
            if "_id" in game:
                del game["_id"]
            games.append(GameDetails(**game))
        
        # Filter by category if specified
        if category:
            games = [game for game in games if category.lower() in [cat.lower() for cat in game.categories]]
        
        return games
        
    except Exception as e:
        logger.error(f"Error fetching collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch collection")

@app.put("/api/games/{game_id}/borrow", response_model=GameDetails)
async def borrow_game(game_id: str, borrow_request: BorrowRequest):
    """Mark a game as borrowed"""
    try:
        return_date = datetime.strptime(borrow_request.return_date, "%Y-%m-%d")
        
        result = await db.games.update_one(
            {"id": game_id, "status": "available"},
            {
                "$set": {
                    "status": "borrowed",
                    "borrowed_by": borrow_request.borrower_name,
                    "borrowed_date": datetime.now(),
                    "return_date": return_date
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Game not found or not available")
        
        # Return updated game
        updated_game = await db.games.find_one({"id": game_id})
        if updated_game:
            updated_game["id"] = str(updated_game.get("_id", updated_game.get("id", "")))
            if "_id" in updated_game:
                del updated_game["_id"]
            return GameDetails(**updated_game)
        
        raise HTTPException(status_code=404, detail="Game not found")
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid return date format")
    except Exception as e:
        logger.error(f"Error borrowing game: {e}")
        raise HTTPException(status_code=500, detail="Failed to update game status")

@app.put("/api/games/{game_id}/return", response_model=GameDetails)
async def return_game(game_id: str):
    """Mark a game as returned"""
    try:
        result = await db.games.update_one(
            {"id": game_id, "status": "borrowed"},
            {
                "$set": {
                    "status": "available",
                },
                "$unset": {
                    "borrowed_by": "",
                    "borrowed_date": "",
                    "return_date": ""
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Game not found or not borrowed")
        
        # Return updated game
        updated_game = await db.games.find_one({"id": game_id})
        if updated_game:
            updated_game["id"] = str(updated_game.get("_id", updated_game.get("id", "")))
            if "_id" in updated_game:
                del updated_game["_id"]
            return GameDetails(**updated_game)
        
        raise HTTPException(status_code=404, detail="Game not found")
        
    except Exception as e:
        logger.error(f"Error returning game: {e}")
        raise HTTPException(status_code=500, detail="Failed to update game status")

@app.put("/api/games/{game_id}")
async def update_game(game_id: str, update_data: dict):
    """Update a game in the collection"""
    try:
        logger.info(f"Updating game {game_id} with data: {update_data}")
        
        # Clean up the update data - remove None values and convert dates
        cleaned_data = {}
        for key, value in update_data.items():
            if value is not None:
                if key in ['borrowed_date', 'return_date'] and isinstance(value, str):
                    # Skip datetime conversion for now, just use string
                    continue
                cleaned_data[key] = value
        
        logger.info(f"Cleaned update data: {cleaned_data}")
        
        # Update the game in the database - try both id fields and ObjectId
        query_conditions = [{"id": game_id}]
        
        # Try ObjectId if the game_id looks like one
        try:
            if len(game_id) == 24:  # ObjectId length check
                query_conditions.append({"_id": ObjectId(game_id)})
        except:
            pass
            
        result = await db.games.update_one(
            {"$or": query_conditions},
            {"$set": cleaned_data}
        )
        
        logger.info(f"Update result: matched={result.matched_count}, modified={result.modified_count}")
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Return updated game - try both id fields and ObjectId
        query_conditions = [{"id": game_id}]
        
        # Try ObjectId if the game_id looks like one
        try:
            if len(game_id) == 24:  # ObjectId length check
                query_conditions.append({"_id": ObjectId(game_id)})
        except:
            pass
            
        updated_game = await db.games.find_one({"$or": query_conditions})
        if updated_game:
            updated_game["id"] = str(updated_game.get("_id", updated_game.get("id", "")))
            if "_id" in updated_game:
                del updated_game["_id"]
            return updated_game
        
        raise HTTPException(status_code=404, detail="Game not found")
        
    except Exception as e:
        logger.error(f"Error updating game: {e}")
        raise HTTPException(status_code=500, detail="Failed to update game")

@app.delete("/api/games/{game_id}")
async def delete_game(game_id: str):
    """Remove a game from the collection"""
    try:
        logger.info(f"Deleting game with ID: {game_id}")
        
        # Try both id fields and ObjectId
        query_conditions = [{"id": game_id}]
        
        # Try ObjectId if the game_id looks like one
        try:
            if len(game_id) == 24:  # ObjectId length check
                query_conditions.append({"_id": ObjectId(game_id)})
        except:
            pass
            
        result = await db.games.delete_one({"$or": query_conditions})
        logger.info(f"Delete result: deleted_count={result.deleted_count}")
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Game not found")
        
        return {"message": "Game deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting game: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete game")

# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(game_cache)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)