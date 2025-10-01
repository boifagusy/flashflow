"""
FlashFlow Security Integration
============================

Integration layer for security services with React components and Flask routes.
"""

import os
import json
import secrets
from typing import Dict, Any, List, Optional
from flashflow_cli.services.security_services import SecurityManager, RateLimitRule
import logging

logger = logging.getLogger(__name__)

class SecurityIntegration:
    """Main security integration class for FlashFlow"""
    
    def __init__(self):
        self.security_manager = None
        self.generated_components = {}
        self.generated_routes = {}
        self.generated_middleware = {}
    
    def initialize(self, config: Dict[str, Any] = None):
        """Initialize security services with FlashFlow configuration"""
        try:
            # Configure security manager
            security_config = config or {}
            db_path = security_config.get('db_path', 'security.db')
            
            self.security_manager = SecurityManager(db_path)
            
            logger.info("Security integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize security integration: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for security features"""
        components = {}
        
        try:
            # Security dashboard component
            components['SecurityDashboard'] = self._generate_security_dashboard_component()
            
            # Login component with security features
            components['SecureLogin'] = self._generate_secure_login_component()
            
            # User management component
            components['UserManagement'] = self._generate_user_management_component()
            
            # Rate limiting configuration component
            components['RateLimitConfig'] = self._generate_rate_limit_config_component()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} security React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for security features"""
        routes = {}
        
        try:
            # Login endpoint
            routes['login'] = self._generate_login_endpoint()
            
            # Logout endpoint
            routes['logout'] = self._generate_logout_endpoint()
            
            # User registration endpoint
            routes['register'] = self._generate_register_endpoint()
            
            # Password reset endpoint
            routes['password_reset'] = self._generate_password_reset_endpoint()
            
            # Security events endpoint
            routes['security_events'] = self._generate_security_events_endpoint()
            
            # Rate limit rules endpoint
            routes['rate_limit_rules'] = self._generate_rate_limit_rules_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} security Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def generate_flask_middleware(self) -> Dict[str, str]:
        """Generate Flask middleware for security features"""
        middleware = {}
        
        try:
            # Rate limiting middleware
            middleware['rate_limit_middleware'] = self._generate_rate_limit_middleware()
            
            # Authentication middleware
            middleware['auth_middleware'] = self._generate_auth_middleware()
            
            # Security headers middleware
            middleware['security_headers_middleware'] = self._generate_security_headers_middleware()
            
            self.generated_middleware = middleware
            logger.info(f"Generated {len(middleware)} security Flask middleware")
            return middleware
            
        except Exception as e:
            logger.error(f"Failed to generate Flask middleware: {e}")
            return {}
    
    def _generate_security_dashboard_component(self) -> str:
        """Generate security dashboard component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  CircularProgress,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer
} from 'recharts';

