import React, { useState, useEffect, useMemo } from 'react';
import { Form, ProgressBar, Badge, ListGroup } from 'react-bootstrap';
import { Check, X, Eye, EyeOff, Shield, AlertTriangle, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface PasswordStrengthProps {
  password: string;
  showPassword?: boolean;
  onPasswordChange: (password: string) => void;
  onToggleVisibility?: () => void;
  onStrengthChange?: (strength: number, isValid: boolean) => void;
  minLength?: number;
  requireUppercase?: boolean;
  requireLowercase?: boolean;
  requireNumbers?: boolean;
  requireSpecialChars?: boolean;
  preventCommonPasswords?: boolean;
}

interface PasswordRule {
  id: string;
  label: string;
  test: (password: string) => boolean;
  required: boolean;
}

interface PasswordStrengthResult {
  score: number;
  level: 'very-weak' | 'weak' | 'fair' | 'good' | 'strong';
  color: string;
  message: string;
  isValid: boolean;
}

const PasswordStrengthIndicator: React.FC<PasswordStrengthProps> = ({
  password,
  showPassword = false,
  onPasswordChange,
  onToggleVisibility,
  onStrengthChange,
  minLength = 8,
  requireUppercase = true,
  requireLowercase = true,
  requireNumbers = true,
  requireSpecialChars = true,
  preventCommonPasswords = true
}) => {
  const [showRules, setShowRules] = useState(false);
  const [commonPasswords] = useState([
    'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',
    'admin', 'letmein', 'welcome', 'monkey', '1234567890', 'iloveyou',
    'princess', 'rockyou', 'babygirl', 'michael', 'shadow', 'master',
    'jennifer', 'jordan', 'superman', 'harley', 'robert', 'daniel'
  ]);

  const rules: PasswordRule[] = useMemo(() => [
    {
      id: 'length',
      label: `At least ${minLength} characters`,
      test: (pwd) => pwd.length >= minLength,
      required: true
    },
    {
      id: 'uppercase',
      label: 'At least one uppercase letter (A-Z)',
      test: (pwd) => /[A-Z]/.test(pwd),
      required: requireUppercase
    },
    {
      id: 'lowercase',
      label: 'At least one lowercase letter (a-z)',
      test: (pwd) => /[a-z]/.test(pwd),
      required: requireLowercase
    },
    {
      id: 'numbers',
      label: 'At least one number (0-9)',
      test: (pwd) => /[0-9]/.test(pwd),
      required: requireNumbers
    },
    {
      id: 'special',
      label: 'At least one special character (!@#$%^&*)',
      test: (pwd) => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>?]/.test(pwd),
      required: requireSpecialChars
    },
    {
      id: 'common',
      label: 'Not a common password',
      test: (pwd) => !commonPasswords.includes(pwd.toLowerCase()),
      required: preventCommonPasswords
    },
    {
      id: 'repetitive',
      label: 'No repetitive characters (aaa, 111)',
      test: (pwd) => !/(.)\1{2,}/.test(pwd),
      required: true
    },
    {
      id: 'sequential',
      label: 'No sequential characters (abc, 123)',
      test: (pwd) => {
        const sequential = ['abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij', 'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr', 'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz', '123', '234', '345', '456', '567', '678', '789', '890'];
        return !sequential.some(seq => pwd.toLowerCase().includes(seq));
      },
      required: false
    }
  ], [minLength, requireUppercase, requireLowercase, requireNumbers, requireSpecialChars, preventCommonPasswords, commonPasswords]);

  const passwordStrength: PasswordStrengthResult = useMemo(() => {
    if (!password) {
      return {
        score: 0,
        level: 'very-weak',
        color: 'secondary',
        message: 'Enter a password',
        isValid: false
      };
    }

    const passedRules = rules.filter(rule => rule.test(password));
    const requiredRules = rules.filter(rule => rule.required);
    const passedRequiredRules = requiredRules.filter(rule => rule.test(password));
    
    const score = Math.min((passedRules.length / rules.length) * 100, 100);
    const isValid = passedRequiredRules.length === requiredRules.length;

    let level: PasswordStrengthResult['level'];
    let color: string;
    let message: string;

    if (score < 25) {
      level = 'very-weak';
      color = 'danger';
      message = 'Very weak password';
    } else if (score < 50) {
      level = 'weak';
      color = 'warning';
      message = 'Weak password';
    } else if (score < 75) {
      level = 'fair';
      color = 'info';
      message = 'Fair password';
    } else if (score < 90) {
      level = 'good';
      color = 'primary';
      message = 'Good password';
    } else {
      level = 'strong';
      color = 'success';
      message = 'Strong password';
    }

    return { score, level, color, message, isValid };
  }, [password, rules]);

  useEffect(() => {
    onStrengthChange?.(passwordStrength.score, passwordStrength.isValid);
  }, [passwordStrength.score, passwordStrength.isValid, onStrengthChange]);

  useEffect(() => {
    if (password.length > 0) {
      setShowRules(true);
    }
  }, [password]);

  const getStrengthIcon = () => {
    switch (passwordStrength.level) {
      case 'very-weak':
      case 'weak':
        return <X className="text-danger" size={16} />;
      case 'fair':
        return <AlertTriangle className="text-warning" size={16} />;
      case 'good':
        return <Shield className="text-primary" size={16} />;
      case 'strong':
        return <Check className="text-success" size={16} />;
      default:
        return <Info className="text-secondary" size={16} />;
    }
  };

  return (
    <div className="password-strength-container">
      <Form.Group className="mb-3">
        <Form.Label className="d-flex align-items-center justify-content-between">
          <span>Password</span>
          <div className="d-flex align-items-center gap-2">
            {passwordStrength.score > 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="d-flex align-items-center gap-1"
              >
                {getStrengthIcon()}
                <Badge bg={passwordStrength.color} className="text-white">
                  {passwordStrength.message}
                </Badge>
              </motion.div>
            )}
            {onToggleVisibility && (
              <button
                type="button"
                className="btn btn-link p-0 border-0"
                onClick={onToggleVisibility}
                style={{ minWidth: 'auto' }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            )}
          </div>
        </Form.Label>

        <Form.Control
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(e) => onPasswordChange(e.target.value)}
          onFocus={() => setShowRules(true)}
          className={`${passwordStrength.score > 0 ? `border-${passwordStrength.color}` : ''}`}
          placeholder="Enter your password"
        />

        {password.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2"
          >
            <div className="d-flex align-items-center justify-content-between mb-1">
              <small className="text-muted">Password strength:</small>
              <small className={`text-${passwordStrength.color} fw-bold`}>
                {Math.round(passwordStrength.score)}%
              </small>
            </div>
            <ProgressBar
              variant={passwordStrength.color}
              now={passwordStrength.score}
              className="mb-2"
              style={{ height: '6px' }}
            />
          </motion.div>
        )}
      </Form.Group>

      <AnimatePresence>
        {showRules && password.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ListGroup variant="flush" className="mb-3">
              <ListGroup.Item className="border-0 px-0 py-1">
                <small className="text-muted fw-bold">Password Requirements:</small>
              </ListGroup.Item>
              {rules.map((rule) => {
                const passed = rule.test(password);
                const isRequired = rule.required;
                
                return (
                  <motion.div
                    key={rule.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    <ListGroup.Item className="border-0 px-0 py-1">
                      <div className="d-flex align-items-center gap-2">
                        <motion.div
                          animate={{ 
                            scale: passed ? 1.1 : 1,
                            rotate: passed ? [0, 10, -10, 0] : 0
                          }}
                          transition={{ duration: 0.3 }}
                        >
                          {passed ? (
                            <Check className="text-success" size={14} />
                          ) : (
                            <X className={`text-${isRequired ? 'danger' : 'muted'}`} size={14} />
                          )}
                        </motion.div>
                        <small 
                          className={`${passed ? 'text-success' : isRequired ? 'text-danger' : 'text-muted'} ${passed ? 'text-decoration-line-through' : ''}`}
                        >
                          {rule.label}
                          {!isRequired && (
                            <Badge bg="secondary" className="ms-1" style={{ fontSize: '0.6em' }}>
                              optional
                            </Badge>
                          )}
                        </small>
                      </div>
                    </ListGroup.Item>
                  </motion.div>
                );
              })}
            </ListGroup>

            {passwordStrength.isValid && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="alert alert-success py-2 px-3 d-flex align-items-center gap-2"
              >
                <Check size={16} />
                <small className="mb-0 fw-bold">
                  Great! Your password meets all security requirements.
                </small>
              </motion.div>
            )}

            {password.length >= minLength && !passwordStrength.isValid && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="alert alert-warning py-2 px-3 d-flex align-items-center gap-2"
              >
                <AlertTriangle size={16} />
                <small className="mb-0">
                  Your password doesn't meet all security requirements yet.
                </small>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {password.length > 0 && (
        <div className="mt-2">
          <small className="text-muted">
            💡 <strong>Tip:</strong> Use a mix of letters, numbers, and symbols. 
            Avoid common words and personal information.
          </small>
        </div>
      )}
    </div>
  );
};

export default PasswordStrengthIndicator;
