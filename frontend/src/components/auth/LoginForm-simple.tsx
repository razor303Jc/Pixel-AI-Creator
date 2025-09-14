import React, { useState, useContext } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { Eye, EyeOff, LogIn, Mail, Lock } from 'lucide-react';
import { AuthContext } from '../../contexts/AuthContext';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const authContext = useContext(AuthContext);
  const login = authContext?.login;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    if (!login) {
      setError('Authentication service not available');
      setIsLoading(false);
      return;
    }
    
    try {
      await login({ email, password });
      // Navigation will be handled by AuthContext
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-vh-100 d-flex align-items-center justify-content-center"
      style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '20px'
      }}
    >
      <Container>
        <Row className="justify-content-center">
          <Col md={6} lg={5} xl={4}>
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <Card 
                className="shadow-lg border-0"
                style={{
                  background: 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '20px'
                }}
              >
                <Card.Body className="p-5">
                  <div className="text-center mb-4">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2, duration: 0.5 }}
                      className="d-inline-flex align-items-center justify-content-center bg-primary rounded-circle mb-3"
                      style={{ width: '60px', height: '60px' }}
                    >
                      <LogIn size={30} className="text-white" />
                    </motion.div>
                    <h3 className="fw-bold text-dark mb-2">Welcome Back</h3>
                    <p className="text-muted">Sign in to your account to continue</p>
                  </div>

                  {error && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Alert variant="danger" className="mb-3">
                        {error}
                      </Alert>
                    </motion.div>
                  )}

                  <Form onSubmit={handleSubmit}>
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3, duration: 0.5 }}
                    >
                      <Form.Group className="mb-3">
                        <Form.Label htmlFor="loginEmail" className="fw-semibold text-dark">
                          <Mail size={16} className="me-2" />
                          Email Address
                        </Form.Label>
                        <Form.Control
                          id="loginEmail"
                          type="email"
                          name="email"
                          placeholder="Enter your email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          required
                          className="py-3"
                          style={{
                            borderRadius: '10px',
                            border: '2px solid #e9ecef',
                            fontSize: '16px'
                          }}
                        />
                      </Form.Group>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.4, duration: 0.5 }}
                    >
                      <Form.Group className="mb-4">
                        <Form.Label htmlFor="loginPassword" className="fw-semibold text-dark">
                          <Lock size={16} className="me-2" />
                          Password
                        </Form.Label>
                        <div className="position-relative">
                          <Form.Control
                            id="loginPassword"
                            type={showPassword ? 'text' : 'password'}
                            name="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="py-3 pe-5"
                            style={{
                              borderRadius: '10px',
                              border: '2px solid #e9ecef',
                              fontSize: '16px'
                            }}
                          />
                          <Button
                            variant="link"
                            className="position-absolute top-50 end-0 translate-middle-y border-0 p-3"
                            onClick={() => setShowPassword(!showPassword)}
                            style={{ textDecoration: 'none' }}
                          >
                            {showPassword ? (
                              <EyeOff size={20} className="text-muted" />
                            ) : (
                              <Eye size={20} className="text-muted" />
                            )}
                          </Button>
                        </div>
                      </Form.Group>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5, duration: 0.5 }}
                    >
                      <Button
                        type="submit"
                        className="w-100 py-3 fw-semibold"
                        disabled={isLoading}
                        style={{
                          borderRadius: '10px',
                          background: 'linear-gradient(45deg, #667eea, #764ba2)',
                          border: 'none',
                          fontSize: '16px'
                        }}
                      >
                        {isLoading ? (
                          <>
                            <Spinner
                              as="span"
                              animation="border"
                              size="sm"
                              role="status"
                              aria-hidden="true"
                              className="me-2"
                            />
                            Signing In...
                          </>
                        ) : (
                          <>
                            <LogIn size={18} className="me-2" />
                            Sign In
                          </>
                        )}
                      </Button>
                    </motion.div>
                  </Form>

                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6, duration: 0.5 }}
                    className="text-center mt-4"
                  >
                    <p className="text-muted mb-0">
                      Don't have an account?{' '}
                      <Button 
                        variant="link" 
                        className="p-0 fw-semibold"
                        style={{
                          textDecoration: 'none',
                          color: '#667eea'
                        }}
                      >
                        Sign up here
                      </Button>
                    </p>
                  </motion.div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default LoginForm;
