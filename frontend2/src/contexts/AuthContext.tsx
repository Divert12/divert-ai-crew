
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService, User, LoginRequest, RegisterRequest } from '@/services/api';

interface AuthContextType {
  isLoggedIn: boolean;
  user: User | null;
  login: (data: LoginRequest) => Promise<boolean>;
  register: (data: RegisterRequest) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in on app start
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setIsLoggedIn(true);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
      }
    }
    
    setIsLoading(false);
  }, []);

  const login = async (data: LoginRequest): Promise<boolean> => {
    try {
      const response = await apiService.login(data);
      
      // Store token and user data
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user_data', JSON.stringify(response.user));
      
      setIsLoggedIn(true);
      setUser(response.user);
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (data: RegisterRequest): Promise<boolean> => {
    try {
      const user = await apiService.register(data);
      console.log('User registered successfully:', user);
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    setIsLoggedIn(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
