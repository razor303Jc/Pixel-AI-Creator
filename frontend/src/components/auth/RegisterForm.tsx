import React, { useState, useContext } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { UserPlus, Mail, Lock, User, Building } from 'lucide-react';
import { AuthContext } from '../../contexts/AuthContext';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    companyName: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const { register } = useContext(AuthContext);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      await register(formData);
      // Navigation will be handled by AuthContext
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-vh-100 d-flex align-items-center justify-content-center py-5"
      style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '20px'
      }}
    >
      <Container>
        <Row className="justify-content-center">
          <Col md={8} lg={6} xl={5}>
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
                      className="d-inline-flex align-items-center justify-content-center bg-success rounded-circle mb-3"
                      style={{ width: '60px', height: '60px' }}
                    >
                      <UserPlus size={30} className="text-white" />
                    </motion.div>
                    <h3 className="fw-bold text-dark mb-2">Create Account</h3>
                    <p className="text-muted">Join Pixel AI Creator platform</p>
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
                    <Row>
                      <Col md={6}>
                        <motion.div
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.3, duration: 0.5 }}
                        >
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold text-dark">
                              <User size={16} className="me-2" />
                              First Name
                            </Form.Label>
                            <Form.Control
                              type="text"
                              name="firstName"
                              placeholder="Enter first name"
                              value={formData.firstName}
                              onChange={handleInputChange}
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
                      </Col>
                      <Col md={6}>
                        <motion.div
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.4, duration: 0.5 }}
                        >
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold text-dark">
                              <User size={16} className="me-2" />
                              Last Name
                            </Form.Label>
                            <Form.Control
                              type="text"
                              name="lastName"
                              placeholder="Enter last name"
                              value={formData.lastName}
                              onChange={handleInputChange}
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
                      </Col>
                    </Row>

                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5, duration: 0.5 }}
                    >
                      <Form.Group className="mb-3">
                        <Form.Label className="fw-semibold text-dark">
                          <Mail size={16} className="me-2" />
                          Email Address
                        </Form.Label>
                        <Form.Control
                          type="email"
                          name="email"
                          placeholder="Enter your email"
                          value={formData.email}
                          onChange={handleInputChange}
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
                      transition={{ delay: 0.6, duration: 0.5 }}
                    >
                      <Form.Group className="mb-3">
                        <Form.Label className="fw-semibold text-dark">
                          <Building size={16} className="me-2" />
                          Company Name (Optional)
                        </Form.Label>
                        <Form.Control
                          type="text"
                          name="companyName"
                          placeholder="Enter company name"
                          value={formData.companyName}
                          onChange={handleInputChange}
                          className="py-3"
                          style={{
                            borderRadius: '10px',
                            border: '2px solid #e9ecef',
                            fontSize: '16px'
                          }}
                        />
                      </Form.Group>
                    </motion.div>

                    <Row>
                      <Col md={6}>
                        <motion.div
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.7, duration: 0.5 }}
                        >
                          <Form.Group className="mb-3">
                            <Form.Label className="fw-semibold text-dark">
                              <Lock size={16} className="me-2" />
                              Password
                            </Form.Label>
                            <Form.Control
                              type="password"
                              name="password"
                              placeholder="Enter password"
                              value={formData.password}
                              onChange={handleInputChange}
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
                      </Col>
                      <Col md={6}>
                        <motion.div
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.8, duration: 0.5 }}
                        >
                          <Form.Group className="mb-4">
                            <Form.Label className="fw-semibold text-dark">
                              <Lock size={16} className="me-2" />
                              Confirm Password
                            </Form.Label>
                            <Form.Control
                              type="password"
                              name="confirmPassword"
                              placeholder="Confirm password"
                              value={formData.confirmPassword}
                              onChange={handleInputChange}
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
                      </Col>
                    </Row>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.9, duration: 0.5 }}
                    >
                      <Button
                        type="submit"
                        className="w-100 py-3 fw-semibold"
                        disabled={isLoading}
                        style={{
                          borderRadius: '10px',
                          background: 'linear-gradient(45deg, #28a745, #20c997)',
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
                            Creating Account...
                          </>
                        ) : (
                          <>
                            <UserPlus size={18} className="me-2" />
                            Create Account
                          </>
                        )}
                      </Button>
                    </motion.div>
                  </Form>

                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.0, duration: 0.5 }}
                    className="text-center mt-4"
                  >
                    <p className="text-muted mb-0">
                      Already have an account?{' '}
                      <Button 
                        variant="link" 
                        className="p-0 fw-semibold"
                        onClick={onSwitchToLogin}
                        style={{
                          textDecoration: 'none',
                          color: '#667eea'
                        }}
                      >
                        Sign in here
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

export default RegisterForm;
