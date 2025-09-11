/**
 * Registration Component
 * Handles user registration with backend integration
 */

import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Link,
  Divider,
  Grid,
} from "@mui/material";
import { useAuth } from "../../contexts/AuthContext";

const RegisterForm = ({ onSwitchToLogin }) => {
  const { register, isLoading, error, clearError } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    companyName: "",
    phone: "",
  });
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Clear errors when component unmounts or form changes
  useEffect(() => {
    clearError();
  }, [clearError]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear field-specific error when user starts typing
    if (formErrors[name]) {
      setFormErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }

    // Clear global error
    if (error) {
      clearError();
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.email) {
      errors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "Email is invalid";
    }

    if (!formData.password) {
      errors.password = "Password is required";
    } else if (formData.password.length < 6) {
      errors.password = "Password must be at least 6 characters";
    }

    if (!formData.confirmPassword) {
      errors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = "Passwords do not match";
    }

    if (!formData.firstName) {
      errors.firstName = "First name is required";
    }

    if (!formData.lastName) {
      errors.lastName = "Last name is required";
    }

    // Phone validation (optional but validate format if provided)
    if (formData.phone && !/^\+?[\d\s\-\(\)]+$/.test(formData.phone)) {
      errors.phone = "Please enter a valid phone number";
    }

    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setIsSubmitting(true);

    // Prepare data for API (match backend schema)
    const registrationData = {
      email: formData.email,
      password: formData.password,
      first_name: formData.firstName,
      last_name: formData.lastName,
      company_name: formData.companyName || null,
      phone: formData.phone || null,
    };

    const result = await register(registrationData);

    setIsSubmitting(false);

    if (result.success) {
      // Navigation will be handled by App.js based on authentication state
      console.log("Registration successful:", result.user);
    } else {
      // Error is handled by AuthContext and displayed via error state
      console.error("Registration failed:", result.error);
    }
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="#f5f5f5"
      p={2}
    >
      <Card sx={{ maxWidth: 500, width: "100%" }}>
        <CardContent sx={{ p: 4 }}>
          <Box textAlign="center" mb={3}>
            <Typography variant="h4" component="h1" gutterBottom>
              🤖 Pixel AI Creator
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Create your account
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error.message}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  error={!!formErrors.firstName}
                  helperText={formErrors.firstName}
                  autoComplete="given-name"
                  autoFocus
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  error={!!formErrors.lastName}
                  helperText={formErrors.lastName}
                  autoComplete="family-name"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  error={!!formErrors.email}
                  helperText={formErrors.email}
                  autoComplete="email"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Company Name (Optional)"
                  name="companyName"
                  value={formData.companyName}
                  onChange={handleInputChange}
                  error={!!formErrors.companyName}
                  helperText={formErrors.companyName}
                  autoComplete="organization"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Phone (Optional)"
                  name="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handleInputChange}
                  error={!!formErrors.phone}
                  helperText={formErrors.phone}
                  autoComplete="tel"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  error={!!formErrors.password}
                  helperText={formErrors.password}
                  autoComplete="new-password"
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Confirm Password"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  error={!!formErrors.confirmPassword}
                  helperText={formErrors.confirmPassword}
                  autoComplete="new-password"
                />
              </Grid>
            </Grid>

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isSubmitting || isLoading}
              sx={{ mt: 3, mb: 2, height: 48 }}
            >
              {isSubmitting || isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                "Create Account"
              )}
            </Button>
          </form>

          <Divider sx={{ my: 2 }} />

          <Box textAlign="center">
            <Typography variant="body2" color="text.secondary">
              Already have an account?{" "}
              <Link
                component="button"
                variant="body2"
                onClick={onSwitchToLogin}
                sx={{ textDecoration: "none" }}
              >
                Sign in here
              </Link>
            </Typography>
          </Box>

          <Box textAlign="center" mt={3}>
            <Typography variant="caption" color="text.secondary">
              Join thousands of users creating AI assistants
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default RegisterForm;
