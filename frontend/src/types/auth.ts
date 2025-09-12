// Authentication context types
export interface AuthUser {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  role?: string;
}

export interface AuthContextType {
  // State
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: { email: string; password: string }) => Promise<void>;
  register: (userData: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  updateUser: (userData: Partial<AuthUser>) => void;
}
