/**
 * Dashboard Demo Page
 * Demonstrates the enhanced dashboard with editable cards functionality
 */

import React from 'react';
import { Container, Row, Col, Card, Badge } from 'react-bootstrap';
import { motion } from 'framer-motion';
import EnhancedClientDashboard from '../components/dashboard/EnhancedClientDashboard';

const DashboardDemo: React.FC = () => {
  return (
    <div className="min-vh-100 bg-light">
      {/* Demo Header */}
      <Container fluid className="bg-white shadow-sm border-bottom">
        <Container className="py-4">
          <Row>
            <Col>
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <h1 className="display-5 fw-bold text-dark mb-2">
                  Dashboard Components Demo
                </h1>
                <p className="lead text-muted mb-3">
                  Interactive dashboard with editable cards, drag-and-drop layout management, and real-time data updates
                </p>
                <div className="d-flex gap-2">
                  <Badge bg="primary" className="px-3 py-2">
                    ✨ Editable Cards
                  </Badge>
                  <Badge bg="success" className="px-3 py-2">
                    🎯 Drag & Drop Layout
                  </Badge>
                  <Badge bg="info" className="px-3 py-2">
                    📊 Real-time Metrics
                  </Badge>
                  <Badge bg="warning" className="px-3 py-2">
                    💾 Save/Load Layouts
                  </Badge>
                </div>
              </motion.div>
            </Col>
          </Row>
        </Container>
      </Container>

      {/* Demo Features */}
      <Container className="py-4">
        <Row className="mb-4">
          <Col>
            <Card className="border-0 shadow-sm">
              <Card.Body>
                <h5 className="fw-bold mb-3">🚀 Features Demonstrated</h5>
                <Row>
                  <Col md={3}>
                    <h6 className="text-primary">Card Editing</h6>
                    <ul className="small text-muted">
                      <li>Inline value editing</li>
                      <li>Title customization</li>
                      <li>Input validation</li>
                      <li>Real-time updates</li>
                    </ul>
                  </Col>
                  <Col md={3}>
                    <h6 className="text-success">Layout Management</h6>
                    <ul className="small text-muted">
                      <li>Drag & drop positioning</li>
                      <li>Resizable cards</li>
                      <li>Grid-based layout</li>
                      <li>Responsive design</li>
                    </ul>
                  </Col>
                  <Col md={3}>
                    <h6 className="text-info">Card Actions</h6>
                    <ul className="small text-muted">
                      <li>Copy to clipboard</li>
                      <li>Refresh data</li>
                      <li>Show/hide cards</li>
                      <li>Delete cards</li>
                    </ul>
                  </Col>
                  <Col md={3}>
                    <h6 className="text-warning">Layout Persistence</h6>
                    <ul className="small text-muted">
                      <li>Save custom layouts</li>
                      <li>Load saved layouts</li>
                      <li>Export configurations</li>
                      <li>Import layouts</li>
                    </ul>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Instructions */}
        <Row className="mb-4">
          <Col>
            <Card className="border-start border-4 border-primary bg-primary bg-opacity-10">
              <Card.Body>
                <h6 className="fw-bold text-primary mb-2">
                  💡 How to Use
                </h6>
                <p className="mb-2 small">
                  1. <strong>Edit Cards:</strong> Click the menu button (⋮) on any card and select "Edit" to modify values
                </p>
                <p className="mb-2 small">
                  2. <strong>Layout Mode:</strong> Click "Edit Layout" to enter drag-and-drop mode for repositioning cards
                </p>
                <p className="mb-2 small">
                  3. <strong>Add Cards:</strong> In edit mode, click "Add Card" to create new custom metrics cards
                </p>
                <p className="mb-0 small">
                  4. <strong>Save Layouts:</strong> Use the grid menu to save your current layout configuration
                </p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>

      {/* Enhanced Dashboard Demo */}
      <EnhancedClientDashboard />
    </div>
  );
};

export default DashboardDemo;