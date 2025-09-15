/**
 * API Service Layer for Pixel-AI-Creator Frontend
 * Provides centralized API configuration with authentication, error handling, and retry logic
 */

import axios from "axios";

// API Configuration
const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8002/api";
const API_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
  },
});

// Token management utilities
const tokenManager = {
  getToken: () => localStorage.getItem("access_token"),
  setToken: (token) => localStorage.setItem("access_token", token),
  removeToken: () => localStorage.removeItem("access_token"),
  getRefreshToken: () => localStorage.getItem("refresh_token"),
  setRefreshToken: (token) => localStorage.setItem("refresh_token", token),
  removeRefreshToken: () => localStorage.removeItem("refresh_token"),
};

// Request interceptor to add authentication token
apiClient.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => {
    // Return successful responses
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized - token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = tokenManager.getRefreshToken();
      if (refreshToken) {
        try {
          // Attempt to refresh token
          const refreshResponse = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const newToken = refreshResponse.data.access_token;
          tokenManager.setToken(newToken);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed - redirect to login
          tokenManager.removeToken();
          tokenManager.removeRefreshToken();
          window.location.href = "/login";
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token - redirect to login
        tokenManager.removeToken();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

// Retry logic for failed requests
const retryRequest = async (requestFn, retries = MAX_RETRIES) => {
  try {
    return await requestFn();
  } catch (error) {
    if (retries > 0 && error.code === "ECONNABORTED") {
      console.log(
        `Request failed, retrying... ${
          MAX_RETRIES - retries + 1
        }/${MAX_RETRIES}`
      );
      await new Promise((resolve) => setTimeout(resolve, 1000)); // Wait 1 second
      return retryRequest(requestFn, retries - 1);
    }
    throw error;
  }
};

// API Service Methods
export const apiService = {
  // Generic HTTP methods
  get: async (url) => {
    return await retryRequest(() => apiClient.get(url));
  },

  post: async (url, data) => {
    return await retryRequest(() => apiClient.post(url, data));
  },

  put: async (url, data) => {
    return await retryRequest(() => apiClient.put(url, data));
  },

  delete: async (url) => {
    return await retryRequest(() => apiClient.delete(url));
  },

  // Authentication endpoints
  auth: {
    login: async (credentials) => {
      const response = await retryRequest(() =>
        apiClient.post("auth/login", {
          email: credentials.email,
          password: credentials.password,
        })
      );

      // Store tokens
      if (response.data.access_token) {
        tokenManager.setToken(response.data.access_token);
        if (response.data.refresh_token) {
          tokenManager.setRefreshToken(response.data.refresh_token);
        }
      }

      return response.data;
    },

    register: async (userData) => {
      console.log("🔗 Register API call - Base URL:", API_BASE_URL);
      console.log(
        "🔗 Register API call - Full URL:",
        `${API_BASE_URL}/auth/register`
      );
      console.log("📤 Register payload:", userData);
      return retryRequest(() => apiClient.post("auth/register", userData));
    },

    logout: () => {
      tokenManager.removeToken();
      tokenManager.removeRefreshToken();
    },

    getCurrentUser: async () => {
      return retryRequest(() => apiClient.get("auth/me"));
    },
  },

  // Client management endpoints
  clients: {
    getAll: async (statusFilter = "active") => {
      const params = statusFilter ? `?status=${statusFilter}` : "";
      return retryRequest(() => apiClient.get(`clients/${params}`));
    },

    getById: async (clientId) => {
      return retryRequest(() => apiClient.get(`clients/${clientId}`));
    },

    create: async (clientData) => {
      return retryRequest(() => apiClient.post("clients/", clientData));
    },

    update: async (clientId, clientData) => {
      return retryRequest(() =>
        apiClient.put(`clients/${clientId}`, clientData)
      );
    },

    delete: async (clientId) => {
      return retryRequest(() => apiClient.delete(`clients/${clientId}`));
    },
  },

  // Chatbot management endpoints
  chatbots: {
    getAll: async () => {
      return retryRequest(() => apiClient.get("chatbots/"));
    },

    getById: async (chatbotId) => {
      return retryRequest(() => apiClient.get(`chatbots/${chatbotId}`));
    },

    create: async (chatbotData) => {
      // Extract auto_build from chatbotData to pass as query parameter
      const { auto_build, ...data } = chatbotData;
      const params = auto_build ? { auto_build: true } : {};

      return retryRequest(() => apiClient.post("chatbots/", data, { params }));
    },

    update: async (chatbotId, chatbotData) => {
      return retryRequest(() =>
        apiClient.put(`chatbots/${chatbotId}`, chatbotData)
      );
    },

    delete: async (chatbotId) => {
      return retryRequest(() => apiClient.delete(`chatbots/${chatbotId}`));
    },
  },

  // Conversation endpoints
  conversations: {
    getAll: async () => {
      return retryRequest(() => apiClient.get("conversations/"));
    },

    getById: async (conversationId) => {
      return retryRequest(() =>
        apiClient.get(`conversations/${conversationId}`)
      );
    },

    create: async (conversationData) => {
      return retryRequest(() =>
        apiClient.post("conversations/", conversationData)
      );
    },

    update: async (conversationId, conversationData) => {
      return retryRequest(() =>
        apiClient.put(`conversations/${conversationId}`, conversationData)
      );
    },

    delete: async (conversationId) => {
      return retryRequest(() =>
        apiClient.delete(`conversations/${conversationId}`)
      );
    },
  },

  // Embeddings endpoints
  embeddings: {
    store: async (embeddingData) => {
      return retryRequest(() =>
        apiClient.post("embeddings/store", embeddingData)
      );
    },

    search: async (query, limit = 10) => {
      return retryRequest(() =>
        apiClient.post("embeddings/search", {
          query,
          limit,
        })
      );
    },

    delete: async (embeddingId) => {
      return retryRequest(() =>
        apiClient.delete(`embeddings/delete/${embeddingId}`)
      );
    },
  },

  // Build management endpoints
  builds: {
    getAll: async () => {
      return retryRequest(() => apiClient.get("builds/"));
    },

    getStatus: async (buildId) => {
      return retryRequest(() => apiClient.get(`builds/status/${buildId}`));
    },

    getLogs: async (buildId) => {
      return retryRequest(() => apiClient.get(`builds/logs/${buildId}`));
    },

    queue: async (projectId) => {
      return retryRequest(() => apiClient.post(`builds/queue/${projectId}`));
    },

    cancel: async (buildId) => {
      return retryRequest(() => apiClient.delete(`builds/${buildId}`));
    },

    getDeployment: async (buildId) => {
      return retryRequest(() => apiClient.get(`builds/deployment/${buildId}`));
    },

    cleanup: async (buildId) => {
      return retryRequest(() => apiClient.post(`builds/cleanup/${buildId}`));
    },
  },

  // Health check endpoint
  health: async () => {
    return retryRequest(() => apiClient.get(""));
  },
};

// Error handling utility
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;

    switch (status) {
      case 400:
        return {
          message: data.detail || "Bad request",
          type: "validation",
          details: data,
        };
      case 401:
        return {
          message: "Authentication required",
          type: "auth",
          details: data,
        };
      case 403:
        return {
          message: "Access forbidden",
          type: "permission",
          details: data,
        };
      case 404:
        return {
          message: "Resource not found",
          type: "notfound",
          details: data,
        };
      case 422:
        return {
          message: "Validation error",
          type: "validation",
          details: data,
        };
      case 500:
        return {
          message: "Internal server error",
          type: "server",
          details: data,
        };
      default:
        return {
          message: `Request failed with status ${status}`,
          type: "unknown",
          details: data,
        };
    }
  } else if (error.request) {
    // Request made but no response received
    return {
      message: "Network error - please check your connection",
      type: "network",
      details: error,
    };
  } else {
    // Error in setting up request
    return {
      message: error.message || "Unknown error occurred",
      type: "unknown",
      details: error,
    };
  }
};

// Export configured axios instance for direct use if needed
export default apiClient;
