import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Nav, Tab } from 'react-bootstrap';
import { 
  MFASetup, 
  MFAVerification, 
  SocialLogin, 
  PasswordStrengthIndicator, 
  SecurityDashboard, 
  AccountSettings 
} from '../components/auth';

const AuthDemo: React.FC = () => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  return (
    <Container fluid className="py-4">
      <div className="text-center mb-4">
        <h1>Advanced Authentication Components Demo</h1>
        <p className="text-muted">
          Interactive demonstration of all Advanced Authentication UI components
        </p>
      </div>

      <Tab.Container defaultActiveKey="mfa-setup">
        <Row>
          <Col md={2}>
            <Nav variant="pills" className="flex-column">
              <Nav.Item>
                <Nav.Link eventKey="mfa-setup">MFA Setup</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="mfa-verification">MFA Verification</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="social-login">Social Login</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="password-strength">Password Strength</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="security-dashboard">Security Dashboard</Nav.Link>
              </Nav.Item>
              <Nav.Item>
                <Nav.Link eventKey="account-settings">Account Settings</Nav.Link>
              </Nav.Item>
            </Nav>
          </Col>

          <Col md={10}>
            <Tab.Content>
              <Tab.Pane eventKey="mfa-setup">
                <Card>
                  <Card.Header>
                    <h4>MFA Setup Component</h4>
                    <p className="mb-0 text-muted">
                      Multi-factor authentication setup with QR code generation and verification
                    </p>
                  </Card.Header>
                  <Card.Body>
                    <MFASetup 
                      onSetupComplete={(backupCodes) => {
                        console.log('MFA setup completed with backup codes:', backupCodes);
                        alert('MFA setup completed successfully!');
                      }}
                    />
                  </Card.Body>
                </Card>
              </Tab.Pane>

              <Tab.Pane eventKey="mfa-verification">
                <Card>
                  <Card.Header>
                    <h4>MFA Verification Component</h4>
                    <p className="mb-0 text-muted">
                      Two-factor authentication verification for login flow
                    </p>
                  </Card.Header>
                  <Card.Body>
                    <MFAVerification 
                      tempToken="demo-temp-token-12345"
                      onVerificationSuccess={(token) => {
                        console.log('MFA verified with token:', token);
                        alert('MFA verification successful!');
                      }}
                      onVerificationError={(error) => {
                        console.error('MFA verification failed:', error);
                        alert(`MFA verification failed: ${error}`);
                      }}
                    />
                  </Card.Body>
                </Card>
              </Tab.Pane>

              <Tab.Pane eventKey="social-login">
                <Row>
                  <Col lg={6} className="mb-4">
                    <Card>
                      <Card.Header>
                        <h5>Social Login (Login Mode)</h5>
                        <p className="mb-0 text-muted">OAuth login buttons</p>
                      </Card.Header>
                      <Card.Body>
                        <SocialLogin 
                          mode="login"
                          onLoginSuccess={(token) => {
                            console.log('Social login successful:', token);
                            alert('Social login successful!');
                          }}
                        />
                      </Card.Body>
                    </Card>
                  </Col>

                  <Col lg={6} className="mb-4">
                    <Card>
                      <Card.Header>
                        <h5>Social Login (Connect Mode)</h5>
                        <p className="mb-0 text-muted">Account connection management</p>
                      </Card.Header>
                      <Card.Body>
                        <SocialLogin 
                          mode="connect"
                          onConnectionUpdate={() => {
                            console.log('Social account connection updated');
                            alert('Account connection updated!');
                          }}
                        />
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              </Tab.Pane>

              <Tab.Pane eventKey="password-strength">
                <Card>
                  <Card.Header>
                    <h4>Password Strength Indicator</h4>
                    <p className="mb-0 text-muted">
                      Real-time password validation with strength meter and requirements
                    </p>
                  </Card.Header>
                  <Card.Body>
                    <Row>
                      <Col md={8}>
                        <PasswordStrengthIndicator
                          password={password}
                          showPassword={showPassword}
                          onPasswordChange={setPassword}
                          onToggleVisibility={() => setShowPassword(!showPassword)}
                          onStrengthChange={(strength, isValid) => {
                            console.log(`Password strength: ${strength}%, Valid: ${isValid}`);
                          }}
                        />
                      </Col>
                      <Col md={4}>
                        <Card className="bg-light">
                          <Card.Body>
                            <h6>Demo Controls</h6>
                            <Button 
                              variant="outline-secondary" 
                              size="sm" 
                              className="mb-2 w-100"
                              onClick={() => setPassword('weak123')}
                            >
                              Set Weak Password
                            </Button>
                            <Button 
                              variant="outline-secondary" 
                              size="sm" 
                              className="mb-2 w-100"
                              onClick={() => setPassword('StrongP@ssw0rd!')}
                            >
                              Set Strong Password
                            </Button>
                            <Button 
                              variant="outline-secondary" 
                              size="sm" 
                              className="w-100"
                              onClick={() => setPassword('')}
                            >
                              Clear Password
                            </Button>
                          </Card.Body>
                        </Card>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Tab.Pane>

              <Tab.Pane eventKey="security-dashboard">
                <Card>
                  <Card.Header>
                    <h4>Security Dashboard</h4>
                    <p className="mb-0 text-muted">
                      Device management, login history, and security overview
                    </p>
                  </Card.Header>
                  <Card.Body>
                    <SecurityDashboard />
                  </Card.Body>
                </Card>
              </Tab.Pane>

              <Tab.Pane eventKey="account-settings">
                <Card>
                  <Card.Header>
                    <h4>Account Settings</h4>
                    <p className="mb-0 text-muted">
                      Complete account management with security, notifications, and privacy settings
                    </p>
                  </Card.Header>
                  <Card.Body>
                    <AccountSettings />
                  </Card.Body>
                </Card>
              </Tab.Pane>
            </Tab.Content>
          </Col>
        </Row>
      </Tab.Container>

      {/* Demo Information */}
      <Card className="mt-4">
        <Card.Header>
          <h5>Demo Information</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <h6>Features Implemented:</h6>
              <ul>
                <li>✅ MFA Setup Flow with QR codes and backup codes</li>
                <li>✅ MFA Verification with authenticator app support</li>
                <li>✅ Social Login Integration (OAuth flow simulation)</li>
                <li>✅ Real-time Password Strength Validation</li>
                <li>✅ Security Dashboard with device management</li>
                <li>✅ Account Settings with comprehensive preferences</li>
              </ul>
            </Col>
            <Col md={6}>
              <h6>Technology Stack:</h6>
              <ul>
                <li>React 18 with TypeScript</li>
                <li>React Bootstrap 5.3.2</li>
                <li>Framer Motion animations</li>
                <li>Lucide React icons</li>
                <li>QR Code generation</li>
                <li>Responsive design patterns</li>
              </ul>
            </Col>
          </Row>
          
          <div className="mt-3">
            <h6>Testing Notes:</h6>
            <p className="text-muted mb-0">
              This is a frontend-only demo. API calls will fail since the backend endpoints are not available. 
              All components include proper error handling and loading states. 
              Console logs will show component interactions and state changes.
            </p>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default AuthDemo;
