"""
Debug Integration for FlashFlow
Provides intelligent debug report and admin panel integration with React components and Flask routes
"""

import os
import json
from typing import Dict, Any, List, Optional
from ..services.debug_services import IntelligentDebugManager, ErrorReport, PerformanceMetric
import logging

logger = logging.getLogger(__name__)

class DebugIntegration:
    """Main debug integration class for FlashFlow"""
    
    def __init__(self):
        self.debug_manager = IntelligentDebugManager()
        self.generated_components = {}
        self.generated_routes = {}
    
    def initialize(self, config: Dict[str, Any] = None):
        """Initialize debug services"""
        try:
            debug_config = config or {'db_path': 'debug.db'}
            self.debug_manager = IntelligentDebugManager(debug_config.get('db_path', 'debug.db'))
            
            logger.info("Debug integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize debug integration: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for debug and admin panel"""
        components = {}
        
        try:
            # Admin dashboard component
            components['AdminDashboard'] = self._generate_admin_dashboard()
            
            # Error reports component
            components['ErrorReports'] = self._generate_error_reports_component()
            
            # Debug panel component
            components['DebugPanel'] = self._generate_debug_panel_component()
            
            # Debug hooks
            components['useDebugData'] = self._generate_debug_hooks()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} debug React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for debug and admin API"""
        routes = {}
        
        try:
            # Debug report endpoint
            routes['debug_report'] = self._generate_debug_report_endpoint()
            
            # Error tracking endpoint
            routes['error_tracking'] = self._generate_error_tracking_endpoint()
            
            # System health endpoint
            routes['system_health'] = self._generate_system_health_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} debug Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_admin_dashboard(self) -> str:
        """Generate admin dashboard component"""
        return '''import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Alert, Chip, LinearProgress
} from '@mui/material';

export const AdminDashboard = () => {
  const [systemHealth, setSystemHealth] = useState(null);
  const [errorSummary, setErrorSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [healthResponse, errorResponse] = await Promise.all([
        fetch('/api/admin/system-health'),
        fetch('/api/admin/error-summary')
      ]);

      setSystemHealth(await healthResponse.json());
      setErrorSummary(await errorResponse.json());
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LinearProgress />;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        FlashFlow Admin Dashboard
      </Typography>
      
      {systemHealth && (
        <Alert severity={systemHealth.status === 'healthy' ? 'success' : 'warning'} sx={{ mb: 3 }}>
          System Status: {systemHealth.status.toUpperCase()}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">CPU Usage</Typography>
              <Typography variant="h4" color="primary">
                {systemHealth?.cpu_percent?.toFixed(1)}%
              </Typography>
              <LinearProgress variant="determinate" value={systemHealth?.cpu_percent || 0} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Memory</Typography>
              <Typography variant="h4" color="primary">
                {systemHealth?.memory_percent?.toFixed(1)}%
              </Typography>
              <LinearProgress variant="determinate" value={systemHealth?.memory_percent || 0} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Error Rate</Typography>
              <Typography variant="h4" color="error">
                {errorSummary?.error_rate?.toFixed(2)}%
              </Typography>
              <Typography variant="body2">{errorSummary?.total_errors} total errors</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Response Time</Typography>
              <Typography variant="h4" color="primary">
                {systemHealth?.avg_response_time?.toFixed(0)}ms
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdminDashboard;'''
    
    def _generate_error_reports_component(self) -> str:
        """Generate error reports component"""
        return '''import React, { useState, useEffect } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Chip, Button, Dialog, DialogTitle, DialogContent, DialogActions, Typography, Box
} from '@mui/material';

export const ErrorReports = () => {
  const [errors, setErrors] = useState([]);
  const [selectedError, setSelectedError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);

  useEffect(() => {
    fetchErrors();
  }, []);

  const fetchErrors = async () => {
    try {
      const response = await fetch('/api/admin/errors');
      const data = await response.json();
      setErrors(data.errors || []);
    } catch (error) {
      console.error('Failed to fetch errors:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'error': return 'error';
      case 'warning': return 'warning';
      default: return 'info';
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>Error Reports</Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Message</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {errors.map((error) => (
              <TableRow key={error.id}>
                <TableCell>{new Date(error.timestamp).toLocaleString()}</TableCell>
                <TableCell>{error.error_type}</TableCell>
                <TableCell>
                  <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                    {error.error_message}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip label={error.severity} color={getSeverityColor(error.severity)} size="small" />
                </TableCell>
                <TableCell>
                  <Button size="small" onClick={() => {
                    setSelectedError(error);
                    setOpenDialog(true);
                  }}>View</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Error Details</DialogTitle>
        <DialogContent>
          {selectedError && (
            <Box>
              <Typography variant="h6">{selectedError.error_type}: {selectedError.error_message}</Typography>
              <Typography variant="body2" color="textSecondary">
                Occurred: {new Date(selectedError.timestamp).toLocaleString()}
              </Typography>
              <Typography variant="body2"><strong>Stack Trace:</strong></Typography>
              <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px', fontSize: '12px' }}>
                {selectedError.stack_trace}
              </pre>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ErrorReports;'''
    
    def _generate_debug_panel_component(self) -> str:
        """Generate debug panel component"""
        return '''import React, { useState } from 'react';
import { Drawer, Box, Typography, List, ListItem, ListItemText, Divider } from '@mui/material';
import AdminDashboard from './AdminDashboard';
import ErrorReports from './ErrorReports';

export const DebugPanel = ({ open, onClose }) => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard': return <AdminDashboard />;
      case 'errors': return <ErrorReports />;
      default: return <AdminDashboard />;
    }
  };

  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 800, height: '100%', display: 'flex' }}>
        <Box sx={{ width: 200, borderRight: 1, borderColor: 'divider' }}>
          <Box p={2}>
            <Typography variant="h6">Debug Panel</Typography>
          </Box>
          <Divider />
          <List>
            <ListItem button onClick={() => setActiveTab('dashboard')}>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem button onClick={() => setActiveTab('errors')}>
              <ListItemText primary="Error Reports" />
            </ListItem>
          </List>
        </Box>
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          {renderContent()}
        </Box>
      </Box>
    </Drawer>
  );
};

export default DebugPanel;'''
    
    def _generate_debug_hooks(self) -> str:
        """Generate debug hooks"""
        return '''import { useState, useEffect } from 'react';

export const useDebugData = () => {
  const [systemHealth, setSystemHealth] = useState(null);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDebugData();
    const interval = setInterval(fetchDebugData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDebugData = async () => {
    try {
      const [healthRes, errorsRes] = await Promise.all([
        fetch('/api/admin/system-health'),
        fetch('/api/admin/errors')
      ]);

      setSystemHealth(await healthRes.json());
      setErrors(await errorsRes.json());
    } catch (error) {
      console.error('Failed to fetch debug data:', error);
    } finally {
      setLoading(false);
    }
  };

  const reportError = async (error, context = {}) => {
    try {
      await fetch('/api/admin/report-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: error.message, context })
      });
    } catch (err) {
      console.error('Failed to report error:', err);
    }
  };

  return { systemHealth, errors, loading, reportError, refresh: fetchDebugData };
};

export default useDebugData;'''
    
    def _generate_debug_report_endpoint(self) -> str:
        """Generate debug report endpoint"""
        return '''from flask import Blueprint, jsonify, request

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug-report', methods=['GET'])
def get_debug_report():
    """Generate comprehensive debug report"""
    try:
        from flashflow_cli.integrations.debug_integration import get_debug_manager
        
        debug_manager = get_debug_manager()
        if not debug_manager:
            return jsonify({'error': 'Debug system not initialized'}), 500
        
        include_performance = request.args.get('include_performance', 'true').lower() == 'true'
        report = debug_manager.generate_debug_report(include_performance)
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate debug report: {str(e)}'}), 500

def register_debug_routes(app):
    app.register_blueprint(debug_bp, url_prefix='/api/admin')'''
    
    def _generate_error_tracking_endpoint(self) -> str:
        """Generate error tracking endpoint"""
        return '''from flask import Blueprint, jsonify, request

errors_bp = Blueprint('errors', __name__)

@errors_bp.route('/errors', methods=['GET'])
def get_errors():
    """Get error reports with filters"""
    try:
        from flashflow_cli.integrations.debug_integration import get_debug_manager
        
        debug_manager = get_debug_manager()
        if not debug_manager:
            return jsonify({'error': 'Debug system not initialized'}), 500
        
        severity = request.args.get('severity')
        limit = int(request.args.get('limit', 100))
        
        errors = debug_manager.error_tracker.get_error_reports(
            severity=severity if severity != 'all' else None,
            limit=limit
        )
        
        return jsonify({
            'errors': [
                {
                    'id': e.id,
                    'timestamp': e.timestamp.isoformat(),
                    'error_type': e.error_type,
                    'error_message': e.error_message,
                    'severity': e.severity,
                    'user_id': e.user_id,
                    'resolved': e.resolved,
                    'stack_trace': e.stack_trace
                } for e in errors
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get errors: {str(e)}'}), 500

@errors_bp.route('/error-summary', methods=['GET'])
def get_error_summary():
    """Get error analytics summary"""
    try:
        from flashflow_cli.integrations.debug_integration import get_debug_manager
        
        debug_manager = get_debug_manager()
        analytics = debug_manager.error_tracker.get_error_analytics()
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get error summary: {str(e)}'}), 500

def register_error_routes(app):
    app.register_blueprint(errors_bp, url_prefix='/api/admin')'''
    
    def _generate_system_health_endpoint(self) -> str:
        """Generate system health endpoint"""
        return '''from flask import Blueprint, jsonify
import psutil
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/system-health', methods=['GET'])
def get_system_health():
    """Get current system health status"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Determine status
        if cpu_percent > 90 or memory.percent > 90:
            status = 'critical'
        elif cpu_percent > 70 or memory.percent > 70:
            status = 'warning'
        else:
            status = 'healthy'
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'status': status,
            'avg_response_time': 100.0,  # Placeholder
            'active_connections': len(psutil.net_connections())
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get system health: {str(e)}'}), 500

def register_health_routes(app):
    app.register_blueprint(health_bp, url_prefix='/api/admin')'''

# Global functions for Flask integration
_integration_instance = None

def initialize_debug_integration(config: Dict[str, Any] = None):
    """Initialize global debug integration"""
    global _integration_instance
    _integration_instance = DebugIntegration()
    return _integration_instance.initialize(config)

def get_debug_manager():
    """Get debug manager from global integration"""
    if _integration_instance:
        return _integration_instance.debug_manager
    return None

def get_generated_components():
    """Get generated React components"""
    if _integration_instance:
        return _integration_instance.generate_react_components()
    return {}

def get_generated_routes():
    """Get generated Flask routes"""
    if _integration_instance:
        return _integration_instance.generate_flask_routes()
    return {}