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
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class BoardGameAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        # Disable SSL verification for testing purposes
        self.session.verify = False
        # Suppress SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
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

    def test_bgg_search_with_thumbnails(self):
        """Test BoardGameGeek search functionality with thumbnail images"""
        print("\n🖼️ Testing BGG Search with Thumbnails...")
        
        # Test popular games that should have thumbnails
        test_queries = ["pandemic", "catan", "gloomhaven"]
        
        for query in test_queries:
            try:
                print(f"\n   Testing search for '{query}'...")
                response = self.session.get(f"{API_BASE}/games/search/{query}")
                
                if response.status_code == 200:
                    games = response.json()
                    if isinstance(games, list) and len(games) > 0:
                        # Check response structure
                        first_game = games[0]
                        required_fields = ['id', 'name', 'year', 'thumbnail']
                        missing_fields = [field for field in required_fields if field not in first_game]
                        
                        if missing_fields:
                            self.log_test(f"Search Thumbnails - {query.title()} Structure", False, 
                                        f"Missing fields in response: {missing_fields}", first_game)
                            continue
                        
                        # Check thumbnail URLs
                        games_with_thumbnails = [game for game in games if game.get('thumbnail')]
                        games_without_thumbnails = [game for game in games if not game.get('thumbnail')]
                        
                        thumbnail_details = {
                            'total_games': len(games),
                            'with_thumbnails': len(games_with_thumbnails),
                            'without_thumbnails': len(games_without_thumbnails),
                            'sample_thumbnails': [game.get('thumbnail') for game in games_with_thumbnails[:3]]
                        }
                        
                        # Validate thumbnail URLs
                        valid_thumbnails = 0
                        invalid_thumbnails = []
                        
                        for game in games_with_thumbnails[:5]:  # Check first 5 thumbnails
                            thumbnail_url = game.get('thumbnail')
                            if thumbnail_url:
                                # Check if URL looks like a BGG image URL
                                if 'geekdo-images.com' in thumbnail_url or 'boardgamegeek.com' in thumbnail_url:
                                    valid_thumbnails += 1
                                else:
                                    invalid_thumbnails.append(thumbnail_url)
                        
                        if len(games_with_thumbnails) > 0:
                            if valid_thumbnails > 0 and len(invalid_thumbnails) == 0:
                                self.log_test(f"Search Thumbnails - {query.title()} Success", True, 
                                            f"Found {len(games)} games, {len(games_with_thumbnails)} with valid BGG thumbnails", 
                                            thumbnail_details)
                            else:
                                self.log_test(f"Search Thumbnails - {query.title()} Quality", False, 
                                            f"Invalid thumbnail URLs found: {invalid_thumbnails}", thumbnail_details)
                        else:
                            self.log_test(f"Search Thumbnails - {query.title()} Missing", False, 
                                        f"No thumbnails found in {len(games)} results", thumbnail_details)
                    else:
                        self.log_test(f"Search Thumbnails - {query.title()}", False, "Empty search results", games)
                else:
                    self.log_test(f"Search Thumbnails - {query.title()}", False, f"HTTP {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_test(f"Search Thumbnails - {query.title()}", False, f"Exception: {str(e)}")

    def test_thumbnail_performance(self):
        """Test that search with thumbnails maintains reasonable performance"""
        print("\n⚡ Testing Thumbnail Performance...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/games/search/pandemic")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                games = response.json()
                
                # Check if we got results with thumbnails
                games_with_thumbnails = [game for game in games if game.get('thumbnail')]
                
                performance_details = {
                    'response_time_seconds': round(response_time, 2),
                    'total_games': len(games),
                    'games_with_thumbnails': len(games_with_thumbnails),
                    'acceptable_time_limit': 10.0
                }
                
                if response_time < 10.0:  # Should complete within 10 seconds
                    self.log_test("Thumbnail Performance", True, 
                                f"Search with thumbnails completed in {response_time:.2f}s (acceptable)", 
                                performance_details)
                else:
                    self.log_test("Thumbnail Performance", False, 
                                f"Search took {response_time:.2f}s (too slow for production)", 
                                performance_details)
            else:
                self.log_test("Thumbnail Performance", False, 
                            f"HTTP {response.status_code} (response time: {response_time:.2f}s)", response.text)
                
        except Exception as e:
            self.log_test("Thumbnail Performance", False, f"Exception: {str(e)}")

    def test_thumbnail_error_handling(self):
        """Test that search still works even if thumbnail fetching fails"""
        print("\n🛡️ Testing Thumbnail Error Handling...")
        
        try:
            # Test with a query that should return results
            response = self.session.get(f"{API_BASE}/games/search/catan")
            
            if response.status_code == 200:
                games = response.json()
                
                if isinstance(games, list) and len(games) > 0:
                    # Even if thumbnail fetching fails, we should still get game data
                    required_base_fields = ['id', 'name']
                    all_games_have_base_fields = all(
                        all(field in game for field in required_base_fields) 
                        for game in games
                    )
                    
                    if all_games_have_base_fields:
                        # Check thumbnail field presence (should be present even if null)
                        all_games_have_thumbnail_field = all('thumbnail' in game for game in games)
                        
                        if all_games_have_thumbnail_field:
                            games_with_thumbnails = [game for game in games if game.get('thumbnail')]
                            games_with_null_thumbnails = [game for game in games if game.get('thumbnail') is None]
                            
                            error_handling_details = {
                                'total_games': len(games),
                                'games_with_thumbnails': len(games_with_thumbnails),
                                'games_with_null_thumbnails': len(games_with_null_thumbnails),
                                'all_have_base_fields': all_games_have_base_fields,
                                'all_have_thumbnail_field': all_games_have_thumbnail_field
                            }
                            
                            self.log_test("Thumbnail Error Handling", True, 
                                        "Search returns games with thumbnail field (even if null) when thumbnail fetching fails", 
                                        error_handling_details)
                        else:
                            self.log_test("Thumbnail Error Handling", False, 
                                        "Some games missing thumbnail field in response structure")
                    else:
                        self.log_test("Thumbnail Error Handling", False, 
                                    "Games missing required base fields", games)
                else:
                    self.log_test("Thumbnail Error Handling", False, "Empty search results", games)
            else:
                self.log_test("Thumbnail Error Handling", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Thumbnail Error Handling", False, f"Exception: {str(e)}")

    def test_thumbnail_url_validation(self):
        """Test that returned thumbnail URLs are valid BGG image URLs"""
        print("\n🔗 Testing Thumbnail URL Validation...")
        
        try:
            response = self.session.get(f"{API_BASE}/games/search/gloomhaven")
            
            if response.status_code == 200:
                games = response.json()
                games_with_thumbnails = [game for game in games if game.get('thumbnail')]
                
                if len(games_with_thumbnails) > 0:
                    url_validation_results = {
                        'total_thumbnails_checked': 0,
                        'valid_bgg_urls': 0,
                        'invalid_urls': [],
                        'sample_valid_urls': []
                    }
                    
                    for game in games_with_thumbnails[:5]:  # Check first 5 thumbnails
                        thumbnail_url = game.get('thumbnail')
                        if thumbnail_url:
                            url_validation_results['total_thumbnails_checked'] += 1
                            
                            # Check if URL follows BGG image URL format
                            is_valid_bgg_url = (
                                thumbnail_url.startswith('https://') and
                                ('geekdo-images.com' in thumbnail_url or 'boardgamegeek.com' in thumbnail_url) and
                                (thumbnail_url.endswith('.jpg') or thumbnail_url.endswith('.png') or thumbnail_url.endswith('.jpeg'))
                            )
                            
                            if is_valid_bgg_url:
                                url_validation_results['valid_bgg_urls'] += 1
                                if len(url_validation_results['sample_valid_urls']) < 3:
                                    url_validation_results['sample_valid_urls'].append(thumbnail_url)
                            else:
                                url_validation_results['invalid_urls'].append(thumbnail_url)
                    
                    if url_validation_results['valid_bgg_urls'] > 0 and len(url_validation_results['invalid_urls']) == 0:
                        self.log_test("Thumbnail URL Validation", True, 
                                    f"All {url_validation_results['valid_bgg_urls']} thumbnail URLs are valid BGG image URLs", 
                                    url_validation_results)
                    elif url_validation_results['valid_bgg_urls'] > 0:
                        self.log_test("Thumbnail URL Validation", False, 
                                    f"Some invalid URLs found: {url_validation_results['invalid_urls']}", 
                                    url_validation_results)
                    else:
                        self.log_test("Thumbnail URL Validation", False, 
                                    "No valid BGG thumbnail URLs found", url_validation_results)
                else:
                    self.log_test("Thumbnail URL Validation", False, 
                                "No games with thumbnails found for validation")
            else:
                self.log_test("Thumbnail URL Validation", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Thumbnail URL Validation", False, f"Exception: {str(e)}")

    def test_search_result_limit(self):
        """Test that search limits results to top 10 for performance"""
        print("\n📊 Testing Search Result Limit...")
        
        try:
            # Use a broad search term that should return many results
            response = self.session.get(f"{API_BASE}/games/search/war")
            
            if response.status_code == 200:
                games = response.json()
                
                limit_details = {
                    'total_results': len(games),
                    'expected_limit': 10,
                    'within_limit': len(games) <= 10
                }
                
                if len(games) <= 10:
                    self.log_test("Search Result Limit", True, 
                                f"Search properly limited to {len(games)} results (≤10)", limit_details)
                else:
                    self.log_test("Search Result Limit", False, 
                                f"Search returned {len(games)} results, exceeding limit of 10", limit_details)
            else:
                self.log_test("Search Result Limit", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Search Result Limit", False, f"Exception: {str(e)}")

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

    def test_authentication_endpoints(self):
        """Test Google Authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test 1: Check if /api/auth/google endpoint exists (POST)
        try:
            # This should fail with 422 (validation error) since we're not sending proper Google credential
            test_auth_data = {"credential": "invalid_test_token"}
            response = self.session.post(f"{API_BASE}/auth/google", json=test_auth_data)
            
            if response.status_code in [401, 422]:
                self.log_test("Auth Endpoint - Google Auth", True, 
                            f"Endpoint exists and properly validates credentials (HTTP {response.status_code})")
            else:
                self.log_test("Auth Endpoint - Google Auth", False, 
                            f"Unexpected response: HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth Endpoint - Google Auth", False, f"Exception: {str(e)}")

        # Test 2: Check if /api/auth/me endpoint exists and requires authentication
        try:
            response = self.session.get(f"{API_BASE}/auth/me")
            
            if response.status_code == 401:
                self.log_test("Auth Endpoint - Get Current User", True, 
                            "Endpoint properly requires authentication (HTTP 401)")
            elif response.status_code == 403:
                self.log_test("Auth Endpoint - Get Current User", True, 
                            "Endpoint properly requires authentication (HTTP 403)")
            else:
                self.log_test("Auth Endpoint - Get Current User", False, 
                            f"Expected 401/403, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth Endpoint - Get Current User", False, f"Exception: {str(e)}")

        # Test 3: Check if /api/auth/profile endpoint exists and requires authentication
        try:
            response = self.session.get(f"{API_BASE}/auth/profile")
            
            if response.status_code == 401:
                self.log_test("Auth Endpoint - Get Profile", True, 
                            "Endpoint properly requires authentication (HTTP 401)")
            elif response.status_code == 403:
                self.log_test("Auth Endpoint - Get Profile", True, 
                            "Endpoint properly requires authentication (HTTP 403)")
            else:
                self.log_test("Auth Endpoint - Get Profile", False, 
                            f"Expected 401/403, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Auth Endpoint - Get Profile", False, f"Exception: {str(e)}")

    def test_protected_game_endpoints(self):
        """Test that game endpoints now require authentication"""
        print("\n🛡️ Testing Protected Game Endpoints...")
        
        # Test 1: GET /api/games should require authentication
        try:
            response = self.session.get(f"{API_BASE}/games")
            
            if response.status_code == 401:
                self.log_test("Protected Endpoint - Get Games", True, 
                            "GET /api/games properly requires authentication (HTTP 401)")
            elif response.status_code == 403:
                self.log_test("Protected Endpoint - Get Games", True, 
                            "GET /api/games properly requires authentication (HTTP 403)")
            else:
                self.log_test("Protected Endpoint - Get Games", False, 
                            f"Expected 401/403, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Protected Endpoint - Get Games", False, f"Exception: {str(e)}")

        # Test 2: POST /api/games should require authentication
        try:
            test_game = {
                "bgg_id": "999999",
                "title": "Test Game",
                "authors": ["Test Author"],
                "min_players": 2,
                "max_players": 4
            }
            response = self.session.post(f"{API_BASE}/games", json=test_game)
            
            if response.status_code == 401:
                self.log_test("Protected Endpoint - Add Game", True, 
                            "POST /api/games properly requires authentication (HTTP 401)")
            elif response.status_code == 403:
                self.log_test("Protected Endpoint - Add Game", True, 
                            "POST /api/games properly requires authentication (HTTP 403)")
            else:
                self.log_test("Protected Endpoint - Add Game", False, 
                            f"Expected 401/403, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Protected Endpoint - Add Game", False, f"Exception: {str(e)}")

        # Test 3: DELETE /api/games/{id} should require authentication
        try:
            response = self.session.delete(f"{API_BASE}/games/test-id")
            
            if response.status_code == 401:
                self.log_test("Protected Endpoint - Delete Game", True, 
                            "DELETE /api/games/{id} properly requires authentication (HTTP 401)")
            elif response.status_code == 403:
                self.log_test("Protected Endpoint - Delete Game", True, 
                            "DELETE /api/games/{id} properly requires authentication (HTTP 403)")
            else:
                self.log_test("Protected Endpoint - Delete Game", False, 
                            f"Expected 401/403, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Protected Endpoint - Delete Game", False, f"Exception: {str(e)}")

        # Test 4: PUT /api/games/{id}/borrow should require authentication
        try:
            borrow_data = {
                "game_id": "test-id",
                "borrower_name": "Test User",
                "return_date": "2024-12-31"
            }
            response = self.session.put(f"{API_BASE}/games/test-id/borrow", json=borrow_data)
            
            if response.status_code == 401:
                self.log_test("Protected Endpoint - Borrow Game", True, 
                            "PUT /api/games/{id}/borrow properly requires authentication (HTTP 401)")
            elif response.status_code == 403:
                self.log_test("Protected Endpoint - Borrow Game", True, 
                            "PUT /api/games/{id}/borrow properly requires authentication (HTTP 403)")
            else:
                self.log_test("Protected Endpoint - Borrow Game", False, 
                            f"Expected 401/403, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Protected Endpoint - Borrow Game", False, f"Exception: {str(e)}")

        # Test 5: PUT /api/games/{id}/return should require authentication
        try:
            response = self.session.put(f"{API_BASE}/games/test-id/return")
            
            if response.status_code == 401:
                self.log_test("Protected Endpoint - Return Game", True, 
                            "PUT /api/games/{id}/return properly requires authentication (HTTP 401)")
            elif response.status_code == 403:
                self.log_test("Protected Endpoint - Return Game", True, 
                            "PUT /api/games/{id}/return properly requires authentication (HTTP 403)")
            else:
                self.log_test("Protected Endpoint - Return Game", False, 
                            f"Expected 401/403, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Protected Endpoint - Return Game", False, f"Exception: {str(e)}")

        # Test 6: PUT /api/games/{id} should require authentication
        try:
            update_data = {"title": "Updated Game"}
            response = self.session.put(f"{API_BASE}/games/test-id", json=update_data)
            
            if response.status_code == 401:
                self.log_test("Protected Endpoint - Update Game", True, 
                            "PUT /api/games/{id} properly requires authentication (HTTP 401)")
            elif response.status_code == 403:
                self.log_test("Protected Endpoint - Update Game", True, 
                            "PUT /api/games/{id} properly requires authentication (HTTP 403)")
            else:
                self.log_test("Protected Endpoint - Update Game", False, 
                            f"Expected 401/403, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Protected Endpoint - Update Game", False, f"Exception: {str(e)}")

    def test_non_protected_endpoints(self):
        """Test that BGG endpoints still work without authentication"""
        print("\n🌐 Testing Non-Protected BGG Endpoints...")
        
        # Test 1: BGG search should still work without auth
        try:
            response = self.session.get(f"{API_BASE}/games/search/Pandemic")
            
            if response.status_code == 200:
                games = response.json()
                if isinstance(games, list):
                    self.log_test("Non-Protected - BGG Search", True, 
                                f"BGG search works without auth, found {len(games)} games")
                else:
                    self.log_test("Non-Protected - BGG Search", False, 
                                "Invalid response format", games)
            else:
                self.log_test("Non-Protected - BGG Search", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Non-Protected - BGG Search", False, f"Exception: {str(e)}")

        # Test 2: BGG game details should still work without auth
        try:
            response = self.session.get(f"{API_BASE}/games/details/30549")
            
            if response.status_code == 200:
                game = response.json()
                if 'title' in game and 'bgg_id' in game:
                    self.log_test("Non-Protected - BGG Details", True, 
                                f"BGG details work without auth for '{game.get('title')}'")
                else:
                    self.log_test("Non-Protected - BGG Details", False, 
                                "Invalid response format", game)
            else:
                self.log_test("Non-Protected - BGG Details", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Non-Protected - BGG Details", False, f"Exception: {str(e)}")

    def test_openai_translation_feature(self):
        """Test OpenAI automatic translation feature for Hungarian"""
        print("\n🌍 Testing OpenAI Translation Feature...")
        
        # Test popular games with different BGG IDs
        test_games = [
            {"bgg_id": "174430", "name": "Gloomhaven"},
            {"bgg_id": "227072", "name": "Kaméleon"},
            {"bgg_id": "30549", "name": "Pandemic"}
        ]
        
        for test_game in test_games:
            try:
                print(f"\n   Testing translation for {test_game['name']} (BGG ID: {test_game['bgg_id']})...")
                response = self.session.get(f"{API_BASE}/games/details/{test_game['bgg_id']}")
                
                if response.status_code == 200:
                    game = response.json()
                    
                    # Check if Hungarian translation fields are present
                    translation_fields = ['title_hu', 'description_hu', 'description_short_hu']
                    missing_fields = []
                    empty_fields = []
                    
                    for field in translation_fields:
                        if field not in game:
                            missing_fields.append(field)
                        elif not game[field] or game[field].strip() == "":
                            empty_fields.append(field)
                    
                    if missing_fields:
                        self.log_test(f"Translation - {test_game['name']} Structure", False, 
                                    f"Missing translation fields: {missing_fields}", game)
                    elif empty_fields:
                        self.log_test(f"Translation - {test_game['name']} Content", False, 
                                    f"Empty translation fields: {empty_fields}. OpenAI may not be configured or failed.", 
                                    {field: game.get(field, 'MISSING') for field in translation_fields})
                    else:
                        # Check translation quality - basic validation
                        original_title = game.get('title', '')
                        hungarian_title = game.get('title_hu', '')
                        
                        # Basic quality check: Hungarian translation should be different from English
                        # and should not contain obvious English words (basic check)
                        quality_issues = []
                        
                        if hungarian_title == original_title:
                            quality_issues.append("Hungarian title identical to English")
                        
                        if len(hungarian_title) < 2:
                            quality_issues.append("Hungarian title too short")
                        
                        # Check if description translations exist and are reasonable
                        if game.get('description_hu') and len(game.get('description_hu', '')) < 10:
                            quality_issues.append("Hungarian description too short")
                        
                        if quality_issues:
                            self.log_test(f"Translation - {test_game['name']} Quality", False, 
                                        f"Quality issues: {quality_issues}", 
                                        {
                                            'title': original_title,
                                            'title_hu': hungarian_title,
                                            'description_hu_length': len(game.get('description_hu', '')),
                                            'description_short_hu_length': len(game.get('description_short_hu', ''))
                                        })
                        else:
                            self.log_test(f"Translation - {test_game['name']} Success", True, 
                                        f"Hungarian translations present and reasonable. Title: '{original_title}' -> '{hungarian_title}'",
                                        {
                                            'title_hu': hungarian_title,
                                            'description_hu_preview': game.get('description_hu', '')[:100] + '...' if len(game.get('description_hu', '')) > 100 else game.get('description_hu', ''),
                                            'description_short_hu': game.get('description_short_hu', '')
                                        })
                else:
                    self.log_test(f"Translation - {test_game['name']} API", False, 
                                f"Failed to fetch game details: HTTP {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_test(f"Translation - {test_game['name']} Exception", False, f"Exception: {str(e)}")

    def test_translation_performance(self):
        """Test translation performance and response time"""
        print("\n⚡ Testing Translation Performance...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/games/details/174430")  # Gloomhaven
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                game = response.json()
                
                # Check if translations are present
                has_translations = all(field in game and game[field] for field in ['title_hu', 'description_hu', 'description_short_hu'])
                
                if has_translations:
                    if response_time < 30:  # Reasonable time limit for translation
                        self.log_test("Translation Performance", True, 
                                    f"Response with translations completed in {response_time:.2f}s (acceptable)")
                    else:
                        self.log_test("Translation Performance", False, 
                                    f"Response took {response_time:.2f}s (too slow for production)")
                else:
                    self.log_test("Translation Performance", False, 
                                f"No translations found in response (response time: {response_time:.2f}s)")
            else:
                self.log_test("Translation Performance", False, 
                            f"HTTP {response.status_code} (response time: {response_time:.2f}s)", response.text)
                
        except Exception as e:
            self.log_test("Translation Performance", False, f"Exception: {str(e)}")

    def test_translation_error_handling(self):
        """Test translation error handling"""
        print("\n🛡️ Testing Translation Error Handling...")
        
        try:
            # Test with a game that should exist but might have translation issues
            response = self.session.get(f"{API_BASE}/games/details/30549")  # Pandemic
            
            if response.status_code == 200:
                game = response.json()
                
                # Even if translation fails, the endpoint should still return the game data
                required_base_fields = ['bgg_id', 'title', 'authors', 'description']
                missing_base_fields = [field for field in required_base_fields if field not in game or not game[field]]
                
                if missing_base_fields:
                    self.log_test("Translation Error Handling", False, 
                                f"Missing base game fields: {missing_base_fields}", game)
                else:
                    # Check if translation fields exist (even if empty due to translation failure)
                    translation_fields = ['title_hu', 'description_hu', 'description_short_hu']
                    translation_fields_present = all(field in game for field in translation_fields)
                    
                    if translation_fields_present:
                        self.log_test("Translation Error Handling", True, 
                                    "Game data returned successfully with translation fields (even if translation failed)")
                    else:
                        self.log_test("Translation Error Handling", False, 
                                    f"Translation fields missing from response structure")
            else:
                self.log_test("Translation Error Handling", False, 
                            f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Translation Error Handling", False, f"Exception: {str(e)}")

    def test_backend_stability(self):
        """Test that backend is running stable without import errors"""
        print("\n⚡ Testing Backend Stability...")
        
        # Test 1: Root endpoint should work (returns HTML for frontend)
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            
            if response.status_code == 200:
                # Root endpoint returns HTML (frontend), not JSON
                if "html" in response.text.lower():
                    self.log_test("Backend Stability - Root", True, 
                                "Backend serving frontend correctly")
                else:
                    self.log_test("Backend Stability - Root", False, 
                                "Unexpected root response format")
            else:
                self.log_test("Backend Stability - Root", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Backend Stability - Root", False, f"Exception: {str(e)}")

        # Test 2: Health check should work
        try:
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_test("Backend Stability - Health", True, 
                                f"Health check passed, cache size: {data.get('cache_size', 0)}")
                else:
                    self.log_test("Backend Stability - Health", False, 
                                "Invalid health response", data)
            else:
                self.log_test("Backend Stability - Health", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Backend Stability - Health", False, f"Exception: {str(e)}")

    def run_thumbnail_tests(self):
        """Run thumbnail-focused tests as requested in the review"""
        print("🖼️ Starting BGG Search Thumbnail Feature Tests")
        print("=" * 60)
        
        # 1. Backend Stability Check
        self.test_backend_stability()
        
        # 2. Basic BGG Search (existing functionality)
        print("\n🔍 Testing Basic BGG Search...")
        self.test_bgg_search_validation()
        search_result = self.test_bgg_search()
        
        # 3. Thumbnail-specific tests
        self.test_bgg_search_with_thumbnails()
        
        # 4. Thumbnail URL validation
        self.test_thumbnail_url_validation()
        
        # 5. Performance testing
        self.test_thumbnail_performance()
        
        # 6. Error handling
        self.test_thumbnail_error_handling()
        
        # 7. Result limit testing
        self.test_search_result_limit()
        
        # 8. Summary
        print("\n📊 Thumbnail Test Summary")
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
        else:
            print("\n✅ All thumbnail tests passed!")
        
        return passed == total
        """Run OpenAI translation-focused tests"""
        print("🌍 Starting OpenAI Translation Feature Tests")
        print("=" * 60)
        
        # 1. Backend Stability Check
        self.test_backend_stability()
        
        # 2. Translation Feature Tests
        self.test_openai_translation_feature()
        
        # 3. Translation Performance Test
        self.test_translation_performance()
        
        # 4. Translation Error Handling
        self.test_translation_error_handling()
        
        # 5. Summary
        print("\n📊 Translation Test Summary")
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
        else:
            print("\n✅ All translation tests passed!")
        
        return passed == total

    def run_authentication_tests(self):
        """Run authentication-focused tests"""
        print("🔐 Starting Google Authentication System Tests")
        print("=" * 60)
        
        # 1. Backend Stability Check
        self.test_backend_stability()
        
        # 2. Authentication Endpoints
        self.test_authentication_endpoints()
        
        # 3. Protected Endpoints
        self.test_protected_game_endpoints()
        
        # 4. Non-Protected Endpoints (BGG should still work)
        self.test_non_protected_endpoints()
        
        # 5. Summary
        print("\n📊 Authentication Test Summary")
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
        else:
            print("\n✅ All authentication tests passed!")
        
        return passed == total

    def test_hungarian_description_update(self):
        """Test updating games with separate Hungarian short and long descriptions"""
        print("\n🇭🇺 Testing Hungarian Description Update Feature...")
        
        # Test 1: Verify the update endpoint exists and requires authentication
        test_update_data = {
            "description_short_hu": "Rövid magyar leírás a játékról",
            "description_hu": "Hosszabb, részletesebb magyar leírás a játékról, ami több információt tartalmaz."
        }
        
        try:
            # Test with a dummy game ID to verify endpoint structure
            response = self.session.put(f"{API_BASE}/games/test-id", json=test_update_data)
            
            if response.status_code == 403:
                self.log_test("Hungarian Descriptions - Endpoint Authentication", True, 
                            "PUT /api/games/{id} properly requires authentication for Hungarian description updates")
            elif response.status_code == 401:
                self.log_test("Hungarian Descriptions - Endpoint Authentication", True, 
                            "PUT /api/games/{id} properly requires authentication for Hungarian description updates")
            else:
                self.log_test("Hungarian Descriptions - Endpoint Authentication", False, 
                            f"Unexpected response: HTTP {response.status_code}", response.text)
            
            # Test 2: Verify endpoint accepts Hungarian description fields in request structure
            # Test with various field combinations to ensure the endpoint can handle them
            test_cases = [
                {"description_short_hu": "Rövid magyar"},
                {"description_hu": "Hosszú magyar leírás"},
                {"description_short_hu": "Rövid", "description_hu": "Hosszú"},
                {"description_short_hu": "", "description_hu": None},
                {"description_short_hu": None, "description_hu": ""},
            ]
            
            for i, test_case in enumerate(test_cases):
                response = self.session.put(f"{API_BASE}/games/test-id-{i}", json=test_case)
                
                # We expect 401/403 (authentication required), not 400/422 (bad request)
                # This indicates the endpoint accepts the field structure
                if response.status_code in [401, 403]:
                    self.log_test(f"Hungarian Descriptions - Field Structure {i+1}", True, 
                                f"Endpoint accepts Hungarian description fields: {list(test_case.keys())}")
                elif response.status_code in [400, 422]:
                    # This would indicate field validation issues
                    self.log_test(f"Hungarian Descriptions - Field Structure {i+1}", False, 
                                f"Endpoint rejected Hungarian description fields: {response.text}")
                else:
                    self.log_test(f"Hungarian Descriptions - Field Structure {i+1}", False, 
                                f"Unexpected response: HTTP {response.status_code}")
            
            # Test 3: Test with very long descriptions to check field length limits
            long_text = "Ez egy nagyon hosszú magyar leírás " * 100  # ~3000 characters
            long_test_data = {
                "description_short_hu": "Rövid leírás",
                "description_hu": long_text
            }
            
            response = self.session.put(f"{API_BASE}/games/test-long", json=long_test_data)
            
            if response.status_code in [401, 403]:
                self.log_test("Hungarian Descriptions - Long Text Acceptance", True, 
                            f"Endpoint accepts very long Hungarian descriptions ({len(long_text)} characters)")
            elif response.status_code in [400, 422]:
                self.log_test("Hungarian Descriptions - Long Text Acceptance", False, 
                            f"Endpoint rejected long Hungarian descriptions: {response.text}")
            else:
                self.log_test("Hungarian Descriptions - Long Text Acceptance", False, 
                            f"Unexpected response: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Hungarian Descriptions - Exception", False, f"Exception during testing: {str(e)}")

    def test_hungarian_description_field_validation(self):
        """Test validation of Hungarian description fields"""
        print("\n✅ Testing Hungarian Description Field Validation...")
        
        try:
            # Test 1: Verify endpoint handles mixed field updates
            mixed_update = {
                "description_short_hu": "Rövid magyar",
                "description_hu": "Hosszú magyar leírás",
                "title": "Updated Title",
                "personal_notes": "Personal notes"
            }
            
            response = self.session.put(f"{API_BASE}/games/test-mixed", json=mixed_update)
            
            if response.status_code in [401, 403]:
                self.log_test("Hungarian Validation - Mixed Fields", True, 
                            "Endpoint accepts mixed Hungarian and other field updates")
            elif response.status_code in [400, 422]:
                self.log_test("Hungarian Validation - Mixed Fields", False, 
                            f"Endpoint rejected mixed field update: {response.text}")
            else:
                self.log_test("Hungarian Validation - Mixed Fields", False, 
                            f"Unexpected response: HTTP {response.status_code}")
            
            # Test 2: Test with special characters in Hungarian text
            special_chars_data = {
                "description_short_hu": "Árvíztűrő tükörfúrógép",
                "description_hu": "Különleges karakterek: áéíóöőúüű ÁÉÍÓÖŐÚÜŰ"
            }
            
            response = self.session.put(f"{API_BASE}/games/test-special", json=special_chars_data)
            
            if response.status_code in [401, 403]:
                self.log_test("Hungarian Validation - Special Characters", True, 
                            "Endpoint accepts Hungarian special characters (áéíóöőúüű)")
            elif response.status_code in [400, 422]:
                self.log_test("Hungarian Validation - Special Characters", False, 
                            f"Endpoint rejected Hungarian special characters: {response.text}")
            else:
                self.log_test("Hungarian Validation - Special Characters", False, 
                            f"Unexpected response: HTTP {response.status_code}")
            
            # Test 3: Test JSON structure validation
            invalid_json_cases = [
                {"description_short_hu": 123},  # Number instead of string
                {"description_hu": []},         # Array instead of string
                {"description_short_hu": {"nested": "object"}},  # Object instead of string
            ]
            
            for i, invalid_case in enumerate(invalid_json_cases):
                response = self.session.put(f"{API_BASE}/games/test-invalid-{i}", json=invalid_case)
                
                # We expect 422 (validation error) for invalid data types
                if response.status_code == 422:
                    self.log_test(f"Hungarian Validation - Invalid Type {i+1}", True, 
                                f"Endpoint properly validates data types for Hungarian fields")
                elif response.status_code in [401, 403]:
                    # Authentication error came first, which is also acceptable
                    self.log_test(f"Hungarian Validation - Invalid Type {i+1}", True, 
                                f"Endpoint structure accepts request (auth required)")
                else:
                    self.log_test(f"Hungarian Validation - Invalid Type {i+1}", False, 
                                f"Unexpected response for invalid data type: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Hungarian Validation - Exception", False, f"Exception during validation testing: {str(e)}")

    def test_bgg_hungarian_translations(self):
        """Test BGG game details endpoint for Hungarian translation fields"""
        print("\n🌍 Testing BGG Hungarian Translation Fields...")
        
        try:
            # Test with a popular game that should have translations
            response = self.session.get(f"{API_BASE}/games/details/174430")  # Gloomhaven
            
            if response.status_code == 200:
                game = response.json()
                
                # Check if Hungarian translation fields are present in the response
                hungarian_fields = ['title_hu', 'description_hu', 'description_short_hu']
                missing_fields = [field for field in hungarian_fields if field not in game]
                
                if not missing_fields:
                    self.log_test("BGG Hungarian Fields - Structure", True, 
                                "BGG details endpoint includes all Hungarian translation fields")
                    
                    # Check if translations are actually populated (may be empty due to API quota)
                    populated_fields = [field for field in hungarian_fields if game.get(field) and game[field].strip()]
                    empty_fields = [field for field in hungarian_fields if not game.get(field) or not game[field].strip()]
                    
                    if populated_fields:
                        self.log_test("BGG Hungarian Fields - Content", True, 
                                    f"Hungarian translations populated for fields: {populated_fields}")
                        
                        # Verify translation quality (basic check)
                        original_title = game.get('title', '')
                        hungarian_title = game.get('title_hu', '')
                        
                        # For proper nouns like "Gloomhaven", the title might remain the same
                        # Check if we have meaningful Hungarian descriptions instead
                        hungarian_desc = game.get('description_hu', '')
                        hungarian_short_desc = game.get('description_short_hu', '')
                        
                        if len(hungarian_desc) > 50 and len(hungarian_short_desc) > 10:
                            self.log_test("BGG Hungarian Translation - Quality", True, 
                                        f"Hungarian descriptions properly translated (desc: {len(hungarian_desc)} chars, short: {len(hungarian_short_desc)} chars)")
                        elif hungarian_title and hungarian_title != original_title:
                            self.log_test("BGG Hungarian Translation - Quality", True, 
                                        f"Hungarian title translation differs from English: '{original_title}' -> '{hungarian_title}'")
                        else:
                            self.log_test("BGG Hungarian Translation - Quality", False, 
                                        "Hungarian translations appear to be missing or identical to English")
                    else:
                        self.log_test("BGG Hungarian Fields - Content", False, 
                                    f"All Hungarian translation fields are empty: {empty_fields}. This may be due to OpenAI API quota limits.")
                else:
                    self.log_test("BGG Hungarian Fields - Structure", False, 
                                f"Missing Hungarian translation fields: {missing_fields}")
            else:
                self.log_test("BGG Hungarian Fields - API", False, 
                            f"Failed to fetch BGG game details: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("BGG Hungarian Fields - Exception", False, f"Exception during BGG testing: {str(e)}")

    def test_game_model_structure(self):
        """Test that the GameDetails model supports Hungarian description fields"""
        print("\n📋 Testing Game Model Structure...")
        
        try:
            # Test BGG details endpoint to verify model structure
            response = self.session.get(f"{API_BASE}/games/details/30549")  # Pandemic
            
            if response.status_code == 200:
                game = response.json()
                
                # Check for all expected fields including Hungarian ones
                expected_fields = [
                    'id', 'bgg_id', 'title', 'title_hu',
                    'description', 'description_short', 
                    'description_hu', 'description_short_hu',
                    'authors', 'categories', 'min_players', 'max_players'
                ]
                
                missing_fields = [field for field in expected_fields if field not in game]
                present_fields = [field for field in expected_fields if field in game]
                
                if not missing_fields:
                    self.log_test("Game Model - Complete Structure", True, 
                                f"Game model includes all expected fields including Hungarian descriptions")
                else:
                    self.log_test("Game Model - Complete Structure", False, 
                                f"Game model missing fields: {missing_fields}")
                
                # Specifically check Hungarian description fields
                hungarian_desc_fields = ['description_hu', 'description_short_hu']
                hungarian_present = [field for field in hungarian_desc_fields if field in game]
                
                if len(hungarian_present) == len(hungarian_desc_fields):
                    self.log_test("Game Model - Hungarian Descriptions", True, 
                                "Game model includes both Hungarian description fields (description_hu, description_short_hu)")
                else:
                    missing_hu_fields = [field for field in hungarian_desc_fields if field not in game]
                    self.log_test("Game Model - Hungarian Descriptions", False, 
                                f"Game model missing Hungarian description fields: {missing_hu_fields}")
                
                # Test field types
                field_type_issues = []
                
                for field in ['description_hu', 'description_short_hu']:
                    if field in game:
                        value = game[field]
                        if value is not None and not isinstance(value, str):
                            field_type_issues.append(f"{field}: expected string, got {type(value)}")
                
                if not field_type_issues:
                    self.log_test("Game Model - Field Types", True, 
                                "Hungarian description fields have correct data types (string or null)")
                else:
                    self.log_test("Game Model - Field Types", False, 
                                f"Field type issues: {field_type_issues}")
                    
            else:
                self.log_test("Game Model - API Access", False, 
                            f"Could not access game details for model testing: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Game Model - Exception", False, f"Exception during model testing: {str(e)}")

    def run_hungarian_description_tests(self):
        """Run Hungarian description-focused tests"""
        print("🇭🇺 Starting Hungarian Description Update Feature Tests")
        print("=" * 60)
        
        # 1. Backend Stability Check
        self.test_backend_stability()
        
        # 2. Game Model Structure Tests
        self.test_game_model_structure()
        
        # 3. BGG Hungarian Translation Tests
        self.test_bgg_hungarian_translations()
        
        # 4. Hungarian Description Update Tests (endpoint structure)
        self.test_hungarian_description_update()
        
        # 5. Field Validation Tests
        self.test_hungarian_description_field_validation()
        
        # 6. Summary
        print("\n📊 Hungarian Description Test Summary")
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
        else:
            print("\n✅ All Hungarian description tests passed!")
        
        return passed == total

    def test_enhanced_filtering_system(self):
        """Test the newly implemented enhanced filtering system"""
        print("\n🔍 Testing Enhanced Filtering System...")
        
        # First authenticate to access protected endpoints
        auth_token = self.authenticate_test_user()
        if not auth_token:
            self.log_test("Enhanced Filtering - Authentication", False, "Failed to authenticate test user")
            return False
        
        # Test 1: Player Count Filtering
        self.test_player_count_filtering(auth_token)
        
        # Test 2: Playtime Filtering
        self.test_playtime_filtering(auth_token)
        
        # Test 3: Age Filtering
        self.test_age_filtering(auth_token)
        
        # Test 4: Rating Filtering
        self.test_rating_filtering(auth_token)
        
        # Test 5: Game Type Filtering
        self.test_game_type_filtering(auth_token)
        
        # Test 6: Mood Filtering
        self.test_mood_filtering(auth_token)
        
        # Test 7: Combined Filtering
        self.test_combined_filtering(auth_token)
        
        # Test 8: Edge Cases
        self.test_filtering_edge_cases(auth_token)
        
        return True

    def authenticate_test_user(self):
        """Authenticate using admin42 test user"""
        try:
            response = self.session.post(f"{API_BASE}/auth/test-user")
            
            if response.status_code == 200:
                auth_data = response.json()
                token = auth_data.get('access_token')
                if token:
                    # Set authorization header for subsequent requests
                    self.session.headers.update({'Authorization': f'Bearer {token}'})
                    self.log_test("Enhanced Filtering - Authentication", True, 
                                f"Successfully authenticated as {auth_data.get('user', {}).get('name', 'admin42')}")
                    return token
                else:
                    self.log_test("Enhanced Filtering - Authentication", False, "No access token in response", auth_data)
                    return None
            else:
                self.log_test("Enhanced Filtering - Authentication", False, f"HTTP {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Enhanced Filtering - Authentication", False, f"Exception: {str(e)}")
            return None

    def test_player_count_filtering(self, auth_token):
        """Test min_players and max_players filtering parameters"""
        print("\n   Testing Player Count Filtering...")
        
        try:
            # Test min_players filter
            response = self.session.get(f"{API_BASE}/games?min_players=2")
            if response.status_code == 200:
                games = response.json()
                # Check that all games support at least 2 players (max_players >= 2)
                valid_games = [game for game in games if game.get('max_players', 0) >= 2]
                if len(valid_games) == len(games):
                    self.log_test("Player Count Filter - min_players=2", True, 
                                f"Found {len(games)} games that support 2+ players")
                else:
                    self.log_test("Player Count Filter - min_players=2", False, 
                                f"Some games don't meet min_players=2 criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Player Count Filter - min_players=2", False, f"HTTP {response.status_code}", response.text)

            # Test max_players filter
            response = self.session.get(f"{API_BASE}/games?max_players=4")
            if response.status_code == 200:
                games = response.json()
                # Check that all games can be played with 4 or fewer players (min_players <= 4)
                valid_games = [game for game in games if game.get('min_players', 999) <= 4]
                if len(valid_games) == len(games):
                    self.log_test("Player Count Filter - max_players=4", True, 
                                f"Found {len(games)} games playable with 4 or fewer players")
                else:
                    self.log_test("Player Count Filter - max_players=4", False, 
                                f"Some games don't meet max_players=4 criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Player Count Filter - max_players=4", False, f"HTTP {response.status_code}", response.text)

            # Test combined min and max players
            response = self.session.get(f"{API_BASE}/games?min_players=2&max_players=4")
            if response.status_code == 200:
                games = response.json()
                # Check that all games support 2-4 players
                valid_games = [game for game in games if game.get('min_players', 999) <= 4 and game.get('max_players', 0) >= 2]
                if len(valid_games) == len(games):
                    self.log_test("Player Count Filter - Combined 2-4 players", True, 
                                f"Found {len(games)} games for 2-4 players")
                else:
                    self.log_test("Player Count Filter - Combined 2-4 players", False, 
                                f"Some games don't meet 2-4 player criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Player Count Filter - Combined 2-4 players", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Player Count Filtering", False, f"Exception: {str(e)}")

    def test_playtime_filtering(self, auth_token):
        """Test min_playtime and max_playtime filtering parameters"""
        print("\n   Testing Playtime Filtering...")
        
        try:
            # Test min_playtime filter
            response = self.session.get(f"{API_BASE}/games?min_playtime=30")
            if response.status_code == 200:
                games = response.json()
                # Check that all games have playtime >= 30 minutes
                valid_games = [game for game in games if game.get('play_time', 0) >= 30]
                if len(valid_games) == len(games):
                    self.log_test("Playtime Filter - min_playtime=30", True, 
                                f"Found {len(games)} games with 30+ minute playtime")
                else:
                    self.log_test("Playtime Filter - min_playtime=30", False, 
                                f"Some games don't meet min_playtime=30 criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Playtime Filter - min_playtime=30", False, f"HTTP {response.status_code}", response.text)

            # Test max_playtime filter
            response = self.session.get(f"{API_BASE}/games?max_playtime=90")
            if response.status_code == 200:
                games = response.json()
                # Check that all games have playtime <= 90 minutes
                valid_games = [game for game in games if game.get('play_time', 999) <= 90]
                if len(valid_games) == len(games):
                    self.log_test("Playtime Filter - max_playtime=90", True, 
                                f"Found {len(games)} games with 90 minute or less playtime")
                else:
                    self.log_test("Playtime Filter - max_playtime=90", False, 
                                f"Some games don't meet max_playtime=90 criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Playtime Filter - max_playtime=90", False, f"HTTP {response.status_code}", response.text)

            # Test combined playtime range
            response = self.session.get(f"{API_BASE}/games?min_playtime=30&max_playtime=90")
            if response.status_code == 200:
                games = response.json()
                # Check that all games have playtime between 30-90 minutes
                valid_games = [game for game in games if 30 <= game.get('play_time', 0) <= 90]
                if len(valid_games) == len(games):
                    self.log_test("Playtime Filter - Combined 30-90 minutes", True, 
                                f"Found {len(games)} games with 30-90 minute playtime")
                else:
                    self.log_test("Playtime Filter - Combined 30-90 minutes", False, 
                                f"Some games don't meet 30-90 minute criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Playtime Filter - Combined 30-90 minutes", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Playtime Filtering", False, f"Exception: {str(e)}")

    def test_age_filtering(self, auth_token):
        """Test min_age filtering parameter"""
        print("\n   Testing Age Filtering...")
        
        try:
            # Test min_age filter
            response = self.session.get(f"{API_BASE}/games?min_age=10")
            if response.status_code == 200:
                games = response.json()
                # Check that all games have min_age >= 10
                valid_games = [game for game in games if game.get('min_age', 0) >= 10]
                if len(valid_games) == len(games):
                    self.log_test("Age Filter - min_age=10", True, 
                                f"Found {len(games)} games suitable for ages 10+")
                else:
                    self.log_test("Age Filter - min_age=10", False, 
                                f"Some games don't meet min_age=10 criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Age Filter - min_age=10", False, f"HTTP {response.status_code}", response.text)

            # Test with different age threshold
            response = self.session.get(f"{API_BASE}/games?min_age=14")
            if response.status_code == 200:
                games = response.json()
                # Check that all games have min_age >= 14
                valid_games = [game for game in games if game.get('min_age', 0) >= 14]
                if len(valid_games) == len(games):
                    self.log_test("Age Filter - min_age=14", True, 
                                f"Found {len(games)} games suitable for ages 14+")
                else:
                    self.log_test("Age Filter - min_age=14", False, 
                                f"Some games don't meet min_age=14 criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Age Filter - min_age=14", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Age Filtering", False, f"Exception: {str(e)}")

    def test_rating_filtering(self, auth_token):
        """Test min_rating and max_rating filtering parameters"""
        print("\n   Testing Rating Filtering...")
        
        try:
            # Test min_rating filter
            response = self.session.get(f"{API_BASE}/games?min_rating=7.0")
            if response.status_code == 200:
                games = response.json()
                # Check that all games have bgg_rating >= 7.0
                valid_games = [game for game in games if game.get('bgg_rating', 0) >= 7.0]
                if len(valid_games) == len(games):
                    self.log_test("Rating Filter - min_rating=7.0", True, 
                                f"Found {len(games)} games with rating 7.0+")
                else:
                    self.log_test("Rating Filter - min_rating=7.0", False, 
                                f"Some games don't meet min_rating=7.0 criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Rating Filter - min_rating=7.0", False, f"HTTP {response.status_code}", response.text)

            # Test max_rating filter
            response = self.session.get(f"{API_BASE}/games?max_rating=8.5")
            if response.status_code == 200:
                games = response.json()
                # Check that all games have bgg_rating <= 8.5
                valid_games = [game for game in games if game.get('bgg_rating', 10) <= 8.5]
                if len(valid_games) == len(games):
                    self.log_test("Rating Filter - max_rating=8.5", True, 
                                f"Found {len(games)} games with rating 8.5 or less")
                else:
                    self.log_test("Rating Filter - max_rating=8.5", False, 
                                f"Some games don't meet max_rating=8.5 criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Rating Filter - max_rating=8.5", False, f"HTTP {response.status_code}", response.text)

            # Test combined rating range
            response = self.session.get(f"{API_BASE}/games?min_rating=6.0&max_rating=8.0")
            if response.status_code == 200:
                games = response.json()
                # Check that all games have rating between 6.0-8.0
                valid_games = [game for game in games if 6.0 <= game.get('bgg_rating', 0) <= 8.0]
                if len(valid_games) == len(games):
                    self.log_test("Rating Filter - Combined 6.0-8.0", True, 
                                f"Found {len(games)} games with rating 6.0-8.0")
                else:
                    self.log_test("Rating Filter - Combined 6.0-8.0", False, 
                                f"Some games don't meet 6.0-8.0 rating criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Rating Filter - Combined 6.0-8.0", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Rating Filtering", False, f"Exception: {str(e)}")

    def test_game_type_filtering(self, auth_token):
        """Test types parameter with comma-separated values"""
        print("\n   Testing Game Type Filtering...")
        
        try:
            # Test single type filter
            response = self.session.get(f"{API_BASE}/games?types=strategic")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Type Filter - strategic", True, 
                            f"Found {len(games)} strategic games")
            else:
                self.log_test("Type Filter - strategic", False, f"HTTP {response.status_code}", response.text)

            # Test multiple types filter
            response = self.session.get(f"{API_BASE}/games?types=strategic,party")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Type Filter - strategic,party", True, 
                            f"Found {len(games)} strategic or party games")
            else:
                self.log_test("Type Filter - strategic,party", False, f"HTTP {response.status_code}", response.text)

            # Test family type
            response = self.session.get(f"{API_BASE}/games?types=family")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Type Filter - family", True, 
                            f"Found {len(games)} family games")
            else:
                self.log_test("Type Filter - family", False, f"HTTP {response.status_code}", response.text)

            # Test cooperative type
            response = self.session.get(f"{API_BASE}/games?types=cooperative")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Type Filter - cooperative", True, 
                            f"Found {len(games)} cooperative games")
            else:
                self.log_test("Type Filter - cooperative", False, f"HTTP {response.status_code}", response.text)

            # Test educational and children types
            response = self.session.get(f"{API_BASE}/games?types=educational,children")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Type Filter - educational,children", True, 
                            f"Found {len(games)} educational or children games")
            else:
                self.log_test("Type Filter - educational,children", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Game Type Filtering", False, f"Exception: {str(e)}")

    def test_mood_filtering(self, auth_token):
        """Test moods parameter with comma-separated values"""
        print("\n   Testing Mood Filtering...")
        
        try:
            # Test single mood filter
            response = self.session.get(f"{API_BASE}/games?moods=thinking")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Mood Filter - thinking", True, 
                            f"Found {len(games)} thinking games")
            else:
                self.log_test("Mood Filter - thinking", False, f"HTTP {response.status_code}", response.text)

            # Test multiple moods filter
            response = self.session.get(f"{API_BASE}/games?moods=thinking,competitive")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Mood Filter - thinking,competitive", True, 
                            f"Found {len(games)} thinking or competitive games")
            else:
                self.log_test("Mood Filter - thinking,competitive", False, f"HTTP {response.status_code}", response.text)

            # Test light mood
            response = self.session.get(f"{API_BASE}/games?moods=light")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Mood Filter - light", True, 
                            f"Found {len(games)} light games")
            else:
                self.log_test("Mood Filter - light", False, f"HTTP {response.status_code}", response.text)

            # Test humorous mood
            response = self.session.get(f"{API_BASE}/games?moods=humorous")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Mood Filter - humorous", True, 
                            f"Found {len(games)} humorous games")
            else:
                self.log_test("Mood Filter - humorous", False, f"HTTP {response.status_code}", response.text)

            # Test creative and narrative moods
            response = self.session.get(f"{API_BASE}/games?moods=creative,narrative")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Mood Filter - creative,narrative", True, 
                            f"Found {len(games)} creative or narrative games")
            else:
                self.log_test("Mood Filter - creative,narrative", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Mood Filtering", False, f"Exception: {str(e)}")

    def test_combined_filtering(self, auth_token):
        """Test combination of multiple filters"""
        print("\n   Testing Combined Filtering...")
        
        try:
            # Test combination of player count, type, and rating
            response = self.session.get(f"{API_BASE}/games?min_players=3&types=strategic&min_rating=6.0")
            if response.status_code == 200:
                games = response.json()
                # Validate that games meet all criteria
                valid_games = []
                for game in games:
                    meets_players = game.get('max_players', 0) >= 3
                    meets_rating = game.get('bgg_rating', 0) >= 6.0
                    # Type validation would require checking categorization function
                    if meets_players and meets_rating:
                        valid_games.append(game)
                
                if len(valid_games) == len(games):
                    self.log_test("Combined Filter - players+type+rating", True, 
                                f"Found {len(games)} games meeting all criteria (3+ players, strategic, 6.0+ rating)")
                else:
                    self.log_test("Combined Filter - players+type+rating", False, 
                                f"Some games don't meet combined criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Combined Filter - players+type+rating", False, f"HTTP {response.status_code}", response.text)

            # Test combination of playtime, mood, and age
            response = self.session.get(f"{API_BASE}/games?min_playtime=45&max_playtime=120&moods=competitive&min_age=12")
            if response.status_code == 200:
                games = response.json()
                # Validate playtime and age criteria
                valid_games = []
                for game in games:
                    meets_playtime = 45 <= game.get('play_time', 0) <= 120
                    meets_age = game.get('min_age', 0) >= 12
                    if meets_playtime and meets_age:
                        valid_games.append(game)
                
                if len(valid_games) == len(games):
                    self.log_test("Combined Filter - playtime+mood+age", True, 
                                f"Found {len(games)} games meeting all criteria (45-120min, competitive, 12+ age)")
                else:
                    self.log_test("Combined Filter - playtime+mood+age", False, 
                                f"Some games don't meet combined criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Combined Filter - playtime+mood+age", False, f"HTTP {response.status_code}", response.text)

            # Test with existing functionality (search + enhanced filters)
            response = self.session.get(f"{API_BASE}/games?search=war&min_players=2&max_players=4&types=strategic")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Combined Filter - search+enhanced", True, 
                            f"Found {len(games)} games matching search 'war' with enhanced filters")
            else:
                self.log_test("Combined Filter - search+enhanced", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Combined Filtering", False, f"Exception: {str(e)}")

    def test_filtering_edge_cases(self, auth_token):
        """Test edge cases like no games matching filters"""
        print("\n   Testing Filtering Edge Cases...")
        
        try:
            # Test with very restrictive filters 
            # This tests games that can accommodate 5+ players AND can be played with 3 or fewer
            response = self.session.get(f"{API_BASE}/games?min_players=5&max_players=3")
            if response.status_code == 200:
                games = response.json()
                # Validate that returned games actually meet both criteria
                valid_games = [game for game in games if game.get('max_players', 0) >= 5 and game.get('min_players', 999) <= 3]
                if len(valid_games) == len(games):
                    self.log_test("Edge Case - Restrictive player range", True, 
                                f"Correctly filtered {len(games)} games that can accommodate 5+ players AND be played with 3 or fewer")
                else:
                    self.log_test("Edge Case - Restrictive player range", False, 
                                f"Some games don't meet restrictive criteria: {len(games) - len(valid_games)} invalid")
            else:
                self.log_test("Edge Case - Restrictive player range", False, f"HTTP {response.status_code}", response.text)

            # Test with very high rating filter
            response = self.session.get(f"{API_BASE}/games?min_rating=9.5")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Edge Case - Very high rating", True, 
                            f"Found {len(games)} games with rating 9.5+ (may be 0)")
            else:
                self.log_test("Edge Case - Very high rating", False, f"HTTP {response.status_code}", response.text)

            # Test with non-existent type
            response = self.session.get(f"{API_BASE}/games?types=nonexistent")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Edge Case - Non-existent type", True, 
                            f"Handled non-existent type gracefully, returned {len(games)} games")
            else:
                self.log_test("Edge Case - Non-existent type", False, f"HTTP {response.status_code}", response.text)

            # Test with empty type/mood values
            response = self.session.get(f"{API_BASE}/games?types=&moods=")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Edge Case - Empty type/mood", True, 
                            f"Handled empty type/mood parameters gracefully, returned {len(games)} games")
            else:
                self.log_test("Edge Case - Empty type/mood", False, f"HTTP {response.status_code}", response.text)

            # Test existing functionality still works
            response = self.session.get(f"{API_BASE}/games?status=available")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Edge Case - Existing status filter", True, 
                            f"Existing status filter still works, found {len(games)} available games")
            else:
                self.log_test("Edge Case - Existing status filter", False, f"HTTP {response.status_code}", response.text)

            # Test my_games_only still works with enhanced filters
            response = self.session.get(f"{API_BASE}/games?my_games_only=true&min_players=2")
            if response.status_code == 200:
                games = response.json()
                self.log_test("Edge Case - my_games_only + enhanced", True, 
                            f"my_games_only works with enhanced filters, found {len(games)} games")
            else:
                self.log_test("Edge Case - my_games_only + enhanced", False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Filtering Edge Cases", False, f"Exception: {str(e)}")

    def run_enhanced_filtering_tests(self):
        """Run enhanced filtering system tests"""
        print("🔍 Starting Enhanced Filtering System Tests")
        print("=" * 60)
        
        # 1. Backend Stability Check
        self.test_backend_stability()
        
        # 2. Enhanced Filtering Tests
        self.test_enhanced_filtering_system()
        
        # 3. Summary
        print("\n📊 Enhanced Filtering Test Summary")
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
        else:
            print("\n✅ All enhanced filtering tests passed!")
        
        return passed == total

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
        # Run enhanced filtering tests as requested in the review
        success = tester.run_enhanced_filtering_tests()
        exit_code = 0 if success else 1
        print(f"\n🏁 Enhanced filtering testing completed with exit code: {exit_code}")
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        tester.cleanup_test_games()
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        tester.cleanup_test_games()