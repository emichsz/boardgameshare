import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
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
  const { handleGoogleLoginSuccess, handleGoogleLoginError, loginAsTestUser, error, setError } = useAuth();
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

  const handleTestLogin = () => {
    setError(null);
    loginAsTestUser();
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
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleLoginSuccess}
                onError={handleGoogleLoginError}
                text="signin_with"
                shape="rectangular"
                size="large"
                width="300"
                locale={language}
              />
            </div>
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