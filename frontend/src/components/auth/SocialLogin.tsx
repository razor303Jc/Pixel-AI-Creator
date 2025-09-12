import React, { useState, useEffect, useCallback } from 'react';
import { Card, Button, Alert, Badge, Spinner } from 'react-bootstrap';
import { Github, Mail, Linkedin, Link, Unlink, Check, X, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';

interface SocialAccount {
  provider: string;
  provider_id: string;
  email: string;
  name: string;
  connected_at: string;
  is_primary: boolean;
}

interface SocialLoginProps {
  mode?: 'login' | 'connect';
  onLoginSuccess?: (token: string) => void;
  onConnectionUpdate?: () => void;
}

const SocialLogin: React.FC<SocialLoginProps> = ({ 
  mode = 'login', 
  onLoginSuccess,
  onConnectionUpdate 
}) => {
  const [connectedAccounts, setConnectedAccounts] = useState<SocialAccount[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProvider, setLoadingProvider] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const providers = [
    {
      name: 'google',
      displayName: 'Google',
      icon: Mail,
      color: 'danger',
      description: 'Sign in with your Google account'
    },
    {
      name: 'github',
      displayName: 'GitHub',
      icon: Github,
      color: 'dark',
      description: 'Sign in with your GitHub account'
    },
    {
      name: 'linkedin',
      displayName: 'LinkedIn',
      icon: Linkedin,
      color: 'primary',
      description: 'Sign in with your LinkedIn account'
    }
  ];

  const loadConnectedAccounts = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/social/accounts', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const accounts = await response.json();
        setConnectedAccounts(accounts);
      }
    } catch (err) {
      console.error('Failed to load connected accounts:', err);
    }
  }, []);

  const handleOAuthCallback = useCallback(async (provider: string, code: string, state: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const endpoint = mode === 'login'
        ? `/api/v1/auth/social/${provider}/callback`
        : `/api/v1/auth/social/${provider}/callback`;

      const headers: HeadersInit = {
        'Content-Type': 'application/json'
      };

      if (mode === 'connect') {
        const token = localStorage.getItem('token');
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          code,
          state
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'OAuth callback failed');
      }

      const result = await response.json();

      if (mode === 'login' && result.access_token) {
        localStorage.setItem('token', result.access_token);
        onLoginSuccess?.(result.access_token);
      } else if (mode === 'connect') {
        setSuccess(`Successfully connected ${provider} account!`);
        loadConnectedAccounts();
        onConnectionUpdate?.();
      }

      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'OAuth callback failed');
    } finally {
      setIsLoading(false);
    }
  }, [mode, onLoginSuccess, onConnectionUpdate, loadConnectedAccounts]);

  useEffect(() => {
    if (mode === 'connect') {
      loadConnectedAccounts();
    }

    // Handle OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const provider = urlParams.get('provider');
    const error = urlParams.get('error');

    if (error) {
      setError(`OAuth error: ${error}`);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (code && state && provider) {
      handleOAuthCallback(provider, code, state);
    }
  }, [mode, handleOAuthCallback, loadConnectedAccounts]);

  const disconnectAccount = async (provider: string) => {
    setLoadingProvider(provider);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/auth/social/${provider}/disconnect`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to disconnect account');
      }

      setSuccess(`Successfully disconnected ${provider} account!`);
      loadConnectedAccounts();
      onConnectionUpdate?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to disconnect account');
    } finally {
      setLoadingProvider(null);
    }
  };

  const isConnected = (provider: string) => {
    return connectedAccounts.some(account => account.provider === provider);
  };

  const initiateOAuth = async (provider: string) => {
    setLoadingProvider(provider);
    setError(null);
    setSuccess(null);

    try {
      const endpoint = `/api/v1/auth/social/${provider}/authorize`;
      const params = new URLSearchParams({
        redirect_uri: `${window.location.origin}/auth/callback`,
        mode: mode
      });

      // Redirect to OAuth authorization URL
      window.location.href = `${endpoint}?${params.toString()}`;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initiate OAuth');
      setLoadingProvider(null);
    }
  };

  const getConnectedAccount = (provider: string) => {
    return connectedAccounts.find(account => account.provider === provider);
  };

  if (isLoading && mode === 'login') {
    return (
      <Card className="text-center p-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Processing OAuth...</span>
        </Spinner>
        <p className="mt-3 mb-0">Completing social login...</p>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card>
        <Card.Header>
          <h5 className="mb-0 d-flex align-items-center">
            <Link className="me-2" size={20} />
            {mode === 'login' ? 'Social Login' : 'Connected Accounts'}
          </h5>
          {mode === 'connect' && (
            <small className="text-muted">
              Connect your social accounts for easier login
            </small>
          )}
        </Card.Header>

        <Card.Body>
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              <X size={16} className="me-2" />
              {error}
            </Alert>
          )}

          {success && (
            <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
              <Check size={16} className="me-2" />
              {success}
            </Alert>
          )}

          <div className="d-grid gap-3">
            {providers.map((provider) => {
              const connected = isConnected(provider.name);
              const account = getConnectedAccount(provider.name);
              const isProviderLoading = loadingProvider === provider.name;

              return (
                <motion.div
                  key={provider.name}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card className={`border ${connected ? 'border-success' : ''}`}>
                    <Card.Body className="p-3">
                      <div className="d-flex align-items-center justify-content-between">
                        <div className="d-flex align-items-center">
                          <provider.icon 
                            className={`text-${provider.color} me-3`} 
                            size={24} 
                          />
                          <div>
                            <h6 className="mb-0 d-flex align-items-center">
                              {provider.displayName}
                              {connected && (
                                <Badge bg="success" className="ms-2">
                                  Connected
                                </Badge>
                              )}
                              {account?.is_primary && (
                                <Badge bg="primary" className="ms-2">
                                  Primary
                                </Badge>
                              )}
                            </h6>
                            {mode === 'login' && (
                              <small className="text-muted">
                                {provider.description}
                              </small>
                            )}
                            {mode === 'connect' && account && (
                              <small className="text-muted">
                                {account.email} • Connected {new Date(account.connected_at).toLocaleDateString()}
                              </small>
                            )}
                          </div>
                        </div>

                        <div>
                          {mode === 'login' ? (
                            <Button
                              variant={`outline-${provider.color}`}
                              onClick={() => initiateOAuth(provider.name)}
                              disabled={isProviderLoading}
                              className="d-flex align-items-center"
                            >
                              {isProviderLoading ? (
                                <Spinner size="sm" className="me-2" />
                              ) : (
                                <ExternalLink size={16} className="me-2" />
                              )}
                              {isProviderLoading ? 'Connecting...' : 'Sign In'}
                            </Button>
                          ) : (
                            <>
                              {connected ? (
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => disconnectAccount(provider.name)}
                                  disabled={isProviderLoading}
                                  className="d-flex align-items-center"
                                >
                                  {isProviderLoading ? (
                                    <Spinner size="sm" className="me-2" />
                                  ) : (
                                    <Unlink size={14} className="me-2" />
                                  )}
                                  {isProviderLoading ? 'Disconnecting...' : 'Disconnect'}
                                </Button>
                              ) : (
                                <Button
                                  variant={`outline-${provider.color}`}
                                  size="sm"
                                  onClick={() => initiateOAuth(provider.name)}
                                  disabled={isProviderLoading}
                                  className="d-flex align-items-center"
                                >
                                  {isProviderLoading ? (
                                    <Spinner size="sm" className="me-2" />
                                  ) : (
                                    <Link size={14} className="me-2" />
                                  )}
                                  {isProviderLoading ? 'Connecting...' : 'Connect'}
                                </Button>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    </Card.Body>
                  </Card>
                </motion.div>
              );
            })}
          </div>

          {mode === 'login' && (
            <div className="text-center mt-3">
              <small className="text-muted">
                By continuing, you agree to our Terms of Service and Privacy Policy
              </small>
            </div>
          )}

          {mode === 'connect' && connectedAccounts.length > 0 && (
            <Alert variant="info" className="mt-3 mb-0">
              <small>
                <strong>Tip:</strong> You can use any connected account to sign in to your account. 
                We recommend keeping at least one account connected as a backup login method.
              </small>
            </Alert>
          )}
        </Card.Body>
      </Card>
    </motion.div>
  );
};

export default SocialLogin;
