import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import { AuthProvider, useAuth } from './AuthContext';
import LoginScreen from './LoginScreen';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Nyelvi fordítások
const translations = {
  hu: {
    // Fejléc
    title: '🎲 Társasjáték Gyűjteményem',
    addGame: 'Játék hozzáadása',
    language: 'Language',
    
    // Szűrők
    allGames: 'Minden játék',
    myGames: 'Saját játékok',
    available: 'Elérhető',
    borrowed: 'Kölcsönadva',
    searchCollection: 'Keresés a gyűjteményben...',
    
    // Üres állapot
    noGamesYet: 'Még nincsenek játékok a gyűjteményben',
    startByAdding: 'Kezdd el az első társasjáték hozzáadásával!',
    addFirstGame: 'Első játék hozzáadása',
    
    // Játék kártya
    players: 'Játékosok',
    time: 'Idő',
    min: 'perc',
    complexity: 'Bonyolultság',
    designer: 'Tervező',
    borrowedBy: 'Kölcsönvevő',
    returnDate: 'Visszahozás',
    lendGame: 'Játék kölcsönadása',
    markReturned: 'Visszahozva',
    remove: 'Eltávolítás',
    
    // Játék hozzáadása modal
    addNewGame: 'Új játék hozzáadása',
    searchBGG: 'Keresés BoardGameGeek-en',
    enterGameName: 'Játék neve...',
    search: 'Keresés',
    searching: 'Keresés...',
    searchResults: 'Találatok:',
    released: 'Kiadás',
    
    // Játék részletek
    year: 'Év',
    categories: 'Kategóriák',
    description: 'Leírás',
    language: 'Nyelv',
    backToSearch: 'Vissza a kereséshez',
    addToCollection: 'Hozzáadás a gyűjteményhez',
    loadingDetails: 'Játék részletek betöltése...',
    
    // Magyar lokalizáció mezők
    hungarianTitle: 'Magyar cím',
    hungarianDescription: 'Magyar leírás',
    hungarianShortDescription: 'Magyar rövid leírás',
    hungarianLongDescription: 'Magyar hosszú leírás',
    gameLanguage: 'Játék nyelve',
    hungarian: 'Magyar',
    english: 'Angol',
    multilingual: 'Többnyelvű',
    optional: '(opcionális)',
    
    // Kölcsönzés modal
    lendGameTitle: 'Játék kölcsönadása',
    borrowerName: 'Kölcsönvevő neve',
    expectedReturn: 'Várható visszahozás',
    cancel: 'Mégse',
    confirm: 'Megerősítés',
    
    // Üzenetek
    gameAlreadyExists: 'Ez a játék már szerepel a gyűjteményben!',
    failedToAdd: 'Nem sikerült hozzáadni a játékot',
    failedToBorrow: 'Nem sikerült kölcsönadni a játékot',
    failedToReturn: 'Nem sikerült visszahozni a játékot',
    failedToDelete: 'Nem sikerült törölni a játékot',
    confirmDelete: 'Biztosan el szeretnéd távolítani ezt a játékot a gyűjteményből?',
    
    // Összetett szűrők
    advancedFilters: 'Részletes szűrők',
    showFilters: 'Szűrők megjelenítése',
    hideFilters: 'Szűrők elrejtése',
    
    // Új szűrők
    filterPlayers: 'Játékosok száma',
    filterDuration: 'Játékidő',
    filterAge: 'Ajánlott korosztály',
    filterType: 'Játék típusa',
    filterMood: 'Játék hangulata',
    filterRating: 'Értékelés',
    
    // Játékosok szűrő
    players1: '1 játékos',
    players2: '2 játékos',
    players3to4: '3-4 játékos', 
    players5plus: '5+ játékos',
    
    // Játékidő szűrő
    duration0to30: '0-30 perc',
    duration30to60: '30-60 perc',
    duration60to120: '60-120 perc',
    duration120plus: '120+ perc',
    
    // Korosztály
    age3plus: '3+',
    age6plus: '6+',
    age10plus: '10+',
    age14plus: '14+',
    age18plus: '18+',
    
    // Játék típusa
    typeParty: 'Party',
    typeStrategic: 'Stratégiai',
    typeFamily: 'Családi',
    typeCooperative: 'Kooperatív',
    typeEducational: 'Oktatási',
    typeChildren: 'Gyerek',
    typeSolo: 'Egyszemélyes',
    
    // Hangulat/stílus
    moodLight: 'Könnyed',
    moodHumorous: 'Humoros',
    moodThinking: 'Agyalós',
    moodCompetitive: 'Kompetitív',
    moodCreative: 'Kreatív',
    moodNarrative: 'Narratív',
    
    // Tulajdonosok
    owners: 'Tulajdonosok',
    ownedBy: 'Birtokosa',
    addToMyCollection: 'Nekem is megvan',
    alreadyOwned: 'Már a tiéd',
    multipleOwners: 'tulajdonos',
    minPlayers: 'Min. játékosok',
    maxPlayers: 'Max. játékosok',
    minTime: 'Min. játékidő (perc)',
    maxTime: 'Max. játékidő (perc)',
    minComplexity: 'Min. bonyolultság',
    maxComplexity: 'Max. bonyolultság',
    minYear: 'Legkorábbi év',
    maxYear: 'Legkésőbbi év',
    categoryFilter: 'Kategória',
    designerFilter: 'Tervező',
    clearFilters: 'Szűrők törlése',
    applyFilters: 'Szűrés',
    gridView: 'Rács nézet',
    listView: 'Lista nézet',
    
    // Sorrendezés
    sortBy: 'Rendezés',
    sortByRating: 'Értékelés szerint',
    sortByAlphabetical: 'ABC sorrend',
    sortByPlaytime: 'Játékidő szerint',
    sortOrderAsc: 'Növekvő',
    sortOrderDesc: 'Csökkenő',
    
    // Korhatár
    minAge: 'Korhatár',
    ageYears: 'éves kortól',
    
    // Rövid leírások
    shortDescription: 'Rövid leírás',
    editGame: 'Játék szerkesztése',
    saveChanges: 'Változtatások mentése',
    personalNotes: 'Saját megjegyzések',
    editTitle: 'Cím szerkesztése',
    editDescription: 'Leírás szerkesztése',
    
    // Játék részletek modal
    gameDetails: 'Játék részletei',
    rulesLink: 'Játékszabályok',
    website: 'Weboldal',
    close: 'Bezárás',
    
    // Authentikáció
    welcome: 'Üdvözöljük',
    logout: 'Kijelentkezés',
    profile: 'Profil',
  },
  en: {
    // Header
    title: '🎲 My Board Game Collection',
    addGame: 'Add Game',
    language: 'Nyelv',
    
    // Filters
    allGames: 'All Games',
    myGames: 'My Games',
    available: 'Available',
    borrowed: 'Borrowed',
    searchCollection: 'Search your collection...',
    showFilters: 'Show Filters',
    hideFilters: 'Hide Filters',
    
    // New filters
    filterPlayers: 'Player Count',
    filterDuration: 'Duration',
    filterAge: 'Recommended Age',
    filterType: 'Game Type',
    filterMood: 'Game Mood',
    filterRating: 'Rating',
    
    // Player count filter
    players1: '1 Player',
    players2: '2 Players',
    players3to4: '3-4 Players',
    players5plus: '5+ Players',
    
    // Duration filter
    duration0to30: '0-30 minutes',
    duration30to60: '30-60 minutes',
    duration60to120: '60-120 minutes',
    duration120plus: '120+ minutes',
    
    // Age categories
    age3plus: '3+',
    age6plus: '6+',
    age10plus: '10+',
    age14plus: '14+',
    age18plus: '18+',
    
    // Game types
    typeParty: 'Party',
    typeStrategic: 'Strategic',
    typeFamily: 'Family',
    typeCooperative: 'Cooperative',
    typeEducational: 'Educational',
    typeChildren: 'Children',
    typeSolo: 'Solo',
    
    // Mood/style
    moodLight: 'Light',
    moodHumorous: 'Humorous',
    moodThinking: 'Thinking',
    moodCompetitive: 'Competitive',
    moodCreative: 'Creative',
    moodNarrative: 'Narrative',
    
    // Empty state
    noGamesYet: 'No games in your collection yet',
    startByAdding: 'Start by adding your first board game!',
    addFirstGame: 'Add Your First Game',
    
    // Game card
    players: 'Players',
    time: 'Time',
    min: 'min',
    complexity: 'Complexity',
    designer: 'Designer',
    borrowedBy: 'Borrowed by',
    returnDate: 'Return date',
    lendGame: 'Lend Game',
    markReturned: 'Mark Returned',
    remove: 'Remove',
    
    // Add game modal
    addNewGame: 'Add New Game',
    searchBGG: 'Search BoardGameGeek',
    enterGameName: 'Enter game name...',
    search: 'Search',
    searching: 'Searching...',
    searchResults: 'Search Results:',
    released: 'Released',
    
    // Game details
    year: 'Year',
    categories: 'Categories',
    description: 'Description',
    language: 'Language',
    backToSearch: 'Back to Search',
    addToCollection: 'Add to Collection',
    loadingDetails: 'Loading game details...',
    
    // Hungarian localization fields
    hungarianTitle: 'Hungarian Title',
    hungarianDescription: 'Hungarian Description',
    hungarianShortDescription: 'Hungarian Short Description',
    hungarianLongDescription: 'Hungarian Long Description',
    gameLanguage: 'Game Language',
    hungarian: 'Hungarian',
    english: 'English',
    multilingual: 'Multilingual',
    optional: '(optional)',
    
    // Borrow modal
    lendGameTitle: 'Lend Game',
    borrowerName: 'Borrower Name',
    expectedReturn: 'Expected Return Date',
    cancel: 'Cancel',
    confirm: 'Confirm',
    
    // Messages
    gameAlreadyExists: 'This game is already in your collection!',
    failedToAdd: 'Failed to add game to collection',
    failedToBorrow: 'Failed to mark game as borrowed',
    failedToReturn: 'Failed to mark game as returned',
    failedToDelete: 'Failed to delete game',
    confirmDelete: 'Are you sure you want to remove this game from your collection?',
    
    // Advanced filters
    advancedFilters: 'Advanced Filters',
    
    // Owners
    owners: 'Owners',
    ownedBy: 'Owned by',
    addToMyCollection: 'I own this too',
    alreadyOwned: 'Already yours',
    multipleOwners: 'owners',
    minPlayers: 'Min. Players',
    maxPlayers: 'Max. Players',
    minTime: 'Min. Time (min)',
    maxTime: 'Max. Time (min)',
    minComplexity: 'Min. Complexity',
    maxComplexity: 'Max. Complexity',
    minYear: 'Earliest Year',
    maxYear: 'Latest Year',
    categoryFilter: 'Category',
    designerFilter: 'Designer',
    clearFilters: 'Clear Filters',
    applyFilters: 'Apply Filters',
    
    // View toggle
    gridView: 'Grid View',
    listView: 'List View',
    
    // Sorting
    sortBy: 'Sort by',
    sortByRating: 'By Rating',
    sortByAlphabetical: 'Alphabetical',
    sortByPlaytime: 'By Playtime',
    sortOrderAsc: 'Ascending',
    sortOrderDesc: 'Descending',
    
    // Age rating
    minAge: 'Age Rating',
    ageYears: 'years+',
    
    // Short descriptions
    shortDescription: 'Short Description',
    
    // Game edit
    editGame: 'Edit Game',
    saveChanges: 'Save Changes',
    personalNotes: 'Personal Notes',
    editTitle: 'Edit Title',
    editDescription: 'Edit Description',
    
    // Game details modal
    gameDetails: 'Game Details',
    rulesLink: 'Rules',
    website: 'Website',
    close: 'Close',
    
    // Authentication  
    welcome: 'Welcome',
    logout: 'Logout',
    profile: 'Profile',
    
    // Status
    statusAvailable: 'Available',
    statusBorrowed: 'Borrowed'
  }
};

