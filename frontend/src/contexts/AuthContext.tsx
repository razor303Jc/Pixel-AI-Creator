/**
 * Authentication Context Provider
 * Manages user authentication state across the application
 */

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from "react";
import { apiService, handleApiError } from "../services/api";
import { AuthContextType, AuthUser } from "../types/auth";

// Initial authentication state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Authentication actions
const authActions = {
  SET_LOADING: "SET_LOADING",
  LOGIN_SUCCESS: "LOGIN_SUCCESS",
  LOGIN_ERROR: "LOGIN_ERROR",
  LOGOUT: "LOGOUT",
  SET_USER: "SET_USER",
  CLEAR_ERROR: "CLEAR_ERROR",
};

// Authentication reducer
const authReducer = (state: any, action: any) => {
  switch (action.type) {
    case authActions.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
        error: null,
      };

    case authActions.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      };

    case authActions.LOGIN_ERROR:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
      };

    case authActions.LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };

    case authActions.SET_USER:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        isLoading: false,
        error: null,
      };

    case authActions.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };

    default:
      return state;
  }
};

// Create authentication context
export const AuthContext = createContext<AuthContextType | null>(null);

// Authentication provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize authentication on app start
  useEffect(() => {
    initializeAuth();
  }, []);

  // Initialize authentication by checking for existing token
  const initializeAuth = async () => {
    const token = localStorage.getItem("access_token");

    if (token) {
      try {
        dispatch({ type: authActions.SET_LOADING, payload: true });
        const response = await apiService.auth.getCurrentUser();
        dispatch({
          type: authActions.SET_USER,
          payload: response.data,
        });
      } catch (error) {
        // Token invalid or expired
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        dispatch({ type: authActions.LOGOUT });
      }
    } else {
      dispatch({ type: authActions.SET_LOADING, payload: false });
    }
  };

  // Login function
  const login = async (credentials: { email: string; password: string }): Promise<void> => {
    try {
      dispatch({ type: authActions.SET_LOADING, payload: true });

      const tokenResponse = await apiService.auth.login(credentials);
      
      // Create user object from login response instead of calling /me endpoint
      const user = {
        id: tokenResponse.user_id,
        email: credentials.email, // We know the email from login
        role: tokenResponse.role,
      };

      dispatch({
        type: authActions.LOGIN_SUCCESS,
        payload: {
          user,
          token: tokenResponse.access_token,
        },
      });
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({
        type: authActions.LOGIN_ERROR,
        payload: apiError,
      });
      throw new Error(apiError.message);
    }
  };

  // Register function
  const register = async (userData: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }): Promise<void> => {
    try {
      dispatch({ type: authActions.SET_LOADING, payload: true });

      await apiService.auth.register(userData);

      // After successful registration, automatically log in
      await login({
        email: userData.email,
        password: userData.password,
      });
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({
        type: authActions.LOGIN_ERROR,
        payload: apiError,
      });
      throw new Error(apiError.message);
    }
  };

  // Logout function
  const logout = () => {
    apiService.auth.logout();
    dispatch({ type: authActions.LOGOUT });
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: authActions.CLEAR_ERROR });
  };

  // Update user profile
  const updateUser = (userData: Partial<AuthUser>): void => {
    dispatch({
      type: authActions.SET_USER,
      payload: { ...state.user, ...userData },
    });
  };

  const value = {
    // State
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,

    // Actions
    login,
    register,
    logout,
    clearError,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use authentication context
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
};
