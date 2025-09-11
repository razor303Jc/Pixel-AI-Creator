/**
 * Authentication Context Provider
 * Manages user authentication state across the application
 */

import React, { createContext, useContext, useReducer, useEffect } from "react";
import { apiService, handleApiError } from "../services/api";

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
const authReducer = (state, action) => {
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
const AuthContext = createContext();

// Authentication provider component
export const AuthProvider = ({ children }) => {
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
  const login = async (credentials) => {
    try {
      dispatch({ type: authActions.SET_LOADING, payload: true });

      const tokenResponse = await apiService.auth.login(credentials);
      const userResponse = await apiService.auth.getCurrentUser();

      dispatch({
        type: authActions.LOGIN_SUCCESS,
        payload: {
          user: userResponse.data,
          token: tokenResponse.access_token,
        },
      });

      return { success: true, user: userResponse.data };
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({
        type: authActions.LOGIN_ERROR,
        payload: apiError,
      });
      return { success: false, error: apiError };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      dispatch({ type: authActions.SET_LOADING, payload: true });

      const registerResponse = await apiService.auth.register(userData);

      // After successful registration, automatically log in
      const loginResult = await login({
        email: userData.email,
        password: userData.password,
      });

      return loginResult;
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({
        type: authActions.LOGIN_ERROR,
        payload: apiError,
      });
      return { success: false, error: apiError };
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
  const updateUser = (userData) => {
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
