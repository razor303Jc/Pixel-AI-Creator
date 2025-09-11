/**
 * Analytics Dashboard Component
 * Displays conversation analytics, performance metrics, and client insights
 */

import React, { useEffect, useState } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Spinner,
  Alert,
  ProgressBar,
  Dropdown,
  ButtonGroup
} from 'react-bootstrap';
import { motion } from 'framer-motion';
import {
  BarChart,
  LineChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';
import {
  TrendingUp,
  MessageCircle,
  Users,
  Clock,
  Target,
  Activity,
  Calendar,
  Download,
  Filter
} from 'lucide-react';
import { apiService } from '../../services/api';

interface AnalyticsData {
  conversationVolume: Array<{
    date: string;
    conversations: number;
    messages: number;
  }>;
  responseMetrics: {
    averageResponseTime: number;
    successRate: number;
    totalConversations: number;
    totalMessages: number;
  };
  clientSatisfaction: Array<{
    rating: number;
    count: number;
    percentage: number;
  }>;
  topTopics: Array<{
    topic: string;
    count: number;
    sentiment: 'positive' | 'neutral' | 'negative';
  }>;
  chatbotPerformance: Array<{
    chatbotName: string;
    conversations: number;
    avgRating: number;
    responseTime: number;
  }>;
}

const AnalyticsDashboard: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Simulate API calls for analytics data
      const [volumeData, metricsData, satisfactionData, topicsData, performanceData] = 
        await Promise.all([
          apiService.get(`/api/analytics/conversation-volume?range=${timeRange}`),
          apiService.get(`/api/analytics/response-metrics?range=${timeRange}`),
          apiService.get(`/api/analytics/satisfaction?range=${timeRange}`),
          apiService.get(`/api/analytics/topics?range=${timeRange}`),
          apiService.get(`/api/analytics/chatbot-performance?range=${timeRange}`)
        ]);

      setAnalyticsData({
        conversationVolume: volumeData.data || generateMockVolumeData(),
        responseMetrics: metricsData.data || generateMockMetrics(),
        clientSatisfaction: satisfactionData.data || generateMockSatisfaction(),
        topTopics: topicsData.data || generateMockTopics(),
        chatbotPerformance: performanceData.data || generateMockPerformance()
      });
    } catch (err: any) {
      // Generate mock data for demonstration
      setAnalyticsData({
        conversationVolume: generateMockVolumeData(),
        responseMetrics: generateMockMetrics(),
        clientSatisfaction: generateMockSatisfaction(),
        topTopics: generateMockTopics(),
        chatbotPerformance: generateMockPerformance()
      });
    } finally {
      setLoading(false);
    }
  };

  const generateMockVolumeData = () => [
    { date: '2024-01-01', conversations: 45, messages: 234 },
    { date: '2024-01-02', conversations: 52, messages: 287 },
    { date: '2024-01-03', conversations: 38, messages: 198 },
    { date: '2024-01-04', conversations: 67, messages: 345 },
    { date: '2024-01-05', conversations: 71, messages: 389 },
    { date: '2024-01-06', conversations: 58, messages: 312 },
    { date: '2024-01-07', conversations: 63, messages: 334 }
  ];

  const generateMockMetrics = () => ({
    averageResponseTime: 1.8,
    successRate: 94.2,
    totalConversations: 394,
    totalMessages: 2099
  });

  const generateMockSatisfaction = () => [
    { rating: 5, count: 156, percentage: 65.3 },
    { rating: 4, count: 52, percentage: 21.8 },
    { rating: 3, count: 19, percentage: 7.9 },
    { rating: 2, count: 8, percentage: 3.3 },
    { rating: 1, count: 4, percentage: 1.7 }
  ];

  const generateMockTopics = () => [
    { topic: 'Product Information', count: 89, sentiment: 'positive' as const },
    { topic: 'Order Support', count: 67, sentiment: 'neutral' as const },
    { topic: 'Technical Issues', count: 45, sentiment: 'negative' as const },
    { topic: 'Billing Questions', count: 34, sentiment: 'neutral' as const },
    { topic: 'Feature Requests', count: 28, sentiment: 'positive' as const }
  ];

  const generateMockPerformance = () => [
    { chatbotName: 'Customer Support Bot', conversations: 156, avgRating: 4.6, responseTime: 1.2 },
    { chatbotName: 'Sales Assistant', conversations: 123, avgRating: 4.4, responseTime: 1.5 },
    { chatbotName: 'Tech Help Bot', conversations: 89, avgRating: 4.2, responseTime: 2.1 },
    { chatbotName: 'Order Tracker', conversations: 67, avgRating: 4.7, responseTime: 0.9 }
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <Spinner animation="border" variant="primary" />
      </Container>
    );
  }

  if (error) {
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
                <Activity className="me-2" />
                Analytics Dashboard
              </h2>
              <div className="d-flex gap-2">
                <Dropdown as={ButtonGroup}>
                  <Button variant="outline-primary" size="sm">
                    <Calendar className="me-1" size={16} />
                    {timeRange === '7d' ? 'Last 7 days' : 
                     timeRange === '30d' ? 'Last 30 days' : 'Last 90 days'}
                  </Button>
                  <Dropdown.Toggle split variant="outline-primary" size="sm" />
                  <Dropdown.Menu>
                    <Dropdown.Item onClick={() => setTimeRange('7d')}>Last 7 days</Dropdown.Item>
                    <Dropdown.Item onClick={() => setTimeRange('30d')}>Last 30 days</Dropdown.Item>
                    <Dropdown.Item onClick={() => setTimeRange('90d')}>Last 90 days</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
                <Button variant="success" size="sm">
                  <Download className="me-1" size={16} />
                  Export
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
                      <h3 className="fw-bold mb-0">{analyticsData?.responseMetrics.totalConversations}</h3>
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
                      <Target className="text-success" size={24} />
                    </div>
                    <div>
                      <h6 className="text-muted mb-0">Success Rate</h6>
                      <h3 className="fw-bold mb-0">{analyticsData?.responseMetrics.successRate}%</h3>
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
                      <h6 className="text-muted mb-0">Avg Response Time</h6>
                      <h3 className="fw-bold mb-0">{analyticsData?.responseMetrics.averageResponseTime}s</h3>
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
                      <TrendingUp className="text-warning" size={24} />
                    </div>
                    <div>
                      <h6 className="text-muted mb-0">Total Messages</h6>
                      <h3 className="fw-bold mb-0">{analyticsData?.responseMetrics.totalMessages}</h3>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>

        {/* Charts Section */}
        <Row className="mb-4">
          {/* Conversation Volume Chart */}
          <Col lg={8}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="bg-white border-0">
                <h5 className="fw-bold mb-0">Conversation Volume</h5>
              </Card.Header>
              <Card.Body>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={analyticsData?.conversationVolume}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
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

          {/* Client Satisfaction Chart */}
          <Col lg={4}>
            <Card className="border-0 shadow-sm h-100">
              <Card.Header className="bg-white border-0">
                <h5 className="fw-bold mb-0">Client Satisfaction</h5>
              </Card.Header>
              <Card.Body>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analyticsData?.clientSatisfaction}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry: any) => `${entry.rating}★ (${entry.percentage}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {analyticsData?.clientSatisfaction.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Bottom Section */}
        <Row>
          {/* Chatbot Performance */}
          <Col lg={8}>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0">
                <h5 className="fw-bold mb-0">Chatbot Performance</h5>
              </Card.Header>
              <Card.Body>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analyticsData?.chatbotPerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="chatbotName" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="conversations" fill="#8884d8" />
                    <Bar dataKey="avgRating" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </Card.Body>
            </Card>
          </Col>

          {/* Top Topics */}
          <Col lg={4}>
            <Card className="border-0 shadow-sm">
              <Card.Header className="bg-white border-0">
                <h5 className="fw-bold mb-0">Top Topics</h5>
              </Card.Header>
              <Card.Body>
                {analyticsData?.topTopics.map((topic, index) => (
                  <div key={index} className="mb-3">
                    <div className="d-flex justify-content-between align-items-center mb-1">
                      <span className="fw-medium">{topic.topic}</span>
                      <span className={`badge bg-${topic.sentiment === 'positive' ? 'success' : 
                                                   topic.sentiment === 'negative' ? 'danger' : 'secondary'}`}>
                        {topic.count}
                      </span>
                    </div>
                    <ProgressBar 
                      now={topic.count} 
                      max={100} 
                      variant={topic.sentiment === 'positive' ? 'success' : 
                              topic.sentiment === 'negative' ? 'danger' : 'info'}
                    />
                  </div>
                ))}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </motion.div>
    </Container>
  );
};

export default AnalyticsDashboard;
