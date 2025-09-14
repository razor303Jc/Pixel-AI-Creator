/**
 * Card Layout Manager
 * Drag-and-drop interface for organizing dashboard cards with layout customization
 */

import React, { useState, useCallback } from 'react';
import {
  Container,
  Row,
  Col,
  Button,
  Modal,
  Form,
  Badge,
  Dropdown
} from 'react-bootstrap';
import { AnimatePresence } from 'framer-motion';
import {
  Layout,
  Grid,
  Plus,
  Settings,
  Save,
  RotateCcw,
  Move,
  Download
} from 'lucide-react';
import EditableCard from './EditableCard';

export interface DashboardCard {
  id: string;
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'success' | 'info' | 'warning' | 'danger';
  position: { row: number; col: number };
  size: { width: number; height?: number }; // Bootstrap col size (1-12)
  editable?: boolean;
  deletable?: boolean;
  copyable?: boolean;
  refreshable?: boolean;
  hidden?: boolean;
  dataSource?: string;
  formatValue?: (value: string | number) => string;
  validateValue?: (value: string) => boolean;
  inputType?: 'text' | 'number' | 'email' | 'url';
}

export interface LayoutConfig {
  id: string;
  name: string;
  description?: string;
  cards: DashboardCard[];
  columns: number;
  isDefault?: boolean;
  createdAt: Date;
  updatedAt: Date;
}

interface CardLayoutManagerProps {
  cards: DashboardCard[];
  onCardsChange: (cards: DashboardCard[]) => void;
  onSaveLayout?: (layout: LayoutConfig) => void;
  onLoadLayout?: (layoutId: string) => void;
  savedLayouts?: LayoutConfig[];
  allowCustomCards?: boolean;
  maxColumns?: number;
}

