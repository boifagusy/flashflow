"""
FlashFlow Cron Integration
========================

Integration layer for cron jobs with React components and Flask routes.
"""

import os
import json
from typing import Dict, Any, List, Optional
from flashflow_cli.services.cron_services import CronJobManager
import logging

logger = logging.getLogger(__name__)

class CronIntegration:
    """Main cron jobs integration class for FlashFlow"""
    
    def __init__(self):
        self.cron_manager = None
        self.generated_components = {}
        self.generated_routes = {}
    
    def initialize(self, config: Dict[str, Any] = None):
        """Initialize cron services with FlashFlow configuration"""
        try:
            # Configure cron manager
            cron_config = config or {}
            db_path = cron_config.get('db_path', 'cron.db')
            
            self.cron_manager = CronJobManager(db_path)
            
            logger.info("Cron integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize cron integration: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for cron jobs"""
        components = {}
        
        try:
            # Cron dashboard component
            components['CronDashboard'] = self._generate_cron_dashboard_component()
            
            # Job management component
            components['JobManagement'] = self._generate_job_management_component()
            
            # Job execution logs component
            components['JobExecutionLogs'] = self._generate_job_execution_logs_component()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} cron React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for cron jobs"""
        routes = {}
        
        try:
            # Get all jobs endpoint
            routes['get_jobs'] = self._generate_get_jobs_endpoint()
            
            # Get job details endpoint
            routes['get_job_details'] = self._generate_get_job_details_endpoint()
            
            # Create job endpoint
            routes['create_job'] = self._generate_create_job_endpoint()
            
            # Update job endpoint
            routes['update_job'] = self._generate_update_job_endpoint()
            
            # Delete job endpoint
            routes['delete_job'] = self._generate_delete_job_endpoint()
            
            # Enable/disable job endpoint
            routes['toggle_job'] = self._generate_toggle_job_endpoint()
            
            # Execute job endpoint
            routes['execute_job'] = self._generate_execute_job_endpoint()
            
            # Get execution logs endpoint
            routes['get_execution_logs'] = self._generate_get_execution_logs_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} cron Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_cron_dashboard_component(self) -> str:
        """Generate cron dashboard component"""
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
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Refresh as RefreshIcon,
  BarChart as BarChartIcon
} from '@mui/icons-material';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as ChartTooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

export const CronDashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/cron/jobs');
      const data = await response.json();
      setJobs(data.jobs || []);
      
      // Calculate stats
      const enabledJobs = data.jobs ? data.jobs.filter(job => job.enabled).length : 0;
      const disabledJobs = data.jobs ? data.jobs.filter(job => !job.enabled).length : 0;
      const successCount = data.jobs ? data.jobs.reduce((sum, job) => sum + job.success_count, 0) : 0;
      const failureCount = data.jobs ? data.jobs.reduce((sum, job) => sum + job.failure_count, 0) : 0;
      
      setStats({
        total: data.jobs ? data.jobs.length : 0,
        enabled: enabledJobs,
        disabled: disabledJobs,
        success: successCount,
        failed: failureCount,
        successRate: successCount + failureCount > 0 ? (successCount / (successCount + failureCount) * 100).toFixed(1) : 0
      });
    } catch (err) {
      setError('Failed to fetch cron jobs');
    } finally {
      setLoading(false);
    }
  };

  const toggleJob = async (jobId, enabled) => {
    try {
      const response = await fetch(`/api/cron/jobs/${jobId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: !enabled }),
      });
      
      if (response.ok) {
        fetchJobs();
      } else {
        setError('Failed to toggle job');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const executeJob = async (jobId) => {
    try {
      const response = await fetch(`/api/cron/jobs/${jobId}/execute`, {
        method: 'POST',
      });
      
      if (response.ok) {
        fetchJobs();
      } else {
        setError('Failed to execute job');
      }
    } catch (err) {
      setError('Network error');
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

  // Data for charts
  const statusData = [
    { name: 'Enabled', value: stats.enabled },
    { name: 'Disabled', value: stats.disabled },
  ];
  
  const executionData = [
    { name: 'Success', value: stats.success },
    { name: 'Failed', value: stats.failed },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Cron Jobs Dashboard
        </Typography>
        <IconButton onClick={fetchJobs} color="primary">
          <RefreshIcon />
        </IconButton>
      </Box>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Jobs
              </Typography>
              <Typography variant="h4" color="primary">
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Enabled Jobs
              </Typography>
              <Typography variant="h4" color="success">
                {stats.enabled}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Success Rate
              </Typography>
              <Typography variant="h4" color="success">
                {stats.successRate}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Failed Jobs
              </Typography>
              <Typography variant="h4" color="error">
                {stats.failed}
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
                Job Status
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <ChartTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Execution Results
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={executionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {executionData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={index === 0 ? '#00C49F' : '#FF8042'} 
                      />
                    ))}
                  </Pie>
                  <ChartTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box mt={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Cron Jobs
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Schedule</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Last Run</TableCell>
                    <TableCell>Success</TableCell>
                    <TableCell>Failed</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.name}</TableCell>
                      <TableCell>{job.schedule}</TableCell>
                      <TableCell>
                        <Chip 
                          label={job.enabled ? 'Enabled' : 'Disabled'} 
                          color={job.enabled ? 'success' : 'default'} 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        {job.last_run ? new Date(job.last_run).toLocaleString() : 'Never'}
                      </TableCell>
                      <TableCell>{job.success_count}</TableCell>
                      <TableCell>{job.failure_count}</TableCell>
                      <TableCell>
                        <Tooltip title={job.enabled ? 'Disable' : 'Enable'}>
                          <IconButton 
                            size="small" 
                            onClick={() => toggleJob(job.id, job.enabled)}
                          >
                            {job.enabled ? <PauseIcon /> : <PlayIcon />}
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Execute Now">
                          <IconButton 
                            size="small" 
                            onClick={() => executeJob(job.id)}
                          >
                            <RefreshIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default CronDashboard;'''
    
    def _generate_job_management_component(self) -> str:
        """Generate job management component"""
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

export const JobManagement = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    schedule: 'every_hour',
    enabled: true
  });

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/cron/jobs');
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      setError('Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingJob ? `/api/cron/jobs/${editingJob.id}` : '/api/cron/jobs';
      const method = editingJob ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        await fetchJobs();
        handleCloseDialog();
      } else {
        const data = await response.json();
        setError(data.message || 'Operation failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleDelete = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job?')) return;
    
    try {
      const response = await fetch(`/api/cron/jobs/${jobId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        await fetchJobs();
      } else {
        const data = await response.json();
        setError(data.message || 'Delete failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleToggleEnabled = async (jobId, enabled) => {
    try {
      const response = await fetch(`/api/cron/jobs/${jobId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled }),
      });
      
      if (response.ok) {
        await fetchJobs();
      } else {
        const data = await response.json();
        setError(data.message || 'Update failed');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleOpenDialog = (job = null) => {
    setEditingJob(job);
    setFormData(job || {
      name: '',
      description: '',
      schedule: 'every_hour',
      enabled: true
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingJob(null);
    setFormData({
      name: '',
      description: '',
      schedule: 'every_hour',
      enabled: true
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
          Job Management
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Job
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
              <TableCell>Description</TableCell>
              <TableCell>Schedule</TableCell>
              <TableCell>Enabled</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.map((job) => (
              <TableRow key={job.id}>
                <TableCell>{job.name}</TableCell>
                <TableCell>{job.description}</TableCell>
                <TableCell>{job.schedule}</TableCell>
                <TableCell>
                  <Switch
                    checked={job.enabled}
                    onChange={(e) => handleToggleEnabled(job.id, e.target.checked)}
                    color="primary"
                  />
                </TableCell>
                <TableCell>
                  <IconButton 
                    size="small" 
                    onClick={() => handleOpenDialog(job)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    onClick={() => handleDelete(job.id)}
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
          {editingJob ? 'Edit Job' : 'Add Job'}
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
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
            margin="normal"
            multiline
            rows={2}
          />
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Schedule</InputLabel>
            <Select
              value={formData.schedule}
              onChange={(e) => setFormData({...formData, schedule: e.target.value})}
            >
              <MenuItem value="every_minute">Every Minute</MenuItem>
              <MenuItem value="every_5_minutes">Every 5 Minutes</MenuItem>
              <MenuItem value="every_10_minutes">Every 10 Minutes</MenuItem>
              <MenuItem value="every_30_minutes">Every 30 Minutes</MenuItem>
              <MenuItem value="every_hour">Every Hour</MenuItem>
              <MenuItem value="every_2_hours">Every 2 Hours</MenuItem>
              <MenuItem value="every_day">Every Day</MenuItem>
              <MenuItem value="every_week">Every Week</MenuItem>
            </Select>
          </FormControl>
          
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
            {editingJob ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default JobManagement;'''
    
    def _generate_job_execution_logs_component(self) -> str:
        """Generate job execution logs component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { 
  Refresh as RefreshIcon 
} from '@mui/icons-material';

