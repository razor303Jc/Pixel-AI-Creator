/**
 * Chatbot Management Context Provider
 * Manages chatbot and client state across the application
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useCallback,
  ReactNode,
} from "react";
import { apiService, handleApiError } from "../services/api";
import { ChatbotContextType } from "../types/chatbot";

// Initialize context state for chatbot management
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
  DELETE_CHATBOT: "DELETE_CHATBOT",
  SET_CURRENT_CHATBOT: "SET_CURRENT_CHATBOT",

  // Conversation actions
  SET_CONVERSATIONS_LOADING: "SET_CONVERSATIONS_LOADING",
  SET_CONVERSATIONS: "SET_CONVERSATIONS",
  SET_CONVERSATIONS_ERROR: "SET_CONVERSATIONS_ERROR",
  ADD_CONVERSATION: "ADD_CONVERSATION",
  UPDATE_CONVERSATION: "UPDATE_CONVERSATION",
  DELETE_CONVERSATION: "DELETE_CONVERSATION",
  SET_CURRENT_CONVERSATION: "SET_CURRENT_CONVERSATION",

  // General actions
  CLEAR_ALL_ERRORS: "CLEAR_ALL_ERRORS",
};

// Reducer function
const chatbotReducer = (state: any, action: any) => {
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
        clients: state.clients.map((client: any) =>
          client.id === action.payload.id ? action.payload : client
        ),
      };

    case actionTypes.REMOVE_CLIENT:
      return {
        ...state,
        clients: state.clients.filter((client: any) => client.id !== action.payload),
      };

    case actionTypes.SET_CURRENT_CLIENT:
      return {
        ...state,
        currentClient: action.payload,
      };

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
        chatbots: state.chatbots.map((chatbot: any) =>
          chatbot.id === action.payload.id ? action.payload : chatbot
        ),
      };

    case actionTypes.DELETE_CHATBOT:
      return {
        ...state,
        chatbots: state.chatbots.filter(
          (chatbot: any) => chatbot.id !== action.payload
        ),
      };

    case actionTypes.SET_CURRENT_CHATBOT:
      return {
        ...state,
        currentChatbot: action.payload,
      };

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
        conversations: state.conversations.map((conversation: any) =>
          conversation.id === action.payload.id ? action.payload : conversation
        ),
      };

    case actionTypes.DELETE_CONVERSATION:
      return {
        ...state,
        conversations: state.conversations.filter(
          (conversation: any) => conversation.id !== action.payload
        ),
      };

    case actionTypes.SET_CURRENT_CONVERSATION:
      return {
        ...state,
        currentConversation: action.payload,
      };

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

// Create the context
const ChatbotContext = createContext<ChatbotContextType | null>(null);

// Provider component
export const ChatbotProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(chatbotReducer, initialState);

  // Client Management Functions
  const fetchClients = useCallback(async (): Promise<void> => {
    dispatch({ type: actionTypes.SET_CLIENTS_LOADING, payload: true });
    try {
      const response = await apiService.clients.getAll();
      dispatch({ type: actionTypes.SET_CLIENTS, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({ type: actionTypes.SET_CLIENTS_ERROR, payload: apiError.message });
    }
  }, []);

  const createClient = useCallback(async (clientData: any): Promise<void> => {
    try {
      const response = await apiService.clients.create(clientData);
      dispatch({ type: actionTypes.ADD_CLIENT, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }, []);

  const updateClient = useCallback(async (clientId: string, clientData: any): Promise<void> => {
    try {
      const response = await apiService.clients.update(clientId, clientData);
      dispatch({ type: actionTypes.UPDATE_CLIENT, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }, []);

  const deleteClient = useCallback(async (clientId: string): Promise<void> => {
    try {
      await apiService.clients.delete(clientId);
      dispatch({ type: actionTypes.REMOVE_CLIENT, payload: clientId });
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }, []);

  const setCurrentClient = useCallback((client: any): void => {
    dispatch({ type: actionTypes.SET_CURRENT_CLIENT, payload: client });
  }, []);

  // Chatbot Management Functions
  const fetchChatbots = useCallback(async (): Promise<void> => {
    dispatch({ type: actionTypes.SET_CHATBOTS_LOADING, payload: true });
    try {
      const response = await apiService.chatbots.getAll();
      dispatch({ type: actionTypes.SET_CHATBOTS, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({ type: actionTypes.SET_CHATBOTS_ERROR, payload: apiError.message });
    }
  }, []);

  const createChatbot = useCallback(async (chatbotData: any): Promise<void> => {
    try {
      const response = await apiService.chatbots.create(chatbotData);
      dispatch({ type: actionTypes.ADD_CHATBOT, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }, []);

  const updateChatbot = useCallback(async (chatbotId: string, chatbotData: any): Promise<void> => {
    try {
      const response = await apiService.chatbots.update(chatbotId, chatbotData);
      dispatch({ type: actionTypes.UPDATE_CHATBOT, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }, []);

  const deleteChatbot = useCallback(async (chatbotId: string): Promise<void> => {
    try {
      await apiService.chatbots.delete(chatbotId);
      dispatch({ type: actionTypes.DELETE_CHATBOT, payload: chatbotId });
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }, []);

  const setCurrentChatbot = useCallback((chatbot: any): void => {
    dispatch({ type: actionTypes.SET_CURRENT_CHATBOT, payload: chatbot });
  }, []);

  // Conversation Management Functions
  const fetchConversations = useCallback(async (): Promise<void> => {
    dispatch({ type: actionTypes.SET_CONVERSATIONS_LOADING, payload: true });
    try {
      const response = await apiService.conversations.getAll();
      dispatch({ type: actionTypes.SET_CONVERSATIONS, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      dispatch({ type: actionTypes.SET_CONVERSATIONS_ERROR, payload: apiError.message });
    }
  }, []);

  const createConversation = useCallback(async (conversationData: any): Promise<void> => {
    try {
      const response = await apiService.conversations.create(conversationData);
      dispatch({ type: actionTypes.ADD_CONVERSATION, payload: response.data });
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }, []);

  const updateConversation = useCallback(
    async (conversationId: string, conversationData: any): Promise<void> => {
      try {
        const response = await apiService.conversations.update(
          conversationId,
          conversationData
        );
        dispatch({ type: actionTypes.UPDATE_CONVERSATION, payload: response.data });
      } catch (error) {
        const apiError = handleApiError(error);
        throw new Error(apiError.message);
      }
    },
    []
  );

  const deleteConversation = useCallback(async (conversationId: string): Promise<void> => {
    try {
      await apiService.conversations.delete(conversationId);
      dispatch({ type: actionTypes.DELETE_CONVERSATION, payload: conversationId });
    } catch (error) {
      const apiError = handleApiError(error);
      throw new Error(apiError.message);
    }
  }, []);

  const setCurrentConversation = useCallback((conversation: any): void => {
    dispatch({
      type: actionTypes.SET_CURRENT_CONVERSATION,
      payload: conversation,
    });
  }, []);

  // Clear errors
  const clearAllErrors = useCallback((): void => {
    dispatch({ type: actionTypes.CLEAR_ALL_ERRORS });
  }, []);

  const contextValue: ChatbotContextType = {
    // State
    ...state,
    
    // Generic loading state for backward compatibility
    loading: state.isLoadingChatbots,

    // Client functions
    fetchClients,
    createClient,
    updateClient,
    deleteClient,
    setCurrentClient,

    // Chatbot functions
    fetchChatbots,
    createChatbot,
    updateChatbot,
    deleteChatbot,
    setCurrentChatbot,

    // Conversation functions
    fetchConversations,
    createConversation,
    updateConversation,
    deleteConversation,
    setCurrentConversation,

    // Utility functions
    clearAllErrors,
  };

  return (
    <ChatbotContext.Provider value={contextValue}>
      {children}
    </ChatbotContext.Provider>
  );
};

// Custom hook to use the context
export const useChatbotContext = (): ChatbotContextType => {
  const context = useContext(ChatbotContext);
  if (!context) {
    throw new Error("useChatbotContext must be used within a ChatbotProvider");
  }
  return context;
};

// Export alias for backward compatibility
export const useChatbot = useChatbotContext;

export default ChatbotContext;
