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
import AnalyticsDashboard from './AnalyticsDashboard';
import Templates from './Templates';
import EnhancedClientDashboard from './EnhancedClientDashboard';
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
  template?: string;
  client_id?: string;
}

type FormData = ClientFormData | ChatbotFormData;

// Template categories and options
const PERSONALITY_OPTIONS = [
  { value: 'helpful', label: 'Helpful - Friendly and supportive' },
  { value: 'professional', label: 'Professional - Formal and business-oriented' },
  { value: 'creative', label: 'Creative - Innovative and imaginative' },
  { value: 'analytical', label: 'Analytical - Data-driven and logical' },
  { value: 'friendly', label: 'Friendly - Casual and approachable' },
  { value: 'technical', label: 'Technical - Expert and detailed' },
  { value: 'persuasive', label: 'Persuasive - Convincing and sales-oriented' },
  { value: 'educational', label: 'Educational - Teaching and informative' }
];

const TEMPLATE_OPTIONS = [
  // Personal Assistant (PA) Templates
  { value: 'pa-general', label: 'PA - General Assistant', category: 'Personal Assistant' },
  { value: 'pa-executive', label: 'PA - Executive Assistant', category: 'Personal Assistant' },
  { value: 'pa-scheduling', label: 'PA - Scheduling Assistant', category: 'Personal Assistant' },
  { value: 'pa-travel', label: 'PA - Travel Assistant', category: 'Personal Assistant' },
  
  // Project Management (PM) Templates
  { value: 'pm-scrum', label: 'PM - Scrum Master', category: 'Project Management' },
  { value: 'pm-agile', label: 'PM - Agile Coach', category: 'Project Management' },
  { value: 'pm-waterfall', label: 'PM - Waterfall Manager', category: 'Project Management' },
  { value: 'pm-stakeholder', label: 'PM - Stakeholder Manager', category: 'Project Management' },
  
  // Marketing & Sales (M&S) Templates
  { value: 'ms-lead-gen', label: 'M&S - Lead Generation', category: 'Marketing & Sales' },
  { value: 'ms-customer-service', label: 'M&S - Customer Service', category: 'Marketing & Sales' },
  { value: 'ms-sales-funnel', label: 'M&S - Sales Funnel', category: 'Marketing & Sales' },
  { value: 'ms-content-marketing', label: 'M&S - Content Marketing', category: 'Marketing & Sales' },
  { value: 'ms-social-media', label: 'M&S - Social Media Manager', category: 'Marketing & Sales' },
  
  // Analytics & Data (A&D) Templates
  { value: 'ad-data-analyst', label: 'A&D - Data Analyst', category: 'Analytics & Data' },
  { value: 'ad-business-intelligence', label: 'A&D - Business Intelligence', category: 'Analytics & Data' },
  { value: 'ad-reporting', label: 'A&D - Reporting Assistant', category: 'Analytics & Data' },
  { value: 'ad-machine-learning', label: 'A&D - ML Assistant', category: 'Analytics & Data' },
  
  // Technical Templates
  { value: 'tech-support', label: 'Technical Support', category: 'Technical' },
  { value: 'tech-documentation', label: 'Documentation Assistant', category: 'Technical' },
  { value: 'tech-code-review', label: 'Code Review Assistant', category: 'Technical' },
  { value: 'tech-devops', label: 'DevOps Assistant', category: 'Technical' },
  
  // Healthcare Templates
  { value: 'health-patient-care', label: 'Patient Care Assistant', category: 'Healthcare' },
  { value: 'health-appointment', label: 'Appointment Scheduler', category: 'Healthcare' },
  { value: 'health-wellness', label: 'Wellness Coach', category: 'Healthcare' },
  
  // Education Templates
  { value: 'edu-tutor', label: 'Educational Tutor', category: 'Education' },
  { value: 'edu-training', label: 'Training Assistant', category: 'Education' },
  { value: 'edu-student-support', label: 'Student Support', category: 'Education' },
  
  // General Templates
  { value: 'general-basic', label: 'Basic Assistant', category: 'General' },
  { value: 'general-custom', label: 'Custom Template', category: 'General' }
];

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
  
  // Edit modal state
  const [showEditModal, setShowEditModal] = useState(false);
  const [editType, setEditType] = useState('client');
  const [editItem, setEditItem] = useState(null);
  const [editItemData, setEditItemData] = useState<ClientFormData | ChatbotFormData>({});
  
  // Delete confirmation modal state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteItem, setDeleteItem] = useState<any>(null);
  const [deleteType, setDeleteType] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [deletingItemId, setDeletingItemId] = useState<string | null>(null);
  
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [showProfileSettings, setShowProfileSettings] = useState(false);
  
  // Navigation state
  const [activeView, setActiveView] = useState('dashboard');

  // Form validation state
  const [formErrors, setFormErrors] = useState<{[key: string]: string}>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationTouched, setValidationTouched] = useState<{[key: string]: boolean}>({});

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
    setFormErrors({});
    setValidationTouched({});
    setIsSubmitting(false);
  };

  // Validation functions
  const validateEmail = (email: string): string => {
    if (!email) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Please enter a valid email address';
    if (email.length > 100) return 'Email must be less than 100 characters';
    return '';
  };

  const validateName = (name: string): string => {
    if (!name) return 'Name is required';
    if (name.length < 2) return 'Name must be at least 2 characters';
    if (name.length > 50) return 'Name must be less than 50 characters';
    if (!/^[a-zA-Z0-9\s\-_.,&]+$/.test(name)) return 'Name contains invalid characters';
    return '';
  };

  const validateCompany = (company: string): string => {
    if (!company) return 'Company is required';
    if (company.length < 2) return 'Company name must be at least 2 characters';
    if (company.length > 100) return 'Company name must be less than 100 characters';
    return '';
  };

  const validateDescription = (description: string): string => {
    if (description && description.length > 500) return 'Description must be less than 500 characters';
    return '';
  };

  const validateClientForm = (data: ClientFormData): {[key: string]: string} => {
    const errors: {[key: string]: string} = {};
    
    const nameError = validateName(data.name || '');
    if (nameError) errors.name = nameError;
    
    const emailError = validateEmail(data.email || '');
    if (emailError) errors.email = emailError;
    
    const companyError = validateCompany(data.company || '');
    if (companyError) errors.company = companyError;
    
    const descriptionError = validateDescription(data.description || '');
    if (descriptionError) errors.description = descriptionError;
    
    return errors;
  };

  const validateChatbotForm = (data: ChatbotFormData): {[key: string]: string} => {
    const errors: {[key: string]: string} = {};
    
    const nameError = validateName(data.name || '');
    if (nameError) errors.name = nameError;
    
    if (!data.personality) {
      errors.personality = 'Personality is required';
    }
    
    if (!data.template) {
      errors.template = 'Template selection is required';
    }
    
    const descriptionError = validateDescription(data.description || '');
    if (descriptionError) errors.description = descriptionError;
    
    return errors;
  };

  const handleFieldChange = (field: string, value: string) => {
    setNewItemData(prev => ({ ...prev, [field]: value }));
    
    // Mark field as touched
    setValidationTouched(prev => ({ ...prev, [field]: true }));
    
    // Real-time validation
    let error = '';
    if (field === 'name') {
      error = validateName(value);
    } else if (field === 'email') {
      error = validateEmail(value);
    } else if (field === 'company') {
      error = validateCompany(value);
    } else if (field === 'description') {
      error = validateDescription(value);
    } else if (field === 'personality' && createType === 'chatbot') {
      error = !value ? 'Personality is required' : '';
    } else if (field === 'template' && createType === 'chatbot') {
      error = !value ? 'Template selection is required' : '';
    }
    
    setFormErrors(prev => ({ 
      ...prev, 
      [field]: error 
    }));
  };

  const handleCreateSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      let errors: {[key: string]: string} = {};
      
      if (createType === 'client') {
        const clientData = newItemData as ClientFormData;
        errors = validateClientForm(clientData);
      } else if (createType === 'chatbot') {
        const chatbotData = newItemData as ChatbotFormData;
        errors = validateChatbotForm(chatbotData);
      }
      
      setFormErrors(errors);
      
      // If there are validation errors, don't submit
      if (Object.keys(errors).length > 0) {
        setIsSubmitting(false);
        setToastMessage('Please fix the errors in the form before submitting.');
        setShowToast(true);
        return;
      }

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
          assistant_type: 'chatbot',
          complexity: 'basic',
          personality_config: {
            personality: chatbotData.personality || 'helpful',
            template: chatbotData.template || 'general-basic'
          },
          client_id: chatbotData.client_id ? parseInt(chatbotData.client_id) : null,
        });
      }

      // If we reach here, the operation was successful
      closeCreateModal();
      setToastMessage(`${createType === 'client' ? 'Client' : 'Assistant'} created successfully!`);
      setShowToast(true);
    } catch (error) {
      console.error('Failed to create item:', error);
      setToastMessage(`Failed to create ${createType}. Please try again.`);
      setShowToast(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle delete - improved version with modal confirmation
  const handleDeleteRequest = (item: any, type: string) => {
    setDeleteItem(item);
    setDeleteType(type);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteItem || !deleteType) return;
    
    setIsDeleting(true);
    setDeletingItemId(deleteItem.id.toString());
    
    try {
      if (deleteType === 'client') {
        await deleteClient(deleteItem.id.toString());
        // Refresh clients data to ensure UI is updated
        await fetchClients();
        setToastMessage(`Client "${deleteItem.name}" deleted successfully!`);
      } else if (deleteType === 'chatbot') {
        await deleteChatbot(deleteItem.id.toString());
        // Refresh chatbots data to ensure UI is updated
        await fetchChatbots();
        setToastMessage(`Assistant "${deleteItem.name}" deleted successfully!`);
      }
      
      setShowToast(true);
      setShowDeleteModal(false);
    } catch (error) {
      console.error('Failed to delete item:', error);
      setToastMessage(`Failed to delete ${deleteType}. Please try again.`);
      setShowToast(true);
    } finally {
      setIsDeleting(false);
      setDeletingItemId(null);
      setDeleteItem(null);
      setDeleteType('');
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setDeleteItem(null);
    setDeleteType('');
  };

  // Handle edit
  const handleEdit = (item: any, type: string) => {
    setEditItem(item);
    setEditType(type);
    if (type === 'client') {
      setEditItemData({
        name: item.name || '',
        email: item.email || '',
        company: item.company || '',
        description: item.description || ''
      });
    } else {
      setEditItemData({
        name: item.name || '',
        description: item.description || ''
      });
    }
    setShowEditModal(true);
  };

  // Handle edit submit
  const handleEditSubmit = async () => {
    try {
      // Implementation for updating client/chatbot will be added here
      console.log('Editing:', editType, editItemData);
      setShowEditModal(false);
      setToastMessage(`${editType} updated successfully!`);
      setShowToast(true);
    } catch (error) {
      console.error('Failed to update item:', error);
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
              <Nav.Link 
                active={activeView === 'dashboard'}
                onClick={() => setActiveView('dashboard')}
                data-testid="nav-dashboard"
              >
                Dashboard
              </Nav.Link>
              <Nav.Link 
                active={activeView === 'analytics'}
                onClick={() => setActiveView('analytics')}
                data-testid="nav-analytics"
              >
                Analytics
              </Nav.Link>
              <Nav.Link 
                active={activeView === 'templates'}
                onClick={() => setActiveView('templates')}
                data-testid="nav-templates"
              >
                Templates
              </Nav.Link>
              <Nav.Link 
                active={activeView === 'enhanced-dashboard'}
                onClick={() => setActiveView('enhanced-dashboard')}
                data-testid="nav-enhanced-dashboard"
              >
                Enhanced Dashboard
              </Nav.Link>
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

        {/* Conditional View Rendering */}
        {activeView === 'dashboard' && (
          <>
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
                    <Card 
                      className={`border-0 shadow-sm h-100 ${deletingItemId === client.id.toString() ? 'opacity-50' : ''}`} 
                      style={{ borderRadius: '15px', position: 'relative' }}
                    >
                      {deletingItemId === client.id.toString() && (
                        <div 
                          className="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
                          style={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.8)', 
                            zIndex: 10,
                            borderRadius: '15px'
                          }}
                        >
                          <div className="text-center">
                            <div className="spinner-border text-danger mb-2" role="status" aria-hidden="true"></div>
                            <div className="small text-danger fw-semibold">Deleting...</div>
                          </div>
                        </div>
                      )}
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
                              onClick={() => handleEdit(client, 'client')}
                              disabled={deletingItemId === client.id.toString()}
                            >
                              <Edit3 size={14} />
                            </Button>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              className="rounded-pill border-0"
                              onClick={() => handleDeleteRequest(client, 'client')}
                              disabled={deletingItemId === client.id.toString()}
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
                    <Card 
                      className={`border-0 shadow-sm h-100 ${deletingItemId === chatbot.id.toString() ? 'opacity-50' : ''}`} 
                      style={{ borderRadius: '15px', position: 'relative' }}
                    >
                      {deletingItemId === chatbot.id.toString() && (
                        <div 
                          className="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
                          style={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.8)', 
                            zIndex: 10,
                            borderRadius: '15px'
                          }}
                        >
                          <div className="text-center">
                            <div className="spinner-border text-danger mb-2" role="status" aria-hidden="true"></div>
                            <div className="small text-danger fw-semibold">Deleting...</div>
                          </div>
                        </div>
                      )}
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
                          <div className="d-flex flex-column">
                            <Badge 
                              bg="primary" 
                              className="rounded-pill mb-1"
                              style={{ fontSize: '0.75rem' }}
                            >
                              <Zap size={12} className="me-1" />
                              {(chatbot.personality_config?.personality) || chatbot.personality || 'Helpful'}
                            </Badge>
                            {chatbot.personality_config?.template && (
                              <Badge 
                                bg="info" 
                                className="rounded-pill"
                                style={{ fontSize: '0.7rem' }}
                              >
                                {TEMPLATE_OPTIONS.find(t => t.value === chatbot.personality_config.template)?.label || chatbot.personality_config.template}
                              </Badge>
                            )}
                          </div>
                          <div>
                            <Button
                              variant="outline-primary"
                              size="sm"
                              className="me-2 rounded-pill border-0"
                              onClick={() => handleEdit(chatbot, 'chatbot')}
                              disabled={deletingItemId === chatbot.id.toString()}
                            >
                              <Edit3 size={14} />
                            </Button>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              className="rounded-pill border-0"
                              onClick={() => handleDeleteRequest(chatbot, 'chatbot')}
                              disabled={deletingItemId === chatbot.id.toString()}
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
          </>
        )}

        {/* Analytics View */}
        {activeView === 'analytics' && (
          <AnalyticsDashboard />
        )}

        {/* Templates View */}
        {activeView === 'templates' && (
          <Templates />
        )}

        {/* Enhanced Dashboard View */}
        {activeView === 'enhanced-dashboard' && (
          <EnhancedClientDashboard />
        )}
      </Container>

      {/* Create Modal */}
      <Modal show={showCreateModal} onHide={closeCreateModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>Create New {createType === 'client' ? 'Client' : 'AI Assistant'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {/* Validation Summary */}
          {Object.keys(formErrors).length > 0 && Object.values(formErrors).some(error => error) && (
            <Alert variant="danger" className="mb-3">
              <AlertCircle size={16} className="me-2" />
              <strong>Please fix the following errors:</strong>
              <ul className="mb-0 mt-2">
                {Object.entries(formErrors).map(([field, error]) => 
                  error ? <li key={field}><strong>{field.charAt(0).toUpperCase() + field.slice(1)}:</strong> {error}</li> : null
                )}
              </ul>
            </Alert>
          )}
          
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Name <span className="text-danger">*</span></Form.Label>
              <Form.Control
                type="text"
                value={newItemData.name || ''}
                onChange={(e) => handleFieldChange('name', e.target.value)}
                placeholder={`Enter ${createType} name`}
                className={`rounded-3 ${formErrors.name ? 'is-invalid' : validationTouched.name && !formErrors.name ? 'is-valid' : ''}`}
                isInvalid={!!formErrors.name}
              />
              {formErrors.name && (
                <Form.Control.Feedback type="invalid">
                  {formErrors.name}
                </Form.Control.Feedback>
              )}
            </Form.Group>
            
            {createType === 'client' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Email <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="email"
                    value={(newItemData as ClientFormData).email || ''}
                    onChange={(e) => handleFieldChange('email', e.target.value)}
                    placeholder="Enter email address (e.g., john@company.com)"
                    className={`rounded-3 ${formErrors.email ? 'is-invalid' : validationTouched.email && !formErrors.email ? 'is-valid' : ''}`}
                    isInvalid={!!formErrors.email}
                  />
                  {formErrors.email && (
                    <Form.Control.Feedback type="invalid">
                      {formErrors.email}
                    </Form.Control.Feedback>
                  )}
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Company <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={(newItemData as ClientFormData).company || ''}
                    onChange={(e) => handleFieldChange('company', e.target.value)}
                    placeholder="Enter company name"
                    className={`rounded-3 ${formErrors.company ? 'is-invalid' : validationTouched.company && !formErrors.company ? 'is-valid' : ''}`}
                    isInvalid={!!formErrors.company}
                  />
                  {formErrors.company && (
                    <Form.Control.Feedback type="invalid">
                      {formErrors.company}
                    </Form.Control.Feedback>
                  )}
                </Form.Group>
              </>
            )}
            
            {createType === 'chatbot' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Personality <span className="text-danger">*</span></Form.Label>
                  <Form.Select 
                    value={(newItemData as ChatbotFormData).personality || ''}
                    onChange={(e) => handleFieldChange('personality', e.target.value)}
                    className={`rounded-3 ${formErrors.personality ? 'is-invalid' : ''}`}
                    isInvalid={!!formErrors.personality}
                  >
                    <option value="">Select personality type</option>
                    {PERSONALITY_OPTIONS.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Form.Select>
                  {formErrors.personality && (
                    <Form.Control.Feedback type="invalid">
                      {formErrors.personality}
                    </Form.Control.Feedback>
                  )}
                  <Form.Text className="text-muted">
                    Choose the personality that best fits your assistant's purpose
                  </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Template <span className="text-danger">*</span></Form.Label>
                  <Form.Select 
                    value={(newItemData as ChatbotFormData).template || ''}
                    onChange={(e) => handleFieldChange('template', e.target.value)}
                    className={`rounded-3 ${formErrors.template ? 'is-invalid' : ''}`}
                    isInvalid={!!formErrors.template}
                  >
                    <option value="">Select a template</option>
                    {/* Group templates by category */}
                    {['Personal Assistant', 'Project Management', 'Marketing & Sales', 'Analytics & Data', 'Technical', 'Healthcare', 'Education', 'General'].map(category => (
                      <optgroup key={category} label={category}>
                        {TEMPLATE_OPTIONS
                          .filter(template => template.category === category)
                          .map(template => (
                            <option key={template.value} value={template.value}>
                              {template.label}
                            </option>
                          ))
                        }
                      </optgroup>
                    ))}
                  </Form.Select>
                  {formErrors.template && (
                    <Form.Control.Feedback type="invalid">
                      {formErrors.template}
                    </Form.Control.Feedback>
                  )}
                  <Form.Text className="text-muted">
                    Select a template that matches your intended use case
                  </Form.Text>
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
                  <Form.Text className="text-muted">
                    Optionally assign this assistant to a specific client
                  </Form.Text>
                </Form.Group>
              </>
            )}
            
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={newItemData.description || ''}
                onChange={(e) => handleFieldChange('description', e.target.value)}
                placeholder="Enter description (optional)"
                className={`rounded-3 ${formErrors.description ? 'is-invalid' : validationTouched.description && !formErrors.description ? 'is-valid' : ''}`}
                isInvalid={!!formErrors.description}
              />
              {formErrors.description && (
                <Form.Control.Feedback type="invalid">
                  {formErrors.description}
                </Form.Control.Feedback>
              )}
              <Form.Text className="text-muted">
                Max 500 characters. {newItemData.description ? `${newItemData.description.length}/500` : '0/500'}
              </Form.Text>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeCreateModal} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button 
            variant="primary"
            onClick={handleCreateSubmit}
            disabled={isSubmitting || Object.keys(formErrors).some(key => formErrors[key])}
            style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none' }}
          >
            {isSubmitting ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Creating...
              </>
            ) : (
              <>Create {createType === 'client' ? 'Client' : 'Assistant'}</>
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Edit Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)} centered>
        <Modal.Header closeButton className="border-0">
          <Modal.Title>Edit {editType === 'client' ? 'Client' : 'Assistant'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                value={(editItemData as any).name || ''}
                onChange={(e) => setEditItemData({ ...editItemData, name: e.target.value })}
                placeholder="Enter name"
                className="rounded-3"
              />
            </Form.Group>
            
            {editType === 'client' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    value={(editItemData as ClientFormData).email || ''}
                    onChange={(e) => setEditItemData({ ...editItemData, email: e.target.value })}
                    placeholder="Enter email"
                    className="rounded-3"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Company</Form.Label>
                  <Form.Control
                    type="text"
                    value={(editItemData as ClientFormData).company || ''}
                    onChange={(e) => setEditItemData({ ...editItemData, company: e.target.value })}
                    placeholder="Enter company"
                    className="rounded-3"
                  />
                </Form.Group>
              </>
            )}

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={(editItemData as any).description || ''}
                onChange={(e) => setEditItemData({ ...editItemData, description: e.target.value })}
                placeholder="Enter description"
                className="rounded-3"
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowEditModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary"
            onClick={handleEditSubmit}
            style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none' }}
          >
            Update {editType === 'client' ? 'Client' : 'Assistant'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={handleDeleteCancel} centered>
        <Modal.Header closeButton className="border-0">
          <Modal.Title className="text-danger">
            <Trash2 size={20} className="me-2" />
            Confirm Deletion
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="text-center">
            <div className="mb-3">
              <Trash2 size={48} className="text-danger opacity-50" />
            </div>
            <h5 className="mb-3">
              Are you sure you want to delete this {deleteType}?
            </h5>
            {deleteItem && (
              <div className="bg-light p-3 rounded-3 mb-3">
                <strong>{deleteItem.name}</strong>
                {deleteType === 'client' && deleteItem.email && (
                  <div className="text-muted small">{deleteItem.email}</div>
                )}
                {deleteItem.description && (
                  <div className="text-muted small mt-1">{deleteItem.description}</div>
                )}
              </div>
            )}
            <p className="text-muted">
              This action cannot be undone. All associated data will be permanently removed.
            </p>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={handleDeleteCancel}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={handleDeleteConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Deleting...
              </>
            ) : (
              <>
                <Trash2 size={16} className="me-1" />
                Delete {deleteType === 'client' ? 'Client' : 'Assistant'}
              </>
            )}
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
