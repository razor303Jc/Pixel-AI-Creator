import React, { useState, useEffect, useRef } from 'react';
import { Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { Shield, Key, RefreshCw, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

interface MFAVerificationProps {
  onVerificationSuccess: (token: string) => void;
  onVerificationError?: (error: any) => void;
  onCancel?: () => void;
  tempToken: string;
}

const MFAVerification: React.FC<MFAVerificationProps> = ({ 
  onVerificationSuccess, 
  onVerificationError,
  onCancel, 
  tempToken 
}) => {
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(30);
  const [useBackupCode, setUseBackupCode] = useState(false);
  const [backupCode, setBackupCode] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Auto-focus input
    if (inputRef.current) {
      inputRef.current.focus();
    }

    // Start countdown timer
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const verifyMFA = async (code: string, isBackupCode: boolean = false) => {
    if ((!isBackupCode && code.length !== 6) || (isBackupCode && code.length < 8)) {
      setError(isBackupCode ? 'Please enter a valid backup code' : 'Please enter a valid 6-digit code');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/auth/mfa/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tempToken}`
        },
        body: JSON.stringify({
          code: code,
          is_backup_code: isBackupCode
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Verification failed');
      }

      const result = await response.json();
      if (result.access_token) {
        onVerificationSuccess(result.access_token);
      } else {
        setError('Verification failed. Please try again.');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Verification failed';
      setError(errorMessage);
      onVerificationError?.(errorMessage);
      // Clear the input on error
      if (isBackupCode) {
        setBackupCode('');
      } else {
        setVerificationCode('');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (useBackupCode) {
      verifyMFA(backupCode, true);
    } else {
      verifyMFA(verificationCode, false);
    }
  };

  const handleCodeChange = (value: string) => {
    const numericValue = value.replace(/\D/g, '').slice(0, 6);
    setVerificationCode(numericValue);
    setError(null);

    // Auto-submit when 6 digits are entered
    if (numericValue.length === 6) {
      setTimeout(() => verifyMFA(numericValue, false), 100);
    }
  };

  const handleBackupCodeChange = (value: string) => {
    // Allow alphanumeric for backup codes
    const cleanValue = value.replace(/[^a-zA-Z0-9]/g, '').slice(0, 12);
    setBackupCode(cleanValue);
    setError(null);
  };

  const requestNewCode = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/auth/mfa/resend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tempToken}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to resend verification code');
      }

      setCountdown(30);
      setVerificationCode('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resend code');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card>
        <Card.Header className="text-center">
          <Shield className="text-primary mb-2" size={32} />
          <h4 className="mb-0">Two-Factor Authentication</h4>
          <p className="text-muted mb-0">
            {useBackupCode 
              ? 'Enter your backup code' 
              : 'Enter the code from your authenticator app'
            }
          </p>
        </Card.Header>

        <Card.Body>
          {error && (
            <Alert variant="danger" className="mb-3">
              {error}
            </Alert>
          )}

          <Form onSubmit={handleSubmit}>
            {!useBackupCode ? (
              // Regular MFA code input
              <Form.Group className="mb-3">
                <Form.Label className="d-flex align-items-center justify-content-center">
                  <Key className="me-2" size={16} />
                  Authentication Code
                </Form.Label>
                <Form.Control
                  ref={inputRef}
                  type="text"
                  placeholder="000000"
                  value={verificationCode}
                  onChange={(e) => handleCodeChange(e.target.value)}
                  className="text-center font-monospace"
                  style={{ 
                    fontSize: '1.5rem', 
                    letterSpacing: '0.3rem',
                    height: '60px'
                  }}
                  maxLength={6}
                  disabled={isLoading}
                />
                <Form.Text className="text-muted d-flex align-items-center justify-content-center mt-2">
                  <Clock className="me-1" size={14} />
                  {countdown > 0 ? (
                    `New code in ${countdown}s`
                  ) : (
                    <Button 
                      variant="link" 
                      size="sm" 
                      className="p-0"
                      onClick={requestNewCode}
                      disabled={isLoading}
                    >
                      <RefreshCw className="me-1" size={14} />
                      Get new code
                    </Button>
                  )}
                </Form.Text>
              </Form.Group>
            ) : (
              // Backup code input
              <Form.Group className="mb-3">
                <Form.Label className="d-flex align-items-center justify-content-center">
                  <Key className="me-2" size={16} />
                  Backup Code
                </Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Enter backup code"
                  value={backupCode}
                  onChange={(e) => handleBackupCodeChange(e.target.value)}
                  className="text-center font-monospace"
                  style={{ 
                    fontSize: '1.2rem', 
                    letterSpacing: '0.2rem',
                    height: '50px'
                  }}
                  maxLength={12}
                  disabled={isLoading}
                />
                <Form.Text className="text-muted text-center">
                  Each backup code can only be used once
                </Form.Text>
              </Form.Group>
            )}

            <div className="d-grid gap-2 mb-3">
              <Button 
                type="submit" 
                variant="primary" 
                size="lg"
                disabled={
                  isLoading || 
                  (!useBackupCode && verificationCode.length !== 6) ||
                  (useBackupCode && backupCode.length < 8)
                }
              >
                {isLoading ? (
                  <>
                    <Spinner size="sm" className="me-2" />
                    Verifying...
                  </>
                ) : (
                  'Verify'
                )}
              </Button>
            </div>

            <div className="text-center">
              <Button 
                variant="link" 
                size="sm"
                onClick={() => {
                  setUseBackupCode(!useBackupCode);
                  setError(null);
                  setVerificationCode('');
                  setBackupCode('');
                }}
                disabled={isLoading}
              >
                {useBackupCode 
                  ? 'Use authenticator app instead' 
                  : 'Use backup code instead'
                }
              </Button>

              {onCancel && (
                <>
                  <br />
                  <Button 
                    variant="link" 
                    size="sm"
                    onClick={onCancel}
                    disabled={isLoading}
                    className="text-muted"
                  >
                    Cancel and sign out
                  </Button>
                </>
              )}
            </div>
          </Form>

          <Alert variant="info" className="mt-3 mb-0">
            <small>
              <strong>Tip:</strong> If you don't have access to your authenticator app, 
              you can use one of your backup codes instead.
            </small>
          </Alert>
        </Card.Body>
      </Card>
    </motion.div>
  );
};

export default MFAVerification;
