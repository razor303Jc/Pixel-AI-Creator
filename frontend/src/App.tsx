import React from 'react';
// TEMPORARY: Commented out unused imports for auth bypass
// import { useState } from 'react';
// import { Spinner } from 'react-bootstrap';
// import { motion } from 'framer-motion';
import { AuthProvider } from './contexts/AuthContext';
// import { useAuth } from './contexts/AuthContext';
import { ChatbotProvider } from './contexts/ChatbotContext';
// import LoginForm from './components/auth/LoginForm';
// import RegisterForm from './components/auth/RegisterForm';
import Dashboard from './components/dashboard/Dashboard';
import 'bootstrap/dist/css/bootstrap.min.css';

// Main App Content Component - TEMPORARY: AUTH BYPASS FOR MANUAL TESTING
const AppContent = () => {
  // const { isAuthenticated, isLoading } = useAuth();
  // const [showRegister, setShowRegister] = useState(false);

  // TEMPORARY: Skip authentication checks - go directly to dashboard
  // TODO: Re-enable authentication once auth system is fixed
  
  /*
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
          <Spinner animation="border" className="mb-3" style={{ width: '3rem', height: '3rem' }} />
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
  */

  // Show dashboard directly (bypassing authentication for manual testing)
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
