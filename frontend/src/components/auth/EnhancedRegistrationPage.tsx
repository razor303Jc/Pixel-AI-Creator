import React, { useState } from 'react';
import { Card, Form, Button, Alert, Modal, Tab, Tabs, Row, Col, Badge } from 'react-bootstrap';
import { Shield, Lock, Globe, FileText, CheckCircle, AlertTriangle, Eye, Users } from 'lucide-react';

interface RegistrationFormData {
  // Basic Information
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  companyName: string;
  jobTitle: string;
  
  // Subscription Selection
  selectedTier: 'free' | 'premium' | 'enterprise';
  
  // Legal Consents
  termsAccepted: boolean;
  privacyPolicyAccepted: boolean;
  cookieConsent: {
    necessary: boolean;
    functional: boolean;
    analytics: boolean;
    marketing: boolean;
  };
  dataProcessingConsent: boolean;
  marketingConsent: boolean;
  
  // Privacy Preferences
  dataResidency: 'us' | 'eu' | 'uk' | 'canada' | 'australia';
  communicationPreferences: {
    productUpdates: boolean;
    securityAlerts: boolean;
    marketingEmails: boolean;
    usageTips: boolean;
  };
  
  // Compliance Requirements
  complianceRequirements: {
    gdpr: boolean;
    ccpa: boolean;
    hipaa: boolean;
    sox: boolean;
  };
}

