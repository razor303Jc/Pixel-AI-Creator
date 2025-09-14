/**
 * Editable Card Component
 * Reusable card component with inline editing capabilities for dashboard metrics
 */

import React, { useState } from 'react';
import {
  Card,
  Button,
  Form,
  InputGroup,
  Modal,
  Dropdown
} from 'react-bootstrap';
import { motion } from 'framer-motion';
import {
  Edit2,
  Save,
  X,
  MoreVertical,
  Copy,
  Trash2,
  Eye,
  EyeOff,
  RefreshCw
} from 'lucide-react';

interface EditableCardProps {
  id: string;
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'success' | 'info' | 'warning' | 'danger';
  editable?: boolean;
  deletable?: boolean;
  copyable?: boolean;
  refreshable?: boolean;
  hidden?: boolean;
  onEdit?: (id: string, newValue: string | number, newTitle?: string) => void;
  onDelete?: (id: string) => void;
  onToggleVisibility?: (id: string) => void;
  onRefresh?: (id: string) => void;
  formatValue?: (value: string | number) => string;
  validateValue?: (value: string) => boolean;
  inputType?: 'text' | 'number' | 'email' | 'url';
  placeholder?: string;
  className?: string;
}

const EditableCard: React.FC<EditableCardProps> = ({
  id,
  title,
  value,
  subtitle,
  icon,
  color = 'primary',
  editable = true,
  deletable = false,
  copyable = false,
  refreshable = false,
  hidden = false,
  onEdit,
  onDelete,
  onToggleVisibility,
  onRefresh,
  formatValue,
  validateValue,
  inputType = 'text',
  placeholder,
  className = ''
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value.toString());
  const [editTitle, setEditTitle] = useState(title);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    setError('');
    
    // Validate if validator function is provided
    if (validateValue && !validateValue(editValue)) {
      setError('Invalid value entered');
      return;
    }

    setIsLoading(true);
    try {
      const newValue = inputType === 'number' ? parseFloat(editValue) : editValue;
      await onEdit?.(id, newValue, editTitle);
      setIsEditing(false);
    } catch (err) {
      setError('Failed to save changes');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setEditValue(value.toString());
    setEditTitle(title);
    setIsEditing(false);
    setError('');
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value.toString());
    } catch (err) {
      console.error('Failed to copy to clipboard');
    }
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      await onRefresh?.(id);
    } catch (err) {
      setError('Failed to refresh data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete?.(id);
      setShowDeleteConfirm(false);
    } catch (err) {
      setError('Failed to delete card');
    } finally {
      setIsLoading(false);
    }
  };

  const displayValue = formatValue ? formatValue(value) : value.toString();

  if (hidden) {
    return null;
  }

  return (
    <>
      <motion.div
        whileHover={{ scale: 1.02 }}
        transition={{ duration: 0.2 }}
        className={className}
      >
        <Card className="border-0 shadow-sm h-100 position-relative">
          <Card.Body>
            {/* Card Header with Actions */}
            <div className="d-flex justify-content-between align-items-start mb-2">
              <div className="d-flex align-items-center flex-grow-1">
                {icon && (
                  <div className={`bg-${color} bg-opacity-10 p-2 rounded-circle me-3 flex-shrink-0`}>
                    <div className={`text-${color}`}>
                      {icon}
                    </div>
                  </div>
                )}
                <div className="flex-grow-1">
                  {isEditing ? (
                    <Form.Control
                      size="sm"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      placeholder="Card title"
                      className="mb-1 fw-bold"
                    />
                  ) : (
                    <h6 className="text-muted mb-0 fw-medium">{title}</h6>
                  )}
                </div>
              </div>

              {/* Action Dropdown */}
              <Dropdown align="end">
                <Dropdown.Toggle
                  variant="link"
                  className="p-1 text-muted border-0"
                  style={{ fontSize: '0.875rem' }}
                >
                  <MoreVertical size={16} />
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  {editable && (
                    <Dropdown.Item onClick={() => setIsEditing(!isEditing)}>
                      <Edit2 size={14} className="me-2" />
                      {isEditing ? 'Cancel Edit' : 'Edit'}
                    </Dropdown.Item>
                  )}
                  {copyable && (
                    <Dropdown.Item onClick={handleCopy}>
                      <Copy size={14} className="me-2" />
                      Copy Value
                    </Dropdown.Item>
                  )}
                  {refreshable && (
                    <Dropdown.Item onClick={handleRefresh} disabled={isLoading}>
                      <RefreshCw size={14} className="me-2" />
                      Refresh
                    </Dropdown.Item>
                  )}
                  {onToggleVisibility && (
                    <Dropdown.Item onClick={() => onToggleVisibility(id)}>
                      {hidden ? <Eye size={14} /> : <EyeOff size={14} />}
                      <span className="ms-2">{hidden ? 'Show' : 'Hide'}</span>
                    </Dropdown.Item>
                  )}
                  {deletable && (
                    <>
                      <Dropdown.Divider />
                      <Dropdown.Item
                        onClick={() => setShowDeleteConfirm(true)}
                        className="text-danger"
                      >
                        <Trash2 size={14} className="me-2" />
                        Delete
                      </Dropdown.Item>
                    </>
                  )}
                </Dropdown.Menu>
              </Dropdown>
            </div>

            {/* Main Value Display/Edit */}
            {isEditing ? (
              <div>
                <InputGroup size="sm" className="mb-2">
                  <Form.Control
                    type={inputType}
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    placeholder={placeholder || 'Enter value'}
                    isInvalid={!!error}
                  />
                  <Button
                    variant="success"
                    onClick={handleSave}
                    disabled={isLoading}
                    size="sm"
                  >
                    {isLoading ? (
                      <RefreshCw size={14} className="spin" />
                    ) : (
                      <Save size={14} />
                    )}
                  </Button>
                  <Button
                    variant="outline-secondary"
                    onClick={handleCancel}
                    size="sm"
                  >
                    <X size={14} />
                  </Button>
                </InputGroup>
                {error && (
                  <div className="text-danger small">{error}</div>
                )}
              </div>
            ) : (
              <div>
                <h3 className="fw-bold mb-0 text-dark">{displayValue}</h3>
                {subtitle && (
                  <small className="text-muted">{subtitle}</small>
                )}
              </div>
            )}
          </Card.Body>

          {/* Loading Overlay */}
          {isLoading && (
            <div className="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-white bg-opacity-75 rounded">
              <RefreshCw className="spin text-primary" size={20} />
            </div>
          )}
        </Card>
      </motion.div>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteConfirm} onHide={() => setShowDeleteConfirm(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Are you sure you want to delete the "{title}" card?</p>
          <p className="text-muted small">This action cannot be undone.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteConfirm(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={isLoading}>
            {isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default EditableCard;