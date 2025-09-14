/**
 * Templates Management Component
 * Manages chatbot templates with CRUD operations
 */

import React, { useState, useEffect } from 'react';
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
  Tab,
  Tabs,
  InputGroup
} from 'react-bootstrap';
import { motion } from 'framer-motion';
import {
  FileText,
  Plus,
  Edit,
  Trash2,
  Copy,
  Download,
  Search,
  Filter,
  Star,
  Clock,
  User,
  Bot
} from 'lucide-react';

interface Template {
  id: number;
  name: string;
  description: string;
  category: string;
  personality: string;
  instructions: string;
  isPublic: boolean;
  isFavorite: boolean;
  createdAt: string;
  updatedAt: string;
  usageCount: number;
  author: string;
  tags: string[];
}

interface TemplateFormData {
  name: string;
  description: string;
  category: string;
  personality: string;
  instructions: string;
  isPublic: boolean;
  tags: string[];
}

const Templates: React.FC = () => {
  // State management
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [formData, setFormData] = useState<TemplateFormData>({
    name: '',
    description: '',
    category: 'general',
    personality: 'professional',
    instructions: '',
    isPublic: false,
    tags: []
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState('my-templates');

  // Mock data for demonstration
  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setTemplates([
        {
          id: 1,
          name: 'Customer Support Assistant',
          description: 'Professional customer support chatbot template',
          category: 'support',
          personality: 'helpful',
          instructions: 'You are a helpful customer support assistant. Always be polite and try to resolve customer issues efficiently.',
          isPublic: true,
          isFavorite: true,
          createdAt: '2024-01-15',
          updatedAt: '2024-01-20',
          usageCount: 42,
          author: 'Admin',
          tags: ['support', 'customer-service', 'helpful']
        },
        {
          id: 2,
          name: 'Sales Assistant',
          description: 'Engaging sales chatbot template',
          category: 'sales',
          personality: 'persuasive',
          instructions: 'You are a sales assistant focused on helping customers find the right products and closing deals.',
          isPublic: false,
          isFavorite: false,
          createdAt: '2024-01-10',
          updatedAt: '2024-01-18',
          usageCount: 23,
          author: 'User',
          tags: ['sales', 'conversion', 'products']
        },
        {
          id: 3,
          name: 'Technical Support Bot',
          description: 'Technical troubleshooting assistant',
          category: 'technical',
          personality: 'analytical',
          instructions: 'You are a technical support specialist. Provide detailed, step-by-step solutions to technical problems.',
          isPublic: true,
          isFavorite: false,
          createdAt: '2024-01-12',
          updatedAt: '2024-01-22',
          usageCount: 18,
          author: 'TechTeam',
          tags: ['technical', 'troubleshooting', 'IT']
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  // Filter templates based on search and category
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesTab = activeTab === 'my-templates' ? !template.isPublic : template.isPublic;
    
    return matchesSearch && matchesCategory && matchesTab;
  });

  const categories = ['all', 'general', 'support', 'sales', 'technical', 'education', 'healthcare'];

  // Modal handlers
  const handleCreateTemplate = () => {
    setFormData({
      name: '',
      description: '',
      category: 'general',
      personality: 'professional',
      instructions: '',
      isPublic: false,
      tags: []
    });
    setShowCreateModal(true);
  };

  const handleEditTemplate = (template: Template) => {
    setSelectedTemplate(template);
    setFormData({
      name: template.name,
      description: template.description,
      category: template.category,
      personality: template.personality,
      instructions: template.instructions,
      isPublic: template.isPublic,
      tags: template.tags
    });
    setShowEditModal(true);
  };

  const handleDeleteTemplate = (templateId: number) => {
    if (window.confirm('Are you sure you want to delete this template?')) {
      setTemplates(prev => prev.filter(t => t.id !== templateId));
    }
  };

  const handleSubmitTemplate = async (isEdit: boolean = false) => {
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      if (isEdit && selectedTemplate) {
        setTemplates(prev => prev.map(t => 
          t.id === selectedTemplate.id 
            ? { ...t, ...formData, updatedAt: new Date().toISOString().split('T')[0] }
            : t
        ));
        setShowEditModal(false);
      } else {
        const newTemplate: Template = {
          id: Date.now(),
          ...formData,
          isFavorite: false,
          createdAt: new Date().toISOString().split('T')[0],
          updatedAt: new Date().toISOString().split('T')[0],
          usageCount: 0,
          author: 'User'
        };
        setTemplates(prev => [...prev, newTemplate]);
        setShowCreateModal(false);
      }
      setLoading(false);
    }, 500);
  };

  const handleDuplicateTemplate = (template: Template) => {
    const duplicatedTemplate: Template = {
      ...template,
      id: Date.now(),
      name: `${template.name} (Copy)`,
      isPublic: false,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0],
      usageCount: 0,
      author: 'User'
    };
    setTemplates(prev => [...prev, duplicatedTemplate]);
  };

  // Animation variants
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  return (
    <Container fluid className="px-4">
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <h2 className="fw-bold text-dark" data-testid="templates-title">
              <FileText className="me-2" />
              Template Library
            </h2>
            <Button 
              variant="primary" 
              onClick={handleCreateTemplate}
              data-testid="create-template-btn"
            >
              <Plus className="me-1" size={16} />
              Create Template
            </Button>
          </div>
        </Col>
      </Row>

      {/* Search and Filters */}
      <Row className="mb-4">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text>
              <Search size={16} />
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              data-testid="search-templates"
            />
          </InputGroup>
        </Col>
        <Col md={3}>
          <Form.Select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            data-testid="filter-category"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </Form.Select>
        </Col>
      </Row>

      {/* Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={(tab) => setActiveTab(tab || 'my-templates')}
        className="mb-4"
        data-testid="template-tabs"
      >
        <Tab eventKey="my-templates" title="My Templates" data-testid="my-templates-tab">
          {/* My Templates Content */}
        </Tab>
        <Tab eventKey="public-templates" title="Public Templates" data-testid="public-templates-tab">
          {/* Public Templates Content */}
        </Tab>
      </Tabs>

      {/* Templates Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {loading ? (
          <div className="text-center py-5">
            <Spinner animation="border" role="status" data-testid="loading-spinner">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        ) : filteredTemplates.length === 0 ? (
          <Card className="text-center py-5" data-testid="no-templates">
            <Card.Body>
              <FileText size={48} className="text-muted mb-3" />
              <h5 className="text-muted">No templates found</h5>
              <p className="text-muted">
                {searchQuery || selectedCategory !== 'all' 
                  ? 'Try adjusting your search or filter criteria'
                  : 'Create your first template to get started!'
                }
              </p>
            </Card.Body>
          </Card>
        ) : (
          <Row>
            {filteredTemplates.map((template) => (
              <Col lg={4} md={6} key={template.id} className="mb-4">
                <motion.div
                  variants={cardVariants}
                  whileHover="hover"
                >
                  <Card className="border-0 shadow-sm h-100" data-testid={`template-card-${template.id}`}>
                    <Card.Header className="bg-white border-0 d-flex justify-content-between align-items-center">
                      <div className="d-flex align-items-center">
                        <h6 className="fw-bold mb-0">{template.name}</h6>
                        {template.isFavorite && <Star size={16} className="text-warning ms-2" />}
                      </div>
                      <div className="dropdown">
                        <Button variant="outline-secondary" size="sm" className="dropdown-toggle" data-bs-toggle="dropdown">
                          <Edit size={16} />
                        </Button>
                        <ul className="dropdown-menu">
                          <li>
                            <a 
                              className="dropdown-item" 
                              href="#" 
                              onClick={() => handleEditTemplate(template)}
                              data-testid={`edit-template-${template.id}`}
                            >
                              <Edit size={14} className="me-2" />Edit
                            </a>
                          </li>
                          <li>
                            <a 
                              className="dropdown-item" 
                              href="#" 
                              onClick={() => handleDuplicateTemplate(template)}
                              data-testid={`duplicate-template-${template.id}`}
                            >
                              <Copy size={14} className="me-2" />Duplicate
                            </a>
                          </li>
                          <li>
                            <a className="dropdown-item" href="#">
                              <Download size={14} className="me-2" />Export
                            </a>
                          </li>
                          <li><hr className="dropdown-divider" /></li>
                          <li>
                            <a 
                              className="dropdown-item text-danger" 
                              href="#" 
                              onClick={() => handleDeleteTemplate(template.id)}
                              data-testid={`delete-template-${template.id}`}
                            >
                              <Trash2 size={14} className="me-2" />Delete
                            </a>
                          </li>
                        </ul>
                      </div>
                    </Card.Header>
                    <Card.Body>
                      <p className="text-muted small mb-3">{template.description}</p>
                      <div className="mb-3">
                        <Badge bg="secondary" className="me-1">{template.category}</Badge>
                        <Badge bg="info" className="me-1">{template.personality}</Badge>
                        {template.isPublic && <Badge bg="success">Public</Badge>}
                      </div>
                      <div className="d-flex flex-wrap gap-1 mb-3">
                        {template.tags.map((tag, index) => (
                          <Badge key={index} bg="light" text="dark" className="small">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <div className="d-flex justify-content-between text-muted small">
                        <span><User size={12} className="me-1" />{template.author}</span>
                        <span><Clock size={12} className="me-1" />{template.updatedAt}</span>
                      </div>
                      <div className="text-muted small">
                        <Bot size={12} className="me-1" />Used {template.usageCount} times
                      </div>
                    </Card.Body>
                  </Card>
                </motion.div>
              </Col>
            ))}
          </Row>
        )}
      </motion.div>

      {/* Create Template Modal */}
      <Modal 
        show={showCreateModal} 
        onHide={() => setShowCreateModal(false)} 
        size="lg"
        data-testid="create-template-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>
            <Plus className="me-2" />
            Create New Template
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Template Name</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter template name"
                    data-testid="template-name-input"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    data-testid="template-category-select"
                  >
                    {categories.slice(1).map(category => (
                      <option key={category} value={category}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe your template"
                data-testid="template-description-input"
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Personality</Form.Label>
                  <Form.Select
                    value={formData.personality}
                    onChange={(e) => setFormData(prev => ({ ...prev, personality: e.target.value }))}
                    data-testid="template-personality-select"
                  >
                    <option value="professional">Professional</option>
                    <option value="friendly">Friendly</option>
                    <option value="casual">Casual</option>
                    <option value="technical">Technical</option>
                    <option value="helpful">Helpful</option>
                    <option value="persuasive">Persuasive</option>
                    <option value="analytical">Analytical</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Tags (comma-separated)</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.tags.join(', ')}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag) 
                    }))}
                    placeholder="e.g., support, customer-service"
                    data-testid="template-tags-input"
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Instructions</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                value={formData.instructions}
                onChange={(e) => setFormData(prev => ({ ...prev, instructions: e.target.value }))}
                placeholder="Enter detailed instructions for the chatbot behavior"
                data-testid="template-instructions-input"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Make this template public"
                checked={formData.isPublic}
                onChange={(e) => setFormData(prev => ({ ...prev, isPublic: e.target.checked }))}
                data-testid="template-public-checkbox"
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary"
            onClick={() => handleSubmitTemplate(false)}
            disabled={!formData.name || !formData.description}
            data-testid="submit-template-btn"
          >
            Create Template
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Edit Template Modal */}
      <Modal 
        show={showEditModal} 
        onHide={() => setShowEditModal(false)} 
        size="lg"
        data-testid="edit-template-modal"
      >
        <Modal.Header closeButton>
          <Modal.Title>
            <Edit className="me-2" />
            Edit Template
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {/* Same form as create modal */}
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Template Name</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter template name"
                    data-testid="edit-template-name-input"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                    data-testid="edit-template-category-select"
                  >
                    {categories.slice(1).map(category => (
                      <option key={category} value={category}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe your template"
                data-testid="edit-template-description-input"
              />
            </Form.Group>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Personality</Form.Label>
                  <Form.Select
                    value={formData.personality}
                    onChange={(e) => setFormData(prev => ({ ...prev, personality: e.target.value }))}
                    data-testid="edit-template-personality-select"
                  >
                    <option value="professional">Professional</option>
                    <option value="friendly">Friendly</option>
                    <option value="casual">Casual</option>
                    <option value="technical">Technical</option>
                    <option value="helpful">Helpful</option>
                    <option value="persuasive">Persuasive</option>
                    <option value="analytical">Analytical</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Tags (comma-separated)</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.tags.join(', ')}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      tags: e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag) 
                    }))}
                    placeholder="e.g., support, customer-service"
                    data-testid="edit-template-tags-input"
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Instructions</Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                value={formData.instructions}
                onChange={(e) => setFormData(prev => ({ ...prev, instructions: e.target.value }))}
                placeholder="Enter detailed instructions for the chatbot behavior"
                data-testid="edit-template-instructions-input"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Make this template public"
                checked={formData.isPublic}
                onChange={(e) => setFormData(prev => ({ ...prev, isPublic: e.target.checked }))}
                data-testid="edit-template-public-checkbox"
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
            onClick={() => handleSubmitTemplate(true)}
            disabled={!formData.name || !formData.description}
            data-testid="update-template-btn"
          >
            Update Template
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Templates;