const CardLayoutManager: React.FC<CardLayoutManagerProps> = ({
  cards,
  onCardsChange,
  onSaveLayout,
  onLoadLayout,
  savedLayouts = [],
  allowCustomCards = true,
  maxColumns = 12
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [showAddCardModal, setShowAddCardModal] = useState(false);
  const [showLayoutModal, setShowLayoutModal] = useState(false);
  const [draggedCard, setDraggedCard] = useState<string | null>(null);
  const [layoutName, setLayoutName] = useState('');
  const [layoutDescription, setLayoutDescription] = useState('');
  const [newCard, setNewCard] = useState<Partial<DashboardCard>>({
    title: '',
    value: '',
    color: 'primary',
    size: { width: 3 },
    position: { row: 0, col: 0 },
    editable: true,
    deletable: true
  });

  // Group cards by rows for layout
  const cardsByRow = cards.reduce((acc, card) => {
    if (!card.hidden) {
      const row = card.position.row;
      if (!acc[row]) acc[row] = [];
      acc[row].push(card);
    }
    return acc;
  }, {} as Record<number, DashboardCard[]>);

  // Sort cards within each row by column position
  Object.values(cardsByRow).forEach(rowCards => {
    rowCards.sort((a, b) => a.position.col - b.position.col);
  });

  const handleCardEdit = useCallback((id: string, newValue: string | number, newTitle?: string) => {
    const updatedCards = cards.map(card => {
      if (card.id === id) {
        return {
          ...card,
          value: newValue,
          ...(newTitle && { title: newTitle })
        };
      }
      return card;
    });
    onCardsChange(updatedCards);
  }, [cards, onCardsChange]);

  const handleCardDelete = useCallback((id: string) => {
    const updatedCards = cards.filter(card => card.id !== id);
    onCardsChange(updatedCards);
  }, [cards, onCardsChange]);

  const handleCardVisibility = useCallback((id: string) => {
    const updatedCards = cards.map(card => {
      if (card.id === id) {
        return { ...card, hidden: !card.hidden };
      }
      return card;
    });
    onCardsChange(updatedCards);
  }, [cards, onCardsChange]);

  const handleCardRefresh = useCallback(async (id: string) => {
    // Simulate refresh - in real implementation, fetch fresh data
    const card = cards.find(c => c.id === id);
    if (card?.dataSource) {
      // Fetch new data from API based on dataSource
      console.log(`Refreshing data for card ${id} from ${card.dataSource}`);
    }
  }, [cards]);

  const handleDragStart = (cardId: string) => {
    setDraggedCard(cardId);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (targetRow: number, targetCol: number) => {
    if (!draggedCard) return;

    const updatedCards = cards.map(card => {
      if (card.id === draggedCard) {
        return {
          ...card,
          position: { row: targetRow, col: targetCol }
        };
      }
      return card;
    });

    onCardsChange(updatedCards);
    setDraggedCard(null);
  };

  const addNewCard = () => {
    if (!newCard.title || newCard.value === undefined) return;

    const maxId = cards.length > 0 ? Math.max(...cards.map(c => parseInt(c.id))) : 0;
    const card: DashboardCard = {
      id: (maxId + 1).toString(),
      title: newCard.title,
      value: newCard.value,
      subtitle: newCard.subtitle,
      color: newCard.color || 'primary',
      position: newCard.position || { row: 0, col: 0 },
      size: newCard.size || { width: 3 },
      editable: newCard.editable ?? true,
      deletable: newCard.deletable ?? true,
      copyable: newCard.copyable ?? false,
      refreshable: newCard.refreshable ?? false
    };

    onCardsChange([...cards, card]);
    setShowAddCardModal(false);
    setNewCard({
      title: '',
      value: '',
      color: 'primary',
      size: { width: 3 },
      position: { row: 0, col: 0 },
      editable: true,
      deletable: true
    });
  };

  const saveCurrentLayout = () => {
    if (!layoutName.trim()) return;

    const layout: LayoutConfig = {
      id: Date.now().toString(),
      name: layoutName,
      description: layoutDescription,
      cards: [...cards],
      columns: maxColumns,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    onSaveLayout?.(layout);
    setShowLayoutModal(false);
    setLayoutName('');
    setLayoutDescription('');
  };

  const resetLayout = () => {
    // Reset to original positions
    const resetCards = cards.map((card, index) => ({
      ...card,
      position: { row: Math.floor(index / 4), col: (index % 4) * 3 },
      size: { width: 3 }
    }));
    onCardsChange(resetCards);
  };

  const exportLayout = () => {
    const layoutData = {
      cards,
      exportedAt: new Date().toISOString(),
      version: '1.0'
    };
    
    const blob = new Blob([JSON.stringify(layoutData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard-layout-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Container fluid>
      {/* Layout Controls */}
      <Row className="mb-3">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div className="d-flex align-items-center gap-2">
              <h5 className="mb-0 fw-bold">
                <Layout className="me-2" size={20} />
                Dashboard Layout
              </h5>
              <Badge bg={isEditing ? 'warning' : 'success'}>
                {isEditing ? 'Edit Mode' : 'View Mode'}
              </Badge>
            </div>
            
            <div className="d-flex gap-2">
              <Button
                variant={isEditing ? 'success' : 'outline-primary'}
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                {isEditing ? <Save size={16} /> : <Settings size={16} />}
                <span className="ms-1">{isEditing ? 'Save' : 'Edit Layout'}</span>
              </Button>
              
              {allowCustomCards && (
                <Button
                  variant="outline-success"
                  size="sm"
                  onClick={() => setShowAddCardModal(true)}
                  disabled={!isEditing}
                >
                  <Plus size={16} />
                  <span className="ms-1">Add Card</span>
                </Button>
              )}
              
              <Dropdown>
                <Dropdown.Toggle variant="outline-secondary" size="sm">
                  <Grid size={16} />
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item onClick={() => setShowLayoutModal(true)}>
                    <Save size={14} className="me-2" />
                    Save Layout
                  </Dropdown.Item>
                  <Dropdown.Item onClick={exportLayout}>
                    <Download size={14} className="me-2" />
                    Export Layout
                  </Dropdown.Item>
                  <Dropdown.Divider />
                  <Dropdown.Item onClick={resetLayout}>
                    <RotateCcw size={14} className="me-2" />
                    Reset Layout
                  </Dropdown.Item>
                  {savedLayouts.map(layout => (
                    <Dropdown.Item
                      key={layout.id}
                      onClick={() => onLoadLayout?.(layout.id)}
                    >
                      {layout.name}
                    </Dropdown.Item>
                  ))}
                </Dropdown.Menu>
              </Dropdown>
            </div>
          </div>
        </Col>
      </Row>

      {/* Layout Grid */}
      <div className={isEditing ? 'border border-dashed border-primary p-3 rounded' : ''}>
        <AnimatePresence>
          {Object.entries(cardsByRow)
            .sort(([a], [b]) => parseInt(a) - parseInt(b))
            .map(([rowIndex, rowCards]) => (
              <Row key={rowIndex} className="mb-3">
                {rowCards.map(card => (
                  <Col
                    key={card.id}
                    md={card.size.width}
                    className={isEditing ? 'position-relative' : ''}
                    draggable={isEditing}
                    onDragStart={() => handleDragStart(card.id)}
                    onDragOver={handleDragOver}
                    onDrop={() => handleDrop(parseInt(rowIndex), card.position.col)}
                  >
                    <div className="position-relative">
                      <EditableCard
                        id={card.id}
                        title={card.title}
                        value={card.value}
                        subtitle={card.subtitle}
                        icon={card.icon}
                        color={card.color}
                        editable={card.editable && isEditing}
                        deletable={card.deletable && isEditing}
                        copyable={card.copyable}
                        refreshable={card.refreshable}
                        hidden={card.hidden}
                        onEdit={handleCardEdit}
                        onDelete={handleCardDelete}
                        onToggleVisibility={handleCardVisibility}
                        onRefresh={handleCardRefresh}
                        formatValue={card.formatValue}
                        validateValue={card.validateValue}
                        inputType={card.inputType}
                      />
                      
                      {isEditing && (
                        <div className="position-absolute top-0 start-0 m-1">
                          <Badge bg="secondary" className="opacity-75">
                            <Move size={12} />
                          </Badge>
                        </div>
                      )}
                    </div>
                  </Col>
                ))}
              </Row>
            ))}
        </AnimatePresence>
      </div>

      {/* Add Card Modal */}
      <Modal show={showAddCardModal} onHide={() => setShowAddCardModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Add New Card</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Card Title</Form.Label>
                  <Form.Control
                    value={newCard.title || ''}
                    onChange={(e) => setNewCard({ ...newCard, title: e.target.value })}
                    placeholder="Enter card title"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Initial Value</Form.Label>
                  <Form.Control
                    value={newCard.value?.toString() || ''}
                    onChange={(e) => setNewCard({ ...newCard, value: e.target.value })}
                    placeholder="Enter initial value"
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Color Theme</Form.Label>
                  <Form.Select
                    value={newCard.color || 'primary'}
                    onChange={(e) => setNewCard({ ...newCard, color: e.target.value as any })}
                  >
                    <option value="primary">Primary</option>
                    <option value="success">Success</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="danger">Danger</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Card Width</Form.Label>
                  <Form.Select
                    value={newCard.size?.width || 3}
                    onChange={(e) => setNewCard({ 
                      ...newCard, 
                      size: { ...newCard.size, width: parseInt(e.target.value) }
                    })}
                  >
                    <option value={3}>Small (3 cols)</option>
                    <option value={4}>Medium (4 cols)</option>
                    <option value={6}>Large (6 cols)</option>
                    <option value={12}>Full Width (12 cols)</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Position Row</Form.Label>
                  <Form.Control
                    type="number"
                    min="0"
                    value={newCard.position?.row || 0}
                    onChange={(e) => setNewCard({
                      ...newCard,
                      position: { 
                        ...newCard.position, 
                        row: parseInt(e.target.value) || 0 
                      }
                    })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Subtitle (Optional)</Form.Label>
              <Form.Control
                value={newCard.subtitle || ''}
                onChange={(e) => setNewCard({ ...newCard, subtitle: e.target.value })}
                placeholder="Enter subtitle"
              />
            </Form.Group>

            <Row>
              <Col>
                <Form.Check
                  type="checkbox"
                  label="Allow editing"
                  checked={newCard.editable ?? true}
                  onChange={(e) => setNewCard({ ...newCard, editable: e.target.checked })}
                />
              </Col>
              <Col>
                <Form.Check
                  type="checkbox"
                  label="Allow deletion"
                  checked={newCard.deletable ?? true}
                  onChange={(e) => setNewCard({ ...newCard, deletable: e.target.checked })}
                />
              </Col>
              <Col>
                <Form.Check
                  type="checkbox"
                  label="Allow copying"
                  checked={newCard.copyable ?? false}
                  onChange={(e) => setNewCard({ ...newCard, copyable: e.target.checked })}
                />
              </Col>
            </Row>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAddCardModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={addNewCard}>
            Add Card
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Save Layout Modal */}
      <Modal show={showLayoutModal} onHide={() => setShowLayoutModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Save Layout</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Layout Name</Form.Label>
              <Form.Control
                value={layoutName}
                onChange={(e) => setLayoutName(e.target.value)}
                placeholder="Enter layout name"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Description (Optional)</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={layoutDescription}
                onChange={(e) => setLayoutDescription(e.target.value)}
                placeholder="Describe this layout"
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowLayoutModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={saveCurrentLayout}>
            Save Layout
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default CardLayoutManager;