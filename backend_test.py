#!/usr/bin/env python3
"""
Board Game Collection Backend API Tests
Tests all backend endpoints for the board game collection management app.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://4a554923-d638-47cf-b445-367ec8759b1c.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class BoardGameAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.added_games = []  # Track games added during testing for cleanup
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        if response_data:
            result['response_data'] = response_data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()

    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_test("Health Check", True, f"API is healthy. Cache size: {data.get('cache_size', 0)}")
                    return True
                else:
                    self.log_test("Health Check", False, "Invalid health response format", data)
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False

    def test_bgg_search(self):
        """Test BoardGameGeek search functionality"""
        try:
            # Test search for "Pandemic"
            response = self.session.get(f"{API_BASE}/games/search/Pandemic")
            
            if response.status_code == 200:
                games = response.json()
                if isinstance(games, list) and len(games) > 0:
                    # Check if we found Pandemic in results
                    pandemic_found = any('pandemic' in game.get('name', '').lower() for game in games)
                    if pandemic_found:
                        self.log_test("BGG Search - Pandemic", True, f"Found {len(games)} games including Pandemic")
                        return games[0]  # Return first result for further testing
                    else:
                        self.log_test("BGG Search - Pandemic", False, "Pandemic not found in search results", games)
                        return None
                else:
                    self.log_test("BGG Search - Pandemic", False, "Empty search results", games)
                    return None
            else:
                self.log_test("BGG Search - Pandemic", False, f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("BGG Search - Pandemic", False, f"Exception: {str(e)}")
            return None

    def test_bgg_search_validation(self):
        """Test BGG search input validation"""
        try:
            # Test with short query (should fail)
            response = self.session.get(f"{API_BASE}/games/search/a")
            
            if response.status_code == 400:
                self.log_test("BGG Search Validation", True, "Correctly rejected short query")
                return True
            else:
                self.log_test("BGG Search Validation", False, f"Expected 400, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("BGG Search Validation", False, f"Exception: {str(e)}")
            return False

    def test_bgg_game_details(self, bgg_id: str = "30549"):
        """Test getting detailed game information from BGG"""
        try:
            # Test with Pandemic's BGG ID (30549)
            response = self.session.get(f"{API_BASE}/games/details/{bgg_id}")
            
            if response.status_code == 200:
                game = response.json()
                required_fields = ['bgg_id', 'title', 'authors', 'min_players', 'max_players']
                
                missing_fields = [field for field in required_fields if field not in game]
                if not missing_fields:
                    self.log_test("BGG Game Details", True, 
                                f"Retrieved details for '{game.get('title')}' by {', '.join(game.get('authors', []))}")
                    return game
                else:
                    self.log_test("BGG Game Details", False, f"Missing fields: {missing_fields}", game)
                    return None
            else:
                self.log_test("BGG Game Details", False, f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("BGG Game Details", False, f"Exception: {str(e)}")
            return None

    def test_add_game_to_collection(self, game_data: Dict[str, Any]):
        """Test adding a game to the collection"""
        try:
            response = self.session.post(f"{API_BASE}/games", json=game_data)
            
            if response.status_code == 200:
                added_game = response.json()
                if 'id' in added_game:
                    self.added_games.append(added_game['id'])  # Track for cleanup
                    self.log_test("Add Game to Collection", True, 
                                f"Added '{added_game.get('title')}' with ID {added_game['id']}")
                    return added_game
                else:
                    self.log_test("Add Game to Collection", False, "No ID in response", added_game)
                    return None
            elif response.status_code == 409:
                self.log_test("Add Game to Collection", True, "Game already exists (expected behavior)")
                # Try to get the existing game
                return self.get_existing_game_by_bgg_id(game_data.get('bgg_id'))
            else:
                self.log_test("Add Game to Collection", False, f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Add Game to Collection", False, f"Exception: {str(e)}")
            return None

    def get_existing_game_by_bgg_id(self, bgg_id: str):
        """Helper to get existing game by BGG ID"""
        try:
            response = self.session.get(f"{API_BASE}/games")
            if response.status_code == 200:
                games = response.json()
                for game in games:
                    if game.get('bgg_id') == bgg_id:
                        return game
        except:
            pass
        return None

    def test_get_collection(self):
        """Test getting the game collection"""
        try:
            response = self.session.get(f"{API_BASE}/games")
            
            if response.status_code == 200:
                games = response.json()
                if isinstance(games, list):
                    self.log_test("Get Collection", True, f"Retrieved {len(games)} games from collection")
                    return games
                else:
                    self.log_test("Get Collection", False, "Response is not a list", games)
                    return []
            else:
                self.log_test("Get Collection", False, f"HTTP {response.status_code}", response.text)
                return []
                
        except Exception as e:
            self.log_test("Get Collection", False, f"Exception: {str(e)}")
            return []

    def test_collection_filtering(self):
        """Test collection filtering by status and search"""
        try:
            # Test status filtering
            response = self.session.get(f"{API_BASE}/games?status=available")
            if response.status_code == 200:
                available_games = response.json()
                self.log_test("Collection Filter - Status", True, f"Found {len(available_games)} available games")
            else:
                self.log_test("Collection Filter - Status", False, f"HTTP {response.status_code}", response.text)
                return False

            # Test search filtering
            response = self.session.get(f"{API_BASE}/games?search=pandemic")
            if response.status_code == 200:
                search_results = response.json()
                self.log_test("Collection Filter - Search", True, f"Search returned {len(search_results)} games")
                return True
            else:
                self.log_test("Collection Filter - Search", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Collection Filtering", False, f"Exception: {str(e)}")
            return False

    def test_borrow_game(self, game_id: str):
        """Test borrowing a game"""
        try:
            borrow_data = {
                "game_id": game_id,
                "borrower_name": "Alice Johnson",
                "return_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            }
            
            response = self.session.put(f"{API_BASE}/games/{game_id}/borrow", json=borrow_data)
            
            if response.status_code == 200:
                updated_game = response.json()
                if updated_game.get('status') == 'borrowed' and updated_game.get('borrowed_by') == 'Alice Johnson':
                    self.log_test("Borrow Game", True, f"Game borrowed by {updated_game['borrowed_by']}")
                    return updated_game
                else:
                    self.log_test("Borrow Game", False, "Game status not updated correctly", updated_game)
                    return None
            else:
                self.log_test("Borrow Game", False, f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Borrow Game", False, f"Exception: {str(e)}")
            return None

    def test_return_game(self, game_id: str):
        """Test returning a borrowed game"""
        try:
            response = self.session.put(f"{API_BASE}/games/{game_id}/return")
            
            if response.status_code == 200:
                updated_game = response.json()
                if updated_game.get('status') == 'available' and not updated_game.get('borrowed_by'):
                    self.log_test("Return Game", True, "Game successfully returned and marked as available")
                    return updated_game
                else:
                    self.log_test("Return Game", False, "Game status not updated correctly", updated_game)
                    return None
            else:
                self.log_test("Return Game", False, f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Return Game", False, f"Exception: {str(e)}")
            return None

    def test_delete_game(self, game_id: str):
        """Test deleting a game from collection"""
        try:
            response = self.session.delete(f"{API_BASE}/games/{game_id}")
            
            if response.status_code == 200:
                result = response.json()
                if 'message' in result:
                    self.log_test("Delete Game", True, "Game successfully deleted from collection")
                    return True
                else:
                    self.log_test("Delete Game", False, "Unexpected response format", result)
                    return False
            else:
                self.log_test("Delete Game", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Delete Game", False, f"Exception: {str(e)}")
            return False

    def cleanup_test_games(self):
        """Clean up games added during testing"""
        print("\n🧹 Cleaning up test games...")
        for game_id in self.added_games:
            try:
                response = self.session.delete(f"{API_BASE}/games/{game_id}")
                if response.status_code == 200:
                    print(f"   Deleted game {game_id}")
                else:
                    print(f"   Failed to delete game {game_id}: {response.status_code}")
            except Exception as e:
                print(f"   Error deleting game {game_id}: {e}")

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🎲 Starting Board Game Collection Backend API Tests")
        print("=" * 60)
        
        # 1. Health Check
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return False
        
        # 2. BGG Integration Tests
        print("\n🔍 Testing BoardGameGeek Integration...")
        self.test_bgg_search_validation()
        search_result = self.test_bgg_search()
        
        # Use Pandemic's BGG ID for detailed testing
        game_details = self.test_bgg_game_details("30549")
        
        # 3. Collection CRUD Tests
        print("\n📚 Testing Game Collection CRUD...")
        if game_details:
            added_game = self.test_add_game_to_collection(game_details)
        else:
            # Fallback: create a minimal game for testing
            fallback_game = {
                "bgg_id": "999999",
                "title": "Test Game for API Testing",
                "authors": ["Test Author"],
                "min_players": 2,
                "max_players": 4,
                "play_time": 60,
                "categories": ["Strategy"]
            }
            added_game = self.test_add_game_to_collection(fallback_game)
        
        collection = self.test_get_collection()
        self.test_collection_filtering()
        
        # 4. Lending System Tests
        print("\n🤝 Testing Lending System...")
        if added_game and 'id' in added_game:
            game_id = added_game['id']
            
            # Test borrow workflow
            borrowed_game = self.test_borrow_game(game_id)
            if borrowed_game:
                # Test return workflow
                returned_game = self.test_return_game(game_id)
            
            # Test delete (cleanup)
            self.test_delete_game(game_id)
        
        # 5. Summary
        print("\n📊 Test Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed < total:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = BoardGameAPITester()
    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1
        print(f"\n🏁 Testing completed with exit code: {exit_code}")
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        tester.cleanup_test_games()
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        tester.cleanup_test_games()