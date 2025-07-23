import os
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

import httpx
import jwt
from lxml import etree
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from authlib.integrations.starlette_client import OAuth
from openai import OpenAI
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "boardgame_collection")
BGG_API_URL = "https://boardgamegeek.com/xmlapi2"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "482036913993-nh78j7pqkeffjvpa3gh4qhtoh1u9708b.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "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")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Cache for BGG API responses (24 hour TTL)
game_cache = TTLCache(maxsize=1000, ttl=86400)

# OAuth setup
oauth = OAuth()

# OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Security
security = HTTPBearer()

# MongoDB client
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]

# Pydantic models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    google_id: str
    email: str
    name: str
    picture: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class GoogleAuthRequest(BaseModel):
    credential: str
class GameSearch(BaseModel):
    id: str
    name: str
    year: Optional[str] = None
    thumbnail: Optional[str] = None

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
    owner_id: Optional[str] = None  # Ki birtokolja ezt a játékot
    owner_name: Optional[str] = None  # Birtokos neve

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

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-session-secret-key")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OAuth
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Helper functions
async def translate_to_hungarian(text: str) -> str:
    """Translate English text to Hungarian using OpenAI ChatGPT"""
    if not text or len(text.strip()) == 0:
        return ""
    
    try:
        if not openai_client:
            logger.warning("OpenAI client not initialized")
            return text
            
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate the following English text to natural, fluent Hungarian. Maintain the meaning and tone of the original text."},
                    {"role": "user", "content": f"Translate this to Hungarian: {text}"}
                ],
                max_tokens=len(text) * 2,  # Allow enough tokens for translation
                temperature=0.3
            )
        )
        
        translated_text = response.choices[0].message.content.strip()
        logger.info(f"Successfully translated text ({len(text)} chars) to Hungarian ({len(translated_text)} chars)")
        return translated_text
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        # Return original text if translation fails
        return text

async def create_short_description_hungarian(long_description_hu: str) -> str:
    """Create a short Hungarian description from a long Hungarian description using AI"""
    if not long_description_hu or len(long_description_hu.strip()) == 0:
        return ""
    
    try:
        if not openai_client:
            logger.warning("OpenAI client not initialized")
            return long_description_hu[:150] + "..."
            
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional game description writer. Create a concise, engaging 1-2 sentence summary (max 200 characters) from the provided Hungarian game description. Focus on the core gameplay and theme."},
                    {"role": "user", "content": f"Create a short summary from this Hungarian game description: {long_description_hu}"}
                ],
                max_tokens=100,
                temperature=0.3
            )
        )
        
        short_description = response.choices[0].message.content.strip()
        
        # Ensure it's not too long
        if len(short_description) > 250:
            short_description = short_description[:247] + "..."
            
        logger.info(f"Successfully generated short Hungarian description ({len(short_description)} chars)")
        return short_description
        
    except Exception as e:
        logger.error(f"Short description generation error: {e}")
        # Fallback: extract first meaningful part
        import re
        sentences = re.split(r'[.!?]+', long_description_hu)
        if sentences and len(sentences) > 0:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 200:
                return first_sentence[:197] + "..."
            else:
                return first_sentence + "."
        else:
            return long_description_hu[:150] + "..."

def create_access_token(user_id: str, email: str):
    """Create JWT access token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, "your-secret-key", algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, "your-secret-key", algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(user_id: str = Depends(verify_token)):
    """Get current user from database"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["id"] = str(user.get("_id", user.get("id", "")))
    if "_id" in user:
        del user["_id"]
    return User(**user)
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

