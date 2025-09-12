/**
 * Chatbot Management Interface
 * Visual chatbot builder, configuration management, and testing tools
 */

import React, { useEffect, useState } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Modal,
  Form,
  Alert,
  Spinner,
  Badge,
  Tabs,
  Tab,
  Accordion,
  ListGroup,
  InputGroup,
  Toast,
  ToastContainer
} from 'react-bootstrap';
import { motion } from 'framer-motion';
import {
  Bot,
  Settings,
  MessageSquare,
  Play,
  Pause,
  Save,
  Copy,
  Download,
  Upload,
  Eye,
  Edit,
  Trash2,
  Plus,
  Code,
  Brain,
  Zap,
  TestTube,
  Activity,
  Sliders
} from 'lucide-react';
import { useChatbot } from '../../contexts/ChatbotContext';
import { apiService } from '../../services/api';

interface ChatbotConfig {
  id?: number;
  name: string;
  description: string;
  personality: string;
  instructions: string;
  knowledgeBase: string[];
  responseTone: 'professional' | 'friendly' | 'casual' | 'technical';
  responseLength: 'short' | 'medium' | 'detailed';
  languages: string[];
  features: {
    webSearch: boolean;
    fileUpload: boolean;
    voiceResponse: boolean;
    contextMemory: boolean;
  };
  integrations: {
    channels: string[];
    apis: string[];
    webhooks: string[];
  };
  constraints: {
    maxTokens: number;
    temperature: number;
    timeoutSeconds: number;
  };
}

interface TestConversation {
  id: string;
  userMessage: string;
  botResponse: string;
  timestamp: Date;
  rating?: number;
  feedback?: string;
}

