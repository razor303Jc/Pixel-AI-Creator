import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Modal, InputGroup, Spinner } from 'react-bootstrap';
import { QRCodeSVG } from 'qrcode.react';
import { Shield, Key, Smartphone, Check, X, Copy, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface MFASetupProps {
  onSetupComplete?: (success: boolean) => void;
  onCancel?: () => void;
}

interface MFASetupData {
  secret: string;
  qr_code_url: string;
  backup_codes: string[];
}

const MFASetup: React.FC<MFASetupProps> = ({ onSetupComplete, onCancel }) => {
  const [step, setStep] = useState<'setup' | 'verify' | 'backup' | 'complete'>('setup');
  const [setupData, setSetupData] = useState<MFASetupData | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedSecret, setCopiedSecret] = useState(false);
  const [copiedBackupCodes, setCopiedBackupCodes] = useState(false);
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  // Initialize MFA setup
  useEffect(() => {
    initializeMFASetup();
  }, []);

  const initializeMFASetup = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/mfa/setup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to initialize MFA setup');
      }

      const data = await response.json();
      setSetupData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize MFA setup');
    } finally {
      setIsLoading(false);
    }
  };

  const verifyMFACode = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Please enter a valid 6-digit code');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/mfa/verify-setup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          code: verificationCode
        })
      });

      if (!response.ok) {
        throw new Error('Invalid verification code');
      }

      const result = await response.json();
      if (result.success) {
        setStep('backup');
      } else {
        setError('Invalid verification code. Please try again.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    } finally {
      setIsLoading(false);
    }
  };

  const completeMFASetup = async () => {
    setIsLoading(true);
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/mfa/complete-setup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to complete MFA setup');
      }

      setStep('complete');
      setTimeout(() => {
        onSetupComplete?.(true);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete setup');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (text: string, type: 'secret' | 'backup') => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'secret') {
        setCopiedSecret(true);
        setTimeout(() => setCopiedSecret(false), 2000);
      } else {
        setCopiedBackupCodes(true);
        setTimeout(() => setCopiedBackupCodes(false), 2000);
      }
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && step === 'verify') {
      verifyMFACode();
    }
  };

  if (isLoading && !setupData) {
    return (
      <Card className="text-center p-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-3 mb-0">Initializing MFA setup...</p>
      </Card>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={step}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
      >
        <Card>
          <Card.Header className="d-flex align-items-center">
            <Shield className="me-2" size={20} />
            <h5 className="mb-0">
              {step === 'setup' && 'Set Up Two-Factor Authentication'}
              {step === 'verify' && 'Verify Your Authenticator App'}
              {step === 'backup' && 'Save Your Backup Codes'}
              {step === 'complete' && 'MFA Setup Complete!'}
            </h5>
          </Card.Header>

          <Card.Body>
            {error && (
              <Alert variant="danger" dismissible onClose={() => setError(null)}>
                <X size={16} className="me-2" />
                {error}
              </Alert>
            )}

            {/* Setup Step */}
            {step === 'setup' && setupData && (
              <div className="text-center">
                <div className="mb-4">
                  <h6 className="text-muted mb-3">
                    <Smartphone className="me-2" size={16} />
                    Scan this QR code with your authenticator app
                  </h6>
                  
                  <div className="d-flex justify-content-center mb-3">
                    <div className="p-3 bg-white border rounded">
                      <QRCodeSVG 
                        value={setupData.qr_code_url}
                        size={200}
                        level="M"
                        includeMargin={true}
                      />
                    </div>
                  </div>

                  <Alert variant="info" className="text-start">
                    <h6 className="mb-2">Popular Authenticator Apps:</h6>
                    <ul className="mb-0">
                      <li>Google Authenticator</li>
                      <li>Microsoft Authenticator</li>
                      <li>Authy</li>
                      <li>1Password</li>
                    </ul>
                  </Alert>
                </div>

                <div className="mb-4">
                  <h6 className="text-muted mb-2">
                    <Key className="me-2" size={16} />
                    Or enter this secret key manually:
                  </h6>
                  <InputGroup>
                    <Form.Control
                      type="text"
                      value={setupData.secret}
                      readOnly
                      className="font-monospace"
                    />
                    <Button
                      variant="outline-secondary"
                      onClick={() => copyToClipboard(setupData.secret, 'secret')}
                    >
                      {copiedSecret ? <Check size={16} /> : <Copy size={16} />}
                    </Button>
                  </InputGroup>
                  {copiedSecret && (
                    <small className="text-success">Secret copied to clipboard!</small>
                  )}
                </div>

                <div className="d-flex gap-2 justify-content-center">
                  <Button variant="secondary" onClick={onCancel}>
                    Cancel
                  </Button>
                  <Button 
                    variant="primary" 
                    onClick={() => setStep('verify')}
                  >
                    Continue to Verification
                  </Button>
                </div>
              </div>
            )}

            {/* Verify Step */}
            {step === 'verify' && (
              <div className="text-center">
                <div className="mb-4">
                  <Smartphone className="text-primary mb-3" size={48} />
                  <h6 className="mb-2">Enter the 6-digit code from your authenticator app</h6>
                  <p className="text-muted">
                    Open your authenticator app and enter the code that appears for this account.
                  </p>
                </div>

                <div className="mb-4">
                  <Form.Group className="d-flex justify-content-center">
                    <Form.Control
                      type="text"
                      placeholder="000000"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      onKeyPress={handleKeyPress}
                      className="text-center font-monospace"
                      style={{ 
                        maxWidth: '200px', 
                        fontSize: '1.2rem', 
                        letterSpacing: '0.2rem' 
                      }}
                      maxLength={6}
                    />
                  </Form.Group>
                  <small className="text-muted">
                    Code refreshes every 30 seconds
                  </small>
                </div>

                <div className="d-flex gap-2 justify-content-center">
                  <Button 
                    variant="secondary" 
                    onClick={() => setStep('setup')}
                  >
                    Back
                  </Button>
                  <Button 
                    variant="primary" 
                    onClick={verifyMFACode}
                    disabled={isLoading || verificationCode.length !== 6}
                  >
                    {isLoading ? (
                      <>
                        <Spinner size="sm" className="me-2" />
                        Verifying...
                      </>
                    ) : (
                      'Verify Code'
                    )}
                  </Button>
                </div>
              </div>
            )}

            {/* Backup Codes Step */}
            {step === 'backup' && setupData && (
              <div>
                <Alert variant="warning">
                  <h6 className="mb-2">⚠️ Important: Save Your Backup Codes</h6>
                  <p className="mb-0">
                    These backup codes can be used to access your account if you lose your authenticator device. 
                    Store them in a safe place. Each code can only be used once.
                  </p>
                </Alert>

                <div className="mb-4">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <h6 className="mb-0">Backup Codes:</h6>
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={() => copyToClipboard(setupData.backup_codes.join('\n'), 'backup')}
                    >
                      {copiedBackupCodes ? <Check size={14} /> : <Copy size={14} />}
                      {copiedBackupCodes ? ' Copied!' : ' Copy All'}
                    </Button>
                  </div>

                  <Card className="bg-light">
                    <Card.Body>
                      <div className="row">
                        {setupData.backup_codes.map((code, index) => (
                          <div key={index} className="col-md-6 mb-2">
                            <code className="d-block p-2 bg-white border rounded text-center">
                              {code}
                            </code>
                          </div>
                        ))}
                      </div>
                    </Card.Body>
                  </Card>
                </div>

                <Form.Check
                  type="checkbox"
                  id="backup-codes-saved"
                  label="I have saved these backup codes in a secure location"
                  checked={showBackupCodes}
                  onChange={(e) => setShowBackupCodes(e.target.checked)}
                  className="mb-4"
                />

                <div className="d-flex gap-2 justify-content-center">
                  <Button variant="secondary" onClick={() => setStep('verify')}>
                    Back
                  </Button>
                  <Button 
                    variant="success" 
                    onClick={completeMFASetup}
                    disabled={!showBackupCodes || isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Spinner size="sm" className="me-2" />
                        Completing...
                      </>
                    ) : (
                      'Complete Setup'
                    )}
                  </Button>
                </div>
              </div>
            )}

            {/* Complete Step */}
            {step === 'complete' && (
              <div className="text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, damping: 20 }}
                >
                  <div className="text-success mb-3">
                    <Check size={64} />
                  </div>
                </motion.div>
                
                <h4 className="text-success mb-3">Two-Factor Authentication Enabled!</h4>
                <p className="text-muted mb-4">
                  Your account is now protected with two-factor authentication. 
                  You'll need to enter a code from your authenticator app when logging in.
                </p>

                <Alert variant="success">
                  <h6 className="mb-2">What's Next?</h6>
                  <ul className="mb-0 text-start">
                    <li>Test your authenticator app by logging out and back in</li>
                    <li>Keep your backup codes in a safe place</li>
                    <li>Consider adding multiple authenticator devices</li>
                  </ul>
                </Alert>
              </div>
            )}
          </Card.Body>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
};

export default MFASetup;