# Authentication endpoints
@app.post("/api/auth/google")
async def google_auth(auth_request: GoogleAuthRequest):
    """Authenticate user with Google OAuth"""
    try:
        # Verify the Google JWT token
        import requests
        response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={auth_request.credential}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        user_info = response.json()
        
        # Check if user exists (by google_id or email)
        user = await db.users.find_one({"google_id": user_info["sub"]})
        
        if not user:
            # Check if user exists by email (for existing users without google_id)
            user = await db.users.find_one({"email": user_info["email"]})
            
            if user:
                # Update existing user with google_id
                await db.users.update_one(
                    {"email": user_info["email"]},
                    {"$set": {
                        "google_id": user_info["sub"],
                        "name": user_info["name"],
                        "picture": user_info.get("picture")
                    }}
                )
                # Reload user data
                user = await db.users.find_one({"email": user_info["email"]})
            else:
                # Create new user
                new_user = User(
                    google_id=user_info["sub"],
                    email=user_info["email"],
                    name=user_info["name"],
                    picture=user_info.get("picture")
                )
                try:
                    result = await db.users.insert_one(new_user.dict())
                    new_user_dict = new_user.dict()
                    new_user_dict["id"] = str(result.inserted_id)
                    user = new_user_dict
                except Exception as insert_error:
                    # Handle potential duplicate key error
                    logger.error(f"User creation error: {insert_error}")
                    user = await db.users.find_one({"email": user_info["email"]})
                    if not user:
                        raise HTTPException(status_code=500, detail="Failed to create user")
        else:
            # Update existing user
            await db.users.update_one(
                {"google_id": user_info["sub"]},
                {"$set": {
                    "name": user_info["name"],
                    "picture": user_info.get("picture")
                }}
            )
            user["id"] = str(user.get("_id", user.get("id", "")))
        
        # Create access token
        token = create_access_token(user["id"], user["email"])
        
        return {
            "access_token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user.get("picture"),
                "address": user.get("address")
            }
        }
        
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/api/auth/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get user profile with lending information"""
    try:
        # Get games I own that are borrowed by others
        lent_games = []
        async for game in db.games.find({"owner_id": current_user.id, "status": "borrowed"}):
            game["id"] = str(game.get("_id", game.get("id", "")))
            if "_id" in game:
                del game["_id"]
            lent_games.append(game)
        
        # Get games I borrowed from others
        borrowed_games = []
        async for game in db.games.find({"borrowed_by": current_user.name, "status": "borrowed"}):
            game["id"] = str(game.get("_id", game.get("id", "")))
            if "_id" in game:
                del game["_id"]
            borrowed_games.append(game)
        
        return {
            "user": current_user,
            "lent_games": lent_games,
            "borrowed_games": borrowed_games
        }
        
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")

@app.put("/api/auth/profile")
async def update_profile(name: str, address: str, current_user: User = Depends(get_current_user)):
    """Update user profile"""
    try:
        query_conditions = [{"id": current_user.id}]
        try:
            if len(current_user.id) == 24:
                query_conditions.append({"_id": ObjectId(current_user.id)})
        except:
            pass
        
        await db.users.update_one(
            {"$or": query_conditions},
            {"$set": {"name": name, "address": address}}
        )
        return {"message": "Profile updated successfully"}
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@app.get("/api/games/search/{query}", response_model=List[GameSearch])
async def search_games(query: str):
    """Search for games on BoardGameGeek"""
    if len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    try:
        xml_content = await fetch_bgg_data(f"/search?query={query}&type=boardgame")
        root = etree.fromstring(xml_content)
        
        games = []
        game_ids = []
        
        # First pass: collect game data from search
        for item in root.xpath("//item"):
            name_elem = item.find("name")
            year_elem = item.find("yearpublished")
            game_id = item.get("id")
            
            game_data = {
                "id": game_id,
                "name": name_elem.get("value") if name_elem is not None else "Unknown",
                "year": year_elem.get("value") if year_elem is not None else None,
                "thumbnail": None
            }
            games.append(game_data)
            game_ids.append(game_id)
        
        # Limit to top 10 matches for performance
        games = games[:10]
        game_ids = game_ids[:10]
        
        # Second pass: fetch thumbnails for the games
        if game_ids:
            try:
                ids_string = ",".join(game_ids)
                details_xml = await fetch_bgg_data(f"/thing?id={ids_string}&type=boardgame")
                details_root = etree.fromstring(details_xml)
                
                # Create a map of ID to thumbnail
                thumbnail_map = {}
                for item in details_root.xpath("//item"):
                    item_id = item.get("id")
                    thumbnail_elem = item.find("thumbnail")
                    if thumbnail_elem is not None and thumbnail_elem.text:
                        thumbnail_map[item_id] = thumbnail_elem.text
                
                # Update games with thumbnails
                for game in games:
                    if game["id"] in thumbnail_map:
                        game["thumbnail"] = thumbnail_map[game["id"]]
                        
            except Exception as e:
                logger.warning(f"Failed to fetch thumbnails for search results: {e}")
                # Continue without thumbnails
        
        # Convert to Pydantic models
        game_search_results = [GameSearch(**game) for game in games]
        return game_search_results
        
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
        
        # Get BGG rating and other statistics
        rating_elem = item.find(".//statistics/ratings/average")
        bgg_rating = float(rating_elem.get("value", 0)) if rating_elem is not None else 0.0
        
        # Get minimum age
        minage_elem = item.find(".//minage")
        min_age = int(minage_elem.get("value", 0)) if minage_elem is not None else 0
        
        # Process description for short version (smart extraction)
        full_description = clean_html(desc_elem.text if desc_elem is not None else "")
        short_description = ""
        if full_description:
            # Try to extract a meaningful short description
            import re
            
            # Method 1: Look for first paragraph (up to double newline)
            paragraphs = re.split(r'\n\s*\n', full_description)
            first_paragraph = paragraphs[0].strip() if paragraphs else ""
            
            # Method 2: Extract first 1-2 sentences
            sentences = re.split(r'[.!?]+', full_description)
            first_sentence = sentences[0].strip() if sentences else ""
            second_sentence = sentences[1].strip() if len(sentences) > 1 else ""
            
            # Choose the best short description
            if first_paragraph and len(first_paragraph) <= 250 and len(first_paragraph) >= 50:
                # Use first paragraph if it's a good length
                short_description = first_paragraph
                if not short_description.endswith(('.', '!', '?')):
                    short_description += "."
            elif first_sentence and len(first_sentence) >= 30:
                # Use first sentence, possibly with second if short
                if len(first_sentence) < 100 and second_sentence and len(second_sentence) < 100:
                    short_description = f"{first_sentence}. {second_sentence}."
                else:
                    short_description = first_sentence + "."
            else:
                # Fallback: take first 200 characters
                short_description = full_description[:200].strip()
                if not short_description.endswith(('.', '!', '?')):
                    short_description += "..."
            
            # Final length check
            if len(short_description) > 300:
                short_description = short_description[:297] + "..."
        
        game_details = GameDetails(
            bgg_id=bgg_id,
            title=name_elem.get("value") if name_elem is not None else "Unknown Game",
            authors=authors[:3],  # Limit to 3 authors
            cover_image=image_elem.text if image_elem is not None else (thumbnail_elem.text if thumbnail_elem is not None else None),
            min_players=int(minplayers_elem.get("value", 1)) if minplayers_elem is not None else 1,
            max_players=int(maxplayers_elem.get("value", 1)) if maxplayers_elem is not None else 1,
            play_time=int(playtime_elem.get("value", 0)) if playtime_elem is not None else 0,
            complexity_rating=float(weight_elem.get("value", 0)) if weight_elem is not None else 0.0,
            bgg_rating=bgg_rating,
            min_age=min_age,
            rules_link=f"https://boardgamegeek.com/boardgame/{bgg_id}/rules",
            release_year=int(year_elem.get("value", 0)) if year_elem is not None else 0,
            categories=categories[:5],  # Limit to 5 categories
            description=full_description,
            description_short=short_description,
            owner_id="",  # Empty for BGG details endpoint
            owner_name=""  # Empty for BGG details endpoint
        )
        
        # Auto-translate to Hungarian if requested for Hungarian games
        # Check if the game language should be Hungarian (based on some criteria)
        # For now, we'll check if this is for a Hungarian game context
        
        # Only translate if we have OpenAI configured
        if openai_client:
            try:
                # Always provide Hungarian translations for games
                # This will be useful when user selects Hungarian language for the game
                hungarian_title = await translate_to_hungarian(game_details.title)
                game_details.title_hu = hungarian_title
                
                # Translate descriptions to Hungarian
                if game_details.description:
                    hungarian_description = await translate_to_hungarian(game_details.description)
                    game_details.description_hu = hungarian_description
                    
                    # Generate intelligent short description from the Hungarian long description
                    if hungarian_description:
                        hungarian_short_description = await create_short_description_hungarian(hungarian_description)
                        game_details.description_short_hu = hungarian_short_description
                    else:
                        # Fallback: translate the English short description
                        if game_details.description_short:
                            game_details.description_short_hu = await translate_to_hungarian(game_details.description_short)
                elif game_details.description_short:
                    # Only short description available, translate that
                    hungarian_short_description = await translate_to_hungarian(game_details.description_short)
                    game_details.description_short_hu = hungarian_short_description
                    
                logger.info(f"Auto-translated game details to Hungarian: {game_details.title} -> {hungarian_title}")
                
            except Exception as e:
                logger.warning(f"Failed to auto-translate game details: {e}")
                # Continue without translation
                game_details.title_hu = ""
                game_details.description_hu = ""
                game_details.description_short_hu = ""
        else:
            logger.warning("OpenAI not configured, skipping translation")
            game_details.title_hu = ""
            game_details.description_hu = ""
            game_details.description_short_hu = ""
        
        # Cache the result
        game_cache[bgg_id] = game_details
        
        return game_details
        
    except etree.XMLSyntaxError:
        logger.error("Invalid XML from BGG thing API")
        raise HTTPException(status_code=502, detail="Invalid response from BoardGameGeek")

@app.post("/api/games", response_model=GameDetails)
async def add_game_to_collection(game_data: GameDetails, current_user: User = Depends(get_current_user)):
    """Add a game to the collection"""
    try:
        # Set owner information
        game_data.owner_id = current_user.id
        game_data.owner_name = current_user.name
        
        # Check if game already exists for this user
        existing = await db.games.find_one({"bgg_id": game_data.bgg_id, "owner_id": current_user.id})
        if existing:
            raise HTTPException(status_code=409, detail="Game already in your collection")
        
        # Save to database
        game_dict = game_data.dict()
        await db.games.insert_one(game_dict)
        
        logger.info(f"Added game: {game_data.title} for user: {current_user.name}")
        return game_data
        
    except Exception as e:
        logger.error(f"Error adding game: {e}")
        raise HTTPException(status_code=500, detail="Failed to add game to collection")

@app.get("/api/games", response_model=List[GameDetails])
async def get_collection(
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    owner_only: Optional[bool] = True,  # Alapértelmezetten csak saját játékok
    current_user: User = Depends(get_current_user)
):
    """Get games collection with optional filtering"""
    
    query = {}
    if owner_only:
        # Csak a felhasználó saját játékait vagy azokat, amelyekhez még nincs tulajdonos megadva
        query["$or"] = [
            {"owner_id": current_user.id},
            {"owner_id": {"$exists": False}},
            {"owner_id": None},
            {"owner_id": ""}
        ]
    
    if status:
        query["status"] = status
    if search:
        search_query = {
            "$or": [
                {"title": {"$regex": search, "$options": "i"}},
                {"authors": {"$regex": search, "$options": "i"}},
                {"categories": {"$regex": search, "$options": "i"}}
            ]
        }
        if "$or" in query:
            # Kombináljuk a tulajdonos és keresési feltételeket
            query = {"$and": [{"$or": query["$or"]}, search_query]}
        else:
            query.update(search_query)
    
    try:
        cursor = db.games.find(query)
        games = []
        async for game in cursor:
            game["id"] = str(game.get("_id", game.get("id", "")))
            if "_id" in game:
                del game["_id"]
                
            # Ha nincs tulajdonos beállítva, állítsuk be a jelenlegi felhasználót
            if not game.get("owner_id"):
                game["owner_id"] = current_user.id
                game["owner_name"] = current_user.name
                # Frissítsük az adatbázist is
                await db.games.update_one(
                    {"_id": ObjectId(game["id"]) if ObjectId.is_valid(game["id"]) else game["id"]},
                    {"$set": {"owner_id": current_user.id, "owner_name": current_user.name}}
                )
                
            games.append(GameDetails(**game))
        
        # Filter by category if specified
        if category:
            games = [game for game in games if category.lower() in [cat.lower() for cat in game.categories]]
        
        return games
        
    except Exception as e:
        logger.error(f"Error fetching collection: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch collection")

@app.post("/api/games/{game_id}/add-to-my-collection")
async def add_existing_game_to_my_collection(game_id: str, current_user: User = Depends(get_current_user)):
    """Add an existing game to current user's collection"""
    try:
        # Find the original game
        original_game = await db.games.find_one({"id": game_id})
        if not original_game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Check if user already has this game
        existing = await db.games.find_one({"bgg_id": original_game["bgg_id"], "owner_id": current_user.id})
        if existing:
            raise HTTPException(status_code=409, detail="Game already in your collection")
        
        # Create new game instance for current user
        new_game = GameDetails(**original_game)
        new_game.id = str(uuid.uuid4())
        new_game.owner_id = current_user.id
        new_game.owner_name = current_user.name
        new_game.status = "available"
        new_game.borrowed_by = None
        new_game.borrowed_date = None
        new_game.return_date = None
        new_game.personal_notes = None
        
        # Save to database
        await db.games.insert_one(new_game.dict())
        
        return {"message": "Game added to your collection successfully"}
        
    except Exception as e:
        logger.error(f"Error adding existing game: {e}")
        raise HTTPException(status_code=500, detail="Failed to add game to your collection")