const ChatbotManager: React.FC = () => {
  const chatbotContext = useChatbot();
  const { 
    chatbots, 
    loading: chatbotsLoading, 
    fetchChatbots, 
    createChatbot, 
    updateChatbot, 
    deleteChatbot 
  } = chatbotContext || {};
  
  const [selectedChatbot, setSelectedChatbot] = useState<ChatbotConfig | null>(null);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [currentConfig, setCurrentConfig] = useState<ChatbotConfig>({
    name: '',
    description: '',
    personality: 'professional',
    instructions: '',
    knowledgeBase: [],
    responseTone: 'professional',
    responseLength: 'medium',
    languages: ['English'],
    features: {
      webSearch: false,
      fileUpload: false,
      voiceResponse: false,
      contextMemory: true
    },
    integrations: {
      channels: [],
      apis: [],
      webhooks: []
    },
    constraints: {
      maxTokens: 2048,
      temperature: 0.7,
      timeoutSeconds: 30
    }
  });
  
  const [testConversations, setTestConversations] = useState<TestConversation[]>([]);
  const [testMessage, setTestMessage] = useState('');
  const [testLoading, setTestLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [toast, setToast] = useState({ show: false, message: '', variant: 'success' });

  useEffect(() => {
    if (fetchChatbots) {
      fetchChatbots();
    }
  }, [fetchChatbots]);

  const handleCreateNew = () => {
    setCurrentConfig({
      name: '',
      description: '',
      personality: 'professional',
      instructions: '',
      knowledgeBase: [],
      responseTone: 'professional',
      responseLength: 'medium',
      languages: ['English'],
      features: {
        webSearch: false,
        fileUpload: false,
        voiceResponse: false,
        contextMemory: true
      },
      integrations: {
        channels: [],
        apis: [],
        webhooks: []
      },
      constraints: {
        maxTokens: 2048,
        temperature: 0.7,
        timeoutSeconds: 30
      }
    });
    setSelectedChatbot(null);
    setShowConfigModal(true);
  };

  const handleEdit = (chatbot: any) => {
    setCurrentConfig({
      id: chatbot.id,
      name: chatbot.name,
      description: chatbot.description || '',
      personality: chatbot.personality || 'professional',
      instructions: chatbot.instructions || '',
      knowledgeBase: chatbot.knowledge_base || [],
      responseTone: chatbot.response_tone || 'professional',
      responseLength: chatbot.response_length || 'medium',
      languages: chatbot.languages || ['English'],
      features: chatbot.features || {
        webSearch: false,
        fileUpload: false,
        voiceResponse: false,
        contextMemory: true
      },
      integrations: chatbot.integrations || {
        channels: [],
        apis: [],
        webhooks: []
      },
      constraints: chatbot.constraints || {
        maxTokens: 2048,
        temperature: 0.7,
        timeoutSeconds: 30
      }
    });
    setSelectedChatbot(chatbot);
    setShowConfigModal(true);
  };

  const handleSave = async () => {
    try {
      if (currentConfig.id && updateChatbot) {
        await updateChatbot(currentConfig.id.toString(), currentConfig);
        showToast('Chatbot updated successfully!', 'success');
      } else if (createChatbot) {
        await createChatbot(currentConfig);
        showToast('Chatbot created successfully!', 'success');
      }
      setShowConfigModal(false);
      if (fetchChatbots) {
        fetchChatbots();
      }
    } catch (error) {
      showToast('Error saving chatbot configuration', 'danger');
    }
  };

  const handleDelete = async (chatbotId: number) => {
    if (window.confirm('Are you sure you want to delete this chatbot?')) {
      try {
        if (deleteChatbot) {
          await deleteChatbot(chatbotId.toString());
          showToast('Chatbot deleted successfully!', 'success');
          if (fetchChatbots) {
            fetchChatbots();
          }
        }
      } catch (error) {
        showToast('Error deleting chatbot', 'danger');
      }
    }
  };

  const handleTest = (chatbot: any) => {
    setSelectedChatbot(chatbot);
    setTestConversations([]);
    setShowTestModal(true);
  };

  const sendTestMessage = async () => {
    if (!testMessage.trim() || !selectedChatbot) return;

    setTestLoading(true);
    try {
      const response = await apiService.post('/api/ai/chat', {
        message: testMessage,
        chatbot_id: selectedChatbot.id,
        personality: selectedChatbot.personality || 'professional'
      });

      const newConversation: TestConversation = {
        id: Date.now().toString(),
        userMessage: testMessage,
        botResponse: response.data.response || 'No response received',
        timestamp: new Date()
      };

      setTestConversations(prev => [...prev, newConversation]);
      setTestMessage('');
    } catch (error) {
      const errorConversation: TestConversation = {
        id: Date.now().toString(),
        userMessage: testMessage,
        botResponse: 'Error: Unable to generate response. Testing with mock data.',
        timestamp: new Date()
      };
      setTestConversations(prev => [...prev, errorConversation]);
      setTestMessage('');
    } finally {
      setTestLoading(false);
    }
  };

  const showToast = (message: string, variant: string) => {
    setToast({ show: true, message, variant });
    setTimeout(() => setToast({ show: false, message: '', variant: 'success' }), 3000);
  };

  const getStatusBadge = (status: string) => {
    const variants: { [key: string]: string } = {
      'active': 'success',
      'inactive': 'secondary',
      'training': 'warning',
      'error': 'danger'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  if (chatbotsLoading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <Spinner animation="border" variant="primary" />
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Row className="mb-4">
          <Col>
            <div className="d-flex justify-content-between align-items-center">
              <h2 className="fw-bold text-dark">
                <Bot className="me-2" />
                Chatbot Management
              </h2>
              <Button variant="primary" onClick={handleCreateNew}>
                <Plus className="me-1" size={16} />
                Create New Chatbot
              </Button>
            </div>
          </Col>
        </Row>

        {/* Chatbot List */}
        <Row>
          {chatbots.map((chatbot: any) => (
            <Col lg={4} md={6} key={chatbot.id} className="mb-4">
              <motion.div
                whileHover={{ scale: 1.02 }}
                transition={{ duration: 0.2 }}
              >
                <Card className="border-0 shadow-sm h-100">
                  <Card.Header className="bg-white border-0 d-flex justify-content-between align-items-center">
                    <div>
                      <h6 className="fw-bold mb-0">{chatbot.name}</h6>
                      {getStatusBadge(chatbot.status)}
                    </div>
                    <div className="dropdown">
                      <Button variant="outline-secondary" size="sm" className="dropdown-toggle" data-bs-toggle="dropdown">
                        <Settings size={16} />
                      </Button>
                      <ul className="dropdown-menu">
                        <li><a className="dropdown-item" href="#" onClick={() => handleEdit(chatbot)}><Edit size={14} className="me-2" />Edit</a></li>
                        <li><a className="dropdown-item" href="#" onClick={() => handleTest(chatbot)}><TestTube size={14} className="me-2" />Test</a></li>
                        <li><hr className="dropdown-divider" /></li>
                        <li><a className="dropdown-item text-danger" href="#" onClick={() => handleDelete(chatbot.id)}><Trash2 size={14} className="me-2" />Delete</a></li>
                      </ul>
                    </div>
                  </Card.Header>
                  <Card.Body>
                    <p className="text-muted small mb-3">{chatbot.description || 'No description provided'}</p>
                    <div className="d-flex justify-content-between text-muted small">
                      <span>Type: {chatbot.chatbot_type}</span>
                      <span>Complexity: {chatbot.complexity}</span>
                    </div>
                    <div className="mt-3 d-flex gap-2">
                      <Button variant="outline-primary" size="sm" onClick={() => handleEdit(chatbot)}>
                        <Edit size={14} className="me-1" />
                        Configure
                      </Button>
                      <Button variant="outline-success" size="sm" onClick={() => handleTest(chatbot)}>
                        <Play size={14} className="me-1" />
                        Test
                      </Button>
                    </div>
                  </Card.Body>
                </Card>
              </motion.div>
            </Col>
          ))}
        </Row>

        {/* Configuration Modal */}
        <Modal show={showConfigModal} onHide={() => setShowConfigModal(false)} size="lg">
          <Modal.Header closeButton>
            <Modal.Title>
              <Bot className="me-2" />
              {currentConfig.id ? 'Edit Chatbot' : 'Create New Chatbot'}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k || 'overview')}>
              <Tab eventKey="overview" title="Overview">
                <Form className="mt-3">
                  <Form.Group className="mb-3">
                    <Form.Label>Chatbot Name</Form.Label>
                    <Form.Control
                      type="text"
                      value={currentConfig.name}
                      onChange={(e) => setCurrentConfig({...currentConfig, name: e.target.value})}
                      placeholder="Enter chatbot name"
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Description</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={3}
                      value={currentConfig.description}
                      onChange={(e) => setCurrentConfig({...currentConfig, description: e.target.value})}
                      placeholder="Describe your chatbot's purpose"
                    />
                  </Form.Group>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Personality</Form.Label>
                        <Form.Select
                          value={currentConfig.personality}
                          onChange={(e) => setCurrentConfig({...currentConfig, personality: e.target.value})}
                        >
                          <option value="professional">Professional</option>
                          <option value="friendly">Friendly</option>
                          <option value="casual">Casual</option>
                          <option value="technical">Technical</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Response Tone</Form.Label>
                        <Form.Select
                          value={currentConfig.responseTone}
                          onChange={(e) => setCurrentConfig({...currentConfig, responseTone: e.target.value as any})}
                        >
                          <option value="professional">Professional</option>
                          <option value="friendly">Friendly</option>
                          <option value="casual">Casual</option>
                          <option value="technical">Technical</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                  </Row>
                </Form>
              </Tab>
              
              <Tab eventKey="behavior" title="Behavior">
                <Form className="mt-3">
                  <Form.Group className="mb-3">
                    <Form.Label>Instructions</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={5}
                      value={currentConfig.instructions}
                      onChange={(e) => setCurrentConfig({...currentConfig, instructions: e.target.value})}
                      placeholder="Provide specific instructions for how the chatbot should behave"
                    />
                  </Form.Group>
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Response Length</Form.Label>
                        <Form.Select
                          value={currentConfig.responseLength}
                          onChange={(e) => setCurrentConfig({...currentConfig, responseLength: e.target.value as any})}
                        >
                          <option value="short">Short</option>
                          <option value="medium">Medium</option>
                          <option value="detailed">Detailed</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Max Tokens</Form.Label>
                        <Form.Control
                          type="number"
                          value={currentConfig.constraints.maxTokens}
                          onChange={(e) => setCurrentConfig({
                            ...currentConfig, 
                            constraints: {...currentConfig.constraints, maxTokens: parseInt(e.target.value)}
                          })}
                        />
                      </Form.Group>
                    </Col>
                  </Row>
                </Form>
              </Tab>
              
              <Tab eventKey="features" title="Features">
                <div className="mt-3">
                  <h6 className="fw-bold mb-3">Available Features</h6>
                  {Object.entries(currentConfig.features).map(([feature, enabled]) => (
                    <Form.Check
                      key={feature}
                      type="switch"
                      id={`feature-${feature}`}
                      label={feature.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                      checked={enabled}
                      onChange={(e) => setCurrentConfig({
                        ...currentConfig,
                        features: {...currentConfig.features, [feature]: e.target.checked}
                      })}
                      className="mb-2"
                    />
                  ))}
                </div>
              </Tab>
            </Tabs>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowConfigModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSave}>
              <Save className="me-1" size={16} />
              Save Configuration
            </Button>
          </Modal.Footer>
        </Modal>

        {/* Test Modal */}
        <Modal show={showTestModal} onHide={() => setShowTestModal(false)} size="lg">
          <Modal.Header closeButton>
            <Modal.Title>
              <TestTube className="me-2" />
              Test Chatbot: {selectedChatbot?.name}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="chat-container" style={{ height: '400px', overflowY: 'auto' }}>
              {testConversations.map((conv) => (
                <div key={conv.id} className="mb-3">
                  <div className="d-flex justify-content-end mb-2">
                    <div className="bg-primary text-white p-2 rounded" style={{ maxWidth: '70%' }}>
                      {conv.userMessage}
                    </div>
                  </div>
                  <div className="d-flex justify-content-start">
                    <div className="bg-light p-2 rounded" style={{ maxWidth: '70%' }}>
                      {conv.botResponse}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <InputGroup className="mt-3">
              <Form.Control
                type="text"
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                placeholder="Type a test message..."
                onKeyPress={(e) => e.key === 'Enter' && sendTestMessage()}
                disabled={testLoading}
              />
              <Button 
                variant="primary" 
                onClick={sendTestMessage}
                disabled={testLoading || !testMessage.trim()}
              >
                {testLoading ? <Spinner animation="border" size="sm" /> : <MessageSquare size={16} />}
              </Button>
            </InputGroup>
          </Modal.Body>
        </Modal>

        {/* Toast Notifications */}
        <ToastContainer position="top-end" className="p-3">
          <Toast show={toast.show} onClose={() => setToast({...toast, show: false})}>
            <Toast.Header>
              <strong className="me-auto">Notification</strong>
            </Toast.Header>
            <Toast.Body className={`text-${toast.variant}`}>
              {toast.message}
            </Toast.Body>
          </Toast>
        </ToastContainer>
      </motion.div>
    </Container>
  );
};

export default ChatbotManager;
