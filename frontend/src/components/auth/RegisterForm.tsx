import React, { useState, useContext } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { UserPlus, Mail, Lock, User, Building } from 'lucide-react';
import { AuthContext } from '../../contexts/AuthContext';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
}

interface ValidationErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  firstName?: string;
  lastName?: string;
}

interface PasswordStrength {
  score: number;
  feedback: string[];
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
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const authContext = useContext(AuthContext);
  const register = authContext?.register;

  // Validation functions
  const validateEmail = (email: string): string | undefined => {
    if (!email) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Please enter a valid email address';
    return undefined;
  };

  const validatePassword = (password: string): string | undefined => {
    if (!password) return 'Password is required';
    if (password.length < 8) return 'Password must be at least 8 characters long';
    if (!/(?=.*[a-z])/.test(password)) return 'Password must contain at least one lowercase letter';
    if (!/(?=.*[A-Z])/.test(password)) return 'Password must contain at least one uppercase letter';
    if (!/(?=.*\d)/.test(password)) return 'Password must contain at least one number';
    return undefined;
  };

  const validateName = (name: string, fieldName: string): string | undefined => {
    if (!name) return `${fieldName} is required`;
    if (name.length < 2) return `${fieldName} must be at least 2 characters long`;
    return undefined;
  };

