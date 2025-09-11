/**
 * Client Dashboard Component
 * Displays client-specific metrics, billing, and chatbot performance
 */

import React, { useEffect, useState } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Table,
  Badge,
  ProgressBar,
  Modal,
  Form,
  Alert,
  Spinner,
  Tabs,
  Tab
} from 'react-bootstrap';
import { motion } from 'framer-motion';
import {
  User,
  Bot,
  MessageCircle,
  DollarSign,
  TrendingUp,
  Calendar,
  Clock,
  Star,
  Eye,
  Download,
  CreditCard,
  Activity,
  BarChart3,
  PieChart
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { apiService } from '../../services/api';

interface ClientMetrics {
  totalConversations: number;
  totalMessages: number;
  averageRating: number;
  responseTime: number;
  monthlyUsage: Array<{
    month: string;
    conversations: number;
    messages: number;
    cost: number;
  }>;
  chatbotPerformance: Array<{
    chatbotName: string;
    conversations: number;
    rating: number;
    uptime: number;
  }>;
  billingInfo: {
    currentPlan: string;
    monthlySpend: number;
    nextBilling: string;
    usage: {
      conversations: { used: number; limit: number };
      messages: { used: number; limit: number };
      storage: { used: number; limit: number };
    };
  };
}

interface ClientDashboardProps {
  clientId?: number;
}

const ClientDashboard: React.FC<ClientDashboardProps> = ({ clientId }) => {
  const [metrics, setMetrics] = useState<ClientMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [showBillingModal, setShowBillingModal] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadClientMetrics();
  }, [clientId, selectedPeriod]);

  const loadClientMetrics = async () => {
    try {
      setLoading(true);
      setError('');

      if (clientId) {
        const response = await apiService.get(`/api/clients/${clientId}/metrics?period=${selectedPeriod}`);
        setMetrics(response.data);
      } else {
        // Generate mock data for demonstration
        setMetrics(generateMockMetrics());
      }
    } catch (err: any) {
      setError('Failed to load client metrics');
      // Use mock data as fallback
      setMetrics(generateMockMetrics());
    } finally {
      setLoading(false);
    }
  };

  const generateMockMetrics = (): ClientMetrics => ({
    totalConversations: 1247,
    totalMessages: 8934,
    averageRating: 4.6,
    responseTime: 1.8,
    monthlyUsage: [
      { month: 'Jan', conversations: 156, messages: 1203, cost: 89.50 },
      { month: 'Feb', conversations: 189, messages: 1456, cost: 105.20 },
      { month: 'Mar', conversations: 234, messages: 1789, cost: 128.40 },
      { month: 'Apr', conversations: 198, messages: 1534, cost: 110.80 },
      { month: 'May', conversations: 267, messages: 2045, cost: 147.30 },
      { month: 'Jun', conversations: 203, messages: 1607, cost: 115.60 }
    ],
    chatbotPerformance: [
      { chatbotName: 'Customer Support Bot', conversations: 567, rating: 4.7, uptime: 99.2 },
      { chatbotName: 'Sales Assistant', conversations: 423, rating: 4.5, uptime: 98.8 },
      { chatbotName: 'Technical Help', conversations: 257, rating: 4.4, uptime: 97.5 }
    ],
    billingInfo: {
      currentPlan: 'Professional',
      monthlySpend: 147.30,
      nextBilling: '2024-02-01',
      usage: {
        conversations: { used: 1247, limit: 2000 },
        messages: { used: 8934, limit: 15000 },
        storage: { used: 2.3, limit: 10 }
      }
    }
  });

  const getUsagePercentage = (used: number, limit: number) => {
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageVariant = (percentage: number) => {
    if (percentage >= 90) return 'danger';
    if (percentage >= 75) return 'warning';
    return 'success';
  };

  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <Spinner animation="border" variant="primary" />
      </Container>
    );
  }

  if (error && !metrics) {
    return (
      <Container>
        <Alert variant="danger">{error}</Alert>
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
                <User className="me-2" />
                Client Dashboard
              </h2>
              <div className="d-flex gap-2">
                <Button variant="outline-primary" size="sm" onClick={() => setShowBillingModal(true)}>
                  <CreditCard className="me-1" size={16} />
                  Billing
                </Button>
                <Button variant="success" size="sm">
                  <Download className="me-1" size={16} />
                  Export Report
                </Button>
              </div>
            </div>
          </Col>
        </Row>

        {/* Key Metrics Cards */}
        <Row className="mb-4">
          <Col md={3}>
            <motion.div whileHover={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Body>
                  <div className="d-flex align-items-center">
                    <div className="bg-primary bg-opacity-10 p-3 rounded-circle me-3">
                      <MessageCircle className="text-primary" size={24} />
                    </div>
                    <div>
                      <h6 className="text-muted mb-0">Total Conversations</h6>
                      <h3 className="fw-bold mb-0">{metrics?.totalConversations.toLocaleString()}</h3>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
          <Col md={3}>
            <motion.div whileHover={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Body>
                  <div className="d-flex align-items-center">
                    <div className="bg-success bg-opacity-10 p-3 rounded-circle me-3">
                      <Star className="text-success" size={24} />
                    </div>
                    <div>
                      <h6 className="text-muted mb-0">Average Rating</h6>
                      <h3 className="fw-bold mb-0">{metrics?.averageRating}/5</h3>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
          <Col md={3}>
            <motion.div whileHover={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Body>
                  <div className="d-flex align-items-center">
                    <div className="bg-info bg-opacity-10 p-3 rounded-circle me-3">
                      <Clock className="text-info" size={24} />
                    </div>
                    <div>
                      <h6 className="text-muted mb-0">Response Time</h6>
                      <h3 className="fw-bold mb-0">{metrics?.responseTime}s</h3>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
          <Col md={3}>
            <motion.div whileHover={{ scale: 1.02 }} transition={{ duration: 0.2 }}>
              <Card className="border-0 shadow-sm h-100">
                <Card.Body>
                  <div className="d-flex align-items-center">
                    <div className="bg-warning bg-opacity-10 p-3 rounded-circle me-3">
                      <DollarSign className="text-warning" size={24} />
                    </div>
                    <div>
                      <h6 className="text-muted mb-0">Monthly Spend</h6>
                      <h3 className="fw-bold mb-0">${metrics?.billingInfo.monthlySpend}</h3>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>

        {/* Main Content Tabs */}
        <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k || 'overview')} className="mb-4">
          <Tab eventKey="overview" title="Overview">
            <Row>
              {/* Usage Chart */}
              <Col lg={8}>
                <Card className="border-0 shadow-sm h-100">
                  <Card.Header className="bg-white border-0">
                    <h5 className="fw-bold mb-0">Monthly Usage Trends</h5>
                  </Card.Header>
                  <Card.Body>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={metrics?.monthlyUsage}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Area type="monotone" dataKey="conversations" stackId="1" stroke="#8884d8" fill="#8884d8" />
                        <Area type="monotone" dataKey="messages" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </Card.Body>
                </Card>
              </Col>

              {/* Current Usage */}
              <Col lg={4}>
                <Card className="border-0 shadow-sm h-100">
                  <Card.Header className="bg-white border-0">
                    <h5 className="fw-bold mb-0">Current Usage</h5>
                  </Card.Header>
                  <Card.Body>
                    <div className="mb-4">
                      <div className="d-flex justify-content-between mb-2">
                        <span className="fw-medium">Conversations</span>
                        <span className="text-muted">
                          {metrics?.billingInfo.usage.conversations.used} / {metrics?.billingInfo.usage.conversations.limit}
                        </span>
                      </div>
                      <ProgressBar 
                        now={getUsagePercentage(
                          metrics?.billingInfo.usage.conversations.used || 0, 
                          metrics?.billingInfo.usage.conversations.limit || 1
                        )}
                        variant={getUsageVariant(getUsagePercentage(
                          metrics?.billingInfo.usage.conversations.used || 0, 
                          metrics?.billingInfo.usage.conversations.limit || 1
                        ))}
                      />
                    </div>
                    <div className="mb-4">
                      <div className="d-flex justify-content-between mb-2">
                        <span className="fw-medium">Messages</span>
                        <span className="text-muted">
                          {metrics?.billingInfo.usage.messages.used} / {metrics?.billingInfo.usage.messages.limit}
                        </span>
                      </div>
                      <ProgressBar 
                        now={getUsagePercentage(
                          metrics?.billingInfo.usage.messages.used || 0, 
                          metrics?.billingInfo.usage.messages.limit || 1
                        )}
                        variant={getUsageVariant(getUsagePercentage(
                          metrics?.billingInfo.usage.messages.used || 0, 
                          metrics?.billingInfo.usage.messages.limit || 1
                        ))}
                      />
                    </div>
                    <div className="mb-4">
                      <div className="d-flex justify-content-between mb-2">
                        <span className="fw-medium">Storage (GB)</span>
                        <span className="text-muted">
                          {metrics?.billingInfo.usage.storage.used} / {metrics?.billingInfo.usage.storage.limit}
                        </span>
                      </div>
                      <ProgressBar 
                        now={getUsagePercentage(
                          metrics?.billingInfo.usage.storage.used || 0, 
                          metrics?.billingInfo.usage.storage.limit || 1
                        )}
                        variant={getUsageVariant(getUsagePercentage(
                          metrics?.billingInfo.usage.storage.used || 0, 
                          metrics?.billingInfo.usage.storage.limit || 1
                        ))}
                      />
                    </div>
                    <div className="text-center">
                      <Badge bg="info" className="fs-6">
                        {metrics?.billingInfo.currentPlan} Plan
                      </Badge>
                    </div>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Tab>

          <Tab eventKey="performance" title="Performance">
            <Row>
              <Col lg={8}>
                <Card className="border-0 shadow-sm">
                  <Card.Header className="bg-white border-0">
                    <h5 className="fw-bold mb-0">Chatbot Performance</h5>
                  </Card.Header>
                  <Card.Body>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={metrics?.chatbotPerformance}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="chatbotName" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="conversations" fill="#8884d8" />
                        <Bar dataKey="rating" fill="#82ca9d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card.Body>
                </Card>
              </Col>
              <Col lg={4}>
                <Card className="border-0 shadow-sm">
                  <Card.Header className="bg-white border-0">
                    <h5 className="fw-bold mb-0">Performance Summary</h5>
                  </Card.Header>
                  <Card.Body>
                    <Table borderless size="sm">
                      <tbody>
                        {metrics?.chatbotPerformance.map((bot, index) => (
                          <tr key={index}>
                            <td className="fw-medium">{bot.chatbotName}</td>
                            <td>
                              <Badge bg="success">{bot.uptime}% uptime</Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Tab>
        </Tabs>

        {/* Billing Modal */}
        <Modal show={showBillingModal} onHide={() => setShowBillingModal(false)} size="lg">
          <Modal.Header closeButton>
            <Modal.Title>
              <CreditCard className="me-2" />
              Billing Information
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Card className="border-0 bg-light">
                  <Card.Body>
                    <h6 className="fw-bold">Current Plan</h6>
                    <h4 className="text-primary">{metrics?.billingInfo.currentPlan}</h4>
                    <p className="text-muted mb-0">Next billing: {metrics?.billingInfo.nextBilling}</p>
                  </Card.Body>
                </Card>
              </Col>
              <Col md={6}>
                <Card className="border-0 bg-light">
                  <Card.Body>
                    <h6 className="fw-bold">Monthly Spend</h6>
                    <h4 className="text-success">${metrics?.billingInfo.monthlySpend}</h4>
                    <p className="text-muted mb-0">Current month</p>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
            <Row className="mt-4">
              <Col>
                <h6 className="fw-bold mb-3">Cost Breakdown</h6>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={metrics?.monthlyUsage}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [`$${value}`, 'Cost']} />
                    <Line type="monotone" dataKey="cost" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowBillingModal(false)}>
              Close
            </Button>
            <Button variant="primary">
              Upgrade Plan
            </Button>
          </Modal.Footer>
        </Modal>
      </motion.div>
    </Container>
  );
};

export default ClientDashboard;
