/**
 * Document Upload Component
 * Drag-and-drop file upload interface for chatbot knowledge base
 */

import React, { useState, useCallback, useRef } from 'react';
import {
  Modal,
  Button,
  Card,
  Alert,
  ProgressBar,
  ListGroup,
  Badge,
  Form,
  Row,
  Col,
  Spinner
} from 'react-bootstrap';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  File,
  X,
  Check,
  AlertCircle,
  Download
} from 'lucide-react';

interface Document {
  id: number;
  title: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  processed: boolean;
  summary?: string;
  chunk_count?: number;
}

interface DocumentUploadProps {
  show: boolean;
  onHide: () => void;
  chatbotId: number;
  onDocumentUploaded?: (document: Document) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  show,
  onHide,
  chatbotId,
  onDocumentUploaded
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch existing documents when modal opens
  React.useEffect(() => {
    if (show && chatbotId) {
      fetchDocuments();
    }
  }, [show, chatbotId]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/documents/chatbot/${chatbotId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }

      const data = await response.json();
      setDocuments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = async (files: File[]) => {
    if (files.length === 0) return;

    // Validate files
    const allowedTypes = ['.pdf', '.docx', '.doc', '.txt'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    for (const file of files) {
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!allowedTypes.includes(extension)) {
        setError(`File type not supported: ${extension}. Allowed: PDF, DOCX, DOC, TXT`);
        return;
      }
      if (file.size > maxSize) {
        setError(`File too large: ${file.name}. Maximum size is 10MB`);
        return;
      }
    }

    // Upload files
    for (const file of files) {
      await uploadFile(file);
    }
  };

  const uploadFile = async (file: File) => {
    try {
      setUploading(true);
      setError(null);
      setUploadProgress(0);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', file.name);

      const token = localStorage.getItem('token');
      
      const xhr = new XMLHttpRequest();
      
      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = (e.loaded / e.total) * 100;
          setUploadProgress(progress);
        }
      });

      const uploadPromise = new Promise<Document>((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } else {
            reject(new Error(`Upload failed: ${xhr.statusText}`));
          }
        };
        
        xhr.onerror = () => reject(new Error('Upload failed'));
      });

      xhr.open('POST', `/api/documents/upload/${chatbotId}`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);

      const uploadedDocument = await uploadPromise;
      
      // Add to documents list
      setDocuments(prev => [uploadedDocument, ...prev]);
      
      // Notify parent component
      if (onDocumentUploaded) {
        onDocumentUploaded(uploadedDocument);
      }

      setUploadProgress(100);
      
      // Refresh documents list to get updated status
      setTimeout(fetchDocuments, 2000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const deleteDocument = async (documentId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete document');
      }

      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return <FileText className="text-danger" size={20} />;
      case 'docx':
      case 'doc':
        return <File className="text-primary" size={20} />;
      case 'txt':
        return <FileText className="text-secondary" size={20} />;
      default:
        return <File size={20} />;
    }
  };

  const getStatusBadge = (status: string, processed: boolean) => {
    switch (status) {
      case 'completed':
        return <Badge bg="success">Processed</Badge>;
      case 'processing':
        return <Badge bg="warning">Processing...</Badge>;
      case 'failed':
        return <Badge bg="danger">Failed</Badge>;
      default:
        return <Badge bg="secondary">Pending</Badge>;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Modal show={show} onHide={onHide} size="lg" centered>
      <Modal.Header closeButton>
        <Modal.Title>
          <Upload size={24} className="me-2" />
          Document Knowledge Base
        </Modal.Title>
      </Modal.Header>
      
      <Modal.Body>
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Upload Area */}
        <Card className="mb-4">
          <Card.Body>
            <div
              className={`border-2 border-dashed rounded p-4 text-center ${
                dragActive ? 'border-primary bg-light' : 'border-secondary'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              style={{ cursor: 'pointer' }}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                id="fileInput"
                name="files"
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileInput}
                autoComplete="off"
                style={{ display: 'none' }}
              />
              
              <motion.div
                initial={{ scale: 1 }}
                animate={{ scale: dragActive ? 1.05 : 1 }}
                transition={{ duration: 0.2 }}
              >
                <Upload size={48} className="text-muted mb-3" />
                <h5>Upload Documents</h5>
                <p className="text-muted mb-0">
                  Drag and drop files here, or click to browse
                </p>
                <small className="text-muted">
                  Supports PDF, DOCX, DOC, TXT files up to 10MB
                </small>
              </motion.div>
            </div>

            {uploading && (
              <div className="mt-3">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <small>Uploading...</small>
                  <small>{Math.round(uploadProgress)}%</small>
                </div>
                <ProgressBar now={uploadProgress} animated />
              </div>
            )}
          </Card.Body>
        </Card>

        {/* Documents List */}
        <Card>
          <Card.Header>
            <h6 className="mb-0">Knowledge Base Documents</h6>
          </Card.Header>
          <Card.Body style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {loading ? (
              <div className="text-center py-4">
                <Spinner animation="border" />
                <p className="mt-2 text-muted">Loading documents...</p>
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-4 text-muted">
                <FileText size={48} className="mb-3" />
                <p>No documents uploaded yet</p>
              </div>
            ) : (
              <ListGroup variant="flush">
                <AnimatePresence>
                  {documents.map((doc) => (
                    <motion.div
                      key={doc.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ListGroup.Item className="d-flex justify-content-between align-items-start">
                        <div className="d-flex align-items-start">
                          <div className="me-3 mt-1">
                            {getFileIcon(doc.file_type)}
                          </div>
                          <div className="flex-grow-1">
                            <h6 className="mb-1">{doc.title}</h6>
                            <p className="mb-1 text-muted small">
                              {doc.filename} • {formatFileSize(doc.file_size)}
                            </p>
                            {doc.summary && (
                              <p className="mb-1 small text-secondary">
                                {doc.summary.substring(0, 100)}...
                              </p>
                            )}
                            <div className="d-flex align-items-center gap-2">
                              {getStatusBadge(doc.status, doc.processed)}
                              {doc.chunk_count && (
                                <Badge bg="info" className="small">
                                  {doc.chunk_count} chunks
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => deleteDocument(doc.id)}
                        >
                          <X size={16} />
                        </Button>
                      </ListGroup.Item>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </ListGroup>
            )}
          </Card.Body>
        </Card>
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default DocumentUpload;