// Language Context
const LanguageContext = createContext();

function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('hu');
  
  const t = (key) => {
    return translations[language][key] || key;
  };
  
  const toggleLanguage = () => {
    setLanguage(prev => prev === 'hu' ? 'en' : 'hu');
  };
  
  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, toggleLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

function useTranslation() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within LanguageProvider');
  }
  return context;
}

function AppContent() {
  const { t, language, toggleLanguage } = useTranslation();
  const { user, logout, isAuthenticated, loading } = useAuth();
  
  // Show loading screen while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-blue-100">
        <div className="text-center">
          <div className="text-6xl mb-4">🎲</div>
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Betöltés...</p>
        </div>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  // Main app content - all state hooks after auth checks
  const [games, setGames] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedGame, setSelectedGame] = useState(null);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [filter, setFilter] = useState('all');
  const [searchFilter, setSearchFilter] = useState('');
  const [borrowModal, setBorrowModal] = useState({ show: false, game: null });
  const [viewMode, setViewMode] = useState('grid'); // 'grid' vagy 'list'
  const [detailsModal, setDetailsModal] = useState({ show: false, game: null });
  const [editModal, setEditModal] = useState({ show: false, game: null });
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState({
    minPlayers: '',
    maxPlayers: '',
    minTime: '',
    maxTime: '',
    minComplexity: '',
    maxComplexity: '',
    minYear: '',
    maxYear: '',
    category: '',
    designer: ''
  });
  const [sortBy, setSortBy] = useState('rating'); // 'rating', 'alphabetical', 'playtime'
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc', 'desc'
  const [myGamesOnly, setMyGamesOnly] = useState(false); // false = minden játék, true = csak saját
  const [allGamesCount, setAllGamesCount] = useState(0); // Összes játék száma
  const [myGamesCount, setMyGamesCount] = useState(0); // Saját játékok száma
  const [newFilters, setNewFilters] = useState({
    players: [], // ['1', '2', '3-4', '5+']
    duration: [], // ['0-30', '30-60', '60-120', '120+']
    age: [], // ['3+', '6+', '10+', '14+', '18+']
    type: [], // ['party', 'strategic', 'family', 'cooperative', 'educational', 'children', 'solo']
    mood: [], // ['light', 'humorous', 'thinking', 'competitive', 'creative', 'narrative']
    rating: [5, 10] // [min, max] rating range
  });

  // HTML entitások dekódolása
  const decodeHtmlEntities = (str) => {
    if (!str) return str;
    const textArea = document.createElement('textarea');
    textArea.innerHTML = str;
    return textArea.value;
  };

  // Fetch user's game collection
  const fetchGames = async () => {
    try {
      const status = filter === 'all' ? undefined : filter;
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      if (searchFilter) params.append('search', searchFilter);
      if (myGamesOnly) params.append('my_games_only', 'true');
      
      const response = await axios.get(`${API_BASE_URL}/api/games?${params.toString()}`);
      let filteredGames = response.data;
      
      // HTML entitások dekódolása a lista elemekben is
      filteredGames = filteredGames.map(game => ({
        ...game,
        title: decodeHtmlEntities(game.title),
        description: decodeHtmlEntities(game.description),
        description_short: decodeHtmlEntities(game.description_short),
        title_hu: decodeHtmlEntities(game.title_hu),
        description_hu: decodeHtmlEntities(game.description_hu),
        description_short_hu: decodeHtmlEntities(game.description_short_hu)
      }));
      
      // Kliens oldali fejlett szűrés
      if (showAdvancedFilters) {
        filteredGames = filteredGames.filter(game => {
          // Játékosok száma szűrés
          if (advancedFilters.minPlayers && game.min_players < parseInt(advancedFilters.minPlayers)) return false;
          if (advancedFilters.maxPlayers && game.max_players > parseInt(advancedFilters.maxPlayers)) return false;
          
          // Játékidő szűrés
          if (advancedFilters.minTime && game.play_time < parseInt(advancedFilters.minTime)) return false;
          if (advancedFilters.maxTime && game.play_time > parseInt(advancedFilters.maxTime)) return false;
          
          // Bonyolultság szűrés
          if (advancedFilters.minComplexity && game.complexity_rating < parseFloat(advancedFilters.minComplexity)) return false;
          if (advancedFilters.maxComplexity && game.complexity_rating > parseFloat(advancedFilters.maxComplexity)) return false;
          
          // Kiadási év szűrés
          if (advancedFilters.minYear && game.release_year < parseInt(advancedFilters.minYear)) return false;
          if (advancedFilters.maxYear && game.release_year > parseInt(advancedFilters.maxYear)) return false;
          
          // Kategória szűrés
          if (advancedFilters.category && !game.categories.some(cat => 
            cat.toLowerCase().includes(advancedFilters.category.toLowerCase())
          )) return false;
          
          // Tervező szűrés
          if (advancedFilters.designer && !game.authors.some(author => 
            author.toLowerCase().includes(advancedFilters.designer.toLowerCase())
          )) return false;
          
          return true;
        });
      }
      
      // Sorrendezés
      filteredGames.sort((a, b) => {
        let compareValue = 0;
        
        switch (sortBy) {
          case 'rating':
            compareValue = (b.bgg_rating || 0) - (a.bgg_rating || 0);
            break;
          case 'alphabetical':
            const titleA = (language === 'hu' && a.title_hu) ? a.title_hu : a.title;
            const titleB = (language === 'hu' && b.title_hu) ? b.title_hu : b.title;
            compareValue = titleA.localeCompare(titleB, language === 'hu' ? 'hu' : 'en');
            break;
          case 'playtime':
            compareValue = (b.play_time || 0) - (a.play_time || 0);
            break;
          default:
            compareValue = 0;
        }
        
        return sortOrder === 'asc' ? -compareValue : compareValue;
      });
      
      setGames(filteredGames);
    } catch (error) {
      console.error('Error fetching games:', error);
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.log('Authentication expired, logging out...');
        logout();
      }
    }
  };

  useEffect(() => {
    fetchGames();
  }, [filter, searchFilter, advancedFilters, showAdvancedFilters, sortBy, sortOrder, myGamesOnly]);

  // Search BoardGameGeek
  const searchBGG = async () => {
    if (query.trim().length < 2) return;
    
    setIsSearching(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/games/search/${encodeURIComponent(query)}`);
      // HTML entitások dekódolása a keresési eredményekben is
      const decodedResults = response.data.map(game => ({
        ...game,
        name: decodeHtmlEntities(game.name)
      }));
      setSearchResults(decodedResults);
    } catch (error) {
      console.error('Error searching games:', error);
      alert('Hiba a keresés során: ' + (error.response?.data?.detail || error.message));
      setSearchResults([]);
    }
    setIsSearching(false);
  };

  // Get game details from BGG
  const getGameDetails = async (bggId) => {
    setIsLoadingDetails(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/games/details/${bggId}`);
      const gameData = response.data;
      
      // HTML entitások dekódolása
      gameData.title = decodeHtmlEntities(gameData.title);
      gameData.description = decodeHtmlEntities(gameData.description);
      gameData.description_short = decodeHtmlEntities(gameData.description_short);
      
      // Alapértelmezett nyelvi beállítások a felhasználó nyelvének megfelelően
      if (!gameData.title_hu) gameData.title_hu = '';
      if (!gameData.description_hu) gameData.description_hu = '';
      if (!gameData.description_short_hu) gameData.description_short_hu = '';
      if (!gameData.personal_notes) gameData.personal_notes = '';
      if (!gameData.bgg_rating) gameData.bgg_rating = 0;
      if (!gameData.min_age) gameData.min_age = 0;
      if (!gameData.description_short) gameData.description_short = '';
      
      // Ha magyar felületen keresünk, alapértelmezett nyelv legyen magyar
      if (!gameData.language) {
        gameData.language = language === 'hu' ? 'hu' : 'en';
      }
      
      setSelectedGame(gameData);
    } catch (error) {
      console.error('Error fetching game details:', error);
      alert('Hiba a játék részleteinek betöltésekor: ' + (error.response?.data?.detail || error.message));
    }
    setIsLoadingDetails(false);
  };

  // Add existing game to user's collection  
  const addToMyCollection = async (gameId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/games/${gameId}/add-to-my-collection`);
      await fetchGames(); // Frissítsük a listát
      // Nincs alert - silent hozzáadás
    } catch (error) {
      console.error('Error adding to collection:', error);
      if (error.response?.status === 409) {
        // Már birtokolja - silent, csak frissítés
        await fetchGames();
      } else {
        alert('Hiba történt a hozzáadáskor: ' + (error.response?.data?.detail || error.message));
      }
    }
  };

  // Remove game from user's collection
  const removeFromMyCollection = async (gameId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/games/${gameId}`);
      await fetchGames(); // Frissítsük a listát
      // Nincs alert - silent eltávolítás
    } catch (error) {
      console.error('Error removing from collection:', error);
      alert('Hiba történt az eltávolításkor: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Add game to collection
  const addGameToCollection = async (gameData) => {
    try {
      console.log('Adding game to collection:', gameData);
      const response = await axios.post(`${API_BASE_URL}/api/games`, gameData);
      console.log('Game added successfully:', response.data);
      await fetchGames();
      setShowAddModal(false);
      setSelectedGame(null);
      setSearchResults([]);
      setQuery('');
    } catch (error) {
      console.error('Error adding game:', error);
      if (error.response?.status === 409) {
        alert(t('gameAlreadyExists'));
      } else if (error.response?.status === 401 || error.response?.status === 403) {
        alert('Bejelentkezési hiba. Kérem jelentkezzen be újra.');
        logout();
      } else {
        const errorMsg = error.response?.data?.detail || error.message || 'Ismeretlen hiba';
        alert(`${t('failedToAdd')}: ${errorMsg}`);
      }
    }
  };

  // Borrow game
  const borrowGame = async (gameId, borrowerName, returnDate) => {
    try {
      await axios.put(`${API_BASE_URL}/api/games/${gameId}/borrow`, {
        game_id: gameId,
        borrower_name: borrowerName,
        return_date: returnDate
      });
      await fetchGames();
      setBorrowModal({ show: false, game: null });
    } catch (error) {
      console.error('Error borrowing game:', error);
      alert(t('failedToBorrow'));
    }
  };

  // Return game
  const returnGame = async (gameId) => {
    try {
      await axios.put(`${API_BASE_URL}/api/games/${gameId}/return`);
      await fetchGames();
    } catch (error) {
      console.error('Error returning game:', error);
      alert(t('failedToReturn'));
    }
  };

  // Delete game with proper confirmation
  const deleteGame = async (gameId, gameTitle) => {
    console.log('Delete game called:', gameId, gameTitle);
    const confirmMessage = `Biztosan el szeretnéd távolítani a "${gameTitle}" játékot a gyűjteményből?`;
    if (confirm(confirmMessage)) {
      console.log('User confirmed deletion');
      try {
        console.log('Making DELETE request to:', `${API_BASE_URL}/api/games/${gameId}`);
        const response = await axios.delete(`${API_BASE_URL}/api/games/${gameId}`);
        console.log('Delete response:', response.status);
        await fetchGames();
        console.log('Games refetched after deletion');
      } catch (error) {
        console.error('Error deleting game:', error);
        alert('Nem sikerült törölni a játékot: ' + (error.response?.data?.detail || error.message));
      }
    } else {
      console.log('User cancelled deletion');
    }
  };

  // Update game
  const updateGame = async (gameData) => {
    console.log('Update game called with data:', gameData);
    try {
      console.log('Making PUT request to:', `${API_BASE_URL}/api/games/${gameData.id}`);
      const response = await axios.put(`${API_BASE_URL}/api/games/${gameData.id}`, gameData);
      console.log('Update response:', response.status);
      await fetchGames();
      setEditModal({ show: false, game: null });
      console.log('Game updated successfully');
    } catch (error) {
      console.error('Error updating game:', error);
      alert('Nem sikerült frissíteni a játékot: ' + (error.response?.data?.detail || error.message));
    }
  };

  const clearAdvancedFilters = () => {
    setAdvancedFilters({
      minPlayers: '',
      maxPlayers: '',
      minTime: '',
      maxTime: '',
      minComplexity: '',
      maxComplexity: '',
      minYear: '',
      maxYear: '',
      category: '',
      designer: ''
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(language === 'hu' ? 'hu-HU' : 'en-US');
  };

  const AdvancedFilters = () => (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-gray-900">{t('advancedFilters')}</h3>
        <button
          onClick={clearAdvancedFilters}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {t('clearFilters')}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {/* Játékosok száma */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('minPlayers')}</label>
          <input
            type="number"
            min="1"
            value={advancedFilters.minPlayers}
            onChange={(e) => setAdvancedFilters({...advancedFilters, minPlayers: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="1"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('maxPlayers')}</label>
          <input
            type="number"
            min="1"
            value={advancedFilters.maxPlayers}
            onChange={(e) => setAdvancedFilters({...advancedFilters, maxPlayers: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="8"
          />
        </div>

        {/* Játékidő */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('minTime')}</label>
          <input
            type="number"
            min="1"
            value={advancedFilters.minTime}
            onChange={(e) => setAdvancedFilters({...advancedFilters, minTime: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="15"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('maxTime')}</label>
          <input
            type="number"
            min="1"
            value={advancedFilters.maxTime}
            onChange={(e) => setAdvancedFilters({...advancedFilters, maxTime: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="180"
          />
        </div>

        {/* Bonyolultság */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('minComplexity')}</label>
          <input
            type="number"
            min="0"
            max="5"
            step="0.1"
            value={advancedFilters.minComplexity}
            onChange={(e) => setAdvancedFilters({...advancedFilters, minComplexity: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="1.0"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('maxComplexity')}</label>
          <input
            type="number"
            min="0"
            max="5"
            step="0.1"
            value={advancedFilters.maxComplexity}
            onChange={(e) => setAdvancedFilters({...advancedFilters, maxComplexity: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="4.0"
          />
        </div>

        {/* Kiadási év */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('minYear')}</label>
          <input
            type="number"
            min="1900"
            max="2025"
            value={advancedFilters.minYear}
            onChange={(e) => setAdvancedFilters({...advancedFilters, minYear: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="1995"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('maxYear')}</label>
          <input
            type="number"
            min="1900"
            max="2025"
            value={advancedFilters.maxYear}
            onChange={(e) => setAdvancedFilters({...advancedFilters, maxYear: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="2023"
          />
        </div>

        {/* Kategória */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('categoryFilter')}</label>
          <input
            type="text"
            value={advancedFilters.category}
            onChange={(e) => setAdvancedFilters({...advancedFilters, category: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Strategy"
          />
        </div>

        {/* Tervező */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">{t('designerFilter')}</label>
          <input
            type="text"
            value={advancedFilters.designer}
            onChange={(e) => setAdvancedFilters({...advancedFilters, designer: e.target.value})}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Reiner Knizia"
          />
        </div>
      </div>
    </div>
  );

  const GameCard = ({ game }) => {
    const [ownersExpanded, setOwnersExpanded] = useState(false);
    const [showActionMenu, setShowActionMenu] = useState(false);
    
    // Bezárjuk a menüt, ha máshova kattintanak
    useEffect(() => {
      const handleClickOutside = () => {
        setShowActionMenu(false);
      };
      
      if (showActionMenu) {
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
      }
    }, [showActionMenu]);
    
    const getLanguageFlag = (lang) => {
      switch (lang) {
        case 'hu': return '🇭🇺';
        case 'en': return '🇬🇧';
        case 'multilang': return '🌍';
        default: return '🇬🇧';
      }
    };

    const displayTitle = language === 'hu' && game.title_hu ? game.title_hu : game.title;
    const displayShortDesc = language === 'hu' && game.description_short_hu ? game.description_short_hu : game.description_short;
    
    const userOwnsThis = game.owners && game.owners.some(owner => owner.user_id === user?.id);
    
    const handleOwnershipToggle = () => {
      if (userOwnsThis) {
        removeFromMyCollection(game.id);
      } else {
        addToMyCollection(game.id);
      }
    };

    return (
      <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
        <div 
          className="cursor-pointer relative"
          onClick={() => setDetailsModal({ show: true, game })}
        >
          {/* Négyzetes játék kép */}
          <div className="aspect-square relative">
            <img
              src={game.cover_image || '/api/placeholder/300/300'}
              alt={displayTitle}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.src = '/api/placeholder/300/300';
              }}
            />
            
            {/* Overlay információk a képen */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent">
              {/* BGG értékelés bal felső */}
              {game.bgg_rating > 0 && (
                <div className="absolute top-2 left-2 bg-yellow-500 text-black px-2 py-1 rounded-full text-xs font-bold">
                  ⭐ {game.bgg_rating.toFixed(1)}
                </div>
              )}
              
              {/* Játékosok száma és idő jobb felső */}
              <div className="absolute top-2 right-2 text-right">
                <div className="bg-black/70 text-white px-2 py-1 rounded-full text-xs font-medium mb-1">
                  👥 {game.min_players}-{game.max_players}
                </div>
                <div className="bg-black/70 text-white px-2 py-1 rounded-full text-xs font-medium mb-1">
                  ⏱️ {game.play_time}{t('min')}
                </div>
                {/* Korhatár */}
                {game.min_age > 0 && (
                  <div className="bg-black/70 text-white px-2 py-1 rounded-full text-xs font-medium">
                    🔞 {game.min_age}+
                  </div>
                )}
              </div>

              {/* Állapot és nyelvi zászló bal alsó */}
              <div className="absolute bottom-2 left-2 flex flex-col gap-1">
                <div className="text-xl">
                  {game.status === 'available' ? '✅' : '❌'}
                </div>
                <div className="text-xl">
                  {getLanguageFlag(game.language)}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Játék információk a kép alatt */}
        <div className="p-4">
          {/* Játék címe és művelet menü */}
          <div className="flex items-start justify-between mb-2">
            <h3 
              className="font-bold text-lg text-gray-900 line-clamp-2 cursor-pointer flex-1" 
              onClick={() => setDetailsModal({ show: true, game })}
            >
              {displayTitle}
            </h3>
            
            {/* Akció menü (három pont) */}
            <div className="relative ml-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowActionMenu(!showActionMenu);
                }}
                className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
                </svg>
              </button>
              
              {/* Dropdown menü */}
              {showActionMenu && (
                <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                  <div className="py-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setDetailsModal({ show: true, game });
                        setShowActionMenu(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                    >
                      📋 {t('gameDetails')}
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditModal({ show: true, game });
                        setShowActionMenu(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                    >
                      📝 {t('editGame')}
                    </button>
                    
                    {game.status === 'available' ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setBorrowModal({ show: true, game });
                          setShowActionMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                      >
                        🤝 {t('lendGame')}
                      </button>
                    ) : (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          returnGame(game.id);
                          setShowActionMenu(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                      >
                        ↩️ {t('markReturned')}
                      </button>
                    )}
                    
                    <hr className="my-1" />
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteGame(game.id, displayTitle);
                        setShowActionMenu(false);
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                    >
                      🗑️ {t('deleteGame')}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Rövid leírás */}
          {displayShortDesc && (
            <p className="text-sm text-gray-600 mb-4 line-clamp-3 leading-relaxed">
              {displayShortDesc}
            </p>
          )}

          {/* Tulajdonosok lenyíló rész */}
          {game.owners && game.owners.length > 0 && (
            <div className="mb-3 border border-gray-200 rounded-lg">
              {/* Tulajdonosok header - kattintható */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setOwnersExpanded(!ownersExpanded);
                }}
                className="w-full p-3 bg-gray-50 rounded-t-lg flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
              >
                <span className="text-sm font-medium text-gray-700">
                  {t('owners')} ({game.owners.length})
                </span>
                <svg 
                  className={`w-4 h-4 text-gray-500 transform transition-transform ${ownersExpanded ? 'rotate-180' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {/* Lenyíló tartalom */}
              {ownersExpanded && (
                <div className="p-3 border-t border-gray-200">
                  {/* Tulajdonosok listája */}
                  <div className="flex flex-wrap gap-1 mb-3">
                    {game.owners.map((owner, index) => (
                      <span
                        key={index}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          owner.user_id === user?.id 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {owner.user_name}
                      </span>
                    ))}
                  </div>
                  
                  {/* "Nekem is megvan" kapcsoló */}
                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                    <span className="text-sm text-gray-600">{t('addToMyCollection')}</span>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={userOwnsThis}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleOwnershipToggle();
                        }}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Kölcsönzési információ */}
          {game.status === 'borrowed' && (
            <div className="bg-orange-50 p-2 rounded-lg mb-3 text-xs">
              <p><span className="font-medium">{t('borrowedBy')}:</span> {game.borrowed_by}</p>
              <p><span className="font-medium">{t('returnDate')}:</span> {formatDate(game.return_date)}</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  const GameListItem = ({ game }) => {
    const getLanguageFlag = (lang) => {
      switch (lang) {
        case 'hu': return '🇭🇺';
        case 'en': return '🇬🇧';
        case 'multilang': return '🌍';
        default: return '🇬🇧';
      }
    };

    const displayTitle = language === 'hu' && game.title_hu ? game.title_hu : game.title;
    const displayShortDesc = language === 'hu' && game.description_short_hu ? game.description_short_hu : game.description_short;

    return (
      <div 
        className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow cursor-pointer"
        onClick={() => setDetailsModal({ show: true, game })}
      >
        <div className="flex items-start gap-4">
          {/* Négyzetes kép */}
          <div className="w-20 h-20 relative flex-shrink-0">
            <img
              src={game.cover_image || '/api/placeholder/80/80'}
              alt={displayTitle}
              className="w-full h-full object-cover rounded-lg"
              onError={(e) => {
                e.target.src = '/api/placeholder/80/80';
              }}
            />
            
            {/* Overlay BGG értékeléssel */}
            {game.bgg_rating > 0 && (
              <div className="absolute top-1 left-1 bg-yellow-500 text-black px-1 py-0.5 rounded text-xs font-bold">
                ⭐ {game.bgg_rating.toFixed(1)}
              </div>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-bold text-lg text-gray-900 truncate pr-4">{displayTitle}</h3>
              <div className="flex items-center gap-2 flex-shrink-0">
                <div className="text-xl">
                  {game.status === 'available' ? '✅' : '❌'}
                </div>
                <div className="text-lg">
                  {getLanguageFlag(game.language)}
                </div>
              </div>
            </div>
            
            {/* Alapvető játék információk */}
            <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-2">
              <div>👥 {game.min_players}-{game.max_players}</div>
              <div>⏱️ {game.play_time} {t('min')}</div>
              {game.min_age > 0 && <div>🔞 {game.min_age}+</div>}
            </div>

            {/* Rövid leírás */}
            {displayShortDesc && (
              <p className="text-sm text-gray-600 mb-3 line-clamp-2 leading-relaxed">
                {displayShortDesc}
              </p>
            )}

            {/* Kölcsönzési információ */}
            {game.status === 'borrowed' && (
              <div className="bg-orange-50 p-2 rounded-lg mb-3 text-sm">
                <p><span className="font-medium">{t('borrowedBy')}:</span> {game.borrowed_by}</p>
                <p><span className="font-medium">{t('returnDate')}:</span> {formatDate(game.return_date)}</p>
              </div>
            )}
          </div>

          {/* Akció gombok */}
          <div className="flex flex-col gap-2">
            {game.status === 'available' ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setBorrowModal({ show: true, game });
                }}
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                {t('lendGame')}
              </button>
            ) : (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  returnGame(game.id);
                }}
                className="bg-green-600 text-white px-3 py-1 rounded text-sm font-medium hover:bg-green-700 transition-colors"
              >
                {t('markReturned')}
              </button>
            )}
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                setEditModal({ show: true, game });
              }}
              className="border border-blue-300 text-blue-600 px-3 py-1 rounded text-sm font-medium hover:bg-blue-50 transition-colors"
            >
              📝
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation();
                deleteGame(game.id, displayTitle);
              }}
              className="border border-red-300 text-red-600 px-3 py-1 rounded text-sm font-medium hover:bg-red-50 transition-colors"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    );
  };

  const SearchResultCard = ({ game }) => {
    // Generate a consistent color based on game name for placeholder
    const getPlaceholderColor = (name) => {
      const colors = [
        'bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-red-500', 
        'bg-yellow-500', 'bg-indigo-500', 'bg-pink-500', 'bg-gray-500'
      ];
      const index = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
      return colors[index % colors.length];
    };
    
    const placeholderColor = getPlaceholderColor(game.name);
    const gameInitial = game.name.charAt(0).toUpperCase();
    
    return (
      <div 
        className="flex items-center p-4 bg-white rounded-lg shadow hover:shadow-md cursor-pointer transition-shadow"
        onClick={() => getGameDetails(game.id)}
      >
        {/* Game Image or Placeholder */}
        <div className="w-16 h-16 flex-shrink-0 mr-4">
          {game.thumbnail ? (
            <img
              src={game.thumbnail}
              alt={game.name}
              className="w-full h-full object-cover rounded-lg border border-gray-200"
              onError={(e) => {
                // If image fails, replace with colored placeholder
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          
          {/* Colored placeholder with initial */}
          <div 
            className={`w-full h-full ${placeholderColor} rounded-lg flex items-center justify-center text-white font-bold text-xl border border-gray-200 ${game.thumbnail ? 'hidden' : 'flex'}`}
          >
            {gameInitial}
          </div>
        </div>
        
        {/* Game Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{game.name}</h3>
          {game.year && <p className="text-sm text-gray-500">{t('released')}: {game.year}</p>}
        </div>
        
        {/* Arrow Icon */}
        <svg className="w-5 h-5 text-gray-400 flex-shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    );
  };

  const BorrowModal = ({ show, game, onClose, onConfirm }) => {
    const [borrowerName, setBorrowerName] = useState('');
    const [returnDate, setReturnDate] = useState('');

    const handleSubmit = (e) => {
      e.preventDefault();
      if (borrowerName.trim() && returnDate) {
        onConfirm(game.id, borrowerName.trim(), returnDate);
        setBorrowerName('');
        setReturnDate('');
      }
    };

    if (!show) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-xl p-6 max-w-md w-full">
          <h2 className="text-xl font-bold mb-4">{t('lendGameTitle')}: {game?.title}</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('borrowerName')}
              </label>
              <input
                type="text"
                value={borrowerName}
                onChange={(e) => setBorrowerName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('expectedReturn')}
              </label>
              <input
                type="date"
                value={returnDate}
                onChange={(e) => setReturnDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min={new Date().toISOString().split('T')[0]}
                required
              />
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                {t('cancel')}
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {t('confirm')}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const EditGameModal = ({ show, game, onClose, onSave }) => {
    const [editedGame, setEditedGame] = useState(null);

    useEffect(() => {
      if (game) {
        setEditedGame({
          ...game,
          title_hu: game.title_hu || '',
          description_hu: game.description_hu || '',
          description_short_hu: game.description_short_hu || '',
          personal_notes: game.personal_notes || ''
        });
      }
    }, [game]);

    if (!show || !editedGame) return null;

    const handleSave = () => {
      onSave(editedGame);
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">{t('editGame')}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-6">
            <div className="flex gap-4">
              <img
                src={editedGame.cover_image || '/api/placeholder/120/160'}
                alt={editedGame.title}
                className="w-20 h-28 object-cover rounded-lg"
                onError={(e) => {
                  e.target.src = '/api/placeholder/120/160';
                }}
              />
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900 mb-2">{editedGame.title}</h3>
                <p className="text-sm text-gray-600">BGG ID: {editedGame.bgg_id}</p>
              </div>
            </div>

            {/* Magyar cím szerkesztése */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('hungarianTitle')} {t('optional')}
              </label>
              <input
                type="text"
                value={editedGame.title_hu}
                onChange={(e) => setEditedGame({...editedGame, title_hu: e.target.value})}
                placeholder={editedGame.title}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Játék nyelve */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('gameLanguage')}
              </label>
              <select
                value={editedGame.language}
                onChange={(e) => setEditedGame({...editedGame, language: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="hu">{t('hungarian')}</option>
                <option value="en">{t('english')}</option>
                <option value="multilang">{t('multilingual')}</option>
              </select>
            </div>

            {/* Magyar rövid leírás */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('hungarianShortDescription')} {t('optional')}
              </label>
              <textarea
                value={editedGame.description_short_hu}
                onChange={(e) => setEditedGame({...editedGame, description_short_hu: e.target.value})}
                placeholder={editedGame.description_short ? editedGame.description_short : 'Rövid összefoglaló a játékról...'}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Magyar hosszú leírás */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('hungarianLongDescription')} {t('optional')}
              </label>
              <textarea
                value={editedGame.description_hu}
                onChange={(e) => setEditedGame({...editedGame, description_hu: e.target.value})}
                placeholder={editedGame.description ? editedGame.description.substring(0, 100) + '...' : 'Részletes leírás a játékról...'}
                rows={5}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Saját megjegyzések */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('personalNotes')}
              </label>
              <textarea
                value={editedGame.personal_notes}
                onChange={(e) => setEditedGame({...editedGame, personal_notes: e.target.value})}
                placeholder={language === 'hu' ? 'Saját észrevételeid, tapasztalataid erről a játékról...' : 'Your personal thoughts and experiences about this game...'}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="flex gap-3 pt-4">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                {t('cancel')}
              </button>
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {t('saveChanges')}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const GameDetailsModal = ({ show, game, onClose }) => {
    if (!show || !game) return null;

    const displayTitle = language === 'hu' && game.title_hu ? game.title_hu : game.title;
    const displayDescription = language === 'hu' && game.description_hu ? game.description_hu : game.description;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">{t('gameDetails')}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Játék képe és alapadatok */}
            <div className="md:col-span-1">
              <img
                src={game.cover_image || '/api/placeholder/300/400'}
                alt={displayTitle}
                className="w-full rounded-lg shadow-lg"
                onError={(e) => {
                  e.target.src = '/api/placeholder/300/400';
                }}
              />
              
              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    game.status === 'available' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-orange-100 text-orange-800'
                  }`}>
                    {game.status === 'available' ? t('statusAvailable') : t('statusBorrowed')}
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    game.language === 'hu' ? 'bg-red-100 text-red-800' :
                    game.language === 'multilang' ? 'bg-green-100 text-green-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {game.language === 'hu' ? t('hungarian') :
                     game.language === 'multilang' ? t('multilingual') : t('english')}
                  </div>
                </div>
              </div>
            </div>

            {/* Játék részletek */}
            <div className="md:col-span-2">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{displayTitle}</h1>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">{t('year')}</div>
                  <div className="font-semibold">{game.release_year}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">{t('players')}</div>
                  <div className="font-semibold">{game.min_players}-{game.max_players}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">{t('time')}</div>
                  <div className="font-semibold">{game.play_time} {t('min')}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">{t('complexity')}</div>
                  <div className="font-semibold">{game.complexity_rating.toFixed(1)}/5</div>
                </div>
              </div>

              {game.authors.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-medium text-gray-900 mb-2">{t('designer')}</h3>
                  <p className="text-gray-600">{game.authors.join(', ')}</p>
                </div>
              )}

              {game.categories.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-medium text-gray-900 mb-2">{t('categories')}</h3>
                  <div className="flex flex-wrap gap-2">
                    {game.categories.map((category, index) => (
                      <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {displayDescription && (
                <div className="mb-6">
                  <h3 className="font-medium text-gray-900 mb-2">{t('description')}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">{displayDescription}</p>
                </div>
              )}

              {game.personal_notes && (
                <div className="mb-6 bg-yellow-50 p-4 rounded-lg">
                  <h3 className="font-medium text-yellow-900 mb-2">{t('personalNotes')}</h3>
                  <p className="text-yellow-800 text-sm leading-relaxed">{game.personal_notes}</p>
                </div>
              )}

              {game.status === 'borrowed' && (
                <div className="bg-orange-50 p-4 rounded-lg mb-6">
                  <h3 className="font-medium text-orange-900 mb-2">{t('statusBorrowed')}</h3>
                  <p className="text-orange-700"><span className="font-medium">{t('borrowedBy')}:</span> {game.borrowed_by}</p>
                  <p className="text-orange-700"><span className="font-medium">{t('returnDate')}:</span> {formatDate(game.return_date)}</p>
                </div>
              )}

              <div className="flex gap-3">
                <a
                  href={game.rules_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-center font-medium hover:bg-blue-700 transition-colors"
                >
                  {t('rulesLink')}
                </a>

                <button
                  onClick={() => {
                    setEditModal({ show: true, game });
                    onClose();
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors"
                >
                  {t('editGame')}
                </button>
                
                {game.status === 'available' ? (
                  <button
                    onClick={() => {
                      setBorrowModal({ show: true, game });
                      onClose();
                    }}
                    className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors"
                  >
                    {t('lendGame')}
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      returnGame(game.id);
                      onClose();
                    }}
                    className="flex-1 bg-yellow-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-yellow-700 transition-colors"
                  >
                    {t('markReturned')}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">
              {t('title')}
            </h1>
            <div className="flex items-center gap-4">
              {/* User welcome */}
              {user && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span>{t('welcome')}, {user.name || user.email}!</span>
                  {user.picture && (
                    <img
                      src={user.picture}
                      alt="User"
                      className="w-8 h-8 rounded-full border-2 border-gray-200"
                    />
                  )}
                </div>
              )}
              
              <button
                onClick={toggleLanguage}
                className="px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {language === 'hu' ? 'EN' : 'HU'}
              </button>
              
              <button
                onClick={() => setShowAddModal(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                {t('addGame')}
              </button>
              
              <button
                onClick={logout}
                className="px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
              >
                {t('logout')}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="mb-8 flex flex-col sm:flex-row gap-4">
          <div className="flex gap-2">
            <button
              onClick={() => setMyGamesOnly(false)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                !myGamesOnly
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {t('allGames')} ({games.length})
            </button>
            <button
              onClick={() => setMyGamesOnly(true)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                myGamesOnly
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {t('myGames')}
            </button>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {t('available')}
            </button>
            <button
              onClick={() => setFilter('borrowed')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'borrowed'
                  ? 'bg-green-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {t('borrowed')}
            </button>
          </div>
          
          <div className="flex-1">
            <input
              type="text"
              placeholder={t('searchCollection')}
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Sorting Controls */}
          <div className="flex gap-2">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              <option value="rating">{t('sortByRating')}</option>
              <option value="alphabetical">{t('sortByAlphabetical')}</option>
              <option value="playtime">{t('sortByPlaytime')}</option>
            </select>
            
            <button
              onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
              title={sortOrder === 'desc' ? t('sortOrderDesc') : t('sortOrderAsc')}
            >
              {sortOrder === 'desc' ? '↓' : '↑'}
            </button>
          </div>

          {/* View Toggle */}
          <div className="flex gap-2">
            <button
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                showAdvancedFilters
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <svg className="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              {showAdvancedFilters ? t('hideFilters') : t('showFilters')}
            </button>
            
            <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'list'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Advanced Filters */}
        {showAdvancedFilters && <AdvancedFilters />}

        {/* Games Display */}
        {games.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🎲</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('noGamesYet')}</h2>
            <p className="text-gray-600 mb-6">{t('startByAdding')}</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              {t('addFirstGame')}
            </button>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {games.map((game) => (
              <GameCard key={game.id} game={game} />
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {games.map((game) => (
              <GameListItem key={game.id} game={game} />
            ))}
          </div>
        )}
      </div>

      {/* Add Game Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">{t('addNewGame')}</h2>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setSelectedGame(null);
                  setSearchResults([]);
                  setQuery('');
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {!selectedGame ? (
              <div>
                {/* Search */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('searchBGG')}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && searchBGG()}
                      placeholder={t('enterGameName')}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                      onClick={searchBGG}
                      disabled={isSearching || query.trim().length < 2}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {isSearching ? t('searching') : t('search')}
                    </button>
                  </div>
                </div>

                {/* Search Results */}
                {searchResults.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="font-medium text-gray-900">{t('searchResults')}</h3>
                    {searchResults.map((game) => (
                      <SearchResultCard key={game.id} game={game} />
                    ))}
                  </div>
                )}
              </div>
            ) : (
              /* Game Details */
              <div>
                {isLoadingDetails ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">{t('loadingDetails')}</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex gap-4">
                      {selectedGame.cover_image && (
                        <img
                          src={selectedGame.cover_image}
                          alt={selectedGame.title}
                          className="w-32 h-32 object-cover rounded-lg"
                        />
                      )}
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 mb-2">{selectedGame.title}</h3>
                        <div className="space-y-1 text-sm text-gray-600">
                          <p><span className="font-medium">{t('year')}:</span> {selectedGame.release_year}</p>
                          <p><span className="font-medium">{t('players')}:</span> {selectedGame.min_players}-{selectedGame.max_players}</p>
                          <p><span className="font-medium">{t('time')}:</span> {selectedGame.play_time} {t('min')}</p>
                          <p><span className="font-medium">{t('complexity')}:</span> {selectedGame.complexity_rating.toFixed(1)}/5</p>
                          {selectedGame.authors.length > 0 && (
                            <p><span className="font-medium">{t('designer')}:</span> {selectedGame.authors.join(', ')}</p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Magyar lokalizációs mezők */}
                    <div className="space-y-4 bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900">{t('hungarianTitle')} {t('optional')}</h4>
                      <input
                        type="text"
                        value={selectedGame.title_hu || ''}
                        onChange={(e) => setSelectedGame({...selectedGame, title_hu: e.target.value})}
                        placeholder={selectedGame.title}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {t('gameLanguage')}
                        </label>
                        <select
                          value={selectedGame.language || 'en'}
                          onChange={(e) => setSelectedGame({...selectedGame, language: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="hu">{t('hungarian')}</option>
                          <option value="en">{t('english')}</option>
                          <option value="multilang">{t('multilingual')}</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {t('hungarianDescription')} {t('optional')}
                        </label>
                        <textarea
                          value={selectedGame.description_hu || ''}
                          onChange={(e) => setSelectedGame({...selectedGame, description_hu: e.target.value})}
                          placeholder={selectedGame.description.substring(0, 100) + '...'}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    {selectedGame.categories.length > 0 && (
                      <div>
                        <span className="font-medium text-gray-700">{t('categories')}: </span>
                        <div className="inline-flex flex-wrap gap-1 mt-1">
                          {selectedGame.categories.map((category, index) => (
                            <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                              {category}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedGame.description && (
                      <div>
                        <span className="font-medium text-gray-700">{t('description')}:</span>
                        <p className="text-sm text-gray-600 mt-1 max-h-32 overflow-y-auto">
                          {selectedGame.description}
                        </p>
                      </div>
                    )}

                    <div className="flex gap-3 pt-4">
                      <button
                        onClick={() => setSelectedGame(null)}
                        className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                      >
                        {t('backToSearch')}
                      </button>
                      <button
                        onClick={() => addGameToCollection(selectedGame)}
                        className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        {t('addToCollection')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Edit Game Modal */}
      <EditGameModal
        show={editModal.show}
        game={editModal.game}
        onClose={() => setEditModal({ show: false, game: null })}
        onSave={updateGame}
      />

      {/* Game Details Modal */}
      <GameDetailsModal
        show={detailsModal.show}
        game={detailsModal.game}
        onClose={() => setDetailsModal({ show: false, game: null })}
      />

      {/* Borrow Modal */}
      <BorrowModal
        show={borrowModal.show}
        game={borrowModal.game}
        onClose={() => setBorrowModal({ show: false, game: null })}
        onConfirm={borrowGame}
      />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <AppContent />
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;