  const getPasswordStrength = (password: string): PasswordStrength => {
    let score = 0;
    const feedback: string[] = [];

    if (password.length >= 8) score++;
    else feedback.push('At least 8 characters');

    if (/(?=.*[a-z])/.test(password)) score++;
    else feedback.push('One lowercase letter');

    if (/(?=.*[A-Z])/.test(password)) score++;
    else feedback.push('One uppercase letter');

    if (/(?=.*\d)/.test(password)) score++;
    else feedback.push('One number');

    if (/(?=.*[!@#$%^&*])/.test(password)) {
      score++;
      feedback.length === 0 && feedback.push('Strong password!');
    } else {
      feedback.push('One special character (!@#$%^&*)');
    }

    return { score, feedback };
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Mark field as touched for validation feedback
    setTouchedFields(prev => new Set([...prev, name]));

    // Clear general error when user starts typing
    if (error) setError('');

    // Real-time validation
    const newErrors = { ...validationErrors };
    
    switch (name) {
      case 'email':
        const emailError = validateEmail(value);
        if (emailError) newErrors.email = emailError;
        else delete newErrors.email;
        break;
      case 'password':
        const passwordError = validatePassword(value);
        if (passwordError) newErrors.password = passwordError;
        else delete newErrors.password;
        
        // Also revalidate confirm password if it exists
        if (formData.confirmPassword) {
          if (value !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
          } else {
            delete newErrors.confirmPassword;
          }
        }
        break;
      case 'confirmPassword':
        if (formData.password !== value) {
          newErrors.confirmPassword = 'Passwords do not match';
        } else {
          delete newErrors.confirmPassword;
        }
        break;
      case 'firstName':
        const firstNameError = validateName(value, 'First name');
        if (firstNameError) newErrors.firstName = firstNameError;
        else delete newErrors.firstName;
        break;
      case 'lastName':
        const lastNameError = validateName(value, 'Last name');
        if (lastNameError) newErrors.lastName = lastNameError;
        else delete newErrors.lastName;
        break;
    }

    setValidationErrors(newErrors);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Mark all fields as touched to show validation errors
    const allFields = new Set(['email', 'password', 'confirmPassword', 'firstName', 'lastName']);
    setTouchedFields(allFields);

    // Validate all fields
    const errors: ValidationErrors = {};
    errors.email = validateEmail(formData.email);
    errors.password = validatePassword(formData.password);
    errors.firstName = validateName(formData.firstName, 'First name');
    errors.lastName = validateName(formData.lastName, 'Last name');
    
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    // Remove undefined errors
    Object.keys(errors).forEach(key => {
      if (errors[key as keyof ValidationErrors] === undefined) {
        delete errors[key as keyof ValidationErrors];
      }
    });

    setValidationErrors(errors);

    // If there are validation errors, stop submission
    if (Object.keys(errors).length > 0) {
      setIsLoading(false);
      setError('Please fix the validation errors below');
      return;
    }

    if (!register) {
      setError('Authentication service not available');
      setIsLoading(false);
      return;
    }

    try {
      // Prepare data for backend (matching API expectations)
      const registrationData = {
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
        company_name: formData.companyName || undefined,
      };

      await register(registrationData);
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
                              isInvalid={touchedFields.has('firstName') && !!validationErrors.firstName}
                              isValid={touchedFields.has('firstName') && !validationErrors.firstName && formData.firstName}
                              style={{
                                borderRadius: '10px',
                                border: touchedFields.has('firstName') && validationErrors.firstName 
                                  ? '2px solid #dc3545' 
                                  : touchedFields.has('firstName') && !validationErrors.firstName && formData.firstName
                                  ? '2px solid #28a745'
                                  : '2px solid #e9ecef',
                                fontSize: '16px'
                              }}
                            />
                            {touchedFields.has('firstName') && validationErrors.firstName && (
                              <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                                {validationErrors.firstName}
                              </Form.Control.Feedback>
                            )}
                          </Form.Group>
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
                              isInvalid={touchedFields.has('lastName') && !!validationErrors.lastName}
                              isValid={touchedFields.has('lastName') && !validationErrors.lastName && formData.lastName}
                              style={{
                                borderRadius: '10px',
                                border: touchedFields.has('lastName') && validationErrors.lastName 
                                  ? '2px solid #dc3545' 
                                  : touchedFields.has('lastName') && !validationErrors.lastName && formData.lastName
                                  ? '2px solid #28a745'
                                  : '2px solid #e9ecef',
                                fontSize: '16px'
                              }}
                            />
                            {touchedFields.has('lastName') && validationErrors.lastName && (
                              <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                                {validationErrors.lastName}
                              </Form.Control.Feedback>
                            )}
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
                          isInvalid={touchedFields.has('email') && !!validationErrors.email}
                          isValid={touchedFields.has('email') && !validationErrors.email && formData.email}
                          style={{
                            borderRadius: '10px',
                            border: touchedFields.has('email') && validationErrors.email 
                              ? '2px solid #dc3545' 
                              : touchedFields.has('email') && !validationErrors.email && formData.email
                              ? '2px solid #28a745'
                              : '2px solid #e9ecef',
                            fontSize: '16px'
                          }}
                        />
                        {touchedFields.has('email') && validationErrors.email && (
                          <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                            {validationErrors.email}
                          </Form.Control.Feedback>
                        )}
                        {touchedFields.has('email') && !validationErrors.email && formData.email && (
                          <Form.Control.Feedback type="valid" style={{ display: 'block' }}>
                            Valid email address
                          </Form.Control.Feedback>
                        )}
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
                              isInvalid={touchedFields.has('password') && !!validationErrors.password}
                              isValid={touchedFields.has('password') && !validationErrors.password && formData.password}
                              style={{
                                borderRadius: '10px',
                                border: touchedFields.has('password') && validationErrors.password 
                                  ? '2px solid #dc3545' 
                                  : touchedFields.has('password') && !validationErrors.password && formData.password
                                  ? '2px solid #28a745'
                                  : '2px solid #e9ecef',
                                fontSize: '16px'
                              }}
                            />
                            {touchedFields.has('password') && validationErrors.password && (
                              <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                                {validationErrors.password}
                              </Form.Control.Feedback>
                            )}
                            {touchedFields.has('password') && formData.password && (
                              <div className="mt-2">
                                <div className="d-flex justify-content-between align-items-center mb-1">
                                  <small className="text-muted">Password strength:</small>
                                  <small className={`fw-semibold ${
                                    getPasswordStrength(formData.password).score >= 4 ? 'text-success' : 
                                    getPasswordStrength(formData.password).score >= 3 ? 'text-warning' : 'text-danger'
                                  }`}>
                                    {getPasswordStrength(formData.password).score >= 4 ? 'Strong' : 
                                     getPasswordStrength(formData.password).score >= 3 ? 'Medium' : 'Weak'}
                                  </small>
                                </div>
                                <div className="progress" style={{ height: '4px' }}>
                                  <div 
                                    className={`progress-bar ${
                                      getPasswordStrength(formData.password).score >= 4 ? 'bg-success' : 
                                      getPasswordStrength(formData.password).score >= 3 ? 'bg-warning' : 'bg-danger'
                                    }`}
                                    style={{ width: `${(getPasswordStrength(formData.password).score / 5) * 100}%` }}
                                  />
                                </div>
                                {getPasswordStrength(formData.password).feedback.length > 0 && (
                                  <small className="text-muted d-block mt-1">
                                    Needs: {getPasswordStrength(formData.password).feedback.join(', ')}
                                  </small>
                                )}
                              </div>
                            )}
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
                              isInvalid={touchedFields.has('confirmPassword') && !!validationErrors.confirmPassword}
                              isValid={touchedFields.has('confirmPassword') && !validationErrors.confirmPassword && formData.confirmPassword}
                              style={{
                                borderRadius: '10px',
                                border: touchedFields.has('confirmPassword') && validationErrors.confirmPassword 
                                  ? '2px solid #dc3545' 
                                  : touchedFields.has('confirmPassword') && !validationErrors.confirmPassword && formData.confirmPassword
                                  ? '2px solid #28a745'
                                  : '2px solid #e9ecef',
                                fontSize: '16px'
                              }}
                            />
                            {touchedFields.has('confirmPassword') && validationErrors.confirmPassword && (
                              <Form.Control.Feedback type="invalid" style={{ display: 'block' }}>
                                {validationErrors.confirmPassword}
                              </Form.Control.Feedback>
                            )}
                            {touchedFields.has('confirmPassword') && !validationErrors.confirmPassword && formData.confirmPassword && (
                              <Form.Control.Feedback type="valid" style={{ display: 'block' }}>
                                Passwords match!
                              </Form.Control.Feedback>
                            )}
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
