/**
 * Main Dashboard Component
 * Integrates with backend to display clients, chatbots, and conversations
 */

import React, { useEffect, useState } from "react";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from "@mui/material";
import {
  AccountCircle,
  Add,
  Person,
  SmartToy,
  Chat,
  MoreVert,
  Edit,
  Delete,
} from "@mui/icons-material";
import { useAuth } from "../../contexts/AuthContext";
import { useChatbot } from "../../contexts/ChatbotContext";

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
    loadClients,
    loadChatbots,
    loadConversations,
    createClient,
    createChatbot,
    deleteClient,
    deleteChatbot,
    clearAllErrors,
  } = useChatbot();

  // UI state
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedCard, setSelectedCard] = useState(null);
  const [cardMenuAnchor, setCardMenuAnchor] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createDialogType, setCreateDialogType] = useState(null);
  const [newItemData, setNewItemData] = useState({});

  // Load data on component mount
  useEffect(() => {
    loadClients();
    loadChatbots();
    loadConversations();
  }, [loadClients, loadChatbots, loadConversations]);

  // Handle user menu
  const handleUserMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleUserMenuClose();
  };

  // Handle card menu
  const handleCardMenuOpen = (event, item, type) => {
    event.stopPropagation();
    setSelectedCard({ item, type });
    setCardMenuAnchor(event.currentTarget);
  };

  const handleCardMenuClose = () => {
    setSelectedCard(null);
    setCardMenuAnchor(null);
  };

  // Handle create dialog
  const openCreateDialog = (type) => {
    setCreateDialogType(type);
    setNewItemData({});
    setCreateDialogOpen(true);
  };

  const closeCreateDialog = () => {
    setCreateDialogOpen(false);
    setCreateDialogType(null);
    setNewItemData({});
  };

  const handleCreateSubmit = async () => {
    try {
      let result;
      if (createDialogType === "client") {
        result = await createClient({
          name: newItemData.name,
          email: newItemData.email,
          company: newItemData.company,
          description: newItemData.description,
        });
      } else if (createDialogType === "chatbot") {
        result = await createChatbot({
          name: newItemData.name,
          description: newItemData.description,
          personality: newItemData.personality || "helpful",
          client_id: newItemData.client_id
            ? parseInt(newItemData.client_id)
            : null,
        });
      }

      if (result.success) {
        closeCreateDialog();
      }
    } catch (error) {
      console.error("Failed to create item:", error);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!selectedCard) return;

    try {
      let result;
      if (selectedCard.type === "client") {
        result = await deleteClient(selectedCard.item.id);
      } else if (selectedCard.type === "chatbot") {
        result = await deleteChatbot(selectedCard.item.id);
      }

      if (result.success) {
        handleCardMenuClose();
      }
    } catch (error) {
      console.error("Failed to delete item:", error);
    }
  };

  return (
    <Box>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🤖 Pixel AI Creator - Dashboard
          </Typography>
          <Box>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="user-menu"
              aria-haspopup="true"
              onClick={handleUserMenuOpen}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              id="user-menu"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
              keepMounted
              transformOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
              open={Boolean(anchorEl)}
              onClose={handleUserMenuClose}
            >
              <MenuItem disabled>
                <Typography variant="body2">
                  {user?.first_name} {user?.last_name}
                </Typography>
              </MenuItem>
              <MenuItem disabled>
                <Typography variant="caption" color="text.secondary">
                  {user?.email}
                </Typography>
              </MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Error Alerts */}
        {(clientsError || chatbotsError || conversationsError) && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={clearAllErrors}>
            {clientsError?.message ||
              chatbotsError?.message ||
              conversationsError?.message}
          </Alert>
        )}

        {/* Overview Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Person sx={{ fontSize: 40, mr: 2, color: "primary.main" }} />
                  <Box>
                    <Typography variant="h4">
                      {isLoadingClients ? (
                        <CircularProgress size={24} />
                      ) : (
                        clients.length
                      )}
                    </Typography>
                    <Typography color="text.secondary">Clients</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <SmartToy
                    sx={{ fontSize: 40, mr: 2, color: "secondary.main" }}
                  />
                  <Box>
                    <Typography variant="h4">
                      {isLoadingChatbots ? (
                        <CircularProgress size={24} />
                      ) : (
                        chatbots.length
                      )}
                    </Typography>
                    <Typography color="text.secondary">Chatbots</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <Chat sx={{ fontSize: 40, mr: 2, color: "success.main" }} />
                  <Box>
                    <Typography variant="h4">
                      {isLoadingConversations ? (
                        <CircularProgress size={24} />
                      ) : (
                        conversations.length
                      )}
                    </Typography>
                    <Typography color="text.secondary">
                      Conversations
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Clients Section */}
        <Box mb={4}>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={2}
          >
            <Typography variant="h5">Clients</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => openCreateDialog("client")}
            >
              Add Client
            </Button>
          </Box>

          <Grid container spacing={2}>
            {isLoadingClients ? (
              <Grid item xs={12}>
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              </Grid>
            ) : clients.length === 0 ? (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      textAlign="center"
                    >
                      No clients yet. Create your first client to get started!
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ) : (
              clients.map((client) => (
                <Grid item xs={12} sm={6} md={4} key={client.id}>
                  <Card>
                    <CardContent>
                      <Box
                        display="flex"
                        justifyContent="space-between"
                        alignItems="start"
                      >
                        <Box>
                          <Typography variant="h6" component="div">
                            {client.name}
                          </Typography>
                          <Typography color="text.secondary" gutterBottom>
                            {client.email}
                          </Typography>
                          {client.company && (
                            <Typography variant="body2">
                              {client.company}
                            </Typography>
                          )}
                          <Chip
                            label={client.status || "active"}
                            size="small"
                            color="success"
                            sx={{ mt: 1 }}
                          />
                        </Box>
                        <IconButton
                          onClick={(e) =>
                            handleCardMenuOpen(e, client, "client")
                          }
                          size="small"
                        >
                          <MoreVert />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))
            )}
          </Grid>
        </Box>

        {/* Chatbots Section */}
        <Box mb={4}>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mb={2}
          >
            <Typography variant="h5">Chatbots</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => openCreateDialog("chatbot")}
            >
              Create Chatbot
            </Button>
          </Box>

          <Grid container spacing={2}>
            {isLoadingChatbots ? (
              <Grid item xs={12}>
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              </Grid>
            ) : chatbots.length === 0 ? (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      textAlign="center"
                    >
                      No chatbots created yet. Build your first AI assistant!
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ) : (
              chatbots.map((chatbot) => (
                <Grid item xs={12} sm={6} md={4} key={chatbot.id}>
                  <Card>
                    <CardContent>
                      <Box
                        display="flex"
                        justifyContent="space-between"
                        alignItems="start"
                      >
                        <Box>
                          <Typography variant="h6" component="div">
                            {chatbot.name}
                          </Typography>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            gutterBottom
                          >
                            {chatbot.description}
                          </Typography>
                          <Chip
                            label={chatbot.personality || "helpful"}
                            size="small"
                            color="primary"
                            sx={{ mt: 1 }}
                          />
                        </Box>
                        <IconButton
                          onClick={(e) =>
                            handleCardMenuOpen(e, chatbot, "chatbot")
                          }
                          size="small"
                        >
                          <MoreVert />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))
            )}
          </Grid>
        </Box>
      </Container>

      {/* Card Actions Menu */}
      <Menu
        anchorEl={cardMenuAnchor}
        open={Boolean(cardMenuAnchor)}
        onClose={handleCardMenuClose}
      >
        <MenuItem onClick={() => console.log("Edit:", selectedCard)}>
          <Edit sx={{ mr: 1 }} /> Edit
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: "error.main" }}>
          <Delete sx={{ mr: 1 }} /> Delete
        </MenuItem>
      </Menu>

      {/* Create Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={closeCreateDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Create New {createDialogType === "client" ? "Client" : "Chatbot"}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Name"
              value={newItemData.name || ""}
              onChange={(e) =>
                setNewItemData((prev) => ({ ...prev, name: e.target.value }))
              }
              margin="normal"
            />

            {createDialogType === "client" && (
              <>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={newItemData.email || ""}
                  onChange={(e) =>
                    setNewItemData((prev) => ({
                      ...prev,
                      email: e.target.value,
                    }))
                  }
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Company"
                  value={newItemData.company || ""}
                  onChange={(e) =>
                    setNewItemData((prev) => ({
                      ...prev,
                      company: e.target.value,
                    }))
                  }
                  margin="normal"
                />
              </>
            )}

            {createDialogType === "chatbot" && (
              <>
                <TextField
                  fullWidth
                  label="Personality"
                  value={newItemData.personality || "helpful"}
                  onChange={(e) =>
                    setNewItemData((prev) => ({
                      ...prev,
                      personality: e.target.value,
                    }))
                  }
                  margin="normal"
                  helperText="e.g., helpful, friendly, professional, creative"
                />
                <TextField
                  fullWidth
                  label="Client ID (Optional)"
                  type="number"
                  value={newItemData.client_id || ""}
                  onChange={(e) =>
                    setNewItemData((prev) => ({
                      ...prev,
                      client_id: e.target.value,
                    }))
                  }
                  margin="normal"
                  helperText="Associate with a specific client"
                />
              </>
            )}

            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={newItemData.description || ""}
              onChange={(e) =>
                setNewItemData((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              margin="normal"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeCreateDialog}>Cancel</Button>
          <Button onClick={handleCreateSubmit} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Dashboard;