@app.put("/api/games/{game_id}/borrow", response_model=GameDetails)
async def borrow_game(game_id: str, borrow_request: BorrowRequest, current_user: User = Depends(get_current_user)):
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
async def return_game(game_id: str, current_user: User = Depends(get_current_user)):
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
async def update_game(game_id: str, update_data: dict, current_user: User = Depends(get_current_user)):
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
async def delete_game(game_id: str, current_user: User = Depends(get_current_user)):
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

@app.post("/api/games/refresh-bgg-data")
async def refresh_bgg_data():
    """Refresh BGG data for all existing games"""
    try:
        games = []
        async for game in db.games.find():
            games.append(game)
        
        updated_count = 0
        for game in games:
            if "bgg_id" in game:
                try:
                    # Get fresh data from BGG
                    xml_content = await fetch_bgg_data(f"/thing?id={game['bgg_id']}&stats=1")
                    root = etree.fromstring(xml_content)
                    
                    item = root.find(".//item")
                    if item is not None:
                        # Get BGG rating
                        rating_elem = item.find(".//statistics/ratings/average")
                        bgg_rating = float(rating_elem.get("value", 0)) if rating_elem is not None else 0.0
                        
                        # Get minimum age
                        minage_elem = item.find(".//minage")
                        min_age = int(minage_elem.get("value", 0)) if minage_elem is not None else 0
                        
                        # Process description for short version
                        desc_elem = item.find(".//description")
                        full_description = clean_html(desc_elem.text if desc_elem is not None else "")
                        short_description = ""
                        if full_description:
                            import re
                            sentences = re.split(r'[.!?]+', full_description)
                            if sentences:
                                short_description = sentences[0].strip() + "."
                                if len(short_description) > 200:
                                    short_description = short_description[:200] + "..."
                        
                        # Update the game
                        await db.games.update_one(
                            {"id": game["id"]},
                            {"$set": {
                                "bgg_rating": bgg_rating,
                                "min_age": min_age,
                                "description_short": short_description
                            }}
                        )
                        updated_count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to update game {game.get('title', 'Unknown')}: {e}")
                    continue
        
        return {"message": f"Updated {updated_count} games with fresh BGG data"}
        
    except Exception as e:
        logger.error(f"Error refreshing BGG data: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh BGG data")

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