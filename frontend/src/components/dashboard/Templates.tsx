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
  tools?: TemplateTools[];
  integrations?: TemplateIntegration[];
}

interface TemplateTools {
  id: string;
  name: string;
  type: 'mcp-server' | 'api' | 'webhook' | 'database' | 'calendar' | 'email' | 'file-system' | 'browser' | 'analytics';
  description: string;
  configuration: {
    endpoint?: string;
    capabilities?: string[];
    authentication?: {
      type: string;
      [key: string]: any;
    };
    [key: string]: any;
  };
  isEnabled: boolean;
}

interface TemplateIntegration {
  id: string;
  name: string;
  type: 'api-integration' | 'webhook' | 'oauth' | 'api-key' | 'direct';
  description: string;
  configuration: {
    [key: string]: any;
  };
  isEnabled: boolean;
}

interface TemplateFormData {
  name: string;
  description: string;
  category: string;
  personality: string;
  instructions: string;
  isPublic: boolean;
  tags: string[];
  tools?: TemplateTools[];
  integrations?: TemplateIntegration[];
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
          name: 'Executive Personal Assistant (MCP)',
          description: 'AI assistant with MCP server integration for calendar, email, and file management',
          category: 'PA',
          personality: 'professional',
          instructions: 'You are an executive personal assistant with access to calendar management, email handling, and file organization. Use MCP server tools to efficiently manage schedules, communications, and documents.',
          isPublic: true,
          isFavorite: true,
          createdAt: '2024-01-15',
          updatedAt: '2024-01-20',
          usageCount: 156,
          author: 'Admin',
          tags: ['personal-assistant', 'mcp', 'calendar', 'email', 'productivity'],
          tools: [
            {
              id: 'mcp-calendar',
              name: 'Calendar MCP Server',
              type: 'mcp-server',
              description: 'Manages calendar events, scheduling, and meeting coordination',
              configuration: {
                endpoint: 'mcp://calendar-server',
                capabilities: ['read_calendar', 'create_event', 'update_event', 'delete_event', 'check_availability'],
                authentication: { type: 'oauth2', scope: 'calendar.readwrite' }
              },
              isEnabled: true
            },
            {
              id: 'mcp-email',
              name: 'Email MCP Server',
              type: 'mcp-server',
              description: 'Handles email composition, sending, and inbox management',
              configuration: {
                endpoint: 'mcp://email-server',
                capabilities: ['read_email', 'send_email', 'draft_email', 'organize_inbox'],
                authentication: { type: 'oauth2', scope: 'mail.readwrite' }
              },
              isEnabled: true
            }
          ],
          integrations: [
            {
              id: 'google-workspace',
              name: 'Google Workspace',
              type: 'api-integration',
              description: 'Full Google Workspace integration including Gmail, Calendar, Drive, and Docs',
              configuration: {
                apiKey: '{GOOGLE_API_KEY}',
                clientId: '{GOOGLE_CLIENT_ID}',
                scopes: ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/drive.file']
              },
              isEnabled: true
            }
          ]
        },
        {
          id: 2,
          name: 'Project Manager Pro (MCP)',
          description: 'Advanced project management assistant with task tracking and team coordination via MCP',
          category: 'PM',
          personality: 'analytical',
          instructions: 'You are a project management professional with access to task management, team coordination, and project tracking tools. Use MCP servers to manage projects, track progress, and coordinate team activities.',
          isPublic: true,
          isFavorite: true,
          createdAt: '2024-01-18',
          updatedAt: '2024-01-22',
          usageCount: 89,
          author: 'PMTeam',
          tags: ['project-management', 'mcp', 'task-tracking', 'team-coordination', 'agile'],
          tools: [
            {
              id: 'mcp-tasks',
              name: 'Task Management MCP Server',
              type: 'mcp-server',
              description: 'Manages tasks, milestones, and project timelines',
              configuration: {
                endpoint: 'mcp://task-server',
                capabilities: ['create_task', 'update_status', 'assign_task', 'track_progress', 'generate_reports'],
                authentication: { type: 'api_key', key: '{TASK_API_KEY}' }
              },
              isEnabled: true
            },
            {
              id: 'mcp-slack',
              name: 'Slack Communication MCP Server',
              type: 'mcp-server',
              description: 'Integrates with Slack for team communication and notifications',
              configuration: {
                endpoint: 'mcp://slack-server',
                capabilities: ['send_message', 'create_channel', 'schedule_reminder', 'get_team_status'],
                authentication: { type: 'oauth2', scope: 'chat:write,channels:read' }
              },
              isEnabled: true
            }
          ],
          integrations: [
            {
              id: 'asana-integration',
              name: 'Asana Project Management',
              type: 'api-integration',
              description: 'Integration with Asana for project tracking and task management',
              configuration: {
                apiKey: '{ASANA_API_KEY}',
                workspaceId: '{ASANA_WORKSPACE_ID}',
                features: ['task_creation', 'status_updates', 'team_assignments', 'timeline_management']
              },
              isEnabled: true
            },
            {
              id: 'jira-integration',
              name: 'Jira Issue Tracking',
              type: 'api-integration',
              description: 'Jira integration for issue tracking and sprint management',
              configuration: {
                baseUrl: '{JIRA_BASE_URL}',
                username: '{JIRA_USERNAME}',
                apiToken: '{JIRA_API_TOKEN}',
                projectKey: '{JIRA_PROJECT_KEY}'
              },
              isEnabled: false
            }
          ]
        },
        {
          id: 3,
          name: 'Social Media Manager (MCP)',
          description: 'Social media management assistant with multi-platform posting and analytics',
          category: 'M&S',
          personality: 'creative',
          instructions: 'You are a social media marketing specialist with access to multiple social platforms. Use MCP servers to create content, schedule posts, and analyze engagement across social media channels.',
          isPublic: true,
          isFavorite: false,
          createdAt: '2024-01-20',
          updatedAt: '2024-01-23',
          usageCount: 73,
          author: 'MarketingTeam',
          tags: ['social-media', 'mcp', 'content-creation', 'analytics', 'marketing'],
          tools: [
            {
              id: 'mcp-social-scheduler',
              name: 'Social Media Scheduler MCP Server',
              type: 'mcp-server',
              description: 'Schedules and publishes content across multiple social platforms',
              configuration: {
                endpoint: 'mcp://social-scheduler',
                capabilities: ['schedule_post', 'bulk_upload', 'cross_platform_posting', 'content_optimization'],
                authentication: { type: 'multi_oauth', platforms: ['twitter', 'facebook', 'instagram', 'linkedin'] }
              },
              isEnabled: true
            },
            {
              id: 'mcp-analytics',
              name: 'Social Analytics MCP Server',
              type: 'mcp-server',
              description: 'Analyzes social media performance and engagement metrics',
              configuration: {
                endpoint: 'mcp://analytics-server',
                capabilities: ['engagement_analysis', 'audience_insights', 'performance_reports', 'trend_analysis'],
                authentication: { type: 'api_key', key: '{ANALYTICS_API_KEY}' }
              },
              isEnabled: true
            }
          ],
          integrations: [
            {
              id: 'twitter-api',
              name: 'Twitter/X API',
              type: 'api-integration',
              description: 'Twitter API v2 integration for posting and analytics',
              configuration: {
                bearerToken: '{TWITTER_BEARER_TOKEN}',
                apiKey: '{TWITTER_API_KEY}',
                apiSecret: '{TWITTER_API_SECRET}',
                accessToken: '{TWITTER_ACCESS_TOKEN}'
              },
              isEnabled: true
            },
            {
              id: 'facebook-api',
              name: 'Facebook/Meta API',
              type: 'api-integration',
              description: 'Facebook Graph API for page management and posting',
              configuration: {
                appId: '{FACEBOOK_APP_ID}',
                appSecret: '{FACEBOOK_APP_SECRET}',
                pageAccessToken: '{FACEBOOK_PAGE_TOKEN}',
                permissions: ['pages_manage_posts', 'pages_read_engagement']
              },
              isEnabled: true
            },
            {
              id: 'linkedin-api',
              name: 'LinkedIn API',
              type: 'api-integration',
              description: 'LinkedIn API for professional networking and B2B marketing',
              configuration: {
                clientId: '{LINKEDIN_CLIENT_ID}',
                clientSecret: '{LINKEDIN_CLIENT_SECRET}',
                redirectUri: '{LINKEDIN_REDIRECT_URI}',
                scopes: ['w_member_social', 'r_organization_social']
              },
              isEnabled: false
            }
          ]
        },
        {
          id: 4,
          name: 'Data Analytics Assistant (MCP)',
          description: 'Advanced analytics assistant with database and visualization tool integration',
          category: 'A&D',
          personality: 'analytical',
          instructions: 'You are a data analytics specialist with access to databases, visualization tools, and statistical analysis capabilities. Use MCP servers to query data, generate insights, and create visualizations.',
          isPublic: true,
          isFavorite: true,
          createdAt: '2024-01-16',
          updatedAt: '2024-01-24',
          usageCount: 124,
          author: 'DataTeam',
          tags: ['analytics', 'mcp', 'database', 'visualization', 'insights'],
          tools: [
            {
              id: 'mcp-database',
              name: 'Database Query MCP Server',
              type: 'mcp-server',
              description: 'Executes SQL queries and manages database connections',
              configuration: {
                endpoint: 'mcp://database-server',
                capabilities: ['sql_query', 'schema_analysis', 'data_export', 'performance_optimization'],
                authentication: { type: 'database_credentials', host: '{DB_HOST}', port: '{DB_PORT}' }
              },
              isEnabled: true
            },
            {
              id: 'mcp-visualization',
              name: 'Data Visualization MCP Server',
              type: 'mcp-server',
              description: 'Creates charts, graphs, and interactive visualizations',
              configuration: {
                endpoint: 'mcp://viz-server',
                capabilities: ['chart_generation', 'dashboard_creation', 'interactive_plots', 'export_formats'],
                authentication: { type: 'api_key', key: '{VIZ_API_KEY}' }
              },
              isEnabled: true
            }
          ],
          integrations: [
            {
              id: 'tableau-api',
              name: 'Tableau Server',
              type: 'api-integration',
              description: 'Tableau Server integration for advanced data visualization',
              configuration: {
                serverUrl: '{TABLEAU_SERVER_URL}',
                username: '{TABLEAU_USERNAME}',
                password: '{TABLEAU_PASSWORD}',
                siteId: '{TABLEAU_SITE_ID}'
              },
              isEnabled: false
            },
            {
              id: 'powerbi-api',
              name: 'Power BI',
              type: 'api-integration',
              description: 'Microsoft Power BI integration for business intelligence',
              configuration: {
                clientId: '{POWERBI_CLIENT_ID}',
                clientSecret: '{POWERBI_CLIENT_SECRET}',
                tenantId: '{POWERBI_TENANT_ID}',
                workspaceId: '{POWERBI_WORKSPACE_ID}'
              },
              isEnabled: false
            }
          ]
        },
        {
          id: 5,
          name: 'Customer Support Pro (MCP)',
          description: 'Advanced customer support with CRM and ticketing system integration',
          category: 'support',
          personality: 'helpful',
          instructions: 'You are a customer support specialist with access to CRM systems, ticketing platforms, and knowledge bases. Use MCP servers to resolve customer issues efficiently and maintain service quality.',
          isPublic: true,
          isFavorite: false,
          createdAt: '2024-01-14',
          updatedAt: '2024-01-21',
          usageCount: 201,
          author: 'SupportTeam',
          tags: ['customer-support', 'mcp', 'crm', 'ticketing', 'knowledge-base'],
          tools: [
            {
              id: 'mcp-crm',
              name: 'CRM Integration MCP Server',
              type: 'mcp-server',
              description: 'Manages customer relationships and interaction history',
              configuration: {
                endpoint: 'mcp://crm-server',
                capabilities: ['customer_lookup', 'interaction_history', 'contact_management', 'lead_tracking'],
                authentication: { type: 'oauth2', scope: 'crm.read crm.write' }
              },
              isEnabled: true
            },
            {
              id: 'mcp-tickets',
              name: 'Ticketing System MCP Server',
              type: 'mcp-server',
              description: 'Manages support tickets and escalation workflows',
              configuration: {
                endpoint: 'mcp://tickets-server',
                capabilities: ['create_ticket', 'update_status', 'assign_agent', 'escalate_issue'],
                authentication: { type: 'api_key', key: '{TICKETS_API_KEY}' }
              },
              isEnabled: true
            }
          ],
          integrations: [
            {
              id: 'salesforce-api',
              name: 'Salesforce CRM',
              type: 'api-integration',
              description: 'Salesforce integration for comprehensive customer management',
              configuration: {
                instanceUrl: '{SALESFORCE_INSTANCE_URL}',
                clientId: '{SALESFORCE_CLIENT_ID}',
                clientSecret: '{SALESFORCE_CLIENT_SECRET}',
                username: '{SALESFORCE_USERNAME}'
              },
              isEnabled: true
            },
            {
              id: 'zendesk-api',
              name: 'Zendesk Support',
              type: 'api-integration',
              description: 'Zendesk ticketing system integration',
              configuration: {
                subdomain: '{ZENDESK_SUBDOMAIN}',
                email: '{ZENDESK_EMAIL}',
                apiToken: '{ZENDESK_API_TOKEN}',
                features: ['ticket_management', 'customer_profiles', 'knowledge_base']
              },
              isEnabled: false
            }
          ]
        },
        {
          id: 6,
          name: 'DevOps Assistant (MCP)',
          description: 'DevOps automation assistant with CI/CD and infrastructure management',
          category: 'technical',
          personality: 'technical',
          instructions: 'You are a DevOps engineer with access to CI/CD pipelines, infrastructure monitoring, and deployment tools. Use MCP servers to automate deployments, monitor systems, and manage infrastructure.',
          isPublic: true,
          isFavorite: true,
          createdAt: '2024-01-19',
          updatedAt: '2024-01-25',
          usageCount: 67,
          author: 'DevOpsTeam',
          tags: ['devops', 'mcp', 'ci-cd', 'infrastructure', 'monitoring'],
          tools: [
            {
              id: 'mcp-cicd',
              name: 'CI/CD Pipeline MCP Server',
              type: 'mcp-server',
              description: 'Manages continuous integration and deployment pipelines',
              configuration: {
                endpoint: 'mcp://cicd-server',
                capabilities: ['trigger_build', 'deploy_application', 'rollback_deployment', 'pipeline_status'],
                authentication: { type: 'api_key', key: '{CICD_API_KEY}' }
              },
              isEnabled: true
            },
            {
              id: 'mcp-monitoring',
              name: 'Infrastructure Monitoring MCP Server',
              type: 'mcp-server',
              description: 'Monitors system health and performance metrics',
              configuration: {
                endpoint: 'mcp://monitoring-server',
                capabilities: ['system_metrics', 'alert_management', 'log_analysis', 'performance_reports'],
                authentication: { type: 'bearer_token', token: '{MONITORING_TOKEN}' }
              },
              isEnabled: true
            }
          ],
          integrations: [
            {
              id: 'github-actions',
              name: 'GitHub Actions',
              type: 'api-integration',
              description: 'GitHub Actions integration for CI/CD workflows',
              configuration: {
                token: '{GITHUB_TOKEN}',
                repository: '{GITHUB_REPOSITORY}',
                workflows: ['build', 'test', 'deploy'],
                webhookUrl: '{WEBHOOK_URL}'
              },
              isEnabled: true
            },
            {
              id: 'aws-integration',
              name: 'AWS Services',
              type: 'api-integration',
              description: 'Amazon Web Services integration for cloud infrastructure',
              configuration: {
                accessKeyId: '{AWS_ACCESS_KEY_ID}',
                secretAccessKey: '{AWS_SECRET_ACCESS_KEY}',
                region: '{AWS_REGION}',
                services: ['EC2', 'S3', 'RDS', 'Lambda', 'CloudWatch']
              },
              isEnabled: false
            }
          ]
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

  const categories = ['all', 'PA', 'PM', 'M&S', 'A&D', 'support', 'technical', 'general'];

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