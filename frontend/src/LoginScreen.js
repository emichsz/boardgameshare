import React, { useState } from 'react';
import { useAuth } from './AuthContext';

const translations = {
  hu: {
    welcome: 'Üdvözöljük a',
    appTitle: 'Társasjáték Gyűjteményben',
    subtitle: 'Kezelje társasjáték gyűjteményét, kölcsönözze játékait és fedezzen fel új játékokat a BoardGameGeek segítségével.',
    signInWithGoogle: 'Bejelentkezés Google-lal',
    features: {
      title: 'Funkciók:',
      bgg: '🎲 BoardGameGeek integráció',
      collection: '📚 Gyűjtemény kezelés',
      lending: '🤝 Kölcsönzési rendszer',
      multilang: '🌍 Magyar és angol nyelv támogatás'
    },
    language: 'Nyelv',
    loginError: 'Bejelentkezési hiba',
    loading: 'Betöltés...'
  },
  en: {
    welcome: 'Welcome to',
    appTitle: 'Board Game Collection',
    subtitle: 'Manage your board game collection, lend your games, and discover new games with BoardGameGeek integration.',
    signInWithGoogle: 'Sign in with Google',
    features: {
      title: 'Features:',
      bgg: '🎲 BoardGameGeek integration',
      collection: '📚 Collection management',
      lending: '🤝 Lending system',
      multilang: '🌍 Hungarian and English language support'
    },
    language: 'Language',
    loginError: 'Login error',
    loading: 'Loading...'
  }
};

export default function LoginScreen() {
  const { loginWithGoogle, loading, error, setError } = useAuth();
  const [language, setLanguage] = useState('hu');

  const t = (key) => {
    const keys = key.split('.');
    let value = translations[language];
    for (const k of keys) {
      value = value?.[k];
    }
    return value || key;
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'hu' ? 'en' : 'hu');
    setError(null); // Clear any errors when switching language
  };

  const handleGoogleLogin = () => {
    setError(null);
    loginWithGoogle();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100">
      {/* Language Toggle */}
      <div className="absolute top-4 right-4">
        <button
          onClick={toggleLanguage}
          className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-white/80 transition-colors backdrop-blur-sm"
        >
          {language === 'hu' ? 'EN' : 'HU'}
        </button>
      </div>

      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="max-w-md w-full">
          
          {/* Main Card */}
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            
            {/* App Icon/Logo */}
            <div className="text-6xl mb-6">🎲</div>
            
            {/* Title */}
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {t('welcome')} <br />
              <span className="text-blue-600">{t('appTitle')}</span>
            </h1>
            
            {/* Subtitle */}
            <p className="text-gray-600 mb-8 text-sm leading-relaxed">
              {t('subtitle')}
            </p>
            
            {/* Error Message */}
            {error && (
              <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">
                  <span className="font-medium">{t('loginError')}:</span> {error}
                </p>
              </div>
            )}
            
            {/* Google Sign In Button */}
            <button
              onClick={handleGoogleLogin}
              disabled={loading}
              className="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-gray-700 font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
                  {t('loading')}
                </>
              ) : (
                <>
                  {/* Google Icon */}
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  {t('signInWithGoogle')}
                </>
              )}
            </button>
          </div>

          {/* Features Card */}
          <div className="mt-6 bg-white/80 backdrop-blur-sm rounded-lg p-6">
            <h3 className="font-medium text-gray-900 mb-3">{t('features.title')}</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div>{t('features.bgg')}</div>
              <div>{t('features.collection')}</div>
              <div>{t('features.lending')}</div>
              <div>{t('features.multilang')}</div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}