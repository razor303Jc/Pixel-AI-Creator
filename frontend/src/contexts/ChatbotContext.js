/**
 * Chatbot Management Context Provider
 * Manages chatbot and client state across the application
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useCallback,
} from "react";
import { apiService, handleApiError } from "../services/api";

// Initial state for chatbot management
const initialState = {
  // Clients state
  clients: [],
  currentClient: null,
  isLoadingClients: false,
  clientsError: null,

  // Chatbots state
  chatbots: [],
  currentChatbot: null,
  isLoadingChatbots: false,
  chatbotsError: null,

  // Conversations state
  conversations: [],
  currentConversation: null,
  isLoadingConversations: false,
  conversationsError: null,
};

// Action types
const actionTypes = {
  // Client actions
  SET_CLIENTS_LOADING: "SET_CLIENTS_LOADING",
  SET_CLIENTS: "SET_CLIENTS",
  SET_CLIENTS_ERROR: "SET_CLIENTS_ERROR",
  ADD_CLIENT: "ADD_CLIENT",
  UPDATE_CLIENT: "UPDATE_CLIENT",
  REMOVE_CLIENT: "REMOVE_CLIENT",
  SET_CURRENT_CLIENT: "SET_CURRENT_CLIENT",

  // Chatbot actions
  SET_CHATBOTS_LOADING: "SET_CHATBOTS_LOADING",
  SET_CHATBOTS: "SET_CHATBOTS",
  SET_CHATBOTS_ERROR: "SET_CHATBOTS_ERROR",
  ADD_CHATBOT: "ADD_CHATBOT",
  UPDATE_CHATBOT: "UPDATE_CHATBOT",
  REMOVE_CHATBOT: "REMOVE_CHATBOT",
  SET_CURRENT_CHATBOT: "SET_CURRENT_CHATBOT",

  // Conversation actions
  SET_CONVERSATIONS_LOADING: "SET_CONVERSATIONS_LOADING",
  SET_CONVERSATIONS: "SET_CONVERSATIONS",
  SET_CONVERSATIONS_ERROR: "SET_CONVERSATIONS_ERROR",
  ADD_CONVERSATION: "ADD_CONVERSATION",
  UPDATE_CONVERSATION: "UPDATE_CONVERSATION",
  REMOVE_CONVERSATION: "REMOVE_CONVERSATION",
  SET_CURRENT_CONVERSATION: "SET_CURRENT_CONVERSATION",

  // General actions
  CLEAR_ALL_ERRORS: "CLEAR_ALL_ERRORS",
};

// Reducer function
const chatbotReducer = (state, action) => {
  switch (action.type) {
    // Client cases
    case actionTypes.SET_CLIENTS_LOADING:
      return { ...state, isLoadingClients: action.payload, clientsError: null };

    case actionTypes.SET_CLIENTS:
      return {
        ...state,
        clients: action.payload,
        isLoadingClients: false,
        clientsError: null,
      };

    case actionTypes.SET_CLIENTS_ERROR:
      return {
        ...state,
        clientsError: action.payload,
        isLoadingClients: false,
      };

    case actionTypes.ADD_CLIENT:
      return {
        ...state,
        clients: [...state.clients, action.payload],
      };

    case actionTypes.UPDATE_CLIENT:
      return {
        ...state,
        clients: state.clients.map((client) =>
          client.id === action.payload.id ? action.payload : client
        ),
        currentClient:
          state.currentClient?.id === action.payload.id
            ? action.payload
            : state.currentClient,
      };

    case actionTypes.REMOVE_CLIENT:
      return {
        ...state,
        clients: state.clients.filter((client) => client.id !== action.payload),
        currentClient:
          state.currentClient?.id === action.payload
            ? null
            : state.currentClient,
      };

    case actionTypes.SET_CURRENT_CLIENT:
      return { ...state, currentClient: action.payload };

    // Chatbot cases
    case actionTypes.SET_CHATBOTS_LOADING:
      return {
        ...state,
        isLoadingChatbots: action.payload,
        chatbotsError: null,
      };

    case actionTypes.SET_CHATBOTS:
      return {
        ...state,
        chatbots: action.payload,
        isLoadingChatbots: false,
        chatbotsError: null,
      };

    case actionTypes.SET_CHATBOTS_ERROR:
      return {
        ...state,
        chatbotsError: action.payload,
        isLoadingChatbots: false,
      };

    case actionTypes.ADD_CHATBOT:
      return {
        ...state,
        chatbots: [...state.chatbots, action.payload],
      };

    case actionTypes.UPDATE_CHATBOT:
      return {
        ...state,
        chatbots: state.chatbots.map((chatbot) =>
          chatbot.id === action.payload.id ? action.payload : chatbot
        ),
        currentChatbot:
          state.currentChatbot?.id === action.payload.id
            ? action.payload
            : state.currentChatbot,
      };

    case actionTypes.REMOVE_CHATBOT:
      return {
        ...state,
        chatbots: state.chatbots.filter(
          (chatbot) => chatbot.id !== action.payload
        ),
        currentChatbot:
          state.currentChatbot?.id === action.payload
            ? null
            : state.currentChatbot,
      };

    case actionTypes.SET_CURRENT_CHATBOT:
      return { ...state, currentChatbot: action.payload };

    // Conversation cases
    case actionTypes.SET_CONVERSATIONS_LOADING:
      return {
        ...state,
        isLoadingConversations: action.payload,
        conversationsError: null,
      };

    case actionTypes.SET_CONVERSATIONS:
      return {
        ...state,
        conversations: action.payload,
        isLoadingConversations: false,
        conversationsError: null,
      };

    case actionTypes.SET_CONVERSATIONS_ERROR:
      return {
        ...state,
        conversationsError: action.payload,
        isLoadingConversations: false,
      };

    case actionTypes.ADD_CONVERSATION:
      return {
        ...state,
        conversations: [...state.conversations, action.payload],
      };

    case actionTypes.UPDATE_CONVERSATION:
      return {
        ...state,
        conversations: state.conversations.map((conversation) =>
          conversation.id === action.payload.id ? action.payload : conversation
        ),
        currentConversation:
          state.currentConversation?.id === action.payload.id
            ? action.payload
            : state.currentConversation,
      };

    case actionTypes.REMOVE_CONVERSATION:
      return {
        ...state,
        conversations: state.conversations.filter(
          (conversation) => conversation.id !== action.payload
        ),
        currentConversation:
          state.currentConversation?.id === action.payload
            ? null
            : state.currentConversation,
      };

    case actionTypes.SET_CURRENT_CONVERSATION:
      return { ...state, currentConversation: action.payload };

    // General cases
    case actionTypes.CLEAR_ALL_ERRORS:
      return {
        ...state,
        clientsError: null,
        chatbotsError: null,
        conversationsError: null,
      };

    default:
      return state;
  }
};

// Create context
const ChatbotContext = createContext();

// Provider component
export const ChatbotProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatbotReducer, initialState);

  // Client management functions
  const loadClients = useCallback(async () => {
    dispatch({ type: actionTypes.SET_CLIENTS_LOADING, payload: true });
    try {
      const response = await apiService.clients.getAll();
      dispatch({ type: actionTypes.SET_CLIENTS, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({ type: actionTypes.SET_CLIENTS_ERROR, payload: apiError });
    }
  }, []);

  const createClient = useCallback(async (clientData) => {
    try {
      const response = await apiService.clients.create(clientData);
      dispatch({ type: actionTypes.ADD_CLIENT, payload: response.data });
      return { success: true, data: response.data };
    } catch (error) {
      const apiError = handleApiError(error);
      return { success: false, error: apiError };
    }
  }, []);

  const updateClient = useCallback(async (clientId, clientData) => {
    try {
      const response = await apiService.clients.update(clientId, clientData);
      dispatch({ type: actionTypes.UPDATE_CLIENT, payload: response.data });
      return { success: true, data: response.data };
    } catch (error) {
      const apiError = handleApiError(error);
      return { success: false, error: apiError };
    }
  }, []);

  const deleteClient = useCallback(async (clientId) => {
    try {
      await apiService.clients.delete(clientId);
      dispatch({ type: actionTypes.REMOVE_CLIENT, payload: clientId });
      return { success: true };
    } catch (error) {
      const apiError = handleApiError(error);
      return { success: false, error: apiError };
    }
  }, []);

  const setCurrentClient = useCallback((client) => {
    dispatch({ type: actionTypes.SET_CURRENT_CLIENT, payload: client });
  }, []);

  // Chatbot management functions
  const loadChatbots = useCallback(async () => {
    dispatch({ type: actionTypes.SET_CHATBOTS_LOADING, payload: true });
    try {
      const response = await apiService.chatbots.getAll();
      dispatch({ type: actionTypes.SET_CHATBOTS, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({ type: actionTypes.SET_CHATBOTS_ERROR, payload: apiError });
    }
  }, []);

  const createChatbot = useCallback(async (chatbotData) => {
    try {
      const response = await apiService.chatbots.create(chatbotData);
      dispatch({ type: actionTypes.ADD_CHATBOT, payload: response.data });
      return { success: true, data: response.data };
    } catch (error) {
      const apiError = handleApiError(error);
      return { success: false, error: apiError };
    }
  }, []);

  const updateChatbot = useCallback(async (chatbotId, chatbotData) => {
    try {
      const response = await apiService.chatbots.update(chatbotId, chatbotData);
      dispatch({ type: actionTypes.UPDATE_CHATBOT, payload: response.data });
      return { success: true, data: response.data };
    } catch (error) {
      const apiError = handleApiError(error);
      return { success: false, error: apiError };
    }
  }, []);

  const deleteChatbot = useCallback(async (chatbotId) => {
    try {
      await apiService.chatbots.delete(chatbotId);
      dispatch({ type: actionTypes.REMOVE_CHATBOT, payload: chatbotId });
      return { success: true };
    } catch (error) {
      const apiError = handleApiError(error);
      return { success: false, error: apiError };
    }
  }, []);

  const setCurrentChatbot = useCallback((chatbot) => {
    dispatch({ type: actionTypes.SET_CURRENT_CHATBOT, payload: chatbot });
  }, []);

  // Conversation management functions
  const loadConversations = useCallback(async () => {
    dispatch({ type: actionTypes.SET_CONVERSATIONS_LOADING, payload: true });
    try {
      const response = await apiService.conversations.getAll();
      dispatch({ type: actionTypes.SET_CONVERSATIONS, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({
        type: actionTypes.SET_CONVERSATIONS_ERROR,
        payload: apiError,
      });
    }
  }, []);

  const createConversation = useCallback(async (conversationData) => {
    try {
      const response = await apiService.conversations.create(conversationData);
      dispatch({ type: actionTypes.ADD_CONVERSATION, payload: response.data });
      return { success: true, data: response.data };
    } catch (error) {
      const apiError = handleApiError(error);
      return { success: false, error: apiError };
    }
  }, []);

  const updateConversation = useCallback(
    async (conversationId, conversationData) => {
      try {
        const response = await apiService.conversations.update(
          conversationId,
          conversationData
        );
        dispatch({
          type: actionTypes.UPDATE_CONVERSATION,
          payload: response.data,
        });
        return { success: true, data: response.data };
      } catch (error) {
        const apiError = handleApiError(error);
        return { success: false, error: apiError };
      }
    },
    []
  );

  const deleteConversation = useCallback(async (conversationId) => {
    try {
      await apiService.conversations.delete(conversationId);
      dispatch({
        type: actionTypes.REMOVE_CONVERSATION,
        payload: conversationId,
      });
      return { success: true };
    } catch (error) {
      const apiError = handleApiError(error);
      return { success: false, error: apiError };
    }
  }, []);

  const setCurrentConversation = useCallback((conversation) => {
    dispatch({
      type: actionTypes.SET_CURRENT_CONVERSATION,
      payload: conversation,
    });
  }, []);

  // Clear all errors
  const clearAllErrors = useCallback(() => {
    dispatch({ type: actionTypes.CLEAR_ALL_ERRORS });
  }, []);

  const value = {
    // State
    ...state,

    // Client actions
    loadClients,
    createClient,
    updateClient,
    deleteClient,
    setCurrentClient,

    // Chatbot actions
    loadChatbots,
    createChatbot,
    updateChatbot,
    deleteChatbot,
    setCurrentChatbot,

    // Conversation actions
    loadConversations,
    createConversation,
    updateConversation,
    deleteConversation,
    setCurrentConversation,

    // General actions
    clearAllErrors,
  };

  return (
    <ChatbotContext.Provider value={value}>{children}</ChatbotContext.Provider>
  );
};

// Custom hook to use chatbot context
export const useChatbot = () => {
  const context = useContext(ChatbotContext);

  if (!context) {
    throw new Error("useChatbot must be used within a ChatbotProvider");
  }

  return context;
};
