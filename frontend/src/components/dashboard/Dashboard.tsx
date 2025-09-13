/**
 * Modern Dashboard Component with Bootstrap and Magic UI styling
 * Integrates with backend to display clients, chatbots, and conversations
 */

import React, { useEffect, useState } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Navbar,
  Nav,
  NavDropdown,
  Modal,
  Form,
  Alert,
  Spinner,
  Badge,
  ProgressBar,
  Toast,
  ToastContainer
} from 'react-bootstrap';
import { motion } from 'framer-motion';
import {
  Users,
  Bot,
  MessageCircle,
  Plus,
  MoreHorizontal,
  Edit3,
  Trash2,
  Activity,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useChatbot } from '../../contexts/ChatbotContext';
import AccountSettings from '../auth/AccountSettings';
import 'bootstrap/dist/css/bootstrap.min.css';

// Interface definitions for form data
interface ClientFormData {
  name?: string;
  email?: string;
  company?: string;
  description?: string;
}

interface ChatbotFormData {
  name?: string;
  description?: string;
  type?: string;
  prompt?: string;
  personality?: string;
  client_id?: string;
}

type FormData = ClientFormData | ChatbotFormData;

const Dashboard = () => {
  const { user, logout } = useAuth();
  const {
    clients,
    chatbots,
    conversations,
    isLoadingClients,
    isLoadingChatbots,
    isLoadingConversations,
    clientsError,
    chatbotsError,
    conversationsError,
    fetchClients,
    fetchChatbots,
    fetchConversations,
    createClient,
    createChatbot,
    deleteClient,
    deleteChatbot,
    clearAllErrors,
  } = useChatbot();

  // UI state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createType, setCreateType] = useState('client');
  const [selectedItem, setSelectedItem] = useState(null);
  const [showActionModal, setShowActionModal] = useState(false);
  const [newItemData, setNewItemData] = useState<ClientFormData | ChatbotFormData>({});
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [showProfileSettings, setShowProfileSettings] = useState(false);

  // Load data on component mount
  useEffect(() => {
    fetchClients();
    fetchChatbots();
    fetchConversations();
  }, [fetchClients, fetchChatbots, fetchConversations]);

  // Handle create modal
  const openCreateModal = (type: string) => {
    setCreateType(type);
    setNewItemData({});
    setShowCreateModal(true);
  };

  const closeCreateModal = () => {
    setShowCreateModal(false);
    setNewItemData({});
  };

  const handleCreateSubmit = async () => {
    try {
      if (createType === 'client') {
        const clientData = newItemData as ClientFormData;
        await createClient({
          name: clientData.name,
          email: clientData.email,
          company: clientData.company,
          description: clientData.description,
        });
      } else if (createType === 'chatbot') {
        const chatbotData = newItemData as ChatbotFormData;
        await createChatbot({
          name: chatbotData.name,
          description: chatbotData.description,
          personality: chatbotData.personality || 'helpful',
          client_id: chatbotData.client_id ? parseInt(chatbotData.client_id) : null,
        });
      }

      // If we reach here, the operation was successful
      closeCreateModal();
      setToastMessage(`${createType} created successfully!`);
      setShowToast(true);
    } catch (error) {
      console.error('Failed to create item:', error);
    }
  };

  // Handle delete
  const handleDelete = async (item: any, type: string) => {
    if (window.confirm(`Are you sure you want to delete this ${type}?`)) {
      try {
        if (type === 'client') {
          await deleteClient(item.id.toString());
        } else if (type === 'chatbot') {
          await deleteChatbot(item.id.toString());
        }

        // If we reach here, the operation was successful
        setToastMessage(`${type} deleted successfully!`);
        setShowToast(true);
      } catch (error) {
        console.error('Failed to delete item:', error);
      }
    }
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.3 }
    },
    hover: {
      y: -5,
      boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
      transition: { duration: 0.2 }
    }
  };

  const statsVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { duration: 0.4, type: "spring" }
    }
  };

  return (
    <div style={{ background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', minHeight: '100vh' }}>
      {/* Navigation */}
      <Navbar 
        expand="lg" 
        className="shadow-sm mb-4"
        style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderBottom: 'none'
        }}
        variant="dark"
      >
        <Container>
          <Navbar.Brand className="fw-bold">
            🤖 Pixel AI Creator
          </Navbar.Brand>
          <Navbar.Toggle />
          <Navbar.Collapse>
            <Nav className="me-auto">
              <Nav.Link active>Dashboard</Nav.Link>
              <Nav.Link>Analytics</Nav.Link>
              <Nav.Link>Templates</Nav.Link>
            </Nav>
            <Nav>
              <NavDropdown 
                title={`${user?.first_name} ${user?.last_name}`} 
                align="end"
                className="text-white"
              >
                <NavDropdown.Item disabled>
                  <small className="text-muted">{user?.email}</small>
                </NavDropdown.Item>
                <NavDropdown.Divider />
                <NavDropdown.Item onClick={() => setShowProfileSettings(true)}>
                  Profile Settings
                </NavDropdown.Item>
                <NavDropdown.Item onClick={logout} className="text-danger">
                  Logout
                </NavDropdown.Item>
              </NavDropdown>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container fluid className="px-4">
        {/* Error Alerts */}
        {(clientsError || chatbotsError || conversationsError) && (
          <Alert variant="danger" dismissible onClose={clearAllErrors} className="mb-4">
            <AlertCircle size={16} className="me-2" />
            {clientsError || chatbotsError || conversationsError}
          </Alert>
        )}

        {/* Stats Overview */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="mb-5"
        >
          <Row className="g-4">
            <Col md={4}>
              <motion.div variants={statsVariants}>
                <Card 
                  className="border-0 shadow-sm h-100"
                  style={{ borderRadius: '15px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
                >
                  <Card.Body className="text-white">
                    <div className="d-flex align-items-center justify-content-between">
                      <div>
                        <h2 className="display-6 fw-bold mb-0">
                          {isLoadingClients ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            clients.length
                          )}
                        </h2>
                        <p className="mb-0 opacity-75">Total Clients</p>
                      </div>
                      <Users size={48} className="opacity-75" />
                    </div>
                  </Card.Body>
                </Card>
              </motion.div>
            </Col>

            <Col md={4}>
              <motion.div variants={statsVariants}>
                <Card 
                  className="border-0 shadow-sm h-100"
                  style={{ borderRadius: '15px', background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' }}
                >
                  <Card.Body className="text-white">
                    <div className="d-flex align-items-center justify-content-between">
                      <div>
                        <h2 className="display-6 fw-bold mb-0">
                          {isLoadingChatbots ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            chatbots.length
                          )}
                        </h2>
                        <p className="mb-0 opacity-75">AI Assistants</p>
                      </div>
                      <Bot size={48} className="opacity-75" />
                    </div>
                  </Card.Body>
                </Card>
              </motion.div>
            </Col>

            <Col md={4}>
              <motion.div variants={statsVariants}>
                <Card 
                  className="border-0 shadow-sm h-100"
                  style={{ borderRadius: '15px', background: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)' }}
                >
                  <Card.Body className="text-white">
                    <div className="d-flex align-items-center justify-content-between">
                      <div>
                        <h2 className="display-6 fw-bold mb-0">
                          {isLoadingConversations ? (
                            <Spinner animation="border" size="sm" />
                          ) : (
                            conversations.length
                          )}
                        </h2>
                        <p className="mb-0 opacity-75">Conversations</p>
                      </div>
                      <MessageCircle size={48} className="opacity-75" />
                    </div>
                  </Card.Body>
                </Card>
              </motion.div>
            </Col>
          </Row>
        </motion.div>

        {/* Clients Section */}
        <motion.div variants={containerVariants} className="mb-5">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h3 className="fw-bold text-dark">
              <Users className="me-2" size={24} />
              Clients
            </h3>
            <Button 
              variant="primary"
              className="rounded-pill px-4"
              style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none' }}
              onClick={() => openCreateModal('client')}
            >
              <Plus size={16} className="me-2" />
              Add Client
            </Button>
          </div>
          
          <Row className="g-4">
            {isLoadingClients ? (
              <Col xs={12} className="text-center py-5">
                <Spinner animation="border" />
                <p className="mt-2 text-muted">Loading clients...</p>
              </Col>
            ) : clients.length === 0 ? (
              <Col xs={12}>
                <Card className="border-0 shadow-sm text-center py-5" style={{ borderRadius: '15px' }}>
                  <Card.Body>
                    <Users size={48} className="text-muted mb-3" />
                    <h5 className="text-muted">No clients yet</h5>
                    <p className="text-muted">Create your first client to get started!</p>
                  </Card.Body>
                </Card>
              </Col>
            ) : (
              clients.map((client: any) => (
                <Col lg={4} md={6} key={client.id}>
                  <motion.div
                    variants={cardVariants}
                    whileHover="hover"
                  >
                    <Card className="border-0 shadow-sm h-100" style={{ borderRadius: '15px' }}>
                      <Card.Body>
                        <div className="d-flex justify-content-between align-items-start mb-3">
                          <div>
                            <h5 className="fw-bold text-dark mb-1">{client.name}</h5>
                            <p className="text-muted small mb-0">{client.email}</p>
                          </div>
                          <div className="dropdown">
                            <Button variant="light" size="sm" className="border-0 rounded-circle">
                              <MoreHorizontal size={16} />
                            </Button>
                          </div>
                        </div>
                        
                        {client.company && (
                          <p className="small text-secondary mb-2">
                            <span className="fw-semibold">Company:</span> {client.company}
                          </p>
                        )}
                        
                        <div className="d-flex justify-content-between align-items-center">
                          <Badge 
                            bg="success" 
                            className="rounded-pill"
                            style={{ fontSize: '0.75rem' }}
                          >
                            <CheckCircle size={12} className="me-1" />
                            {client.status || 'Active'}
                          </Badge>
                          <div>
                            <Button
                              variant="outline-primary"
                              size="sm"
                              className="me-2 rounded-pill border-0"
                            >
                              <Edit3 size={14} />
                            </Button>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              className="rounded-pill border-0"
                              onClick={() => handleDelete(client, 'client')}
                            >
                              <Trash2 size={14} />
                            </Button>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                  </motion.div>
                </Col>
              ))
            )}
          </Row>
        </motion.div>

        {/* Chatbots Section */}
        <motion.div variants={containerVariants} className="mb-5">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h3 className="fw-bold text-dark">
              <Bot className="me-2" size={24} />
              AI Assistants
            </h3>
            <Button 
              variant="success"
              className="rounded-pill px-4"
              onClick={() => openCreateModal('chatbot')}
            >
              <Plus size={16} className="me-2" />
              Create Assistant
            </Button>
          </div>
          
          <Row className="g-4">
            {isLoadingChatbots ? (
              <Col xs={12} className="text-center py-5">
                <Spinner animation="border" />
                <p className="mt-2 text-muted">Loading AI assistants...</p>
              </Col>
            ) : chatbots.length === 0 ? (
              <Col xs={12}>
                <Card className="border-0 shadow-sm text-center py-5" style={{ borderRadius: '15px' }}>
                  <Card.Body>
                    <Bot size={48} className="text-muted mb-3" />
                    <h5 className="text-muted">No AI assistants yet</h5>
                    <p className="text-muted">Build your first AI assistant!</p>
                  </Card.Body>
                </Card>
              </Col>
            ) : (
              chatbots.map((chatbot: any) => (
                <Col lg={4} md={6} key={chatbot.id}>
                  <motion.div
                    variants={cardVariants}
                    whileHover="hover"
                  >
                    <Card className="border-0 shadow-sm h-100" style={{ borderRadius: '15px' }}>
                      <Card.Body>
                        <div className="d-flex justify-content-between align-items-start mb-3">
                          <div>
                            <h5 className="fw-bold text-dark mb-1">{chatbot.name}</h5>
                            <p className="text-muted small mb-0">{chatbot.description}</p>
                          </div>
                          <div className="dropdown">
                            <Button variant="light" size="sm" className="border-0 rounded-circle">
                              <MoreHorizontal size={16} />
                            </Button>
                          </div>
                        </div>
                        
                        <div className="d-flex justify-content-between align-items-center">
                          <Badge 
                            bg="primary" 
                            className="rounded-pill"
                            style={{ fontSize: '0.75rem' }}
                          >
                            <Zap size={12} className="me-1" />
                            {chatbot.personality || 'Helpful'}
                          </Badge>
                          <div>
                            <Button
                              variant="outline-primary"
                              size="sm"
                              className="me-2 rounded-pill border-0"
                            >
                              <Edit3 size={14} />
                            </Button>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              className="rounded-pill border-0"
                              onClick={() => handleDelete(chatbot, 'chatbot')}
                            >
                              <Trash2 size={14} />
                            </Button>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                  </motion.div>
                </Col>
              ))
            )}
          </Row>
        </motion.div>
      </Container>

      {/* Create Modal */}
      <Modal show={showCreateModal} onHide={closeCreateModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>Create New {createType === 'client' ? 'Client' : 'AI Assistant'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                value={newItemData.name || ''}
                onChange={(e) => setNewItemData(prev => ({ ...prev, name: e.target.value }))}
                placeholder={`Enter ${createType} name`}
                className="rounded-3"
              />
            </Form.Group>
            
            {createType === 'client' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    value={(newItemData as ClientFormData).email || ''}
                    onChange={(e) => setNewItemData(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="Enter email address"
                    className="rounded-3"
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Company</Form.Label>
                  <Form.Control
                    type="text"
                    value={(newItemData as ClientFormData).company || ''}
                    onChange={(e) => setNewItemData(prev => ({ ...prev, company: e.target.value }))}
                    placeholder="Enter company name"
                    className="rounded-3"
                  />
                </Form.Group>
              </>
            )}
            
            {createType === 'chatbot' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Personality</Form.Label>
                  <Form.Select 
                    value={(newItemData as ChatbotFormData).personality || 'helpful'}
                    onChange={(e) => setNewItemData(prev => ({ ...prev, personality: e.target.value }))}
                    className="rounded-3"
                  >
                    <option value="helpful">Helpful</option>
                    <option value="friendly">Friendly</option>
                    <option value="professional">Professional</option>
                    <option value="creative">Creative</option>
                    <option value="analytical">Analytical</option>
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Client (Optional)</Form.Label>
                  <Form.Select 
                    value={(newItemData as ChatbotFormData).client_id || ''}
                    onChange={(e) => setNewItemData(prev => ({ ...prev, client_id: e.target.value }))}
                    className="rounded-3"
                  >
                    <option value="">Select a client</option>
                    {clients.map((client: any) => (
                      <option key={client.id} value={client.id}>{client.name}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </>
            )}
            
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={newItemData.description || ''}
                onChange={(e) => setNewItemData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter description"
                className="rounded-3"
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeCreateModal}>
            Cancel
          </Button>
          <Button 
            variant="primary"
            onClick={handleCreateSubmit}
            style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none' }}
          >
            Create {createType === 'client' ? 'Client' : 'Assistant'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Profile Settings Modal */}
      <Modal 
        show={showProfileSettings} 
        onHide={() => setShowProfileSettings(false)}
        size="lg"
        centered
      >
        <Modal.Header closeButton className="border-0">
          <Modal.Title>Profile Settings</Modal.Title>
        </Modal.Header>
        <Modal.Body className="p-0">
          <AccountSettings />
        </Modal.Body>
      </Modal>

      {/* Toast Notifications */}
      <ToastContainer position="bottom-end" className="p-3">
        <Toast 
          show={showToast} 
          onClose={() => setShowToast(false)}
          delay={3000}
          autohide
        >
          <Toast.Header>
            <CheckCircle size={16} className="text-success me-2" />
            <strong className="me-auto">Success</strong>
          </Toast.Header>
          <Toast.Body>{toastMessage}</Toast.Body>
        </Toast>
      </ToastContainer>
    </div>
  );
};

export default Dashboard;
