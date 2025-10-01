"""
FlashFlow Analytics and Monitoring Integration
========================================

Integration layer for analytics and monitoring engine with React components and Flask routes.
"""

import os
import json
from typing import Dict, Any, List, Optional
from flashflow_cli.services.analytics_services import AnalyticsEngine, Experiment
import logging

logger = logging.getLogger(__name__)

class AnalyticsIntegration:
    """Main analytics and monitoring integration class for FlashFlow"""
    
    def __init__(self):
        self.analytics_engine = AnalyticsEngine()
        self.generated_components = {}
        self.generated_routes = {}
    
    def initialize(self, config: Dict[str, Any] = None):
        """Initialize analytics services with FlashFlow configuration"""
        try:
            # Configure analytics engine
            analytics_config = config or {}
            db_path = analytics_config.get('db_path', 'analytics.db')
            
            self.analytics_engine = AnalyticsEngine(db_path)
            
            logger.info("Analytics integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics integration: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for analytics and monitoring"""
        components = {}
        
        try:
            # Analytics dashboard component
            components['AnalyticsDashboard'] = self._generate_analytics_dashboard_component()
            
            # User behavior component
            components['UserBehavior'] = self._generate_user_behavior_component()
            
            # Conversion tracking component
            components['ConversionTracking'] = self._generate_conversion_tracking_component()
            
            # A/B testing component
            components['ABTesting'] = self._generate_ab_testing_component()
            
            # Real-time monitoring component
            components['RealTimeMonitoring'] = self._generate_realtime_monitoring_component()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} analytics React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for analytics and monitoring"""
        routes = {}
        
        try:
            # Analytics summary endpoint
            routes['analytics_summary'] = self._generate_analytics_summary_endpoint()
            
            # Track event endpoint
            routes['track_event'] = self._generate_track_event_endpoint()
            
            # Track conversion endpoint
            routes['track_conversion'] = self._generate_track_conversion_endpoint()
            
            # Create experiment endpoint
            routes['create_experiment'] = self._generate_create_experiment_endpoint()
            
            # Assign variant endpoint
            routes['assign_variant'] = self._generate_assign_variant_endpoint()
            
            # Get experiment results endpoint
            routes['experiment_results'] = self._generate_experiment_results_endpoint()
            
            # Real-time data endpoint
            routes['realtime_data'] = self._generate_realtime_data_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} analytics Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_analytics_dashboard_component(self) -> str:
        """Generate analytics dashboard component"""
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
  TableRow
} from '@mui/material';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';

export const AnalyticsDashboard = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalyticsData();
    const interval = setInterval(fetchAnalyticsData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/analytics/summary');
      const data = await response.json();
      setAnalyticsData(data);
    } catch (err) {
      setError('Failed to fetch analytics data');
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

  if (!analyticsData) {
    return (
      <Alert severity="info">
        No analytics data available yet.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Unique Users
              </Typography>
              <Typography variant="h4" color="primary">
                {analyticsData.unique_users?.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Events
              </Typography>
              <Typography variant="h4" color="secondary">
                {analyticsData.total_events?.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Conversions
              </Typography>
              <Typography variant="h4" color="success.main">
                {analyticsData.total_conversions?.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Rate: {analyticsData.conversion_rate}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue
              </Typography>
              <Typography variant="h4" color="info.main">
                ${analyticsData.total_revenue?.toLocaleString()}
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
                Popular Pages
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Page</TableCell>
                      <TableCell align="right">Views</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analyticsData.popular_pages?.map((page, index) => (
                      <TableRow key={index}>
                        <TableCell>{page.url}</TableCell>
                        <TableCell align="right">{page.count}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Popular Events
              </Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Event</TableCell>
                      <TableCell align="right">Count</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analyticsData.popular_events?.map((event, index) => (
                      <TableRow key={index}>
                        <TableCell>{event.event}</TableCell>
                        <TableCell align="right">{event.count}</TableCell>
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

export default AnalyticsDashboard;'''
    
    def _generate_user_behavior_component(self) -> str:
        """Generate user behavior component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  CircularProgress,
  Alert,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';

