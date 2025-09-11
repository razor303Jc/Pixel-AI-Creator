import React, { useState } from 'react';
import { Spinner } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ChatbotProvider } from './contexts/ChatbotContext';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import Dashboard from './components/dashboard/Dashboard';
import 'bootstrap/dist/css/bootstrap.min.css';

// Main App Content Component
const AppContent = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div
        className="min-vh-100 d-flex align-items-center justify-content-center"
        style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center text-white"
        >
          <div className="mb-4">
            <span className="display-2">🤖</span>
          </div>
          <Spinner animation="border" size="lg" className="mb-3" />
          <h4 className="fw-light">Loading Pixel AI Creator...</h4>
        </motion.div>
      </div>
    );
  }

  // Show authentication forms if not authenticated
  if (!isAuthenticated) {
    return showRegister ? (
      <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
    ) : (
      <LoginForm onSwitchToRegister={() => setShowRegister(true)} />
    );
  }

  // Show dashboard if authenticated
  return (
    <ChatbotProvider>
      <Dashboard />
    </ChatbotProvider>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