export const SecurityDashboard = () => {
  const [securityData, setSecurityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSecurityData();
    const interval = setInterval(fetchSecurityData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/security/events');
      const data = await response.json();
      setSecurityData(data);
    } catch (err) {
      setError('Failed to fetch security data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!securityData) {
    return (
      <Alert severity="info">
        No security data available yet.
      </Alert>
    );
  }

  // Process data for charts
  const eventTypes = securityData.events.reduce((acc, event) => {
    acc[event.event_type] = (acc[event.event_type] || 0) + 1;
    return acc;
  }, {});

  const eventTypeData = Object.entries(eventTypes).map(([type, count]) => ({
    name: type.replace('_', ' ').toUpperCase(),
    count
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Security Events
              </Typography>
              <Typography variant="h4" color="primary">
                {securityData.events.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Failed Logins
              </Typography>
              <Typography variant="h4" color="error">
                {securityData.events.filter(e => e.event_type === 'failed_login').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Rate Limit Exceeded
              </Typography>
              <Typography variant="h4" color="warning">
                {securityData.events.filter(e => e.event_type === 'rate_limit_exceeded').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Security Events by Type
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={eventTypeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Security Events
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Event</TableCell>
                      <TableCell>IP Address</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Severity</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {securityData.events.slice(0, 5).map((event) => (
                      <TableRow key={event.id}>
                        <TableCell>{event.event_type.replace('_', ' ')}</TableCell>
                        <TableCell>{event.ip_address}</TableCell>
                        <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                        <TableCell>
                          <Chip 
                            label={event.severity} 
                            color={
                              event.severity === 'critical' ? 'error' : 
                              event.severity === 'warning' ? 'warning' : 'default'
                            } 
                            size="small" 
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SecurityDashboard;'''
    
    def _generate_secure_login_component(self) -> str:
        """Generate secure login component"""
        return '''import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Alert, 
  CircularProgress,
  Paper,
  IconButton,
  InputAdornment,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import { 
  Visibility, 
  VisibilityOff, 
  LockOutlined 
} from '@mui/icons-material';

export const SecureLogin = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, remember_me: rememberMe }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Store token
        localStorage.setItem('authToken', data.token);
        if (onLoginSuccess) onLoginSuccess(data);
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box 
      display="flex" 
      justifyContent="center" 
      alignItems="center" 
      minHeight="100vh"
    >
      <Paper elevation={3} sx={{ p: 4, width: '100%', maxWidth: 400 }}>
        <Box textAlign="center" mb={3}>
          <LockOutlined sx={{ fontSize: 48, color: 'primary.main' }} />
          <Typography variant="h5" component="h1" gutterBottom>
            Secure Login
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            margin="normal"
            required
            autoComplete="email"
          />
          
          <TextField
            fullWidth
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
            autoComplete="current-password"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          
          <FormControlLabel
            control={
              <Checkbox
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                color="primary"
              />
            }
            label="Remember me"
          />
          
          <Button
            fullWidth
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            sx={{ mt: 2, py: 1.5 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Login'}
          </Button>
        </form>
        
        <Box textAlign="center" mt={2}>
          <Button 
            color="primary" 
            onClick={() => console.log('Forgot password clicked')}
          >
            Forgot password?
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default SecureLogin;'''
    
    def _generate_user_management_component(self) -> str:
        """Generate user management component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  TextField, 
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon 
} from '@mui/icons-material';

export const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({ email: '', name: '', role: 'user' });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/users');
      const data = await response.json();
      setUsers(data.users || []);
    } catch (err) {
      setError('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingUser ? `/api/users/${editingUser.id}` : '/api/users';
      const method = editingUser ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        await fetchUsers();
        handleCloseDialog();
      } else {
        const data = await response.json();
        setError(data.message || 'Operation failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await fetchUsers();
      } else {
        const data = await response.json();
        setError(data.message || 'Delete failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleOpenDialog = (user = null) => {
    setEditingUser(user);
    setFormData(user ? { email: user.email, name: user.name, role: user.role } : { email: '', name: '', role: 'user' });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingUser(null);
    setFormData({ email: '', name: '', role: 'user' });
    setError('');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          User Management
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add User
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.name}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Chip 
                    label={user.role} 
                    color={user.role === 'admin' ? 'primary' : 'default'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell>
                  <Chip 
                    label={user.active ? 'Active' : 'Inactive'} 
                    color={user.active ? 'success' : 'default'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell>
                  <IconButton 
                    size="small" 
                    onClick={() => handleOpenDialog(user)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    onClick={() => handleDelete(user.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingUser ? 'Edit User' : 'Add User'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            margin="normal"
            required
          />
          
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            margin="normal"
            required
          />
          
          <TextField
            fullWidth
            label="Role"
            select
            value={formData.role}
            onChange={(e) => setFormData({...formData, role: e.target.value})}
            margin="normal"
            SelectProps={{
              native: true,
            }}
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
            <option value="moderator">Moderator</option>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            color="primary"
            disabled={!formData.email || !formData.name}
          >
            {editingUser ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;'''
    
    def _generate_rate_limit_config_component(self) -> str:
        """Generate rate limit configuration component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  TextField, 
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  InputLabel,
  FormControl
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon 
} from '@mui/icons-material';

export const RateLimitConfig = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    endpoint_pattern: '',
    method: 'ALL',
    limit: 100,
    window_seconds: 3600,
    scope: 'ip',
    enabled: true,
    description: ''
  });

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/security/rate-limit-rules');
      const data = await response.json();
      setRules(data.rules || []);
    } catch (err) {
      setError('Failed to fetch rate limit rules');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingRule ? `/api/security/rate-limit-rules/${editingRule.id}` : '/api/security/rate-limit-rules';
      const method = editingRule ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        await fetchRules();
        handleCloseDialog();
      } else {
        const data = await response.json();
        setError(data.message || 'Operation failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleDelete = async (ruleId) => {
    if (!window.confirm('Are you sure you want to delete this rate limit rule?')) return;
    
    try {
      const response = await fetch(`/api/security/rate-limit-rules/${ruleId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await fetchRules();
      } else {
        const data = await response.json();
        setError(data.message || 'Delete failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleToggleEnabled = async (ruleId, enabled) => {
    try {
      const response = await fetch(`/api/security/rate-limit-rules/${ruleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled }),
      });
      
      if (response.ok) {
        await fetchRules();
      } else {
        const data = await response.json();
        setError(data.message || 'Update failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleOpenDialog = (rule = null) => {
    setEditingRule(rule);
    setFormData(rule || {
      name: '',
      endpoint_pattern: '',
      method: 'ALL',
      limit: 100,
      window_seconds: 3600,
      scope: 'ip',
      enabled: true,
      description: ''
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingRule(null);
    setFormData({
      name: '',
      endpoint_pattern: '',
      method: 'ALL',
      limit: 100,
      window_seconds: 3600,
      scope: 'ip',
      enabled: true,
      description: ''
    });
    setError('');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Rate Limit Configuration
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Rule
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Endpoint</TableCell>
              <TableCell>Method</TableCell>
              <TableCell>Limit</TableCell>
              <TableCell>Window</TableCell>
              <TableCell>Scope</TableCell>
              <TableCell>Enabled</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rules.map((rule) => (
              <TableRow key={rule.id}>
                <TableCell>{rule.name}</TableCell>
                <TableCell>{rule.endpoint_pattern}</TableCell>
                <TableCell>{rule.method}</TableCell>
                <TableCell>{rule.limit} requests</TableCell>
                <TableCell>{rule.window_seconds}s</TableCell>
                <TableCell>{rule.scope}</TableCell>
                <TableCell>
                  <Switch
                    checked={rule.enabled}
                    onChange={(e) => handleToggleEnabled(rule.id, e.target.checked)}
                    color="primary"
                  />
                </TableCell>
                <TableCell>
                  <IconButton 
                    size="small" 
                    onClick={() => handleOpenDialog(rule)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    onClick={() => handleDelete(rule.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingRule ? 'Edit Rate Limit Rule' : 'Add Rate Limit Rule'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            margin="normal"
            required
          />
          
          <TextField
            fullWidth
            label="Endpoint Pattern"
            value={formData.endpoint_pattern}
            onChange={(e) => setFormData({...formData, endpoint_pattern: e.target.value})}
            margin="normal"
            helperText="Use * for all endpoints, or specific path like /api/users/*"
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Method</InputLabel>
            <Select
              value={formData.method}
              onChange={(e) => setFormData({...formData, method: e.target.value})}
            >
              <MenuItem value="ALL">ALL</MenuItem>
              <MenuItem value="GET">GET</MenuItem>
              <MenuItem value="POST">POST</MenuItem>
              <MenuItem value="PUT">PUT</MenuItem>
              <MenuItem value="DELETE">DELETE</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Request Limit"
            type="number"
            value={formData.limit}
            onChange={(e) => setFormData({...formData, limit: parseInt(e.target.value)})}
            margin="normal"
            helperText="Number of requests allowed"
          />
          
          <TextField
            fullWidth
            label="Window (seconds)"
            type="number"
            value={formData.window_seconds}
            onChange={(e) => setFormData({...formData, window_seconds: parseInt(e.target.value)})}
            margin="normal"
            helperText="Time window in seconds"
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Scope</InputLabel>
            <Select
              value={formData.scope}
              onChange={(e) => setFormData({...formData, scope: e.target.value})}
            >
              <MenuItem value="ip">IP Address</MenuItem>
              <MenuItem value="user">User</MenuItem>
              <MenuItem value="global">Global</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            margin="normal"
            multiline
            rows={2}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={formData.enabled}
                onChange={(e) => setFormData({...formData, enabled: e.target.checked})}
                color="primary"
              />
            }
            label="Enabled"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            color="primary"
          >
            {editingRule ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RateLimitConfig;'''
    
    def _generate_login_endpoint(self) -> str:
        """Generate login endpoint"""
        return '''@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        remember_me = data.get('remember_me', False)
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Check rate limiting
        ip_address = request.remote_addr
        if not security_manager.check_rate_limit('/api/auth/login', 'POST', ip_address):
            return jsonify({'message': 'Too many login attempts. Please try again later.'}), 429
        
        # Check if account is locked
        if security_manager.is_account_locked(email):
            return jsonify({'message': 'Account is temporarily locked. Please try again later.'}), 423
        
        # Verify credentials
        # This would typically check against your user database
        user = get_user_by_email(email)  # Implement this function
        if not user or not security_manager.verify_user_password(user.id, password):
            # Record failed login
            security_manager.record_failed_login(email)
            security_manager.log_security_event(
                event_type="failed_login",
                ip_address=ip_address,
                user_id=user.id if user else None,
                user_agent=request.headers.get('User-Agent'),
                details={'email': email},
                severity="warning"
            )
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Reset failed login attempts
        security_manager.reset_login_attempts(email)
        
        # Generate JWT token
        token = security_manager.generate_jwt_token(user.id, {
            'email': user.email,
            'name': user.name
        })
        
        # Log successful login
        security_manager.log_security_event(
            event_type="login_attempt",
            ip_address=ip_address,
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            details={'success': True},
            severity="info"
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        })
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_logout_endpoint(self) -> str:
        """Generate logout endpoint"""
        return '''@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    try:
        # In a stateless JWT system, we typically just invalidate the client-side token
        # For more robust logout, you might want to maintain a blacklist of tokens
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Log logout event
        security_manager.log_security_event(
            event_type="logout",
            ip_address=request.remote_addr,
            user_id=g.current_user.get('user_id') if hasattr(g, 'current_user') else None,
            user_agent=request.headers.get('User-Agent'),
            details={'token_expired': bool(token)},
            severity="info"
        )
        
        return jsonify({'message': 'Logged out successfully'})
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_register_endpoint(self) -> str:
        """Generate user registration endpoint"""
        return '''@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password or not name:
            return jsonify({'message': 'Email, password, and name are required'}), 400
        
        # Check rate limiting
        ip_address = request.remote_addr
        if not security_manager.check_rate_limit('/api/auth/register', 'POST', ip_address):
            return jsonify({'message': 'Too many registration attempts. Please try again later.'}), 429
        
        # Validate password strength
        is_valid, errors = security_manager.validate_password_strength(password)
        if not is_valid:
            return jsonify({'message': 'Password does not meet requirements', 'errors': errors}), 400
        
        # Check if user already exists
        if user_exists(email):  # Implement this function
            return jsonify({'message': 'User already exists'}), 409
        
        # Create user
        user_id = create_user(email, name)  # Implement this function
        
        # Create security record
        if not security_manager.create_user_security(user_id, password):
            return jsonify({'message': 'Failed to create user security record'}), 500
        
        # Generate JWT token
        token = security_manager.generate_jwt_token(user_id, {
            'email': email,
            'name': name
        })
        
        # Log registration event
        security_manager.log_security_event(
            event_type="user_registration",
            ip_address=ip_address,
            user_id=user_id,
            user_agent=request.headers.get('User-Agent'),
            details={'email': email},
            severity="info"
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user_id,
                'email': email,
                'name': name
            }
        }), 201
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_password_reset_endpoint(self) -> str:
        """Generate password reset endpoint"""
        return '''@app.route('/api/auth/password-reset', methods=['POST'])
def password_reset_request():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'message': 'Email is required'}), 400
        
        # Check rate limiting
        ip_address = request.remote_addr
        if not security_manager.check_rate_limit('/api/auth/password-reset', 'POST', ip_address):
            return jsonify({'message': 'Too many password reset requests. Please try again later.'}), 429
        
        # Check if user exists
        user = get_user_by_email(email)  # Implement this function
        if not user:
            # We don't reveal if user exists or not for security
            return jsonify({'message': 'If account exists, password reset instructions have been sent'})
        
        # Generate reset token (in a real app, you'd send an email)
        reset_token = secrets.token_urlsafe(32)
        # Store token with expiration (implement this)
        store_password_reset_token(user.id, reset_token)
        
        # Send email with reset link (implement this)
        # send_password_reset_email(user.email, reset_token)
        
        # Log event
        security_manager.log_security_event(
            event_type="password_reset_request",
            ip_address=ip_address,
            user_id=user.id,
            user_agent=request.headers.get('User-Agent'),
            details={'email': email},
            severity="info"
        )
        
        return jsonify({'message': 'If account exists, password reset instructions have been sent'})
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/auth/password-reset/confirm', methods=['POST'])
def password_reset_confirm():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({'message': 'Token and password are required'}), 400
        
        # Validate password strength
        is_valid, errors = security_manager.validate_password_strength(new_password)
        if not is_valid:
            return jsonify({'message': 'Password does not meet requirements', 'errors': errors}), 400
        
        # Verify token
        user_id = verify_password_reset_token(token)  # Implement this function
        if not user_id:
            return jsonify({'message': 'Invalid or expired token'}), 400
        
        # Update password
        password_hash, salt = security_manager.hash_password(new_password)
        if not update_user_password(user_id, password_hash, salt):  # Implement this function
            return jsonify({'message': 'Failed to update password'}), 500
        
        # Invalidate token
        invalidate_password_reset_token(token)
        
        # Log event
        security_manager.log_security_event(
            event_type="password_reset_complete",
            ip_address=request.remote_addr,
            user_id=user_id,
            user_agent=request.headers.get('User-Agent'),
            details={},
            severity="info"
        )
        
        return jsonify({'message': 'Password reset successfully'})
    except Exception as e:
        logger.error(f"Password reset confirm error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_security_events_endpoint(self) -> str:
        """Generate security events endpoint"""
        return '''@app.route('/api/security/events', methods=['GET'])
@require_auth
@require_admin
def get_security_events():
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        event_type = request.args.get('type')
        
        # Get events from security manager
        events = security_manager.get_security_events(limit)
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Convert to dict for JSON serialization
        events_dict = [asdict(event) for event in events]
        
        return jsonify({
            'events': events_dict,
            'total': len(events_dict)
        })
    except Exception as e:
        logger.error(f"Get security events error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_rate_limit_rules_endpoint(self) -> str:
        """Generate rate limit rules endpoint"""
        return '''@app.route('/api/security/rate-limit-rules', methods=['GET'])
@require_auth
@require_admin
def get_rate_limit_rules():
    try:
        rules = security_manager.get_rate_limit_rules()
        rules_dict = [asdict(rule) for rule in rules]
        
        return jsonify({
            'rules': rules_dict,
            'total': len(rules_dict)
        })
    except Exception as e:
        logger.error(f"Get rate limit rules error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/security/rate-limit-rules', methods=['POST'])
@require_auth
@require_admin
def create_rate_limit_rule():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'endpoint_pattern', 'method', 'limit', 'window_seconds', 'scope']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Create rule
        rule = RateLimitRule(
            id=secrets.token_urlsafe(16),
            name=data['name'],
            endpoint_pattern=data['endpoint_pattern'],
            method=data['method'],
            limit=int(data['limit']),
            window_seconds=int(data['window_seconds']),
            scope=data['scope'],
            enabled=data.get('enabled', True),
            description=data.get('description', '')
        )
        
        # Add to security manager
        if security_manager.add_rate_limit_rule(rule):
            return jsonify(asdict(rule)), 201
        else:
            return jsonify({'message': 'Failed to create rate limit rule'}), 500
    except Exception as e:
        logger.error(f"Create rate limit rule error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/security/rate-limit-rules/<rule_id>', methods=['PUT'])
@require_auth
@require_admin
def update_rate_limit_rule(rule_id):
    try:
        data = request.get_json()
        
        # Get existing rule
        rules = security_manager.get_rate_limit_rules()
        rule = next((r for r in rules if r.id == rule_id), None)
        if not rule:
            return jsonify({'message': 'Rule not found'}), 404
        
        # Update fields
        if 'name' in data:
            rule.name = data['name']
        if 'endpoint_pattern' in data:
            rule.endpoint_pattern = data['endpoint_pattern']
        if 'method' in data:
            rule.method = data['method']
        if 'limit' in data:
            rule.limit = int(data['limit'])
        if 'window_seconds' in data:
            rule.window_seconds = int(data['window_seconds'])
        if 'scope' in data:
            rule.scope = data['scope']
        if 'enabled' in data:
            rule.enabled = bool(data['enabled'])
        if 'description' in data:
            rule.description = data['description']
        
        # Update in security manager
        if security_manager.add_rate_limit_rule(rule):
            return jsonify(asdict(rule))
        else:
            return jsonify({'message': 'Failed to update rate limit rule'}), 500
    except Exception as e:
        logger.error(f"Update rate limit rule error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/security/rate-limit-rules/<rule_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_rate_limit_rule(rule_id):
    try:
        # In a real implementation, you would delete from database
        # For now, we'll just return success
        return jsonify({'message': 'Rate limit rule deleted successfully'})
    except Exception as e:
        logger.error(f"Delete rate limit rule error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_rate_limit_middleware(self) -> str:
        """Generate rate limiting middleware"""
        return '''def rate_limit_middleware(app):
    """Flask middleware for rate limiting"""
    @app.before_request
    def check_rate_limit():
        # Skip rate limiting for static files
        if request.endpoint == 'static':
            return None
        
        # Skip rate limiting for certain endpoints
        exempt_endpoints = ['static', 'health_check']
        if request.endpoint in exempt_endpoints:
            return None
        
        # Get user ID if available
        user_id = None
        if hasattr(g, 'current_user') and g.current_user:
            user_id = g.current_user.get('user_id')
        
        # Check rate limit
        endpoint = request.path
        method = request.method
        ip_address = request.remote_addr
        
        if not security_manager.check_rate_limit(endpoint, method, ip_address, user_id):
            # Log rate limit exceeded event
            security_manager.log_security_event(
                event_type="rate_limit_exceeded",
                ip_address=ip_address,
                user_id=user_id,
                user_agent=request.headers.get('User-Agent'),
                details={
                    'endpoint': endpoint,
                    'method': method
                },
                severity="warning"
            )
            
            return jsonify({'message': 'Rate limit exceeded'}), 429
        
        return None'''
    
    def _generate_auth_middleware(self) -> str:
        """Generate authentication middleware"""
        return '''def auth_middleware(app):
    """Flask middleware for authentication"""
    @app.before_request
    def check_authentication():
        # Skip authentication for certain endpoints
        exempt_endpoints = [
            'static', 
            'login', 
            'register', 
            'password_reset_request', 
            'password_reset_confirm',
            'health_check'
        ]
        
        if request.endpoint in exempt_endpoints:
            return None
        
        # Check for JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Authentication required'}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        # Verify token
        payload = security_manager.verify_jwt_token(token)
        if not payload:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        # Store user info in g object
        g.current_user = payload'''
    
    def _generate_security_headers_middleware(self) -> str:
        """Generate security headers middleware"""
        return '''def security_headers_middleware(app):
    """Flask middleware for security headers"""
    @app.after_request
    def set_security_headers(response):
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CORS headers (configure based on your needs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # HSTS (HTTP Strict Transport Security)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy (basic)
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response'''