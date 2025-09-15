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
  InputGroup,
  Alert,
  Dropdown
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
  Bot,
  CheckCircle,
  XCircle
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
  scope?: 'general' | 'specialized' | 'expert' | 'domain-specific';
  trainingQA?: Array<{ question: string; answer: string }>;
  tools?: TemplateTools[] | {[key: string]: { enabled: boolean; apiKey?: string; config?: any }};
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
  scope: 'general' | 'specialized' | 'expert' | 'domain-specific';
  trainingQA: {
    question: string;
    answer: string;
  }[];
  tools: {
    [key: string]: {
      enabled: boolean;
      apiKey?: string;
      config?: {
        [key: string]: string;
      };
    };
  };
  integrations?: TemplateIntegration[];
}

const Templates: React.FC = () => {
  // State management
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState<number | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [formData, setFormData] = useState<TemplateFormData>({
    name: '',
    description: '',
    category: 'general',
    personality: 'professional',
    instructions: '',
    isPublic: false,
    tags: [],
    scope: 'general',
    trainingQA: [{ question: '', answer: '' }],
    tools: {
      'web-search': { enabled: false, apiKey: '' },
      'email': { enabled: false, apiKey: '' },
      'calendar': { enabled: false, apiKey: '' },
      'file-system': { enabled: false },
      'database': { enabled: false, config: { host: '', port: '', database: '' } },
      'api-client': { enabled: false, apiKey: '' },
      'weather': { enabled: false, apiKey: '' },
      'maps': { enabled: false, apiKey: '' },
      'translation': { enabled: false, apiKey: '' },
      'image-analysis': { enabled: false, apiKey: '' }
    }
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState('my-templates');
  
  // Enhanced UX States
  const [formErrors, setFormErrors] = useState<{[key: string]: string}>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showErrorMessage, setShowErrorMessage] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [formTouched, setFormTouched] = useState<{[key: string]: boolean}>({});
  const [isFormValid, setIsFormValid] = useState(false);

  // Helper function to determine if template is editable by user
  const isTemplateEditable = (template: Template) => {
    // System templates have authors like 'Admin', 'PMTeam', etc.
    // User templates have email addresses as authors or 'User' for duplicated templates
    const systemAuthors = ['Admin', 'PMTeam', 'SalesTeam', 'Support', 'TechTeam', 'DataTeam', 'System'];
    return !systemAuthors.includes(template.author) && (template.author.includes('@') || template.author === 'User');
  };

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
        },
        // Example user-created template
        {
          id: 7,
          name: 'My Custom Sales Assistant',
          description: 'Personalized sales assistant created by user for specific client needs',
          category: 'M&S',
          personality: 'persuasive',
          instructions: 'You are my personal sales assistant helping with lead qualification, follow-ups, and customer engagement. Focus on our specific product offerings and company values.',
          isPublic: false,
          isFavorite: false,
          createdAt: '2024-01-25',
          updatedAt: '2024-01-26',
          usageCount: 12,
          author: 'jc@razorflow-ai.com', // User email - makes this template editable
          tags: ['sales', 'custom', 'leads', 'follow-up'],
          scope: 'specialized',
          trainingQA: [
            { question: 'How do I qualify leads?', answer: 'Focus on budget, authority, need, and timeline (BANT framework).' },
            { question: 'What are our main products?', answer: 'Our main offerings include AI solutions, automation tools, and consulting services.' }
          ],
          tools: {
            'web-search': { enabled: true, apiKey: 'user-api-key' },
            'email': { enabled: true, apiKey: 'user-email-key' },
            'api-client': { enabled: false }
          }
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

  // Form validation functions
  const validateField = (fieldName: string, value: any): string => {
    switch (fieldName) {
      case 'name':
        if (!value || value.trim().length === 0) {
          return 'Template name is required';
        }
        if (value.trim().length < 3) {
          return 'Template name must be at least 3 characters long';
        }
        if (value.trim().length > 100) {
          return 'Template name must be less than 100 characters';
        }
        // Check for duplicate names
        const isDuplicate = templates.some(template => 
          template.name.toLowerCase() === value.trim().toLowerCase() && 
          (!selectedTemplate || template.id !== selectedTemplate.id)
        );
        if (isDuplicate) {
          return 'A template with this name already exists';
        }
        return '';
        
      case 'description':
        if (!value || value.trim().length === 0) {
          return 'Description is required';
        }
        if (value.trim().length < 10) {
          return 'Description must be at least 10 characters long';
        }
        if (value.trim().length > 500) {
          return 'Description must be less than 500 characters';
        }
        return '';
        
      case 'instructions':
        if (!value || value.trim().length === 0) {
          return 'Instructions are required';
        }
        if (value.trim().length < 20) {
          return 'Instructions must be at least 20 characters long';
        }
        if (value.trim().length > 2000) {
          return 'Instructions must be less than 2000 characters';
        }
        return '';
        
      case 'tags':
        if (!Array.isArray(value) || value.length === 0) {
          return 'At least one tag is required';
        }
        if (value.length > 10) {
          return 'Maximum 10 tags allowed';
        }
        const invalidTags = value.filter(tag => !tag || tag.trim().length === 0 || tag.trim().length > 30);
        if (invalidTags.length > 0) {
          return 'Tags must be 1-30 characters long';
        }
        return '';
        
      case 'category':
        const validCategories = categories.slice(1); // Remove 'all'
        if (!validCategories.includes(value)) {
          return 'Please select a valid category';
        }
        return '';

      case 'scope':
        const validScopes = ['general', 'specialized', 'expert', 'domain-specific'];
        if (!validScopes.includes(value)) {
          return 'Please select a valid scope level';
        }
        return '';

      case 'trainingQA':
        if (!Array.isArray(value)) {
          return 'Training Q&A must be an array';
        }
        // Check if all Q&A pairs have both question and answer if they exist
        const invalidPairs = value.filter(qa => 
          (qa.question.trim() && !qa.answer.trim()) || 
          (!qa.question.trim() && qa.answer.trim())
        );
        if (invalidPairs.length > 0) {
          return 'Each Q&A pair must have both question and answer filled';
        }
        return '';
        
      default:
        return '';
    }
  };

  const validateAllFields = (): boolean => {
    const errors: {[key: string]: string} = {};
    
    errors.name = validateField('name', formData.name);
    errors.description = validateField('description', formData.description);
    errors.instructions = validateField('instructions', formData.instructions);
    errors.tags = validateField('tags', formData.tags);
    errors.category = validateField('category', formData.category);
    errors.scope = validateField('scope', formData.scope);
    errors.trainingQA = validateField('trainingQA', formData.trainingQA);
    
    setFormErrors(errors);
    
    const hasErrors = Object.values(errors).some(error => error !== '');
    setIsFormValid(!hasErrors);
    return !hasErrors;
  };

  const handleFieldChange = (fieldName: string, value: any) => {
    // Update form data
    setFormData(prev => ({ ...prev, [fieldName]: value }));
    
    // Mark field as touched
    setFormTouched(prev => ({ ...prev, [fieldName]: true }));
    
    // Validate the specific field if it's been touched
    if (formTouched[fieldName] || Object.keys(formTouched).length > 0) {
      const error = validateField(fieldName, value);
      setFormErrors(prev => ({ ...prev, [fieldName]: error }));
      
      // Update overall form validity
      const updatedErrors = { ...formErrors, [fieldName]: error };
      const hasErrors = Object.values(updatedErrors).some(err => err !== '');
      setIsFormValid(!hasErrors);
    }
  };

  const showMessage = (message: string, isError: boolean = false) => {
    if (isError) {
      setErrorMessage(message);
      setShowErrorMessage(true);
      setTimeout(() => setShowErrorMessage(false), 5000);
    } else {
      setSuccessMessage(message);
      setShowSuccessMessage(true);
      setTimeout(() => setShowSuccessMessage(false), 3000);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category: 'general',
      personality: 'professional',
      instructions: '',
      isPublic: false,
      tags: [],
      scope: 'general',
      trainingQA: [{ question: '', answer: '' }],
      tools: {
        'web-search': { enabled: false, apiKey: '' },
        'email': { enabled: false, apiKey: '' },
        'calendar': { enabled: false, apiKey: '' },
        'file-system': { enabled: false },
        'database': { enabled: false, config: { host: '', port: '', database: '' } },
        'api-client': { enabled: false, apiKey: '' },
        'weather': { enabled: false, apiKey: '' },
        'maps': { enabled: false, apiKey: '' },
        'translation': { enabled: false, apiKey: '' },
        'image-analysis': { enabled: false, apiKey: '' }
      }
    });
    setFormErrors({});
    setFormTouched({});
    setIsFormValid(false);
  };

  // Modal handlers
  const handleCreateTemplate = () => {
    resetForm();
    setShowCreateModal(true);
  };

  const handleEditTemplate = (template: Template) => {
    console.log('🔧 handleEditTemplate called with:', { 
      name: template.name, 
      tools: template.tools 
    });
    
    setSelectedTemplate(template);
    
    // Create default tools object with safe property access
    const defaultTools = {
      'web-search': { enabled: false, apiKey: '' },
      'email': { enabled: false, apiKey: '' },
      'calendar': { enabled: false, apiKey: '' },
      'file-system': { enabled: false },
      'database': { enabled: false, config: { host: '', port: '', database: '' } },
      'api-client': { enabled: false, apiKey: '' },
      'weather': { enabled: false, apiKey: '' },
      'maps': { enabled: false, apiKey: '' },
      'translation': { enabled: false, apiKey: '' },
      'image-analysis': { enabled: false, apiKey: '' }
    };

    // Safely merge existing tools with defaults
    let mergedTools = { ...defaultTools };
    if (template.tools && typeof template.tools === 'object' && !Array.isArray(template.tools)) {
      try {
        // Safely merge each tool, ensuring each has the required properties
        Object.keys(defaultTools).forEach(toolKey => {
          if (template.tools?.[toolKey]) {
            mergedTools[toolKey] = {
              ...defaultTools[toolKey],
              ...template.tools[toolKey]
            };
          }
        });
      } catch (error) {
        console.error('Error processing tools:', error);
        mergedTools = defaultTools;
      }
    }

    setFormData({
      name: template.name,
      description: template.description,
      category: template.category,
      personality: template.personality,
      instructions: template.instructions,
      isPublic: template.isPublic,
      tags: template.tags,
      scope: template.scope || 'general',
      trainingQA: template.trainingQA || [{ question: '', answer: '' }],
      tools: mergedTools
    });
    
    // Reset validation state for editing
    setFormErrors({});
    setFormTouched({});
    setIsFormValid(true); // Assume existing template data is valid
    
    console.log('🔧 About to show edit modal...');
    setShowEditModal(true);
    console.log('🔧 Edit modal state set to true');
  };

  const handleDeleteTemplate = (templateId: number) => {
    setTemplateToDelete(templateId);
    setShowDeleteModal(true);
  };

  const confirmDeleteTemplate = () => {
    if (templateToDelete) {
      setTemplates(prev => prev.filter(t => t.id !== templateToDelete));
      const deletedTemplate = templates.find(t => t.id === templateToDelete);
      showMessage(`Template "${deletedTemplate?.name}" deleted successfully!`, false);
      setShowDeleteModal(false);
      setTemplateToDelete(null);
    }
  };

  const handleSubmitTemplate = async (isEdit: boolean = false) => {
    // Validate all fields before submission
    if (!validateAllFields()) {
      showMessage('Please fix the errors below before submitting', true);
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Simulate API call
      setTimeout(() => {
        if (isEdit && selectedTemplate) {
          setTemplates(prev => prev.map(t => 
            t.id === selectedTemplate.id 
              ? { ...t, ...formData, updatedAt: new Date().toISOString().split('T')[0] }
              : t
          ));
          setShowEditModal(false);
          showMessage(`Template "${formData.name}" updated successfully!`);
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
          showMessage(`Template "${formData.name}" created successfully!`);
        }
        resetForm();
        setIsSubmitting(false);
      }, 500);
    } catch (error) {
      console.error('Error saving template:', error);
      showMessage('Failed to save template. Please try again.', true);
      setIsSubmitting(false);
    }
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
      author: 'user@example.com' // Simulated user email for now - will be replaced with actual user auth later
    };
    setTemplates(prev => [...prev, duplicatedTemplate]);
    showMessage(`Template "${template.name}" duplicated successfully!`, false);
  };

  const handleExportTemplate = (template: Template) => {
    try {
      // Create a clean export object without internal IDs and metadata
      const exportData = {
        name: template.name,
        description: template.description,
        category: template.category,
        personality: template.personality,
        instructions: template.instructions,
        tools: template.tools,
        integrations: template.integrations,
        tags: template.tags,
        scope: template.scope,
        trainingQA: template.trainingQA,
        version: "1.0",
        exportedAt: new Date().toISOString(),
        exportedBy: "Pixel AI Creator"
      };

      // Create and download JSON file
      const dataStr = JSON.stringify(exportData, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = `${template.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_template.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
      
      showMessage(`Template "${template.name}" exported successfully!`, false);
    } catch (error) {
      console.error('Error exporting template:', error);
      showMessage('Failed to export template. Please try again.', true);
    }
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

      {/* Success and Error Messages */}
      {showSuccessMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="mb-3"
        >
          <Alert variant="success" className="d-flex align-items-center">
            <CheckCircle size={20} className="me-2" />
            {successMessage}
          </Alert>
        </motion.div>
      )}

      {showErrorMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="mb-3"
        >
          <Alert variant="danger" className="d-flex align-items-center">
            <XCircle size={20} className="me-2" />
            {errorMessage}
          </Alert>
        </motion.div>
      )}

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
                        {!isTemplateEditable(template) && (
                          <Badge bg="secondary" className="ms-2 small">System</Badge>
                        )}
                      </div>
                      {isTemplateEditable(template) ? (
                        <Dropdown>
                          <Dropdown.Toggle 
                            variant="outline-secondary" 
                            size="sm"
                            data-testid={`template-dropdown-${template.id}`}
                          >
                            <Edit size={16} />
                          </Dropdown.Toggle>
                          <Dropdown.Menu>
                            <Dropdown.Item
                              onClick={() => handleEditTemplate(template)}
                              data-testid={`edit-template-${template.id}`}
                            >
                              <Edit size={14} className="me-2" />Edit
                            </Dropdown.Item>
                            <Dropdown.Item
                              onClick={() => handleDuplicateTemplate(template)}
                              data-testid={`duplicate-template-${template.id}`}
                            >
                              <Copy size={14} className="me-2" />Duplicate
                            </Dropdown.Item>
                            <Dropdown.Item
                              onClick={() => handleExportTemplate(template)}
                              data-testid={`export-template-${template.id}`}
                            >
                              <Download size={14} className="me-2" />Export
                            </Dropdown.Item>
                            <Dropdown.Divider />
                            <Dropdown.Item
                              onClick={() => handleDeleteTemplate(template.id)}
                              data-testid={`delete-template-${template.id}`}
                              className="text-danger"
                            >
                              <Trash2 size={14} className="me-2" />Delete
                            </Dropdown.Item>
                          </Dropdown.Menu>
                        </Dropdown>
                      ) : (
                        <div className="d-flex align-items-center">
                          <Badge bg="info" className="me-2 small">Default Template</Badge>
                          <Button 
                            variant="outline-secondary" 
                            size="sm"
                            onClick={() => handleDuplicateTemplate(template)}
                            data-testid={`duplicate-system-template-${template.id}`}
                            title="Duplicate this system template to create your own editable version"
                          >
                            <Copy size={16} />
                          </Button>
                        </div>
                      )}
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
                  <Form.Label>Template Name <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleFieldChange('name', e.target.value)}
                    placeholder="Enter template name"
                    data-testid="template-name-input"
                    isInvalid={formTouched.name && !!formErrors.name}
                    isValid={formTouched.name && !formErrors.name && formData.name.length > 0}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.name}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Category <span className="text-danger">*</span></Form.Label>
                  <Form.Select
                    value={formData.category}
                    onChange={(e) => handleFieldChange('category', e.target.value)}
                    data-testid="template-category-select"
                    isInvalid={formTouched.category && !!formErrors.category}
                    isValid={formTouched.category && !formErrors.category}
                  >
                    {categories.slice(1).map(category => (
                      <option key={category} value={category}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    {formErrors.category}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Description <span className="text-danger">*</span></Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => handleFieldChange('description', e.target.value)}
                placeholder="Describe your template (minimum 10 characters)"
                data-testid="template-description-input"
                isInvalid={formTouched.description && !!formErrors.description}
                isValid={formTouched.description && !formErrors.description && formData.description.length > 0}
              />
              <Form.Control.Feedback type="invalid">
                {formErrors.description}
              </Form.Control.Feedback>
              <Form.Text className="text-muted">
                {formData.description.length}/500 characters
              </Form.Text>
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
                  <Form.Label>Tags (comma-separated) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.tags.join(', ')}
                    onChange={(e) => {
                      const tagsArray = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
                      handleFieldChange('tags', tagsArray);
                    }}
                    placeholder="e.g., support, customer-service (max 10 tags)"
                    data-testid="template-tags-input"
                    isInvalid={formTouched.tags && !!formErrors.tags}
                    isValid={formTouched.tags && !formErrors.tags && formData.tags.length > 0}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.tags}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    {formData.tags.length}/10 tags
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Instructions <span className="text-danger">*</span></Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                value={formData.instructions}
                onChange={(e) => handleFieldChange('instructions', e.target.value)}
                placeholder="Enter detailed instructions for the chatbot behavior (minimum 20 characters)"
                data-testid="template-instructions-input"
                isInvalid={formTouched.instructions && !!formErrors.instructions}
                isValid={formTouched.instructions && !formErrors.instructions && formData.instructions.length > 0}
              />
              <Form.Control.Feedback type="invalid">
                {formErrors.instructions}
              </Form.Control.Feedback>
              <Form.Text className="text-muted">
                {formData.instructions.length}/2000 characters
              </Form.Text>
            </Form.Group>

            {/* Scope & Training Section */}
            <Card className="mb-4">
              <Card.Header>
                <h6 className="mb-0">
                  <Bot className="me-2" size={16} />
                  Scope & Training
                </h6>
              </Card.Header>
              <Card.Body>
                <Form.Group className="mb-3">
                  <Form.Label>AI Scope Level</Form.Label>
                  <Form.Select
                    value={formData.scope}
                    onChange={(e) => setFormData(prev => ({ ...prev, scope: e.target.value as any }))}
                    data-testid="template-scope-select"
                  >
                    <option value="general">General Purpose - Broad knowledge across domains</option>
                    <option value="specialized">Specialized - Focused on specific industry/field</option>
                    <option value="expert">Expert Level - Deep domain expertise required</option>
                    <option value="domain-specific">Domain Specific - Highly specialized knowledge</option>
                  </Form.Select>
                </Form.Group>

                <Form.Label>Training Q&A Pairs</Form.Label>
                <Form.Text className="text-muted d-block mb-2">
                  Add question-answer pairs to train the AI on specific responses and behaviors.
                </Form.Text>
                
                {formData.trainingQA.map((qa, index) => (
                  <Card key={index} className="mb-3 border-light">
                    <Card.Body className="py-2">
                      <Row>
                        <Col md={5}>
                          <Form.Group className="mb-2">
                            <Form.Label className="small">Question {index + 1}</Form.Label>
                            <Form.Control
                              type="text"
                              value={qa.question}
                              onChange={(e) => {
                                const newQA = [...formData.trainingQA];
                                newQA[index].question = e.target.value;
                                setFormData(prev => ({ ...prev, trainingQA: newQA }));
                              }}
                              placeholder="Enter training question..."
                              data-testid={`training-question-${index}`}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={5}>
                          <Form.Group className="mb-2">
                            <Form.Label className="small">Answer {index + 1}</Form.Label>
                            <Form.Control
                              as="textarea"
                              rows={2}
                              value={qa.answer}
                              onChange={(e) => {
                                const newQA = [...formData.trainingQA];
                                newQA[index].answer = e.target.value;
                                setFormData(prev => ({ ...prev, trainingQA: newQA }));
                              }}
                              placeholder="Enter expected answer..."
                              data-testid={`training-answer-${index}`}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={2} className="d-flex align-items-end">
                          {formData.trainingQA.length > 1 && (
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => {
                                const newQA = formData.trainingQA.filter((_, i) => i !== index);
                                setFormData(prev => ({ ...prev, trainingQA: newQA }));
                              }}
                              className="mb-2"
                            >
                              <Trash2 size={14} />
                            </Button>
                          )}
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                ))}
                
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => {
                    setFormData(prev => ({
                      ...prev,
                      trainingQA: [...prev.trainingQA, { question: '', answer: '' }]
                    }));
                  }}
                  className="mb-2"
                >
                  <Plus size={14} className="me-1" />
                  Add Q&A Pair
                </Button>
              </Card.Body>
            </Card>

            {/* Tools Selection Section */}
            <Card className="mb-4">
              <Card.Header>
                <h6 className="mb-0">
                  <FileText className="me-2" size={16} />
                  Tools & Integrations
                </h6>
              </Card.Header>
              <Card.Body>
                <Form.Text className="text-muted d-block mb-3">
                  Enable tools and provide API keys for enhanced AI capabilities.
                </Form.Text>

                <Row>
                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Web Search</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['web-search'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'web-search': { ...prev.tools['web-search'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-web-search-toggle"
                        />
                      </div>
                      {formData.tools['web-search'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Search API Key"
                          value={formData.tools['web-search'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'web-search': { ...prev.tools['web-search'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="tool-web-search-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Email Integration</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['email'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'email': { ...prev.tools['email'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-email-toggle"
                        />
                      </div>
                      {formData.tools['email'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Email Service API Key"
                          value={formData.tools['email'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'email': { ...prev.tools['email'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="tool-email-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Calendar Management</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['calendar'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'calendar': { ...prev.tools['calendar'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-calendar-toggle"
                        />
                      </div>
                      {formData.tools['calendar'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Calendar API Key (Google/Outlook)"
                          value={formData.tools['calendar'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'calendar': { ...prev.tools['calendar'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="tool-calendar-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>File System Access</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['file-system'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'file-system': { ...prev.tools['file-system'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-file-system-toggle"
                        />
                      </div>
                      <small className="text-muted">Read/write access to local files</small>
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Database Access</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['database'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'database': { ...prev.tools['database'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-database-toggle"
                        />
                      </div>
                      {formData.tools['database'].enabled && (
                        <div>
                          <Form.Control
                            type="text"
                            placeholder="Database Host"
                            value={formData.tools['database'].config?.host || ''}
                            onChange={(e) => {
                              setFormData(prev => ({
                                ...prev,
                                tools: {
                                  ...prev.tools,
                                  'database': {
                                    ...prev.tools['database'],
                                    config: { ...prev.tools['database'].config, host: e.target.value }
                                  }
                                }
                              }));
                            }}
                            className="mb-2"
                            data-testid="tool-database-host"
                          />
                          <Row>
                            <Col md={6}>
                              <Form.Control
                                type="text"
                                placeholder="Port"
                                value={formData.tools['database'].config?.port || ''}
                                onChange={(e) => {
                                  setFormData(prev => ({
                                    ...prev,
                                    tools: {
                                      ...prev.tools,
                                      'database': {
                                        ...prev.tools['database'],
                                        config: { ...prev.tools['database'].config, port: e.target.value }
                                      }
                                    }
                                  }));
                                }}
                                data-testid="tool-database-port"
                              />
                            </Col>
                            <Col md={6}>
                              <Form.Control
                                type="text"
                                placeholder="Database Name"
                                value={formData.tools['database'].config?.database || ''}
                                onChange={(e) => {
                                  setFormData(prev => ({
                                    ...prev,
                                    tools: {
                                      ...prev.tools,
                                      'database': {
                                        ...prev.tools['database'],
                                        config: { ...prev.tools['database'].config, database: e.target.value }
                                      }
                                    }
                                  }));
                                }}
                                data-testid="tool-database-name"
                              />
                            </Col>
                          </Row>
                        </div>
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>API Client</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['api-client'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'api-client': { ...prev.tools['api-client'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-api-client-toggle"
                        />
                      </div>
                      {formData.tools['api-client'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="API Base URL or Key"
                          value={formData.tools['api-client'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'api-client': { ...prev.tools['api-client'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="tool-api-client-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Weather Service</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['weather'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'weather': { ...prev.tools['weather'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-weather-toggle"
                        />
                      </div>
                      {formData.tools['weather'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Weather API Key"
                          value={formData.tools['weather'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'weather': { ...prev.tools['weather'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="tool-weather-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Maps & Location</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['maps'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'maps': { ...prev.tools['maps'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-maps-toggle"
                        />
                      </div>
                      {formData.tools['maps'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Maps API Key (Google Maps)"
                          value={formData.tools['maps'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'maps': { ...prev.tools['maps'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="tool-maps-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Translation Service</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['translation'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'translation': { ...prev.tools['translation'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-translation-toggle"
                        />
                      </div>
                      {formData.tools['translation'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Translation API Key"
                          value={formData.tools['translation'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'translation': { ...prev.tools['translation'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="tool-translation-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Image Analysis</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['image-analysis'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'image-analysis': { ...prev.tools['image-analysis'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="tool-image-analysis-toggle"
                        />
                      </div>
                      {formData.tools['image-analysis'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Vision API Key"
                          value={formData.tools['image-analysis'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'image-analysis': { ...prev.tools['image-analysis'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="tool-image-analysis-api-key"
                        />
                      )}
                    </div>
                  </Col>
                </Row>
              </Card.Body>
            </Card>

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
            disabled={isSubmitting || !isFormValid}
            data-testid="submit-template-btn"
          >
            {isSubmitting ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" className="me-2" />
                Creating...
              </>
            ) : (
              'Create Template'
            )}
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
                  <Form.Label>Template Name <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleFieldChange('name', e.target.value)}
                    placeholder="Enter template name"
                    data-testid="edit-template-name-input"
                    isInvalid={formTouched.name && !!formErrors.name}
                    isValid={formTouched.name && !formErrors.name && formData.name.length > 0}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.name}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Category <span className="text-danger">*</span></Form.Label>
                  <Form.Select
                    value={formData.category}
                    onChange={(e) => handleFieldChange('category', e.target.value)}
                    data-testid="edit-template-category-select"
                    isInvalid={formTouched.category && !!formErrors.category}
                    isValid={formTouched.category && !formErrors.category}
                  >
                    {categories.slice(1).map(category => (
                      <option key={category} value={category}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    {formErrors.category}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Description <span className="text-danger">*</span></Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => handleFieldChange('description', e.target.value)}
                placeholder="Describe your template (minimum 10 characters)"
                data-testid="edit-template-description-input"
                isInvalid={formTouched.description && !!formErrors.description}
                isValid={formTouched.description && !formErrors.description && formData.description.length > 0}
              />
              <Form.Control.Feedback type="invalid">
                {formErrors.description}
              </Form.Control.Feedback>
              <Form.Text className="text-muted">
                {formData.description.length}/500 characters
              </Form.Text>
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
                  <Form.Label>Tags (comma-separated) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.tags.join(', ')}
                    onChange={(e) => {
                      const tagsArray = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
                      handleFieldChange('tags', tagsArray);
                    }}
                    placeholder="e.g., support, customer-service (max 10 tags)"
                    data-testid="edit-template-tags-input"
                    isInvalid={formTouched.tags && !!formErrors.tags}
                    isValid={formTouched.tags && !formErrors.tags && formData.tags.length > 0}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.tags}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    {formData.tags.length}/10 tags
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Instructions <span className="text-danger">*</span></Form.Label>
              <Form.Control
                as="textarea"
                rows={5}
                value={formData.instructions}
                onChange={(e) => handleFieldChange('instructions', e.target.value)}
                placeholder="Enter detailed instructions for the chatbot behavior (minimum 20 characters)"
                data-testid="edit-template-instructions-input"
                isInvalid={formTouched.instructions && !!formErrors.instructions}
                isValid={formTouched.instructions && !formErrors.instructions && formData.instructions.length > 0}
              />
              <Form.Control.Feedback type="invalid">
                {formErrors.instructions}
              </Form.Control.Feedback>
              <Form.Text className="text-muted">
                {formData.instructions.length}/2000 characters
              </Form.Text>
            </Form.Group>

            {/* Scope & Training Section */}
            <Card className="mb-4">
              <Card.Header>
                <h6 className="mb-0">
                  <Bot className="me-2" size={16} />
                  Scope & Training
                </h6>
              </Card.Header>
              <Card.Body>
                <Form.Group className="mb-3">
                  <Form.Label>AI Scope Level</Form.Label>
                  <Form.Select
                    value={formData.scope}
                    onChange={(e) => setFormData(prev => ({ ...prev, scope: e.target.value as any }))}
                    data-testid="edit-template-scope-select"
                  >
                    <option value="general">General Purpose - Broad knowledge across domains</option>
                    <option value="specialized">Specialized - Focused on specific industry/field</option>
                    <option value="expert">Expert Level - Deep domain expertise required</option>
                    <option value="domain-specific">Domain Specific - Highly specialized knowledge</option>
                  </Form.Select>
                </Form.Group>

                <Form.Label>Training Q&A Pairs</Form.Label>
                <Form.Text className="text-muted d-block mb-2">
                  Add question-answer pairs to train the AI on specific responses and behaviors.
                </Form.Text>
                
                {formData.trainingQA.map((qa, index) => (
                  <Card key={index} className="mb-3 border-light">
                    <Card.Body className="py-2">
                      <Row>
                        <Col md={5}>
                          <Form.Group className="mb-2">
                            <Form.Label className="small">Question {index + 1}</Form.Label>
                            <Form.Control
                              type="text"
                              value={qa.question}
                              onChange={(e) => {
                                const newQA = [...formData.trainingQA];
                                newQA[index].question = e.target.value;
                                setFormData(prev => ({ ...prev, trainingQA: newQA }));
                              }}
                              placeholder="Enter training question..."
                              data-testid={`edit-training-question-${index}`}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={5}>
                          <Form.Group className="mb-2">
                            <Form.Label className="small">Answer {index + 1}</Form.Label>
                            <Form.Control
                              as="textarea"
                              rows={2}
                              value={qa.answer}
                              onChange={(e) => {
                                const newQA = [...formData.trainingQA];
                                newQA[index].answer = e.target.value;
                                setFormData(prev => ({ ...prev, trainingQA: newQA }));
                              }}
                              placeholder="Enter expected answer..."
                              data-testid={`edit-training-answer-${index}`}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={2} className="d-flex align-items-end">
                          {formData.trainingQA.length > 1 && (
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => {
                                const newQA = formData.trainingQA.filter((_, i) => i !== index);
                                setFormData(prev => ({ ...prev, trainingQA: newQA }));
                              }}
                              className="mb-2"
                            >
                              <Trash2 size={14} />
                            </Button>
                          )}
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                ))}
                
                <Button
                  variant="outline-primary"
                  size="sm"
                  onClick={() => {
                    setFormData(prev => ({
                      ...prev,
                      trainingQA: [...prev.trainingQA, { question: '', answer: '' }]
                    }));
                  }}
                  className="mb-2"
                >
                  <Plus size={14} className="me-1" />
                  Add Q&A Pair
                </Button>
              </Card.Body>
            </Card>

            {/* Tools Selection Section */}
            <Card className="mb-4">
              <Card.Header>
                <h6 className="mb-0">
                  <FileText className="me-2" size={16} />
                  Tools & Integrations
                </h6>
              </Card.Header>
              <Card.Body>
                <Form.Text className="text-muted d-block mb-3">
                  Enable tools and provide API keys for enhanced AI capabilities.
                </Form.Text>

                <Row>
                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Web Search</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['web-search'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'web-search': { ...prev.tools['web-search'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-web-search-toggle"
                        />
                      </div>
                      {formData.tools['web-search'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Search API Key"
                          value={formData.tools['web-search'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'web-search': { ...prev.tools['web-search'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="edit-tool-web-search-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Email Integration</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['email'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'email': { ...prev.tools['email'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-email-toggle"
                        />
                      </div>
                      {formData.tools['email'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Email Service API Key"
                          value={formData.tools['email'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'email': { ...prev.tools['email'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="edit-tool-email-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Calendar Management</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['calendar'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'calendar': { ...prev.tools['calendar'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-calendar-toggle"
                        />
                      </div>
                      {formData.tools['calendar'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Calendar API Key (Google/Outlook)"
                          value={formData.tools['calendar'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'calendar': { ...prev.tools['calendar'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="edit-tool-calendar-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>File System Access</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['file-system'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'file-system': { ...prev.tools['file-system'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-file-system-toggle"
                        />
                      </div>
                      <small className="text-muted">Read/write access to local files</small>
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Database Access</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['database'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'database': { ...prev.tools['database'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-database-toggle"
                        />
                      </div>
                      {formData.tools['database'].enabled && (
                        <div>
                          <Form.Control
                            type="text"
                            placeholder="Database Host"
                            value={formData.tools['database'].config?.host || ''}
                            onChange={(e) => {
                              setFormData(prev => ({
                                ...prev,
                                tools: {
                                  ...prev.tools,
                                  'database': {
                                    ...prev.tools['database'],
                                    config: { ...prev.tools['database'].config, host: e.target.value }
                                  }
                                }
                              }));
                            }}
                            className="mb-2"
                            data-testid="edit-tool-database-host"
                          />
                          <Row>
                            <Col md={6}>
                              <Form.Control
                                type="text"
                                placeholder="Port"
                                value={formData.tools['database'].config?.port || ''}
                                onChange={(e) => {
                                  setFormData(prev => ({
                                    ...prev,
                                    tools: {
                                      ...prev.tools,
                                      'database': {
                                        ...prev.tools['database'],
                                        config: { ...prev.tools['database'].config, port: e.target.value }
                                      }
                                    }
                                  }));
                                }}
                                data-testid="edit-tool-database-port"
                              />
                            </Col>
                            <Col md={6}>
                              <Form.Control
                                type="text"
                                placeholder="Database Name"
                                value={formData.tools['database'].config?.database || ''}
                                onChange={(e) => {
                                  setFormData(prev => ({
                                    ...prev,
                                    tools: {
                                      ...prev.tools,
                                      'database': {
                                        ...prev.tools['database'],
                                        config: { ...prev.tools['database'].config, database: e.target.value }
                                      }
                                    }
                                  }));
                                }}
                                data-testid="edit-tool-database-name"
                              />
                            </Col>
                          </Row>
                        </div>
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>API Client</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['api-client'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'api-client': { ...prev.tools['api-client'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-api-client-toggle"
                        />
                      </div>
                      {formData.tools['api-client'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="API Base URL or Key"
                          value={formData.tools['api-client'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'api-client': { ...prev.tools['api-client'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="edit-tool-api-client-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Weather Service</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['weather'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'weather': { ...prev.tools['weather'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-weather-toggle"
                        />
                      </div>
                      {formData.tools['weather'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Weather API Key"
                          value={formData.tools['weather'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'weather': { ...prev.tools['weather'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="edit-tool-weather-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Maps & Location</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['maps'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'maps': { ...prev.tools['maps'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-maps-toggle"
                        />
                      </div>
                      {formData.tools['maps'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Maps API Key (Google Maps)"
                          value={formData.tools['maps'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'maps': { ...prev.tools['maps'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="edit-tool-maps-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Translation Service</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['translation'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'translation': { ...prev.tools['translation'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-translation-toggle"
                        />
                      </div>
                      {formData.tools['translation'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Translation API Key"
                          value={formData.tools['translation'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'translation': { ...prev.tools['translation'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="edit-tool-translation-api-key"
                        />
                      )}
                    </div>
                  </Col>

                  <Col md={6}>
                    <div className="tool-item mb-3 p-3 border rounded">
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <strong>Image Analysis</strong>
                        <Form.Check
                          type="switch"
                          checked={formData.tools['image-analysis'].enabled}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'image-analysis': { ...prev.tools['image-analysis'], enabled: e.target.checked }
                              }
                            }));
                          }}
                          data-testid="edit-tool-image-analysis-toggle"
                        />
                      </div>
                      {formData.tools['image-analysis'].enabled && (
                        <Form.Control
                          type="text"
                          placeholder="Vision API Key"
                          value={formData.tools['image-analysis'].apiKey || ''}
                          onChange={(e) => {
                            setFormData(prev => ({
                              ...prev,
                              tools: {
                                ...prev.tools,
                                'image-analysis': { ...prev.tools['image-analysis'], apiKey: e.target.value }
                              }
                            }));
                          }}
                          data-testid="edit-tool-image-analysis-api-key"
                        />
                      )}
                    </div>
                  </Col>
                </Row>
              </Card.Body>
            </Card>

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
            disabled={isSubmitting || !isFormValid}
            data-testid="update-template-btn"
          >
            {isSubmitting ? (
              <>
                <Spinner as="span" animation="border" size="sm" role="status" className="me-2" />
                Updating...
              </>
            ) : (
              'Update Template'
            )}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal 
        show={showDeleteModal} 
        onHide={() => setShowDeleteModal(false)}
        data-testid="delete-confirmation-modal"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>
            <Trash2 className="me-2 text-danger" />
            Confirm Delete
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to delete this template?</p>
          {templateToDelete && (
            <div className="alert alert-warning">
              <strong>Template:</strong> {templates.find(t => t.id === templateToDelete)?.name}
            </div>
          )}
          <p className="text-muted small">This action cannot be undone.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button 
            variant="secondary" 
            onClick={() => setShowDeleteModal(false)}
            data-testid="cancel-delete-btn"
          >
            Cancel
          </Button>
          <Button 
            variant="danger"
            onClick={confirmDeleteTemplate}
            data-testid="confirm-delete-btn"
          >
            <Trash2 size={16} className="me-2" />
            Delete Template
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Templates;