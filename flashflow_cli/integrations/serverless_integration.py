"""
FlashFlow Serverless Integration
===============================

Integration layer for serverless functions with React components and Flask routes.
"""

import os
import json
from typing import Dict, Any, List, Optional
from ..services.serverless_services import ServerlessManager, FunctionConfig
import logging

logger = logging.getLogger(__name__)

class ServerlessIntegration:
    """Main serverless integration class for FlashFlow"""
    
    def __init__(self):
        self.serverless_manager = ServerlessManager()
        self.generated_components = {}
        self.generated_routes = {}
        self.registered_functions = []
    
    def initialize(self, config: Dict[str, Any] = None):
        """Initialize serverless services with FlashFlow configuration"""
        try:
            # Configure serverless providers
            serverless_config = config or {}
            
            # Initialize AWS if configured
            if 'aws' in serverless_config:
                result = self.serverless_manager.initialize_provider('aws', serverless_config['aws'])
                if not result['success']:
                    logger.error(f"AWS initialization failed: {result['error']}")
            
            # Initialize Google Cloud if configured
            if 'google' in serverless_config:
                result = self.serverless_manager.initialize_provider('google', serverless_config['google'])
                if not result['success']:
                    logger.error(f"Google Cloud initialization failed: {result['error']}")
            
            # Initialize Azure if configured
            if 'azure' in serverless_config:
                result = self.serverless_manager.initialize_provider('azure', serverless_config['azure'])
                if not result['success']:
                    logger.error(f"Azure initialization failed: {result['error']}")
            
            logger.info("Serverless integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize serverless integration: {e}")
            return False
    
    def register_functions_from_config(self, functions_config: Dict[str, Any]) -> bool:
        """Register functions from configuration"""
        try:
            for func_name, func_config in functions_config.items():
                # Create FunctionConfig object
                function_config = FunctionConfig(
                    name=func_name,
                    handler=func_config.get('handler', f"{func_name}.handler"),
                    runtime=func_config.get('runtime', 'python3.9'),
                    memory=func_config.get('memory', 128),
                    timeout=func_config.get('timeout', 30),
                    environment=func_config.get('environment', {}),
                    triggers=func_config.get('triggers', []),
                    permissions=func_config.get('permissions', [])
                )
                
                # Register the function
                success = self.serverless_manager.register_function(function_config)
                if success:
                    self.registered_functions.append(func_name)
                    logger.info(f"Registered function: {func_name}")
                else:
                    logger.error(f"Failed to register function: {func_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register functions: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for serverless function management"""
        components = {}
        
        try:
            # Function dashboard component
            components['FunctionDashboard'] = self._generate_function_dashboard_component()
            
            # Function editor component
            components['FunctionEditor'] = self._generate_function_editor_component()
            
            # Deployment status component
            components['DeploymentStatus'] = self._generate_deployment_status_component()
            
            # Function logs component
            components['FunctionLogs'] = self._generate_function_logs_component()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} serverless React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for serverless function management"""
        routes = {}
        
        try:
            # List functions endpoint
            routes['list_functions_endpoint'] = self._generate_list_functions_endpoint()
            
            # Deploy function endpoint
            routes['deploy_function_endpoint'] = self._generate_deploy_function_endpoint()
            
            # Get function logs endpoint
            routes['function_logs_endpoint'] = self._generate_function_logs_endpoint()
            
            # Get deployment status endpoint
            routes['deployment_status_endpoint'] = self._generate_deployment_status_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} serverless Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_function_dashboard_component(self) -> str:
        """Generate function dashboard component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Button,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import { 
  Functions as FunctionsIcon,
  CloudUpload as DeployIcon,
  History as LogsIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

export const FunctionDashboard = () => {
  const [functions, setFunctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFunctions();
  }, []);

  const fetchFunctions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/serverless/functions');
      const data = await response.json();
      setFunctions(data.functions || []);
    } catch (err) {
      setError('Failed to fetch functions');
    } finally {
      setLoading(false);
    }
  };

  const deployFunction = async (functionName) => {
    try {
      const response = await fetch(`/api/serverless/functions/${functionName}/deploy`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        // Refresh the function list
        fetchFunctions();
      }
    } catch (err) {
      console.error('Deployment failed:', err);
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
        <FunctionsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Serverless Functions
      </Typography>
      
      <Grid container spacing={3}>
        {functions.map((func) => (
          <Grid item xs={12} md={6} key={func.name}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">{func.name}</Typography>
                  <Chip 
                    label={func.status} 
                    color={func.status === 'active' ? 'success' : 'default'} 
                    size="small"
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Runtime: {func.runtime}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  Memory: {func.memory} MB
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  <Button 
                    variant="outlined" 
                    size="small"
                    startIcon={<DeployIcon />}
                    onClick={() => deployFunction(func.name)}
                    sx={{ mr: 1 }}
                  >
                    Deploy
                  </Button>
                  <Button 
                    variant="outlined" 
                    size="small"
                    startIcon={<LogsIcon />}
                    href={`/functions/${func.name}/logs`}
                  >
                    View Logs
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default FunctionDashboard;'''
    
    def _generate_function_editor_component(self) -> str:
        """Generate function editor component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  Typography, 
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Chip,
  Alert,
  Paper
} from '@mui/material';
import { 
  Save as SaveIcon,
  PlayArrow as TestIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import AceEditor from 'react-ace';

// Import Ace Editor themes and modes
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/mode-javascript';
import 'ace-builds/src-noconflict/theme-github';
import 'ace-builds/src-noconflict/ext-language_tools';

export const FunctionEditor = ({ functionName }) => {
  const [code, setCode] = useState('');
  const [runtime, setRuntime] = useState('python3.9');
  const [memory, setMemory] = useState(128);
  const [timeout, setTimeout] = useState(30);
  const [environment, setEnvironment] = useState({});
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (functionName) {
      loadFunction(functionName);
    } else {
      // Load default template
      setCode(`def handler(event, context):
    # Your function logic here
    return {
        'statusCode': 200,
        'body': 'Hello from FlashFlow!'
    }`);
    }
  }, [functionName]);

  const loadFunction = async (name) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/serverless/functions/${name}`);
      const data = await response.json();
      if (data.function) {
        setCode(data.function.code || '');
        setRuntime(data.function.runtime || 'python3.9');
        setMemory(data.function.memory || 128);
        setTimeout(data.function.timeout || 30);
        setEnvironment(data.function.environment || {});
      }
    } catch (err) {
      console.error('Failed to load function:', err);
    } finally {
      setLoading(false);
    }
  };

  const saveFunction = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/serverless/functions/${functionName || 'new'}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          runtime,
          memory,
          timeout,
          environment
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch (err) {
      console.error('Failed to save function:', err);
    } finally {
      setLoading(false);
    }
  };

  const testFunction = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/serverless/functions/${functionName || 'new'}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          testEvent: { test: 'data' }
        })
      });
      
      const data = await response.json();
      console.log('Test result:', data);
    } catch (err) {
      console.error('Test failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <CodeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Function Editor
      </Typography>
      
      {saved && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Function saved successfully!
        </Alert>
      )}
      
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Runtime</InputLabel>
              <Select
                value={runtime}
                onChange={(e) => setRuntime(e.target.value)}
              >
                <MenuItem value="python3.9">Python 3.9</MenuItem>
                <MenuItem value="python3.8">Python 3.8</MenuItem>
                <MenuItem value="nodejs16.x">Node.js 16.x</MenuItem>
                <MenuItem value="nodejs14.x">Node.js 14.x</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Typography gutterBottom>Memory (MB)</Typography>
            <Slider
              value={memory}
              onChange={(e, newValue) => setMemory(newValue)}
              min={128}
              max={3008}
              step={64}
              valueLabelDisplay="auto"
            />
            <Typography variant="body2" align="center">{memory} MB</Typography>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Typography gutterBottom>Timeout (seconds)</Typography>
            <Slider
              value={timeout}
              onChange={(e, newValue) => setTimeout(newValue)}
              min={1}
              max={900}
              step={1}
              valueLabelDisplay="auto"
            />
            <Typography variant="body2" align="center">{timeout} seconds</Typography>
          </Grid>
        </Grid>
      </Paper>
      
      <Box sx={{ mb: 3 }}>
        <AceEditor
          mode={runtime.startsWith('python') ? 'python' : 'javascript'}
          theme="github"
          onChange={setCode}
          value={code}
          name="function-editor"
          editorProps={{ $blockScrolling: true }}
          setOptions={{
            enableBasicAutocompletion: true,
            enableLiveAutocompletion: true,
            showLineNumbers: true,
            tabSize: 2,
          }}
          style={{
            width: '100%',
            height: '400px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
      </Box>
      
      <Box>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={saveFunction}
          disabled={loading}
          sx={{ mr: 2 }}
        >
          {loading ? 'Saving...' : 'Save Function'}
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<TestIcon />}
          onClick={testFunction}
          disabled={loading}
        >
          {loading ? 'Testing...' : 'Test Function'}
        </Button>
      </Box>
    </Box>
  );
};

export default FunctionEditor;'''
    
    def _generate_deployment_status_component(self) -> str:
        """Generate deployment status component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  LinearProgress, 
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import { 
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  CloudUpload as DeployIcon
} from '@mui/icons-material';

export const DeploymentStatus = ({ functionName }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (functionName) {
      fetchDeploymentStatus(functionName);
    }
  }, [functionName]);

  const fetchDeploymentStatus = async (name) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/serverless/functions/${name}/status`);
      const data = await response.json();
      setStatus(data);
    } catch (err) {
      console.error('Failed to fetch deployment status:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h6">Deployment Status</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (!status) {
    return (
      <Alert severity="info">
        No deployment status available for {functionName}
      </Alert>
    );
  }

  const getStatusIcon = (stepStatus) => {
    switch (stepStatus) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'pending':
        return <PendingIcon color="warning" />;
      default:
        return <DeployIcon />;
    }
  };

  const getStatusColor = (stepStatus) => {
    switch (stepStatus) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Deployment Status for {functionName}
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Chip 
          label={`Status: ${status.overall}`} 
          color={getStatusColor(status.overall)} 
        />
      </Box>
      
      <List>
        {status.steps?.map((step, index) => (
          <ListItem key={index}>
            <ListItemIcon>
              {getStatusIcon(step.status)}
            </ListItemIcon>
            <ListItemText 
              primary={step.name}
              secondary={step.message}
            />
            <Chip 
              label={step.status} 
              color={getStatusColor(step.status)} 
              size="small"
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default DeploymentStatus;'''
    
    def _generate_function_logs_component(self) -> str:
        """Generate function logs component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { 
  History as LogsIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Warning as WarningIcon
} from '@mui/icons-material';

export const FunctionLogs = ({ functionName }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [logLevel, setLogLevel] = useState('all');

  useEffect(() => {
    if (functionName) {
      fetchLogs(functionName);
    }
  }, [functionName, logLevel]);

  const fetchLogs = async (name) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/serverless/functions/${name}/logs?level=${logLevel}`);
      const data = await response.json();
      setLogs(data.logs || []);
    } catch (err) {
      setError('Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  };

  const getLogLevelIcon = (level) => {
    switch (level.toLowerCase()) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getLogLevelColor = (level) => {
    switch (level.toLowerCase()) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          <LogsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Function Logs
        </Typography>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Log Level</InputLabel>
          <Select
            value={logLevel}
            onChange={(e) => setLogLevel(e.target.value)}
            label="Log Level"
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="error">Error</MenuItem>
            <MenuItem value="warning">Warning</MenuItem>
            <MenuItem value="info">Info</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      <Paper sx={{ maxHeight: 400, overflow: 'auto' }}>
        <List>
          {logs.map((log, index) => (
            <ListItem key={index} divider>
              <ListItemText
                primary={
                  <Box display="flex" alignItems="center">
                    {getLogLevelIcon(log.level)}
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      {log.timestamp}
                    </Typography>
                    <Chip 
                      label={log.level} 
                      color={getLogLevelColor(log.level)} 
                      size="small" 
                      sx={{ ml: 1 }}
                    />
                  </Box>
                }
                secondary={
                  <Typography component="span" variant="body2" color="text.primary">
                    {log.message}
                  </Typography>
                }
              />
            </ListItem>
          ))}
          
          {logs.length === 0 && (
            <ListItem>
              <ListItemText 
                primary="No logs available" 
                secondary="Function may not have been executed yet"
              />
            </ListItem>
          )}
        </List>
      </Paper>
    </Box>
  );
};

export default FunctionLogs;'''
    
    def _generate_list_functions_endpoint(self) -> str:
        """Generate endpoint for listing functions"""
        return '''from flask import jsonify, request
from ..services.serverless_services import ServerlessManager

def list_functions():
    """Get list of all registered functions"""
    try:
        serverless_manager = ServerlessManager()
        status = serverless_manager.get_provider_status()
        
        # In a real implementation, this would fetch actual function data
        # For demo, we'll return sample data
        sample_functions = [
            {
                'name': 'process_image',
                'runtime': 'python3.9',
                'memory': 256,
                'timeout': 60,
                'status': 'active',
                'last_deployed': '2023-01-15T10:30:00Z'
            },
            {
                'name': 'send_email',
                'runtime': 'nodejs16.x',
                'memory': 128,
                'timeout': 30,
                'status': 'inactive',
                'last_deployed': '2023-01-10T14:20:00Z'
            },
            {
                'name': 'generate_report',
                'runtime': 'python3.9',
                'memory': 512,
                'timeout': 300,
                'status': 'active',
                'last_deployed': '2023-01-12T09:15:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'functions': sample_functions,
            'providers': status['active_providers']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add to your Flask app:
# @app.route('/api/serverless/functions', methods=['GET'])
# def api_list_functions():
#     return list_functions()'''
    
    def _generate_deploy_function_endpoint(self) -> str:
        """Generate endpoint for deploying a function"""
        return '''from flask import jsonify, request
from ..services.serverless_services import ServerlessManager, FunctionConfig

def deploy_function(function_name):
    """Deploy a function to a provider"""
    try:
        data = request.get_json()
        provider = data.get('provider', 'aws')
        
        serverless_manager = ServerlessManager()
        
        # In a real implementation, this would actually deploy the function
        # For demo, we'll simulate a successful deployment
        return jsonify({
            'success': True,
            'message': f'Function {function_name} deployed to {provider} successfully',
            'function_name': function_name,
            'provider': provider,
            'url': f'https://{function_name}.{provider}.example.com'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add to your Flask app:
# @app.route('/api/serverless/functions/<function_name>/deploy', methods=['POST'])
# def api_deploy_function(function_name):
#     return deploy_function(function_name)'''
    
    def _generate_function_logs_endpoint(self) -> str:
        """Generate endpoint for getting function logs"""
        return '''from flask import jsonify, request
from ..services.serverless_services import ServerlessManager

def get_function_logs(function_name):
    """Get logs for a specific function"""
    try:
        level = request.args.get('level', 'all')
        
        # In a real implementation, this would fetch actual logs from the provider
        # For demo, we'll return sample logs
        sample_logs = [
            {
                'timestamp': '2023-01-15T10:30:01Z',
                'level': 'info',
                'message': 'Function started'
            },
            {
                'timestamp': '2023-01-15T10:30:02Z',
                'level': 'info',
                'message': 'Processing request data'
            },
            {
                'timestamp': '2023-01-15T10:30:05Z',
                'level': 'warning',
                'message': 'High memory usage detected'
            },
            {
                'timestamp': '2023-01-15T10:30:10Z',
                'level': 'info',
                'message': 'Function completed successfully'
            }
        ]
        
        # Filter by log level if specified
        if level != 'all':
            filtered_logs = [log for log in sample_logs if log['level'] == level]
        else:
            filtered_logs = sample_logs
        
        return jsonify({
            'success': True,
            'logs': filtered_logs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add to your Flask app:
# @app.route('/api/serverless/functions/<function_name>/logs', methods=['GET'])
# def api_get_function_logs(function_name):
#     return get_function_logs(function_name)'''
    
    def _generate_deployment_status_endpoint(self) -> str:
        """Generate endpoint for getting deployment status"""
        return '''from flask import jsonify, request
from ..services.serverless_services import ServerlessManager

def get_deployment_status(function_name):
    """Get deployment status for a function"""
    try:
        # In a real implementation, this would fetch actual deployment status
        # For demo, we'll return sample status
        sample_status = {
            'function_name': function_name,
            'overall': 'success',
            'steps': [
                {
                    'name': 'Code Packaging',
                    'status': 'success',
                    'message': 'Code packaged successfully'
                },
                {
                    'name': 'Upload to Provider',
                    'status': 'success',
                    'message': 'Code uploaded to provider'
                },
                {
                    'name': 'Function Creation',
                    'status': 'success',
                    'message': 'Function created successfully'
                },
                {
                    'name': 'Trigger Setup',
                    'status': 'success',
                    'message': 'Triggers configured'
                },
                {
                    'name': 'Permission Configuration',
                    'status': 'success',
                    'message': 'Permissions set'
                }
            ]
        }
        
        return jsonify(sample_status)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add to your Flask app:
# @app.route('/api/serverless/functions/<function_name>/status', methods=['GET'])
# def api_get_deployment_status(function_name):
#     return get_deployment_status(function_name)'''