import React, { createContext, useContext, useState, useEffect } from 'react';
import { GoogleOAuthProvider, GoogleLogin, googleLogout } from '@react-oauth/google';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

// Create Auth Context
const AuthContext = createContext();

// Hook to use Auth Context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider component
function AuthProviderBase({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing session on app load
  useEffect(() => {
    const checkExistingSession = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (token) {
          // Set axios default header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Verify token with backend
          const response = await axios.get(`${API_BASE_URL}/api/auth/me`);
          setUser(response.data);
        }
      } catch (error) {
        console.log('No valid session found:', error);
        localStorage.removeItem('auth_token');
        delete axios.defaults.headers.common['Authorization'];
      } finally {
        setLoading(false);
      }
    };

    checkExistingSession();
  }, []);

  // Google login success handler
  const handleGoogleLoginSuccess = async (credentialResponse) => {
    try {
      setError(null);
      console.log('Google login success:', credentialResponse);
      
      // Send the credential (id_token) to backend
      const response = await axios.post(`${API_BASE_URL}/api/auth/google`, {
        credential: credentialResponse.credential
      });

      const { access_token, user: userData } = response.data;
      
      // Store token in localStorage
      localStorage.setItem('auth_token', access_token);
      
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Set user data
      setUser(userData);
      
      console.log('Login successful:', userData);
    } catch (error) {
      console.error('Login error:', error);
      setError('Bejelentkezés sikertelen. Kérjük próbálja újra!');
    }
  };

  // Google login error handler
  const handleGoogleLoginError = (error) => {
    console.error('Google login error:', error);
    setError('Google bejelentkezés sikertelen.');
  };

  // Logout function
  const logout = () => {
    try {
      // Google logout
      googleLogout();
      
      // Clear localStorage
      localStorage.removeItem('auth_token');
      
      // Clear axios default header
      delete axios.defaults.headers.common['Authorization'];
      
      // Clear user state
      setUser(null);
      setError(null);
      
      console.log('Logout successful');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Context value
  const contextValue = {
    user,
    loading,
    error,
    handleGoogleLoginSuccess,
    handleGoogleLoginError,
    logout,
    isAuthenticated: !!user,
    setError
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Wrapper with Google OAuth Provider
export function AuthProvider({ children }) {
  if (!GOOGLE_CLIENT_ID) {
    console.error('GOOGLE_CLIENT_ID is not set in environment variables');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-xl font-bold text-red-600 mb-2">Konfigurációs hiba</h1>
          <p className="text-gray-600">Google Client ID nincs beállítva.</p>
        </div>
      </div>
    );
  }

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProviderBase>
        {children}
      </AuthProviderBase>
    </GoogleOAuthProvider>
  );
}