export const UserBehavior = () => {
  const [behaviorData, setBehaviorData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('7');

  useEffect(() => {
    fetchBehaviorData();
  }, [timeRange]);

  const fetchBehaviorData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/analytics/behavior?days=${timeRange}`);
      const data = await response.json();
      setBehaviorData(data);
    } catch (err) {
      setError('Failed to fetch behavior data');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

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

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">
          User Behavior Analytics
        </Typography>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            label="Time Range"
          >
            <MenuItem value="1">Last 24 Hours</MenuItem>
            <MenuItem value="7">Last 7 Days</MenuItem>
            <MenuItem value="30">Last 30 Days</MenuItem>
            <MenuItem value="90">Last 90 Days</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Session Duration Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={behaviorData?.session_durations}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {behaviorData?.session_durations?.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Page Flow Analysis
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={behaviorData?.page_flows}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="page" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="visits" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserBehavior;'''
    
    def _generate_conversion_tracking_component(self) -> str:
        """Generate conversion tracking component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  CircularProgress,
  Alert,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer
} from 'recharts';

export const ConversionTracking = () => {
  const [conversionData, setConversionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newConversion, setNewConversion] = useState({
    user_id: '',
    conversion_type: '',
    value: '',
    currency: 'USD'
  });

  useEffect(() => {
    fetchConversionData();
  }, []);

  const fetchConversionData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/analytics/conversions');
      const data = await response.json();
      setConversionData(data);
    } catch (err) {
      setError('Failed to fetch conversion data');
    } finally {
      setLoading(false);
    }
  };

  const handleTrackConversion = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/analytics/track-conversion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newConversion,
          value: parseFloat(newConversion.value)
        })
      });
      
      if (response.ok) {
        fetchConversionData();
        setNewConversion({
          user_id: '',
          conversion_type: '',
          value: '',
          currency: 'USD'
        });
      }
    } catch (err) {
      console.error('Failed to track conversion:', err);
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Conversion Tracking
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Conversion Trends
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart
                  data={conversionData?.trends}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="conversions" stroke="#8884d8" activeDot={{ r: 8 }} />
                  <Line yAxisId="right" type="monotone" dataKey="revenue" stroke="#82ca9d" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Track New Conversion
              </Typography>
              <Box component="form" onSubmit={handleTrackConversion} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="User ID"
                  value={newConversion.user_id}
                  onChange={(e) => setNewConversion({...newConversion, user_id: e.target.value})}
                  required
                />
                
                <TextField
                  label="Conversion Type"
                  value={newConversion.conversion_type}
                  onChange={(e) => setNewConversion({...newConversion, conversion_type: e.target.value})}
                  required
                />
                
                <TextField
                  label="Value"
                  type="number"
                  value={newConversion.value}
                  onChange={(e) => setNewConversion({...newConversion, value: e.target.value})}
                  required
                />
                
                <FormControl fullWidth>
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={newConversion.currency}
                    onChange={(e) => setNewConversion({...newConversion, currency: e.target.value})}
                    label="Currency"
                  >
                    <MenuItem value="USD">USD</MenuItem>
                    <MenuItem value="EUR">EUR</MenuItem>
                    <MenuItem value="GBP">GBP</MenuItem>
                  </Select>
                </FormControl>
                
                <Button type="submit" variant="contained" color="primary">
                  Track Conversion
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ConversionTracking;'''
    
    def _generate_ab_testing_component(self) -> str:
        """Generate A/B testing component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  CircularProgress,
  Alert,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
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

export const ABTesting = () => {
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newExperiment, setNewExperiment] = useState({
    name: '',
    description: '',
    variants: ''
  });

  useEffect(() => {
    fetchExperiments();
  }, []);

  const fetchExperiments = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/analytics/experiments');
      const data = await response.json();
      setExperiments(data.experiments || []);
    } catch (err) {
      setError('Failed to fetch experiments');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateExperiment = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/analytics/experiments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newExperiment,
          variants: newExperiment.variants.split(',').map(v => v.trim())
        })
      });
      
      if (response.ok) {
        fetchExperiments();
        setNewExperiment({
          name: '',
          description: '',
          variants: ''
        });
      }
    } catch (err) {
      console.error('Failed to create experiment:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'completed': return 'info';
      default: return 'default';
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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        A/B Testing
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Experiments
              </Typography>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Variants</TableCell>
                      <TableCell>Results</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {experiments.map((experiment) => (
                      <TableRow key={experiment.id}>
                        <TableCell>
                          <Typography variant="body1">{experiment.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {experiment.description}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={experiment.status} 
                            color={getStatusColor(experiment.status)} 
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {experiment.variants?.map((variant, index) => (
                            <Chip 
                              key={index}
                              label={variant} 
                              size="small"
                              sx={{ mr: 0.5 }}
                            />
                          ))}
                        </TableCell>
                        <TableCell>
                          <Button 
                            size="small" 
                            href={`/analytics/experiments/${experiment.id}`}
                          >
                            View Results
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                    
                    {experiments.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={4} align="center">
                          <Typography variant="body2" color="text.secondary">
                            No experiments found
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Create New Experiment
              </Typography>
              <Box component="form" onSubmit={handleCreateExperiment} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="Experiment Name"
                  value={newExperiment.name}
                  onChange={(e) => setNewExperiment({...newExperiment, name: e.target.value})}
                  required
                />
                
                <TextField
                  label="Description"
                  value={newExperiment.description}
                  onChange={(e) => setNewExperiment({...newExperiment, description: e.target.value})}
                  multiline
                  rows={3}
                />
                
                <TextField
                  label="Variants (comma separated)"
                  value={newExperiment.variants}
                  onChange={(e) => setNewExperiment({...newExperiment, variants: e.target.value})}
                  helperText="e.g., Control, Variant A, Variant B"
                  required
                />
                
                <Button type="submit" variant="contained" color="primary">
                  Create Experiment
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ABTesting;'''
    
    def _generate_realtime_monitoring_component(self) -> str:
        """Generate real-time monitoring component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer
} from 'recharts';

export const RealTimeMonitoring = () => {
  const [realtimeData, setRealtimeData] = useState({
    events: [],
    activeUsers: 0,
    currentEvents: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/analytics/realtime');
        const data = await response.json();
        setRealtimeData(data);
      } catch (err) {
        setError('Failed to fetch real-time data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

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

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Real-Time Monitoring
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Users
              </Typography>
              <Typography variant="h4" color="primary">
                {realtimeData.activeUsers}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Events (Last 5 min)
              </Typography>
              <Typography variant="h4" color="secondary">
                {realtimeData.events.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Activity
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {realtimeData.currentEvents.slice(0, 5).map((event, index) => (
                  <Chip 
                    key={index}
                    label={event.type} 
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Real-Time Event Stream
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart
              data={realtimeData.events}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="count" stroke="#8884d8" fill="#8884d8" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default RealTimeMonitoring;'''
    
    def _generate_analytics_summary_endpoint(self) -> str:
        """Generate analytics summary endpoint"""
        return '''@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary data"""
    try:
        from flashflow_cli.integrations.analytics_integration import get_analytics_engine
        
        analytics_engine = get_analytics_engine()
        days = int(request.args.get('days', 30))
        
        summary = analytics_engine.get_analytics_summary(days)
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        return jsonify({'error': 'Failed to get analytics summary'}), 500'''
    
    def _generate_track_event_endpoint(self) -> str:
        """Generate track event endpoint"""
        return '''@app.route('/api/analytics/track-event', methods=['POST'])
def track_event():
    """Track a user event"""
    try:
        from flashflow_cli.integrations.analytics_integration import get_analytics_engine
        
        data = request.get_json()
        analytics_engine = get_analytics_engine()
        
        event_id = analytics_engine.track_event(
            event_type=data.get('event_type'),
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            properties=data.get('properties'),
            page_url=data.get('page_url'),
            referrer=data.get('referrer'),
            user_agent=data.get('user_agent'),
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'event_id': event_id
        })
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        return jsonify({'error': 'Failed to track event'}), 500'''
    
    def _generate_track_conversion_endpoint(self) -> str:
        """Generate track conversion endpoint"""
        return '''@app.route('/api/analytics/track-conversion', methods=['POST'])
def track_conversion():
    """Track a conversion event"""
    try:
        from flashflow_cli.integrations.analytics_integration import get_analytics_engine
        
        data = request.get_json()
        analytics_engine = get_analytics_engine()
        
        conversion_id = analytics_engine.track_conversion(
            user_id=data.get('user_id'),
            conversion_type=data.get('conversion_type'),
            value=float(data.get('value', 0)),
            currency=data.get('currency', 'USD'),
            properties=data.get('properties'),
            campaign_id=data.get('campaign_id'),
            experiment_id=data.get('experiment_id')
        )
        
        return jsonify({
            'success': True,
            'conversion_id': conversion_id
        })
    except Exception as e:
        logger.error(f"Error tracking conversion: {e}")
        return jsonify({'error': 'Failed to track conversion'}), 500'''
    
    def _generate_create_experiment_endpoint(self) -> str:
        """Generate create experiment endpoint"""
        return '''@app.route('/api/analytics/experiments', methods=['POST'])
def create_experiment():
    """Create a new A/B test experiment"""
    try:
        from flashflow_cli.integrations.analytics_integration import get_analytics_engine
        
        data = request.get_json()
        analytics_engine = get_analytics_engine()
        
        experiment_id = analytics_engine.create_experiment(
            name=data.get('name'),
            description=data.get('description'),
            variants=data.get('variants')
        )
        
        return jsonify({
            'success': True,
            'experiment_id': experiment_id
        })
    except Exception as e:
        logger.error(f"Error creating experiment: {e}")
        return jsonify({'error': 'Failed to create experiment'}), 500'''
    
    def _generate_assign_variant_endpoint(self) -> str:
        """Generate assign variant endpoint"""
        return '''@app.route('/api/analytics/experiments/<experiment_id>/assign', methods=['POST'])
def assign_variant(experiment_id):
    """Assign a user to an experiment variant"""
    try:
        from flashflow_cli.integrations.analytics_integration import get_analytics_engine
        
        data = request.get_json()
        analytics_engine = get_analytics_engine()
        
        variant = analytics_engine.assign_variant(
            experiment_id=experiment_id,
            user_id=data.get('user_id')
        )
        
        return jsonify({
            'success': True,
            'variant': variant
        })
    except Exception as e:
        logger.error(f"Error assigning variant: {e}")
        return jsonify({'error': 'Failed to assign variant'}), 500'''
    
    def _generate_experiment_results_endpoint(self) -> str:
        """Generate experiment results endpoint"""
        return '''@app.route('/api/analytics/experiments/<experiment_id>/results', methods=['GET'])
def get_experiment_results(experiment_id):
    """Get results for an experiment"""
    try:
        from flashflow_cli.integrations.analytics_integration import get_analytics_engine
        
        analytics_engine = get_analytics_engine()
        results = analytics_engine.get_experiment_results(experiment_id)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        logger.error(f"Error getting experiment results: {e}")
        return jsonify({'error': 'Failed to get experiment results'}), 500'''
    
    def _generate_realtime_data_endpoint(self) -> str:
        """Generate real-time data endpoint"""
        return '''@app.route('/api/analytics/realtime', methods=['GET'])
def get_realtime_data():
    """Get real-time analytics data"""
    try:
        from flashflow_cli.integrations.analytics_integration import get_analytics_engine
        
        analytics_engine = get_analytics_engine()
        
        # For demo purposes, return mock data
        # In a real implementation, this would query recent events
        mock_data = {
            'activeUsers': 42,
            'events': [
                {'time': '10:00', 'count': 15},
                {'time': '10:05', 'count': 23},
                {'time': '10:10', 'count': 18},
                {'time': '10:15', 'count': 32},
                {'time': '10:20', 'count': 27}
            ],
            'currentEvents': [
                {'type': 'page_view'},
                {'type': 'click'},
                {'type': 'form_submit'},
                {'type': 'purchase'}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': mock_data
        })
    except Exception as e:
        logger.error(f"Error getting real-time data: {e}")
        return jsonify({'error': 'Failed to get real-time data'}), 500'''

def get_analytics_engine():
    """Get the analytics engine instance"""
    # In a real implementation, this would return a singleton instance
    # For now, we'll create a new instance each time
    return AnalyticsEngine()

def create_analytics_integration():
    """Factory function to create analytics integration"""
    return AnalyticsIntegration()