const EnhancedRegistrationPage: React.FC = () => {
  const [formData, setFormData] = useState<RegistrationFormData>({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    companyName: '',
    jobTitle: '',
    selectedTier: 'free',
    termsAccepted: false,
    privacyPolicyAccepted: false,
    cookieConsent: {
      necessary: true,
      functional: false,
      analytics: false,
      marketing: false
    },
    dataProcessingConsent: false,
    marketingConsent: false,
    dataResidency: 'us',
    communicationPreferences: {
      productUpdates: true,
      securityAlerts: true,
      marketingEmails: false,
      usageTips: true
    },
    complianceRequirements: {
      gdpr: false,
      ccpa: false,
      hipaa: false,
      sox: false
    }
  });

  const [showTermsModal, setShowTermsModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showComplianceModal, setShowComplianceModal] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [registrationComplete, setRegistrationComplete] = useState(false);

  const pricingTiers = {
    free: {
      name: 'Free',
      price: 0,
      features: ['Basic AI Chat', 'Text Generation', '1GB Storage', 'Community Support'],
      limits: '1,000 requests/month'
    },
    premium: {
      name: 'Premium',
      price: 29,
      features: ['MCP Server Integration', 'Database Access', 'Google Workspace', '10GB Storage', 'Priority Support'],
      limits: '10,000 requests/month'
    },
    enterprise: {
      name: 'Enterprise',
      price: 299,
      features: ['Full Feature Access', 'Social Media Analysis', 'Advanced Compliance', '100GB Storage', 'Dedicated Support'],
      limits: 'Unlimited requests'
    }
  };

  const handleRegistration = async () => {
    // Validate all required consents
    if (!formData.termsAccepted || !formData.privacyPolicyAccepted) {
      alert('Please accept the Terms of Service and Privacy Policy to continue.');
      return;
    }

    if (!formData.dataProcessingConsent) {
      alert('Data processing consent is required to provide AI services.');
      return;
    }

    // Simulate registration process
    console.log('Registration Data:', formData);
    setRegistrationComplete(true);
  };

  const renderPricingSelection = () => (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">
          <Badge bg="primary" className="me-2">2</Badge>
          Choose Your Plan
        </h5>
      </Card.Header>
      <Card.Body>
        <Row>
          {Object.entries(pricingTiers).map(([tier, data]) => (
            <Col md={4} key={tier}>
              <Card 
                className={`mb-3 ${formData.selectedTier === tier ? 'border-primary' : ''}`}
                style={{ cursor: 'pointer' }}
                onClick={() => setFormData(prev => ({ ...prev, selectedTier: tier as any }))}
              >
                <Card.Body className="text-center">
                  <h6>{data.name}</h6>
                  <h4 className="text-primary">${data.price}<small className="text-muted">/month</small></h4>
                  <div className="mb-3">
                    <small className="text-muted">{data.limits}</small>
                  </div>
                  {data.features.map((feature, index) => (
                    <div key={index} className="small text-start mb-1">
                      <CheckCircle size={12} className="text-success me-1" />
                      {feature}
                    </div>
                  ))}
                  {formData.selectedTier === tier && (
                    <Badge bg="primary" className="mt-2">Selected</Badge>
                  )}
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </Card.Body>
    </Card>
  );

  const renderComplianceSettings = () => (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">
          <Badge bg="warning" className="me-2">3</Badge>
          Compliance & Privacy Settings
        </h5>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={6}>
            <h6>Data Residency</h6>
            <Form.Select 
              value={formData.dataResidency}
              onChange={(e) => setFormData(prev => ({ 
                ...prev, 
                dataResidency: e.target.value as any 
              }))}
            >
              <option value="us">United States</option>
              <option value="eu">European Union</option>
              <option value="uk">United Kingdom</option>
              <option value="canada">Canada</option>
              <option value="australia">Australia</option>
            </Form.Select>
            <Form.Text className="text-muted">
              Choose where your data will be stored and processed
            </Form.Text>

            <h6 className="mt-4">Compliance Requirements</h6>
            <Form.Check 
              type="checkbox"
              label="GDPR (European Union)"
              checked={formData.complianceRequirements.gdpr}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                complianceRequirements: {
                  ...prev.complianceRequirements,
                  gdpr: e.target.checked
                }
              }))}
            />
            <Form.Check 
              type="checkbox"
              label="CCPA (California)"
              checked={formData.complianceRequirements.ccpa}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                complianceRequirements: {
                  ...prev.complianceRequirements,
                  ccpa: e.target.checked
                }
              }))}
            />
            <Form.Check 
              type="checkbox"
              label="HIPAA (Healthcare)"
              disabled={formData.selectedTier !== 'enterprise'}
              checked={formData.complianceRequirements.hipaa}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                complianceRequirements: {
                  ...prev.complianceRequirements,
                  hipaa: e.target.checked
                }
              }))}
            />
            <Form.Check 
              type="checkbox"
              label="SOX (Financial)"
              disabled={formData.selectedTier !== 'enterprise'}
              checked={formData.complianceRequirements.sox}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                complianceRequirements: {
                  ...prev.complianceRequirements,
                  sox: e.target.checked
                }
              }))}
            />
          </Col>
          <Col md={6}>
            <h6>Cookie Preferences</h6>
            <Form.Check 
              type="checkbox"
              label="Necessary cookies (Required)"
              checked={formData.cookieConsent.necessary}
              disabled
            />
            <Form.Check 
              type="checkbox"
              label="Functional cookies"
              checked={formData.cookieConsent.functional}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                cookieConsent: {
                  ...prev.cookieConsent,
                  functional: e.target.checked
                }
              }))}
            />
            <Form.Check 
              type="checkbox"
              label="Analytics cookies"
              checked={formData.cookieConsent.analytics}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                cookieConsent: {
                  ...prev.cookieConsent,
                  analytics: e.target.checked
                }
              }))}
            />
            <Form.Check 
              type="checkbox"
              label="Marketing cookies"
              checked={formData.cookieConsent.marketing}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                cookieConsent: {
                  ...prev.cookieConsent,
                  marketing: e.target.checked
                }
              }))}
            />

            <h6 className="mt-4">Communication Preferences</h6>
            <Form.Check 
              type="checkbox"
              label="Product updates"
              checked={formData.communicationPreferences.productUpdates}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                communicationPreferences: {
                  ...prev.communicationPreferences,
                  productUpdates: e.target.checked
                }
              }))}
            />
            <Form.Check 
              type="checkbox"
              label="Security alerts (Recommended)"
              checked={formData.communicationPreferences.securityAlerts}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                communicationPreferences: {
                  ...prev.communicationPreferences,
                  securityAlerts: e.target.checked
                }
              }))}
            />
            <Form.Check 
              type="checkbox"
              label="Marketing emails"
              checked={formData.communicationPreferences.marketingEmails}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                communicationPreferences: {
                  ...prev.communicationPreferences,
                  marketingEmails: e.target.checked
                }
              }))}
            />
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );

  const renderLegalConsents = () => (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">
          <Badge bg="danger" className="me-2">4</Badge>
          Legal Agreements & Consents
        </h5>
      </Card.Header>
      <Card.Body>
        <Alert variant="info">
          <Shield size={16} className="me-2" />
          Your privacy and data security are our top priorities. Please review and accept the following agreements.
        </Alert>

        <div className="border rounded p-3 mb-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong>Terms of Service</strong>
            <Button 
              variant="outline-primary" 
              size="sm"
              onClick={() => setShowTermsModal(true)}
            >
              <Eye size={14} className="me-1" />
              Read Terms
            </Button>
          </div>
          <Form.Check 
            type="checkbox"
            label="I have read and agree to the Terms of Service"
            checked={formData.termsAccepted}
            onChange={(e) => setFormData(prev => ({ ...prev, termsAccepted: e.target.checked }))}
            required
          />
        </div>

        <div className="border rounded p-3 mb-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong>Privacy Policy</strong>
            <Button 
              variant="outline-primary" 
              size="sm"
              onClick={() => setShowPrivacyModal(true)}
            >
              <Eye size={14} className="me-1" />
              Read Privacy Policy
            </Button>
          </div>
          <Form.Check 
            type="checkbox"
            label="I have read and agree to the Privacy Policy"
            checked={formData.privacyPolicyAccepted}
            onChange={(e) => setFormData(prev => ({ ...prev, privacyPolicyAccepted: e.target.checked }))}
            required
          />
        </div>

        <div className="border rounded p-3 mb-3">
          <strong>Data Processing Consent</strong>
          <Form.Check 
            type="checkbox"
            label="I consent to the processing of my personal data for AI service provision"
            checked={formData.dataProcessingConsent}
            onChange={(e) => setFormData(prev => ({ ...prev, dataProcessingConsent: e.target.checked }))}
            required
            className="mt-2"
          />
          <Form.Text className="text-muted">
            Required for AI functionality, content generation, and personalized services
          </Form.Text>
        </div>

        <div className="border rounded p-3">
          <strong>Marketing Communications</strong>
          <Form.Check 
            type="checkbox"
            label="I consent to receive marketing communications (Optional)"
            checked={formData.marketingConsent}
            onChange={(e) => setFormData(prev => ({ ...prev, marketingConsent: e.target.checked }))}
            className="mt-2"
          />
          <Form.Text className="text-muted">
            Product updates, feature announcements, and promotional offers
          </Form.Text>
        </div>

        <Alert variant="warning" className="mt-3">
          <AlertTriangle size={16} className="me-2" />
          <strong>Data Rights:</strong> You have the right to access, rectify, erase, or port your data. 
          Contact our Data Protection Officer at privacy@pixel-ai-creator.com for any data-related requests.
        </Alert>
      </Card.Body>
    </Card>
  );

  const isFormValid = () => {
    return formData.email && 
           formData.password && 
           formData.firstName && 
           formData.lastName &&
           formData.termsAccepted && 
           formData.privacyPolicyAccepted && 
           formData.dataProcessingConsent;
  };

  if (registrationComplete) {
    return (
      <div className="container mt-5">
        <div className="row justify-content-center">
          <div className="col-md-8">
            <Card className="text-center">
              <Card.Body className="py-5">
                <CheckCircle size={64} className="text-success mb-4" />
                <h2>Registration Successful!</h2>
                <p className="lead">Welcome to Pixel AI Creator</p>
                <p>Your account has been created with the following settings:</p>
                <ul className="list-unstyled">
                  <li><strong>Plan:</strong> {pricingTiers[formData.selectedTier].name}</li>
                  <li><strong>Data Residency:</strong> {formData.dataResidency.toUpperCase()}</li>
                  <li><strong>Compliance:</strong> {Object.entries(formData.complianceRequirements)
                    .filter(([_, enabled]) => enabled)
                    .map(([key, _]) => key.toUpperCase())
                    .join(', ') || 'Standard'}</li>
                </ul>
                <Button variant="primary" size="lg" href="/dashboard">
                  Access Dashboard
                </Button>
              </Card.Body>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-10">
          <Card>
            <Card.Header>
              <h3 className="text-center mb-0">
                <Users className="me-2" />
                Create Your Pixel AI Creator Account
              </h3>
              <p className="text-center text-muted mt-2 mb-0">
                Join thousands of professionals using AI to enhance their productivity
              </p>
            </Card.Header>
            <Card.Body>
              {/* Basic Information */}
              <Card className="mb-4">
                <Card.Header>
                  <h5 className="mb-0">
                    <Badge bg="primary" className="me-2">1</Badge>
                    Basic Information
                  </h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>First Name *</Form.Label>
                        <Form.Control 
                          type="text"
                          value={formData.firstName}
                          onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
                          required
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Last Name *</Form.Label>
                        <Form.Control 
                          type="text"
                          value={formData.lastName}
                          onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
                          required
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Email Address *</Form.Label>
                        <Form.Control 
                          type="email"
                          value={formData.email}
                          onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                          required
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Company Name</Form.Label>
                        <Form.Control 
                          type="text"
                          value={formData.companyName}
                          onChange={(e) => setFormData(prev => ({ ...prev, companyName: e.target.value }))}
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Password *</Form.Label>
                        <Form.Control 
                          type="password"
                          value={formData.password}
                          onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                          required
                        />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Confirm Password *</Form.Label>
                        <Form.Control 
                          type="password"
                          value={formData.confirmPassword}
                          onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                          required
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>

              {renderPricingSelection()}
              {renderComplianceSettings()}
              {renderLegalConsents()}

              <div className="text-center">
                <Button 
                  variant="primary" 
                  size="lg"
                  disabled={!isFormValid()}
                  onClick={handleRegistration}
                  data-testid="complete-registration-btn"
                >
                  <Lock className="me-2" size={16} />
                  Create Secure Account
                </Button>
              </div>
            </Card.Body>
          </Card>
        </div>
      </div>

      {/* Terms of Service Modal */}
      <Modal show={showTermsModal} onHide={() => setShowTermsModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Terms of Service</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ maxHeight: '500px', overflowY: 'auto' }}>
          <h6>1. Service Description</h6>
          <p>Pixel AI Creator provides AI-powered template creation and management services with optional tool integrations based on subscription tiers.</p>
          
          <h6>2. Subscription Tiers and Billing</h6>
          <p>• <strong>Free Tier:</strong> Basic AI functionality with usage limits</p>
          <p>• <strong>Premium Tier ($29/month):</strong> Advanced tools including MCP servers, database access, and workspace integrations</p>
          <p>• <strong>Enterprise Tier ($299/month):</strong> Full feature access including social media analysis and advanced compliance</p>
          
          <h6>3. Optional Tool Pricing</h6>
          <p>• MCP Server Integration: +$19/month</p>
          <p>• Database Access: +$15/month</p>
          <p>• Social Media Analysis: +$25/month</p>
          
          <h6>4. Data Usage and Privacy</h6>
          <p>We process your data according to your selected compliance settings and data residency preferences. All data is encrypted and stored securely.</p>
          
          <h6>5. Acceptable Use</h6>
          <p>You agree to use our services responsibly and in compliance with applicable laws and regulations.</p>
          
          <h6>6. Limitation of Liability</h6>
          <p>Our liability is limited to the amount paid for the service in the preceding 12 months.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="primary" onClick={() => setShowTermsModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Privacy Policy Modal */}
      <Modal show={showPrivacyModal} onHide={() => setShowPrivacyModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Privacy Policy</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ maxHeight: '500px', overflowY: 'auto' }}>
          <h6>1. Information We Collect</h6>
          <p>We collect information you provide directly, usage data, and technical information necessary to provide our services.</p>
          
          <h6>2. How We Use Your Information</h6>
          <p>• Provide and improve our AI services</p>
          <p>• Process payments and manage subscriptions</p>
          <p>• Communicate service updates and support</p>
          <p>• Comply with legal obligations</p>
          
          <h6>3. Data Security</h6>
          <p>All data is encrypted in transit and at rest using industry-standard encryption protocols. We implement comprehensive security measures to protect your information.</p>
          
          <h6>4. Data Retention</h6>
          <p>We retain your data according to your specified retention settings and applicable legal requirements. You can configure retention periods in your account settings.</p>
          
          <h6>5. International Data Transfers</h6>
          <p>Data is processed in your selected data residency region. Cross-border transfers are protected by appropriate safeguards.</p>
          
          <h6>6. Your Rights</h6>
          <p>You have the right to access, rectify, erase, port, and restrict processing of your personal data. Contact our Data Protection Officer for assistance.</p>
          
          <h6>7. Compliance</h6>
          <p>We comply with GDPR, CCPA, and other applicable privacy laws based on your compliance settings and location.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="primary" onClick={() => setShowPrivacyModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default EnhancedRegistrationPage;