export const JobExecutionLogs = () => {
  const [logs, setLogs] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedJob, setSelectedJob] = useState('all');

  useEffect(() => {
    fetchJobs();
    fetchLogs();
    const interval = setInterval(fetchLogs, 30000);
    return () => clearInterval(interval);
  }, [selectedJob]);

  const fetchJobs = async () => {
    try {
      const response = await fetch('/api/cron/jobs');
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      setError('Failed to fetch jobs');
    }
  };

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const url = selectedJob === 'all' 
        ? '/api/cron/logs' 
        : `/api/cron/jobs/${selectedJob}/logs`;
      
      const response = await fetch(url);
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (err) {
      setError('Failed to fetch execution logs');
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

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Job Execution Logs
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Filter by Job</InputLabel>
            <Select
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
              label="Filter by Job"
            >
              <MenuItem value="all">All Jobs</MenuItem>
              {jobs.map((job) => (
                <MenuItem key={job.id} value={job.id}>{job.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <IconButton onClick={fetchLogs} color="primary">
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Job</TableCell>
              <TableCell>Started</TableCell>
              <TableCell>Finished</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Output</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {logs.map((log) => {
              const job = jobs.find(j => j.id === log.job_id);
              const started = new Date(log.started_at);
              const finished = log.finished_at ? new Date(log.finished_at) : null;
              const duration = finished ? (finished - started) / 1000 : null;
              
              return (
                <TableRow key={log.id}>
                  <TableCell>{job ? job.name : log.job_id}</TableCell>
                  <TableCell>{started.toLocaleString()}</TableCell>
                  <TableCell>
                    {finished ? finished.toLocaleString() : 'Running...'}
                  </TableCell>
                  <TableCell>
                    {duration !== null ? `${duration.toFixed(2)}s` : '-'}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={log.status} 
                      color={
                        log.status === 'success' ? 'success' : 
                        log.status === 'failed' ? 'error' : 'warning'
                      } 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>
                    {log.output && (
                      <Box sx={{ 
                        maxWidth: 300, 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        {log.output}
                      </Box>
                    )}
                    {log.error && (
                      <Box sx={{ 
                        maxWidth: 300, 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        color: 'error.main'
                      }}>
                        {log.error}
                      </Box>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default JobExecutionLogs;'''
    
    def _generate_get_jobs_endpoint(self) -> str:
        """Generate get all jobs endpoint"""
        return '''@app.route('/api/cron/jobs', methods=['GET'])
@require_auth
@require_admin
def get_cron_jobs():
    try:
        jobs = cron_manager.get_jobs()
        jobs_dict = [asdict(job) for job in jobs]
        
        return jsonify({
            'jobs': jobs_dict,
            'total': len(jobs_dict)
        })
    except Exception as e:
        logger.error(f"Get cron jobs error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_get_job_details_endpoint(self) -> str:
        """Generate get job details endpoint"""
        return '''@app.route('/api/cron/jobs/<job_id>', methods=['GET'])
@require_auth
@require_admin
def get_cron_job_details(job_id):
    try:
        job = cron_manager.get_job(job_id)
        if not job:
            return jsonify({'message': 'Job not found'}), 404
        
        stats = cron_manager.get_job_stats(job_id)
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Get cron job details error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_create_job_endpoint(self) -> str:
        """Generate create job endpoint"""
        return '''@app.route('/api/cron/jobs', methods=['POST'])
@require_auth
@require_admin
def create_cron_job():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'schedule']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Create a sample job function (in a real app, you'd define actual functions)
        def sample_job():
            logger.info(f"Executing job: {data['name']}")
            return f"Job {data['name']} executed successfully"
        
        # Add job to cron manager
        job_id = cron_manager.add_job(
            name=data['name'],
            schedule=data['schedule'],
            func=sample_job,
            description=data.get('description', ''),
            enabled=data.get('enabled', True)
        )
        
        # Get the created job
        job = cron_manager.get_job(job_id)
        
        return jsonify(asdict(job)), 201
    except Exception as e:
        logger.error(f"Create cron job error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_update_job_endpoint(self) -> str:
        """Generate update job endpoint"""
        return '''@app.route('/api/cron/jobs/<job_id>', methods=['PUT'])
@require_auth
@require_admin
def update_cron_job(job_id):
    try:
        data = request.get_json()
        
        # Update job
        if cron_manager.update_job(job_id, **data):
            job = cron_manager.get_job(job_id)
            return jsonify(asdict(job))
        else:
            return jsonify({'message': 'Job not found or update failed'}), 404
    except Exception as e:
        logger.error(f"Update cron job error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_delete_job_endpoint(self) -> str:
        """Generate delete job endpoint"""
        return '''@app.route('/api/cron/jobs/<job_id>', methods=['DELETE'])
@require_auth
@require_admin
def delete_cron_job(job_id):
    try:
        if cron_manager.remove_job(job_id):
            return jsonify({'message': 'Job deleted successfully'})
        else:
            return jsonify({'message': 'Job not found or delete failed'}), 404
    except Exception as e:
        logger.error(f"Delete cron job error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_toggle_job_endpoint(self) -> str:
        """Generate toggle job endpoint"""
        return '''@app.route('/api/cron/jobs/<job_id>/toggle', methods=['POST'])
@require_auth
@require_admin
def toggle_cron_job(job_id):
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        if enabled:
            if cron_manager.enable_job(job_id):
                return jsonify({'message': 'Job enabled successfully'})
            else:
                return jsonify({'message': 'Job not found or enable failed'}), 404
        else:
            if cron_manager.disable_job(job_id):
                return jsonify({'message': 'Job disabled successfully'})
            else:
                return jsonify({'message': 'Job not found or disable failed'}), 404
    except Exception as e:
        logger.error(f"Toggle cron job error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_execute_job_endpoint(self) -> str:
        """Generate execute job endpoint"""
        return '''@app.route('/api/cron/jobs/<job_id>/execute', methods=['POST'])
@require_auth
@require_admin
def execute_cron_job(job_id):
    try:
        # In a real implementation, you would trigger the job execution
        # For now, we'll just return success
        return jsonify({'message': 'Job execution started'})
    except Exception as e:
        logger.error(f"Execute cron job error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''
    
    def _generate_get_execution_logs_endpoint(self) -> str:
        """Generate get execution logs endpoint"""
        return '''@app.route('/api/cron/logs', methods=['GET'])
@require_auth
@require_admin
def get_all_execution_logs():
    try:
        limit = int(request.args.get('limit', 100))
        logs = cron_manager.get_execution_logs(limit=limit)
        logs_dict = [asdict(log) for log in logs]
        
        return jsonify({
            'logs': logs_dict,
            'total': len(logs_dict)
        })
    except Exception as e:
        logger.error(f"Get execution logs error: {e}")
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/api/cron/jobs/<job_id>/logs', methods=['GET'])
@require_auth
@require_admin
def get_job_execution_logs(job_id):
    try:
        limit = int(request.args.get('limit', 50))
        logs = cron_manager.get_execution_logs(job_id=job_id, limit=limit)
        logs_dict = [asdict(log) for log in logs]
        
        return jsonify({
            'logs': logs_dict,
            'total': len(logs_dict)
        })
    except Exception as e:
        logger.error(f"Get job execution logs error: {e}")
        return jsonify({'message': 'Internal server error'}), 500'''