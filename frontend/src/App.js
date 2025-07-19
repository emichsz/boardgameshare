import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
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
    allGames: 'Összes játék',
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
    
    // Nézet váltás
    gridView: 'Rács nézet',
    listView: 'Lista nézet',
    
    // Játék részletek modal
    gameDetails: 'Játék részletei',
    rulesLink: 'Játékszabályok',
    website: 'Weboldal',
    close: 'Bezárás',
  },
  en: {
    // Header
    title: '🎲 My Board Game Collection',
    addGame: 'Add Game',
    language: 'Nyelv',
    
    // Filters
    allGames: 'All Games',
    available: 'Available',
    borrowed: 'Borrowed',
    searchCollection: 'Search your collection...',
    
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
    
    // View toggle
    gridView: 'Grid View',
    listView: 'List View',
    
    // Game details modal
    gameDetails: 'Game Details',
    rulesLink: 'Rules',
    website: 'Website',
    close: 'Close',
    
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

  // Fetch user's game collection
  const fetchGames = async () => {
    try {
      const status = filter === 'all' ? undefined : filter;
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      if (searchFilter) params.append('search', searchFilter);
      
      const response = await axios.get(`${API_BASE_URL}/api/games?${params.toString()}`);
      setGames(response.data);
    } catch (error) {
      console.error('Error fetching games:', error);
    }
  };

  useEffect(() => {
    fetchGames();
  }, [filter, searchFilter]);

  // Search BoardGameGeek
  const searchBGG = async () => {
    if (query.trim().length < 2) return;
    
    setIsSearching(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/games/search/${encodeURIComponent(query)}`);
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error searching games:', error);
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
      
      // Alapértelmezett nyelvi beállítások a felhasználó nyelvének megfelelően
      if (!gameData.title_hu) gameData.title_hu = '';
      if (!gameData.description_hu) gameData.description_hu = '';
      
      // Ha magyar felületen keresünk, alapértelmezett nyelv legyen magyar
      if (!gameData.language) {
        gameData.language = language === 'hu' ? 'hu' : 'en';
      }
      
      setSelectedGame(gameData);
    } catch (error) {
      console.error('Error fetching game details:', error);
    }
    setIsLoadingDetails(false);
  };

  // Add game to collection
  const addGameToCollection = async (gameData) => {
    try {
      await axios.post(`${API_BASE_URL}/api/games`, gameData);
      await fetchGames();
      setShowAddModal(false);
      setSelectedGame(null);
      setSearchResults([]);
      setQuery('');
    } catch (error) {
      console.error('Error adding game:', error);
      if (error.response?.status === 409) {
        alert(t('gameAlreadyExists'));
      } else {
        alert(t('failedToAdd'));
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

  // Delete game
  const deleteGame = async (gameId) => {
    if (window.confirm(t('confirmDelete'))) {
      try {
        await axios.delete(`${API_BASE_URL}/api/games/${gameId}`);
        await fetchGames();
      } catch (error) {
        console.error('Error deleting game:', error);
        alert(t('failedToDelete'));
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(language === 'hu' ? 'hu-HU' : 'en-US');
  };

  const GameCard = ({ game }) => {
    const getLanguageLabel = (lang) => {
      switch (lang) {
        case 'hu': return t('hungarian');
        case 'en': return t('english');
        case 'multilang': return t('multilingual');
        default: return t('english');
      }
    };

    const getLanguageColor = (lang) => {
      switch (lang) {
        case 'hu': return 'bg-red-100 text-red-800';
        case 'en': return 'bg-blue-100 text-blue-800';
        case 'multilang': return 'bg-green-100 text-green-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    };

    const displayTitle = language === 'hu' && game.title_hu ? game.title_hu : game.title;

    return (
      <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
        <div 
          className="cursor-pointer"
          onClick={() => setDetailsModal({ show: true, game })}
        >
          <div className="aspect-w-3 aspect-h-4 relative">
            <img
              src={game.cover_image || '/api/placeholder/300/400'}
              alt={displayTitle}
              className="w-full h-48 object-cover"
              onError={(e) => {
                e.target.src = '/api/placeholder/300/400';
              }}
            />
            <div className="absolute top-2 right-2 flex flex-col gap-1">
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                game.status === 'available' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-orange-100 text-orange-800'
              }`}>
                {game.status === 'available' ? t('statusAvailable') : t('statusBorrowed')}
              </div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${getLanguageColor(game.language)}`}>
                {getLanguageLabel(game.language)}
              </div>
            </div>
          </div>
          
          <div className="p-4">
            <h3 className="font-bold text-lg text-gray-900 mb-2 line-clamp-2">{displayTitle}</h3>
            
            <div className="space-y-2 text-sm text-gray-600 mb-4">
              <p><span className="font-medium">{t('players')}:</span> {game.min_players}-{game.max_players}</p>
              <p><span className="font-medium">{t('time')}:</span> {game.play_time} {t('min')}</p>
              <p><span className="font-medium">{t('complexity')}:</span> {game.complexity_rating.toFixed(1)}/5</p>
              {game.authors.length > 0 && (
                <p><span className="font-medium">{t('designer')}:</span> {game.authors.join(', ')}</p>
              )}
            </div>

            {game.status === 'borrowed' && (
              <div className="bg-orange-50 p-2 rounded-lg mb-3 text-sm">
                <p><span className="font-medium">{t('borrowedBy')}:</span> {game.borrowed_by}</p>
                <p><span className="font-medium">{t('returnDate')}:</span> {formatDate(game.return_date)}</p>
              </div>
            )}
          </div>
        </div>

        <div className="px-4 pb-4">
          <div className="flex gap-2">
            {game.status === 'available' ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setBorrowModal({ show: true, game });
                }}
                className="flex-1 bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                {t('lendGame')}
              </button>
            ) : (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  returnGame(game.id);
                }}
                className="flex-1 bg-green-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
              >
                {t('markReturned')}
              </button>
            )}
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                deleteGame(game.id);
              }}
              className="px-3 py-2 border border-red-300 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors"
            >
              {t('remove')}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const GameListItem = ({ game }) => {
    const getLanguageLabel = (lang) => {
      switch (lang) {
        case 'hu': return t('hungarian');
        case 'en': return t('english');
        case 'multilang': return t('multilingual');
        default: return t('english');
      }
    };

    const getLanguageColor = (lang) => {
      switch (lang) {
        case 'hu': return 'bg-red-100 text-red-800';
        case 'en': return 'bg-blue-100 text-blue-800';
        case 'multilang': return 'bg-green-100 text-green-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    };

    const displayTitle = language === 'hu' && game.title_hu ? game.title_hu : game.title;

    return (
      <div 
        className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow cursor-pointer"
        onClick={() => setDetailsModal({ show: true, game })}
      >
        <div className="flex items-center gap-4">
          <img
            src={game.cover_image || '/api/placeholder/100/140'}
            alt={displayTitle}
            className="w-16 h-20 object-cover rounded"
            onError={(e) => {
              e.target.src = '/api/placeholder/100/140';
            }}
          />
          
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <h3 className="font-bold text-lg text-gray-900 truncate">{displayTitle}</h3>
              <div className="flex gap-2 ml-4">
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  game.status === 'available' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-orange-100 text-orange-800'
                }`}>
                  {game.status === 'available' ? t('statusAvailable') : t('statusBorrowed')}
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getLanguageColor(game.language)}`}>
                  {getLanguageLabel(game.language)}
                </div>
              </div>
            </div>
            
            <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
              <div>
                <span className="font-medium">{t('players')}:</span> {game.min_players}-{game.max_players}
              </div>
              <div>
                <span className="font-medium">{t('time')}:</span> {game.play_time} {t('min')}
              </div>
              <div>
                <span className="font-medium">{t('complexity')}:</span> {game.complexity_rating.toFixed(1)}/5
              </div>
              {game.authors.length > 0 && (
                <div>
                  <span className="font-medium">{t('designer')}:</span> {game.authors.join(', ')}
                </div>
              )}
            </div>

            {game.status === 'borrowed' && (
              <div className="mt-3 bg-orange-50 p-2 rounded-lg text-sm">
                <p><span className="font-medium">{t('borrowedBy')}:</span> {game.borrowed_by}</p>
                <p><span className="font-medium">{t('returnDate')}:</span> {formatDate(game.return_date)}</p>
              </div>
            )}
          </div>

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
                deleteGame(game.id);
              }}
              className="border border-red-300 text-red-600 px-3 py-1 rounded text-sm font-medium hover:bg-red-50 transition-colors"
            >
              {t('remove')}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const SearchResultCard = ({ game }) => (
    <div 
      className="flex items-center p-4 bg-white rounded-lg shadow hover:shadow-md cursor-pointer transition-shadow"
      onClick={() => getGameDetails(game.id)}
    >
      <div className="flex-1">
        <h3 className="font-semibold text-gray-900">{game.name}</h3>
        {game.year && <p className="text-sm text-gray-500">{t('released')}: {game.year}</p>}
      </div>
      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
      </svg>
    </div>
  );

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
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {t('allGames')} ({games.length})
            </button>
            <button
              onClick={() => setFilter('available')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'available'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {t('available')}
            </button>
            <button
              onClick={() => setFilter('borrowed')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === 'borrowed'
                  ? 'bg-blue-600 text-white'
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

          {/* View Toggle */}
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
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}

export default App;