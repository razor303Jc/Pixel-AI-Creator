import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Row, Col, Badge, Alert, Modal, Tab, Tabs } from 'react-bootstrap';
import { 
  Shield, 
  CreditCard, 
  Globe, 
  Database, 
  Zap, 
  Users, 
  Lock, 
  CheckCircle, 
  AlertTriangle,
  Settings,
  Eye,
  DollarSign
} from 'lucide-react';
import { EnhancedTemplateForm, PRICING_TIERS, ToolPricingTier } from '../../types/enhanced-template-types';

interface EnhancedTemplateCreationProps {
  onSubmit: (templateData: EnhancedTemplateForm) => void;
  onCancel: () => void;
}

const EnhancedTemplateCreation: React.FC<EnhancedTemplateCreationProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<EnhancedTemplateForm>({
    basicInfo: {
      name: '',
      description: '',
      category: '',
      personality: 'professional',
      tags: [],
      visibility: 'private',
      pricingTier: 'free'
    },
    instructions: '',
    scope: 'general',
    trainingQA: [{ question: '', answer: '' }],
    tools: {
      basicChat: { enabled: true },
      textGeneration: { enabled: true },
      basicAnalytics: { enabled: false },
      mcpServers: { enabled: false, servers: [], pricingModel: 'subscription' },
      databaseAccess: { enabled: false, types: [], pricingModel: 'subscription' },
      apiIntegrations: { enabled: false, apis: [], pricingModel: 'subscription' },
      workspaceIntegrations: {},
      socialMediaAnalysis: { platforms: {}, aiContextGeneration: { enabled: false, analysisTypes: [], updateFrequency: 'weekly', pricingTier: PRICING_TIERS.premium } },
      advancedAnalytics: { enabled: false, features: [] }
    },
    security: {
      dataProtection: {
        encryption: { inTransit: true, atRest: true, keyManagement: 'managed' },
        dataResidency: { region: 'us', crossBorderRestrictions: false, localStorageRequired: false },
        retention: { defaultDays: 365, userConfigurable: true, automaticDeletion: true }
      },
      compliance: {
        gdpr: { enabled: false, dataProcessingBasis: '', rightToErasure: false, dataPortability: false },
        ccpa: { enabled: false, doNotSell: true, dataTransparency: true },
        hipaa: { enabled: false, baa: false, auditLogs: false },
        sox: { enabled: false, financialDataControls: false }
      },
      audit: { enabled: true, logRetentionDays: 90, realTimeMonitoring: false, anomalyDetection: false }
    },
    userConsent: {
      registration: {
        termsOfService: { version: '1.0', acceptedAt: '', ipAddress: '', userAgent: '' },
        privacyPolicy: { version: '1.0', acceptedAt: '', dataProcessingConsent: false, marketingConsent: false, analyticsConsent: false },
        cookieConsent: { necessary: true, functional: false, analytics: false, marketing: false, acceptedAt: '' }
      },
      toolSpecific: {}
    },
    contextSources: {
      websiteAnalysis: { enabled: false, urls: [], analysisDepth: 'basic', updateFrequency: 'manual' },
      socialMediaAnalysis: { platforms: {}, aiContextGeneration: { enabled: false, analysisTypes: [], updateFrequency: 'weekly', pricingTier: PRICING_TIERS.premium } },
      documentLibrary: { enabled: false, sources: [] }
    }
  });

  const [showPricingModal, setShowPricingModal] = useState(false);
  const [selectedTier, setSelectedTier] = useState<'free' | 'premium' | 'enterprise'>('free');
  const [estimatedCost, setEstimatedCost] = useState(0);
  const [showComplianceModal, setShowComplianceModal] = useState(false);

  // Form validation
  const isFormValid = () => {
    return (
      formData.basicInfo.name.trim() !== '' &&
      formData.basicInfo.description.trim() !== '' &&
      formData.basicInfo.category !== ''
    );
  };

  // Calculate estimated monthly cost based on selected tools
  useEffect(() => {
    let cost = PRICING_TIERS[selectedTier].monthlyPrice;
    
    // Add cost for optional tools
    if (formData.tools.mcpServers.enabled) {
      cost += 19; // MCP Server addon
    }
    if (formData.tools.databaseAccess.enabled) {
      cost += 15; // Database access addon
    }
    if (formData.tools.socialMediaAnalysis.aiContextGeneration.enabled) {
      cost += 25; // Social media analysis addon
    }
    if (formData.contextSources.websiteAnalysis.enabled && formData.contextSources.websiteAnalysis.analysisDepth !== 'basic') {
      cost += 10; // Advanced website analysis
    }

    setEstimatedCost(cost);
  }, [selectedTier, formData.tools, formData.contextSources]);

  const handleToolToggle = (toolCategory: string, toolName: string, enabled: boolean) => {
    // Check if user has appropriate pricing tier
    if (enabled && !canUseTool(toolCategory, toolName, selectedTier)) {
      setShowPricingModal(true);
      return;
    }

    setFormData(prev => ({
      ...prev,
      tools: {
        ...prev.tools,
        [toolCategory]: {
          ...prev.tools[toolCategory as keyof typeof prev.tools],
          [toolName]: enabled
        }
      }
    }));
  };

  const canUseTool = (toolCategory: string, toolName: string, tier: string): boolean => {
    const toolTierRequirements = {
      'mcpServers': 'premium',
      'databaseAccess': 'premium', 
      'apiIntegrations': 'premium',
      'workspaceIntegrations': 'premium',
      'socialMediaAnalysis': 'enterprise',
      'advancedAnalytics': 'enterprise'
    };

    const required = toolTierRequirements[toolCategory as keyof typeof toolTierRequirements];
    const tierLevels = { 'free': 0, 'premium': 1, 'enterprise': 2 };
    
    return tierLevels[tier as keyof typeof tierLevels] >= tierLevels[required as keyof typeof tierLevels];
  };

  const renderPricingTier = (tier: 'free' | 'premium' | 'enterprise') => {
    const tierData = PRICING_TIERS[tier];
    const isSelected = selectedTier === tier;
    
    return (
      <Card 
        className={`mb-3 ${isSelected ? 'border-primary' : ''}`}
        style={{ cursor: 'pointer' }}
        onClick={() => setSelectedTier(tier)}
      >
        <Card.Body>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h6 className="mb-1 text-capitalize">{tier}</h6>
              <div className="text-muted small">
                ${tierData.monthlyPrice}/month
              </div>
            </div>
            {isSelected && <CheckCircle className="text-primary" size={20} />}
          </div>
          <div className="mt-2">
            <small className="text-muted">
              {tierData.features.slice(0, 2).join(', ')}
              {tierData.features.length > 2 && '...'}
            </small>
          </div>
        </Card.Body>
      </Card>
    );
  };

  const renderWorkspaceIntegrations = () => (
    <Card className="mb-4">
      <Card.Header>
        <h6 className="mb-0">
          <Globe className="me-2" size={16} />
          Workspace Integrations
          <Badge bg="warning" className="ms-2">Premium+</Badge>
        </h6>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={6}>
            <h6>Google Workspace</h6>
            <Form.Check 
              type="switch"
              label="Gmail Integration"
              disabled={!canUseTool('workspaceIntegrations', 'gmail', selectedTier)}
              onChange={(e) => handleWorkspaceToggle('google', 'gmail', e.target.checked)}
            />
            <Form.Check 
              type="switch"
              label="Google Calendar"
              disabled={!canUseTool('workspaceIntegrations', 'calendar', selectedTier)}
              onChange={(e) => handleWorkspaceToggle('google', 'calendar', e.target.checked)}
            />
            <Form.Check 
              type="switch"
              label="Google Drive"
              disabled={!canUseTool('workspaceIntegrations', 'drive', selectedTier)}
              onChange={(e) => handleWorkspaceToggle('google', 'drive', e.target.checked)}
            />
          </Col>
          <Col md={6}>
            <h6>Microsoft 365</h6>
            <Form.Check 
              type="switch"
              label="Outlook Integration"
              disabled={!canUseTool('workspaceIntegrations', 'outlook', selectedTier)}
              onChange={(e) => handleWorkspaceToggle('microsoft', 'outlook', e.target.checked)}
            />
            <Form.Check 
              type="switch"
              label="Teams Integration"
              disabled={!canUseTool('workspaceIntegrations', 'teams', selectedTier)}
              onChange={(e) => handleWorkspaceToggle('microsoft', 'teams', e.target.checked)}
            />
            <Form.Check 
              type="switch"
              label="OneDrive"
              disabled={!canUseTool('workspaceIntegrations', 'onedrive', selectedTier)}
              onChange={(e) => handleWorkspaceToggle('microsoft', 'onedrive', e.target.checked)}
            />
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );

  const handleWorkspaceToggle = (provider: string, service: string, enabled: boolean) => {
    // Implementation for workspace toggle
  };

  const renderSocialMediaAnalysis = () => (
    <Card className="mb-4">
      <Card.Header>
        <h6 className="mb-0">
          <Users className="me-2" size={16} />
          Social Media & Website Analysis
          <Badge bg="danger" className="ms-2">Enterprise</Badge>
        </h6>
      </Card.Header>
      <Card.Body>
        <Form.Group className="mb-3">
          <Form.Label>Website URL for Analysis</Form.Label>
          <Form.Control 
            type="url" 
            placeholder="https://your-company.com"
            disabled={!canUseTool('socialMediaAnalysis', 'website', selectedTier)}
          />
          <Form.Text className="text-muted">
            We'll analyze your website content to provide better context for your AI assistant
          </Form.Text>
        </Form.Group>

        <Form.Group className="mb-3">
          <Form.Label>Social Media Handles</Form.Label>
          <Row>
            <Col md={6}>
              <Form.Control 
                type="text" 
                placeholder="LinkedIn Company Page"
                className="mb-2"
                disabled={!canUseTool('socialMediaAnalysis', 'linkedin', selectedTier)}
              />
              <Form.Control 
                type="text" 
                placeholder="Twitter Handle"
                className="mb-2"
                disabled={!canUseTool('socialMediaAnalysis', 'twitter', selectedTier)}
              />
            </Col>
            <Col md={6}>
              <Form.Control 
                type="text" 
                placeholder="Facebook Page"
                className="mb-2"
                disabled={!canUseTool('socialMediaAnalysis', 'facebook', selectedTier)}
              />
              <Form.Control 
                type="text" 
                placeholder="Instagram Handle"
                className="mb-2"
                disabled={!canUseTool('socialMediaAnalysis', 'instagram', selectedTier)}
              />
            </Col>
          </Row>
        </Form.Group>

        <Alert variant="info">
          <AlertTriangle size={16} className="me-2" />
          Social media analysis helps create better context for your AI assistant by understanding your brand voice and audience
        </Alert>
      </Card.Body>
    </Card>
  );

  const renderComplianceSettings = () => (
    <Card className="mb-4">
      <Card.Header>
        <h6 className="mb-0">
          <Shield className="me-2" size={16} />
          Security & Compliance
        </h6>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={6}>
            <h6>Data Protection</h6>
            <Form.Check 
              type="switch"
              label="GDPR Compliance"
              onChange={(e) => handleComplianceToggle('gdpr', e.target.checked)}
            />
            <Form.Check 
              type="switch"
              label="CCPA Compliance"
              onChange={(e) => handleComplianceToggle('ccpa', e.target.checked)}
            />
            <Form.Check 
              type="switch"
              label="HIPAA Compliance"
              disabled={selectedTier !== 'enterprise'}
              onChange={(e) => handleComplianceToggle('hipaa', e.target.checked)}
            />
          </Col>
          <Col md={6}>
            <h6>Data Residency</h6>
            <Form.Select>
              <option value="us">United States</option>
              <option value="eu">European Union</option>
              <option value="uk">United Kingdom</option>
              <option value="canada">Canada</option>
            </Form.Select>
            
            <Form.Check 
              type="switch"
              label="Advanced Audit Logging"
              className="mt-3"
              disabled={selectedTier === 'free'}
              onChange={(e) => handleComplianceToggle('audit', e.target.checked)}
            />
          </Col>
        </Row>
        
        <Button 
          variant="outline-primary" 
          size="sm" 
          className="mt-3"
          onClick={() => setShowComplianceModal(true)}
        >
          <Eye size={14} className="me-1" />
          View Privacy Policy & Terms
        </Button>
      </Card.Body>
    </Card>
  );

  const handleComplianceToggle = (compliance: string, enabled: boolean) => {
    // Implementation for compliance toggle
  };

  return (
    <div className="enhanced-template-creation">
      <Tabs defaultActiveKey="basic" className="mb-4">
        {/* Basic Information Tab */}
        <Tab eventKey="basic" title="Basic Information">
          <Card className="mb-4">
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Template Name</Form.Label>
                <Form.Control 
                  type="text"
                  data-testid="template-name-input"
                  value={formData.basicInfo.name}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    basicInfo: { ...prev.basicInfo, name: e.target.value }
                  }))}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Description</Form.Label>
                <Form.Control 
                  as="textarea"
                  rows={3}
                  data-testid="template-description-input"
                  value={formData.basicInfo.description}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    basicInfo: { ...prev.basicInfo, description: e.target.value }
                  }))}
                />
              </Form.Group>

              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Category</Form.Label>
                    <Form.Select 
                      data-testid="template-category-select"
                      value={formData.basicInfo.category}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        basicInfo: { ...prev.basicInfo, category: e.target.value }
                      }))}
                    >
                      <option value="">Select Category</option>
                      <option value="PA">Personal Assistant</option>
                      <option value="PM">Project Manager</option>
                      <option value="M&S">Marketing & Sales</option>
                      <option value="A&D">Analytics & Data</option>
                      <option value="support">Customer Support</option>
                      <option value="technical">Technical Support</option>
                      <option value="general">General Purpose</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Visibility</Form.Label>
                    <Form.Select
                      value={formData.basicInfo.visibility}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        basicInfo: { ...prev.basicInfo, visibility: e.target.value as any }
                      }))}
                    >
                      <option value="private">Private</option>
                      <option value="public">Public</option>
                      <option value="team">Team</option>
                      <option value="enterprise">Enterprise</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Tab>

        {/* Pricing & Tools Tab */}
        <Tab eventKey="pricing" title="Pricing & Tools">
          <Row>
            <Col md={4}>
              <h6 className="mb-3">Select Pricing Tier</h6>
              {renderPricingTier('free')}
              {renderPricingTier('premium')}
              {renderPricingTier('enterprise')}
              
              <Card className="border-success">
                <Card.Body className="text-center">
                  <DollarSign className="text-success mb-2" size={24} />
                  <h6>Estimated Cost</h6>
                  <h4 className="text-success">${estimatedCost}/month</h4>
                </Card.Body>
              </Card>
            </Col>
            <Col md={8}>
              <h6 className="mb-3">Available Tools</h6>
              
              {/* Free Tools */}
              <Card className="mb-3">
                <Card.Header>
                  <Badge bg="success">Free</Badge> Basic Tools
                </Card.Header>
                <Card.Body>
                  <Form.Check 
                    type="switch"
                    label="Basic Chat Functionality"
                    checked={formData.tools.basicChat.enabled}
                    disabled
                  />
                  <Form.Check 
                    type="switch"
                    label="Text Generation"
                    checked={formData.tools.textGeneration.enabled}
                    disabled
                  />
                  <Form.Check 
                    type="switch"
                    label="Basic Analytics"
                    checked={formData.tools.basicAnalytics.enabled}
                    onChange={(e) => handleToolToggle('basicAnalytics', 'enabled', e.target.checked)}
                  />
                </Card.Body>
              </Card>

              {/* Premium Tools */}
              <Card className="mb-3">
                <Card.Header>
                  <Badge bg="warning">Premium</Badge> Advanced Tools
                </Card.Header>
                <Card.Body>
                  <Form.Check 
                    type="switch"
                    label="MCP Server Integration (+$19/month)"
                    checked={formData.tools.mcpServers.enabled}
                    disabled={!canUseTool('mcpServers', 'enabled', selectedTier)}
                    onChange={(e) => handleToolToggle('mcpServers', 'enabled', e.target.checked)}
                  />
                  <Form.Check 
                    type="switch"
                    label="Database Access (+$15/month)"
                    checked={formData.tools.databaseAccess.enabled}
                    disabled={!canUseTool('databaseAccess', 'enabled', selectedTier)}
                    onChange={(e) => handleToolToggle('databaseAccess', 'enabled', e.target.checked)}
                  />
                  <Form.Check 
                    type="switch"
                    label="API Integrations"
                    checked={formData.tools.apiIntegrations.enabled}
                    disabled={!canUseTool('apiIntegrations', 'enabled', selectedTier)}
                    onChange={(e) => handleToolToggle('apiIntegrations', 'enabled', e.target.checked)}
                  />
                </Card.Body>
              </Card>

              {/* Enterprise Tools */}
              <Card className="mb-3">
                <Card.Header>
                  <Badge bg="danger">Enterprise</Badge> Enterprise Tools
                </Card.Header>
                <Card.Body>
                  <Form.Check 
                    type="switch"
                    label="Social Media Analysis (+$25/month)"
                    disabled={!canUseTool('socialMediaAnalysis', 'enabled', selectedTier)}
                    onChange={(e) => handleToolToggle('socialMediaAnalysis', 'enabled', e.target.checked)}
                  />
                  <Form.Check 
                    type="switch"
                    label="Advanced Analytics"
                    disabled={!canUseTool('advancedAnalytics', 'enabled', selectedTier)}
                    onChange={(e) => handleToolToggle('advancedAnalytics', 'enabled', e.target.checked)}
                  />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        {/* Integrations Tab */}
        <Tab eventKey="integrations" title="Integrations">
          {renderWorkspaceIntegrations()}
          {renderSocialMediaAnalysis()}
        </Tab>

        {/* Security & Compliance Tab */}
        <Tab eventKey="security" title="Security & Compliance">
          {renderComplianceSettings()}
          
          <Alert variant="warning">
            <AlertTriangle size={16} className="me-2" />
            By creating this template, you agree to our Terms of Service and Privacy Policy. 
            Sensitive information will be encrypted and stored securely according to your compliance settings.
          </Alert>
        </Tab>
      </Tabs>

      {/* Action Buttons */}
      <div className="d-flex justify-content-between">
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          data-testid="submit-template-btn"
          disabled={!isFormValid()}
          onClick={() => onSubmit(formData)}
        >
          Create Template (${estimatedCost}/month)
        </Button>
      </div>

      {/* Pricing Upgrade Modal */}
      <Modal show={showPricingModal} onHide={() => setShowPricingModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Upgrade Required</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>This feature requires a higher pricing tier. Please upgrade your subscription to access this functionality.</p>
          <div className="d-grid gap-2">
            {(Object.entries(PRICING_TIERS) as [string, typeof PRICING_TIERS[keyof typeof PRICING_TIERS]][]).map(([tier, data]) => (
              <Button 
                key={tier}
                variant={tier === 'enterprise' ? 'primary' : 'outline-primary'}
                onClick={() => {
                  setSelectedTier(tier as any);
                  setShowPricingModal(false);
                }}
              >
                Upgrade to {tier} - ${data.monthlyPrice}/month
              </Button>
            ))}
          </div>
        </Modal.Body>
      </Modal>

      {/* Compliance Modal */}
      <Modal show={showComplianceModal} onHide={() => setShowComplianceModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Privacy Policy & Terms of Service</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Tabs defaultActiveKey="privacy">
            <Tab eventKey="privacy" title="Privacy Policy">
              <div className="mt-3">
                <h6>Data Collection and Usage</h6>
                <p>We collect and process data to provide AI assistant services...</p>
                
                <h6>Data Security</h6>
                <p>All data is encrypted in transit and at rest using industry-standard encryption...</p>
                
                <h6>Data Retention</h6>
                <p>Data is retained according to your specified retention policy...</p>
              </div>
            </Tab>
            <Tab eventKey="terms" title="Terms of Service">
              <div className="mt-3">
                <h6>Service Usage</h6>
                <p>By using Pixel AI Creator, you agree to use the service responsibly...</p>
                
                <h6>Billing and Payments</h6>
                <p>Subscriptions are billed monthly and automatically renewed...</p>
                
                <h6>Limitation of Liability</h6>
                <p>Our liability is limited to the amount paid for the service...</p>
              </div>
            </Tab>
          </Tabs>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="primary" onClick={() => setShowComplianceModal(false)}>
            I Understand
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default EnhancedTemplateCreation;