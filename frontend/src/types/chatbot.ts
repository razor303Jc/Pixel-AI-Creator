// Chatbot context types
export interface ChatbotType {
  id: number;
  name: string;
  description: string;
  personality: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ClientType {
  id: number;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationType {
  id: number;
  chatbot_id: number;
  client_id: number;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ChatbotContextType {
  // State
  clients: ClientType[];
  currentClient: ClientType | null;
  isLoadingClients: boolean;
  clientsError: string | null;

  chatbots: ChatbotType[];
  currentChatbot: ChatbotType | null;
  isLoadingChatbots: boolean;
  chatbotsError: string | null;

  conversations: ConversationType[];
  currentConversation: ConversationType | null;
  isLoadingConversations: boolean;
  conversationsError: string | null;

  // Generic loading state (typically maps to isLoadingChatbots for backward compatibility)
  loading: boolean;

  // Client functions
  fetchClients: () => Promise<void>;
  createClient: (clientData: any) => Promise<void>;
  updateClient: (clientId: string, clientData: any) => Promise<void>;
  deleteClient: (clientId: string) => Promise<void>;
  setCurrentClient: (client: any) => void;

  // Chatbot functions
  fetchChatbots: () => Promise<void>;
  createChatbot: (chatbotData: any) => Promise<void>;
  updateChatbot: (chatbotId: string, chatbotData: any) => Promise<void>;
  deleteChatbot: (chatbotId: string) => Promise<void>;
  setCurrentChatbot: (chatbot: any) => void;

  // Conversation functions
  fetchConversations: () => Promise<void>;
  createConversation: (conversationData: any) => Promise<void>;
  updateConversation: (conversationId: string, conversationData: any) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  setCurrentConversation: (conversation: any) => void;

  // Utility functions
  clearAllErrors: () => void;
}
