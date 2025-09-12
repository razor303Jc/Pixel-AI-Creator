import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Form, 
  Button, 
  Alert, 
  Modal, 
  Badge, 
  Spinner,
  Nav,
  Tab
} from 'react-bootstrap';
import { 
  User, 
  Lock, 
  Shield, 
  Settings, 
  Trash2, 
  Check, 
  X, 
  AlertTriangle,
  Bell,
  Globe,
  Eye,
  EyeOff,
  Download
} from 'lucide-react';
import { motion } from 'framer-motion';
import PasswordStrengthIndicator from './PasswordStrengthIndicator';
import SocialLogin from './SocialLogin';

interface UserProfile {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile_picture?: string;
  created_at: string;
  last_login: string;
  email_verified: boolean;
  mfa_enabled: boolean;
}

interface SecuritySettings {
  mfa_enabled: boolean;
  backup_codes_count: number;
  email_notifications: boolean;
  login_notifications: boolean;
  security_alerts: boolean;
  session_timeout: number;
  login_history_retention: number;
}

interface NotificationSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  marketing_emails: boolean;
  security_alerts: boolean;
  product_updates: boolean;
  weekly_summary: boolean;
}

const AccountSettings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [securitySettings, setSecuritySettings] = useState<SecuritySettings | null>(null);
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings | null>(null);
  
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Profile form state
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: ''
  });
  
  // Password change form state
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [isPasswordValid, setIsPasswordValid] = useState(false);
  
  // Modals
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showMFAModal, setShowMFAModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  useEffect(() => {
    loadAccountData();
  }, []);

  const loadAccountData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`
      };

      const [profileRes, securityRes, notificationsRes] = await Promise.all([
        fetch('/api/v1/auth/profile', { headers }),
        fetch('/api/v1/auth/settings/security', { headers }),
        fetch('/api/v1/auth/settings/notifications', { headers })
      ]);

      if (!profileRes.ok || !securityRes.ok || !notificationsRes.ok) {
        throw new Error('Failed to load account data');
      }

      const [profile, security, notifications] = await Promise.all([
        profileRes.json(),
        securityRes.json(),
        notificationsRes.json()
      ]);

      setUserProfile(profile);
      setSecuritySettings(security);
      setNotificationSettings(notifications);
      
      setProfileForm({
        first_name: profile.first_name || '',
        last_name: profile.last_name || '',
        username: profile.username || '',
        email: profile.email || ''
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load account data');
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async () => {
    setIsSaving(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/profile', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileForm)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update profile');
      }

      const updatedProfile = await response.json();
      setUserProfile(updatedProfile);
      setSuccess('Profile updated successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const changePassword = async () => {
    if (!isPasswordValid) {
      setError('Please ensure your new password meets all requirements');
      return;
    }

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to change password');
      }

      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      setSuccess('Password changed successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to change password');
    } finally {
      setIsSaving(false);
    }
  };

  const updateSecuritySettings = async (updates: Partial<SecuritySettings>) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/settings/security', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        throw new Error('Failed to update security settings');
      }

      const updatedSettings = await response.json();
      setSecuritySettings(updatedSettings);
      setSuccess('Security settings updated successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update security settings');
    }
  };

  const updateNotificationSettings = async (updates: Partial<NotificationSettings>) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/settings/notifications', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        throw new Error('Failed to update notification settings');
      }

      const updatedSettings = await response.json();
      setNotificationSettings(updatedSettings);
      setSuccess('Notification settings updated successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update notification settings');
    }
  };

  const deleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') {
      setError('Please type "DELETE" to confirm account deletion');
      return;
    }

    setIsSaving(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/delete-account', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete account');
      }

      // Clear local storage and redirect
      localStorage.removeItem('token');
      window.location.href = '/login';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete account');
      setIsSaving(false);
    }
  };

  const exportAccountData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1/auth/export-data', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to export account data');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `account-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export account data');
    }
  };

  if (isLoading) {
    return (
      <Card className="text-center p-4">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading account settings...</span>
        </Spinner>
        <p className="mt-3 mb-0">Loading account settings...</p>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="mb-0 d-flex align-items-center">
          <Settings className="me-2" size={24} />
          Account Settings
        </h4>
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={exportAccountData}
          className="d-flex align-items-center"
        >
          <Download size={14} className="me-2" />
          Export Data
        </Button>
      </div>

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

      <Tab.Container activeKey={activeTab} onSelect={(k) => setActiveTab(k || 'profile')}>
        <Card>
          <Card.Header>
            <Nav variant="tabs" className="card-header-tabs">
              <Nav.Item>
                <Nav.Link eventKey="profile" className="d-flex align-items-center">
                  <User size={16} className="me-2" />
                  Profile
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="security" className="d-flex align-items-center">
                  <Shield size={16} className="me-2" />
                  Security
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="notifications" className="d-flex align-items-center">
                  <Bell size={16} className="me-2" />
                  Notifications
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="accounts" className="d-flex align-items-center">
                  <Globe size={16} className="me-2" />
                  Connected Accounts
                </Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="privacy" className="d-flex align-items-center">
                  <Eye size={16} className="me-2" />
                  Privacy
                </Nav.Link>
              </Nav.Item>
            </Nav>
          </Card.Header>

          <Tab.Content>
            {/* Profile Tab */}
            <Tab.Pane eventKey="profile">
              <Card.Body>
                <Row>
                  <Col md={8}>
                    <h5 className="mb-3">Personal Information</h5>
                    <Form>
                      <Row>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label>First Name</Form.Label>
                            <Form.Control
                              type="text"
                              value={profileForm.first_name}
                              onChange={(e) => setProfileForm({
                                ...profileForm,
                                first_name: e.target.value
                              })}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={6}>
                          <Form.Group className="mb-3">
                            <Form.Label>Last Name</Form.Label>
                            <Form.Control
                              type="text"
                              value={profileForm.last_name}
                              onChange={(e) => setProfileForm({
                                ...profileForm,
                                last_name: e.target.value
                              })}
                            />
                          </Form.Group>
                        </Col>
                      </Row>

                      <Form.Group className="mb-3">
                        <Form.Label>Username</Form.Label>
                        <Form.Control
                          type="text"
                          value={profileForm.username}
                          onChange={(e) => setProfileForm({
                            ...profileForm,
                            username: e.target.value
                          })}
                        />
                      </Form.Group>

                      <Form.Group className="mb-3">
                        <Form.Label className="d-flex align-items-center">
                          Email Address
                          {userProfile?.email_verified && (
                            <Badge bg="success" className="ms-2">Verified</Badge>
                          )}
                        </Form.Label>
                        <Form.Control
                          type="email"
                          value={profileForm.email}
                          onChange={(e) => setProfileForm({
                            ...profileForm,
                            email: e.target.value
                          })}
                        />
                      </Form.Group>

                      <Button
                        variant="primary"
                        onClick={updateProfile}
                        disabled={isSaving}
                        className="d-flex align-items-center"
                      >
                        {isSaving ? (
                          <>
                            <Spinner size="sm" className="me-2" />
                            Saving...
                          </>
                        ) : (
                          <>
                            <Check size={16} className="me-2" />
                            Save Changes
                          </>
                        )}
                      </Button>
                    </Form>
                  </Col>

                  <Col md={4}>
                    <h5 className="mb-3">Account Information</h5>
                    <div className="bg-light p-3 rounded">
                      <p className="mb-2">
                        <strong>Account created:</strong><br />
                        <small className="text-muted">
                          {userProfile && new Date(userProfile.created_at).toLocaleDateString()}
                        </small>
                      </p>
                      <p className="mb-0">
                        <strong>Last login:</strong><br />
                        <small className="text-muted">
                          {userProfile && new Date(userProfile.last_login).toLocaleDateString()}
                        </small>
                      </p>
                    </div>
                  </Col>
                </Row>

                <hr className="my-4" />

                <h5 className="mb-3">Change Password</h5>
                <Row>
                  <Col md={8}>
                    <Form>
                      <Form.Group className="mb-3">
                        <Form.Label className="d-flex align-items-center justify-content-between">
                          Current Password
                          <button
                            type="button"
                            className="btn btn-link p-0 border-0"
                            onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                          >
                            {showCurrentPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                          </button>
                        </Form.Label>
                        <Form.Control
                          type={showCurrentPassword ? 'text' : 'password'}
                          value={passwordForm.current_password}
                          onChange={(e) => setPasswordForm({
                            ...passwordForm,
                            current_password: e.target.value
                          })}
                        />
                      </Form.Group>

                      <PasswordStrengthIndicator
                        password={passwordForm.new_password}
                        showPassword={showNewPassword}
                        onPasswordChange={(password) => setPasswordForm({
                          ...passwordForm,
                          new_password: password
                        })}
                        onToggleVisibility={() => setShowNewPassword(!showNewPassword)}
                        onStrengthChange={(strength, isValid) => {
                          setIsPasswordValid(isValid);
                        }}
                      />

                      <Form.Group className="mb-3">
                        <Form.Label>Confirm New Password</Form.Label>
                        <Form.Control
                          type="password"
                          value={passwordForm.confirm_password}
                          onChange={(e) => setPasswordForm({
                            ...passwordForm,
                            confirm_password: e.target.value
                          })}
                          isInvalid={passwordForm.confirm_password !== passwordForm.new_password && passwordForm.confirm_password.length > 0}
                        />
                        <Form.Control.Feedback type="invalid">
                          Passwords do not match
                        </Form.Control.Feedback>
                      </Form.Group>

                      <Button
                        variant="warning"
                        onClick={changePassword}
                        disabled={isSaving || !isPasswordValid || passwordForm.new_password !== passwordForm.confirm_password}
                        className="d-flex align-items-center"
                      >
                        {isSaving ? (
                          <>
                            <Spinner size="sm" className="me-2" />
                            Changing...
                          </>
                        ) : (
                          <>
                            <Lock size={16} className="me-2" />
                            Change Password
                          </>
                        )}
                      </Button>
                    </Form>
                  </Col>
                </Row>
              </Card.Body>
            </Tab.Pane>

            {/* Security Tab */}
            <Tab.Pane eventKey="security">
              <Card.Body>
                <h5 className="mb-3">Security Settings</h5>
                
                {securitySettings && (
                  <>
                    <div className="d-flex justify-content-between align-items-center p-3 border rounded mb-3">
                      <div>
                        <h6 className="mb-1">Two-Factor Authentication</h6>
                        <small className="text-muted">
                          Add an extra layer of security to your account
                        </small>
                      </div>
                      <div className="d-flex align-items-center gap-2">
                        <Badge bg={securitySettings.mfa_enabled ? 'success' : 'secondary'}>
                          {securitySettings.mfa_enabled ? 'Enabled' : 'Disabled'}
                        </Badge>
                        <Button
                          variant={securitySettings.mfa_enabled ? 'outline-danger' : 'outline-primary'}
                          size="sm"
                          onClick={() => setShowMFAModal(true)}
                        >
                          {securitySettings.mfa_enabled ? 'Disable' : 'Enable'}
                        </Button>
                      </div>
                    </div>

                    <div className="mb-3">
                      <Form.Check
                        type="switch"
                        id="email-notifications"
                        label="Email me about suspicious login attempts"
                        checked={securitySettings.email_notifications}
                        onChange={(e) => updateSecuritySettings({
                          email_notifications: e.target.checked
                        })}
                      />
                    </div>

                    <div className="mb-3">
                      <Form.Check
                        type="switch"
                        id="login-notifications"
                        label="Email me about successful logins from new devices"
                        checked={securitySettings.login_notifications}
                        onChange={(e) => updateSecuritySettings({
                          login_notifications: e.target.checked
                        })}
                      />
                    </div>

                    <div className="mb-4">
                      <Form.Check
                        type="switch"
                        id="security-alerts"
                        label="Receive security alerts and recommendations"
                        checked={securitySettings.security_alerts}
                        onChange={(e) => updateSecuritySettings({
                          security_alerts: e.target.checked
                        })}
                      />
                    </div>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Session Timeout (minutes)</Form.Label>
                          <Form.Select
                            value={securitySettings.session_timeout}
                            onChange={(e) => updateSecuritySettings({
                              session_timeout: parseInt(e.target.value)
                            })}
                          >
                            <option value={30}>30 minutes</option>
                            <option value={60}>1 hour</option>
                            <option value={120}>2 hours</option>
                            <option value={240}>4 hours</option>
                            <option value={480}>8 hours</option>
                            <option value={1440}>24 hours</option>
                          </Form.Select>
                        </Form.Group>
                      </Col>

                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Login History Retention (days)</Form.Label>
                          <Form.Select
                            value={securitySettings.login_history_retention}
                            onChange={(e) => updateSecuritySettings({
                              login_history_retention: parseInt(e.target.value)
                            })}
                          >
                            <option value={30}>30 days</option>
                            <option value={90}>90 days</option>
                            <option value={180}>6 months</option>
                            <option value={365}>1 year</option>
                          </Form.Select>
                        </Form.Group>
                      </Col>
                    </Row>
                  </>
                )}
              </Card.Body>
            </Tab.Pane>

            {/* Notifications Tab */}
            <Tab.Pane eventKey="notifications">
              <Card.Body>
                <h5 className="mb-3">Notification Preferences</h5>
                
                {notificationSettings && (
                  <Form>
                    <div className="mb-4">
                      <h6>Communication</h6>
                      <div className="ms-3">
                        <Form.Check
                          type="switch"
                          id="email-notifications-general"
                          label="Email notifications"
                          checked={notificationSettings.email_notifications}
                          onChange={(e) => updateNotificationSettings({
                            email_notifications: e.target.checked
                          })}
                          className="mb-2"
                        />
                        <Form.Check
                          type="switch"
                          id="push-notifications"
                          label="Push notifications"
                          checked={notificationSettings.push_notifications}
                          onChange={(e) => updateNotificationSettings({
                            push_notifications: e.target.checked
                          })}
                          className="mb-2"
                        />
                      </div>
                    </div>

                    <div className="mb-4">
                      <h6>Content</h6>
                      <div className="ms-3">
                        <Form.Check
                          type="switch"
                          id="security-alerts-notifications"
                          label="Security alerts"
                          checked={notificationSettings.security_alerts}
                          onChange={(e) => updateNotificationSettings({
                            security_alerts: e.target.checked
                          })}
                          className="mb-2"
                        />
                        <Form.Check
                          type="switch"
                          id="product-updates"
                          label="Product updates and new features"
                          checked={notificationSettings.product_updates}
                          onChange={(e) => updateNotificationSettings({
                            product_updates: e.target.checked
                          })}
                          className="mb-2"
                        />
                        <Form.Check
                          type="switch"
                          id="weekly-summary"
                          label="Weekly activity summary"
                          checked={notificationSettings.weekly_summary}
                          onChange={(e) => updateNotificationSettings({
                            weekly_summary: e.target.checked
                          })}
                          className="mb-2"
                        />
                      </div>
                    </div>

                    <div className="mb-4">
                      <h6>Marketing</h6>
                      <div className="ms-3">
                        <Form.Check
                          type="switch"
                          id="marketing-emails"
                          label="Marketing emails and promotions"
                          checked={notificationSettings.marketing_emails}
                          onChange={(e) => updateNotificationSettings({
                            marketing_emails: e.target.checked
                          })}
                          className="mb-2"
                        />
                      </div>
                    </div>
                  </Form>
                )}
              </Card.Body>
            </Tab.Pane>

            {/* Connected Accounts Tab */}
            <Tab.Pane eventKey="accounts">
              <Card.Body>
                <h5 className="mb-3">Connected Accounts</h5>
                <p className="text-muted mb-4">
                  Manage your social login connections and linked accounts.
                </p>
                <SocialLogin 
                  mode="connect" 
                  onConnectionUpdate={() => {
                    setSuccess('Account connection updated successfully!');
                  }}
                />
              </Card.Body>
            </Tab.Pane>

            {/* Privacy Tab */}
            <Tab.Pane eventKey="privacy">
              <Card.Body>
                <h5 className="mb-3">Privacy & Data</h5>
                
                <div className="mb-4">
                  <h6>Data Export</h6>
                  <p className="text-muted">
                    Download a copy of your account data including profile information, 
                    settings, and activity history.
                  </p>
                  <Button
                    variant="outline-primary"
                    onClick={exportAccountData}
                    className="d-flex align-items-center"
                  >
                    <Download size={16} className="me-2" />
                    Export Account Data
                  </Button>
                </div>

                <hr />

                <div className="mb-4">
                  <h6 className="text-danger">Danger Zone</h6>
                  <p className="text-muted">
                    Once you delete your account, there is no going back. 
                    Please be certain.
                  </p>
                  <Button
                    variant="outline-danger"
                    onClick={() => setShowDeleteModal(true)}
                    className="d-flex align-items-center"
                  >
                    <Trash2 size={16} className="me-2" />
                    Delete Account
                  </Button>
                </div>
              </Card.Body>
            </Tab.Pane>
          </Tab.Content>
        </Card>
      </Tab.Container>

      {/* Delete Account Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title className="text-danger">Delete Account</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="danger">
            <AlertTriangle size={16} className="me-2" />
            <strong>This action cannot be undone!</strong>
          </Alert>
          <p>
            This will permanently delete your account and all associated data. 
            Your profile, settings, and activity history will be lost forever.
          </p>
          <Form.Group>
            <Form.Label>
              Type <strong>DELETE</strong> to confirm:
            </Form.Label>
            <Form.Control
              type="text"
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder="Type DELETE here"
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => {
              setShowDeleteModal(false);
              setDeleteConfirmText('');
            }}
            disabled={isSaving}
          >
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={deleteAccount}
            disabled={isSaving || deleteConfirmText !== 'DELETE'}
          >
            {isSaving ? (
              <>
                <Spinner size="sm" className="me-2" />
                Deleting...
              </>
            ) : (
              'Delete Account'
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* MFA Toggle Modal */}
      <Modal show={showMFAModal} onHide={() => setShowMFAModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            <Shield className="me-2" size={20} />
            {securitySettings?.mfa_enabled ? 'Disable' : 'Enable'} Multi-Factor Authentication
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            {securitySettings?.mfa_enabled 
              ? 'Are you sure you want to disable multi-factor authentication? This will make your account less secure.'
              : 'Multi-factor authentication adds an extra layer of security to your account. You will need to use an authenticator app to generate verification codes.'
            }
          </p>
          {!securitySettings?.mfa_enabled && (
            <Alert variant="info">
              <AlertTriangle size={16} className="me-2" />
              This will redirect you to the MFA setup page where you can configure your authenticator app.
            </Alert>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowMFAModal(false)}
            disabled={isSaving}
          >
            Cancel
          </Button>
          <Button 
            variant={securitySettings?.mfa_enabled ? 'danger' : 'primary'}
            onClick={() => {
              if (securitySettings?.mfa_enabled) {
                // Handle MFA disable
                setShowMFAModal(false);
              } else {
                // Redirect to MFA setup
                window.location.href = '/auth/mfa-setup';
              }
            }}
            disabled={isSaving}
          >
            {securitySettings?.mfa_enabled ? 'Disable MFA' : 'Setup MFA'}
          </Button>
        </Modal.Footer>
      </Modal>
    </motion.div>
  );
};

export default AccountSettings;
