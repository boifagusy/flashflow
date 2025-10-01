"""
FlashFlow Wallet and Referrals Integration
========================================

Integration layer for wallet and referral systems with React components and Flask routes.
"""

import os
import json
from typing import Dict, Any, List, Optional
from ..services.wallet_services import WalletManager, ReferralManager, Wallet, Transaction, Referral, ReferralProgram
import logging

logger = logging.getLogger(__name__)

class WalletIntegration:
    """Main wallet and referrals integration class for FlashFlow"""
    
    def __init__(self):
        self.wallet_manager = WalletManager()
        self.referral_manager = ReferralManager(self.wallet_manager)
        self.generated_components = {}
        self.generated_routes = {}
    
    def initialize(self, config: Dict[str, Any] = None):
        """Initialize wallet services with FlashFlow configuration"""
        try:
            # Configure wallet system
            wallet_config = config or {}
            
            # Initialize referral programs if provided
            if 'referral_programs' in wallet_config:
                for program_data in wallet_config['referral_programs']:
                    program = ReferralProgram(**program_data)
                    self.referral_manager.create_program(program)
            
            logger.info("Wallet integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize wallet integration: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for wallet and referral management"""
        components = {}
        
        try:
            # Wallet dashboard component
            components['WalletDashboard'] = self._generate_wallet_dashboard_component()
            
            # Transaction history component
            components['TransactionHistory'] = self._generate_transaction_history_component()
            
            # Transfer funds component
            components['TransferFunds'] = self._generate_transfer_funds_component()
            
            # Referral dashboard component
            components['ReferralDashboard'] = self._generate_referral_dashboard_component()
            
            # Referral link generator component
            components['ReferralLinkGenerator'] = self._generate_referral_link_component()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} wallet React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for wallet and referral management"""
        routes = {}
        
        try:
            # Get wallet endpoint
            routes['get_wallet_endpoint'] = self._generate_get_wallet_endpoint()
            
            # Deposit funds endpoint
            routes['deposit_funds_endpoint'] = self._generate_deposit_funds_endpoint()
            
            # Withdraw funds endpoint
            routes['withdraw_funds_endpoint'] = self._generate_withdraw_funds_endpoint()
            
            # Transfer funds endpoint
            routes['transfer_funds_endpoint'] = self._generate_transfer_funds_endpoint()
            
            # Get transactions endpoint
            routes['get_transactions_endpoint'] = self._generate_get_transactions_endpoint()
            
            # Create referral endpoint
            routes['create_referral_endpoint'] = self._generate_create_referral_endpoint()
            
            # Get referrals endpoint
            routes['get_referrals_endpoint'] = self._generate_get_referrals_endpoint()
            
            # Convert referral endpoint
            routes['convert_referral_endpoint'] = self._generate_convert_referral_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} wallet Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_wallet_dashboard_component(self) -> str:
        """Generate wallet dashboard component"""
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
  AccountBalanceWallet as WalletIcon,
  SwapHoriz as TransferIcon,
  History as HistoryIcon,
  People as ReferralIcon
} from '@mui/icons-material';

export const WalletDashboard = () => {
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWallet();
  }, []);

  const fetchWallet = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/wallet');
      const data = await response.json();
      setWallet(data.wallet);
    } catch (err) {
      setError('Failed to fetch wallet');
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

  if (!wallet) {
    return (
      <Alert severity="info">
        You don't have a wallet yet. <Button onClick={createWallet}>Create Wallet</Button>
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <WalletIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Wallet Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Balance
              </Typography>
              <Typography variant="h4" color="primary">
                {wallet.balance} {wallet.currency}
              </Typography>
              <Chip 
                label={wallet.status} 
                color={wallet.status === 'active' ? 'success' : 'default'} 
                size="small"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Actions
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button 
                  variant="outlined" 
                  startIcon={<TransferIcon />}
                  href="/wallet/transfer"
                >
                  Transfer
                </Button>
                <Button 
                  variant="outlined" 
                  startIcon={<HistoryIcon />}
                  href="/wallet/history"
                >
                  History
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <ReferralIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Referrals
              </Typography>
              <Typography variant="body2">
                Earn rewards by referring friends
              </Typography>
              <Button 
                variant="contained" 
                href="/referrals"
                sx={{ mt: 1 }}
              >
                Invite Friends
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default WalletDashboard;'''
    
    def _generate_transaction_history_component(self) -> str:
        """Generate transaction history component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import { 
  History as HistoryIcon,
  ArrowDownward as DepositIcon,
  ArrowUpward as WithdrawalIcon,
  SwapHoriz as TransferIcon
} from '@mui/icons-material';

export const TransactionHistory = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTransactions();
  }, [filter]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/wallet/transactions?filter=${filter}`);
      const data = await response.json();
      setTransactions(data.transactions || []);
    } catch (err) {
      setError('Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'deposit':
        return <DepositIcon color="success" />;
      case 'withdrawal':
        return <WithdrawalIcon color="error" />;
      case 'transfer':
        return <TransferIcon color="primary" />;
      default:
        return null;
    }
  };

  const getTransactionColor = (type) => {
    switch (type) {
      case 'deposit':
        return 'success';
      case 'withdrawal':
        return 'error';
      case 'transfer':
        return 'primary';
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
        <Typography variant="h4">
          <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Transaction History
        </Typography>
        
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Filter</InputLabel>
          <Select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            label="Filter"
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="deposit">Deposits</MenuItem>
            <MenuItem value="withdrawal">Withdrawals</MenuItem>
            <MenuItem value="transfer">Transfers</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transactions.map((transaction) => (
              <TableRow key={transaction.id}>
                <TableCell>
                  {new Date(transaction.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    {getTransactionIcon(transaction.type)}
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      {transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>{transaction.description}</TableCell>
                <TableCell align="right">
                  <Typography 
                    color={transaction.amount > 0 ? 'success.main' : 'error.main'}
                  >
                    {transaction.amount > 0 ? '+' : ''}{transaction.amount} {transaction.currency}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={transaction.status} 
                    color={getTransactionColor(transaction.status)} 
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
            
            {transactions.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No transactions found
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default TransactionHistory;'''
    
    def _generate_transfer_funds_component(self) -> str:
        """Generate transfer funds component"""
        return '''import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button,
  Alert,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress
} from '@mui/material';
import { 
  SwapHoriz as TransferIcon,
  AccountBalance as WalletIcon
} from '@mui/icons-material';

export const TransferFunds = () => {
  const [amount, setAmount] = useState('');
  const [toWallet, setToWallet] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleTransfer = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/wallet/transfer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: parseFloat(amount),
          to_wallet: toWallet,
          description
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuccess(true);
        setAmount('');
        setToWallet('');
        setDescription('');
        setTimeout(() => setSuccess(false), 3000);
      } else {
        setError(data.error || 'Transfer failed');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <TransferIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Transfer Funds
      </Typography>
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Transfer completed successfully!
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Card>
        <CardContent>
          <form onSubmit={handleTransfer}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TextField
                label="Amount"
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
                InputProps={{
                  startAdornment: <WalletIcon sx={{ mr: 1 }} />,
                }}
              />
              
              <TextField
                label="To Wallet ID"
                value={toWallet}
                onChange={(e) => setToWallet(e.target.value)}
                required
                helperText="Enter the recipient's wallet ID"
              />
              
              <TextField
                label="Description (Optional)"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                multiline
                rows={3}
              />
              
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <TransferIcon />}
                >
                  {loading ? 'Processing...' : 'Transfer Funds'}
                </Button>
              </Box>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TransferFunds;'''
    
    def _generate_referral_dashboard_component(self) -> str:
        """Generate referral dashboard component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Grid, 
  Chip, 
  CircularProgress,
  Alert,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { 
  People as ReferralIcon,
  CheckCircle as ConvertedIcon,
  Pending as PendingIcon,
  HourglassEmpty as PendingIconAlt,
  Link as LinkIcon
} from '@mui/icons-material';

export const ReferralDashboard = () => {
  const [referrals, setReferrals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    converted: 0,
    pending: 0,
    earnings: 0
  });

  useEffect(() => {
    fetchReferrals();
  }, []);

  const fetchReferrals = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/referrals');
      const data = await response.json();
      setReferrals(data.referrals || []);
      
      // Calculate stats
      const total = data.referrals?.length || 0;
      const converted = data.referrals?.filter(r => r.status === 'converted').length || 0;
      const pending = data.referrals?.filter(r => r.status === 'pending').length || 0;
      const earnings = data.referrals?.filter(r => r.status === 'converted')
        .reduce((sum, r) => sum + parseFloat(r.reward_amount || 0), 0) || 0;
      
      setStats({ total, converted, pending, earnings });
    } catch (err) {
      setError('Failed to fetch referrals');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'converted': return 'success';
      case 'pending': return 'warning';
      case 'expired': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'converted': return <ConvertedIcon fontSize="small" />;
      case 'pending': return <PendingIcon fontSize="small" />;
      default: return null;
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
        <ReferralIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Referral Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Referrals
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
                Converted
              </Typography>
              <Typography variant="h4" color="success.main">
                {stats.converted}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Pending
              </Typography>
              <Typography variant="h4" color="warning.main">
                {stats.pending}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Earnings
              </Typography>
              <Typography variant="h4" color="secondary">
                ${stats.earnings.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Referral History
            </Typography>
            <Button 
              variant="contained" 
              startIcon={<LinkIcon />}
              href="/referrals/generate"
            >
              Generate Link
            </Button>
          </Box>
          
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Referee</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Reward</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {referrals.map((referral) => (
                  <TableRow key={referral.id}>
                    <TableCell>{referral.referee_id}</TableCell>
                    <TableCell>
                      {new Date(referral.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        icon={getStatusIcon(referral.status)}
                        label={referral.status} 
                        color={getStatusColor(referral.status)} 
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      ${parseFloat(referral.reward_amount || 0).toFixed(2)}
                    </TableCell>
                  </TableRow>
                ))}
                
                {referrals.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No referrals found
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ReferralDashboard;'''
    
    def _generate_referral_link_component(self) -> str:
        """Generate referral link generator component"""
        return '''import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Button,
  TextField,
  Alert,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { 
  Link as LinkIcon,
  ContentCopy as CopyIcon,
  Check as CheckIcon
} from '@mui/icons-material';

export const ReferralLinkGenerator = () => {
  const [referralCode, setReferralCode] = useState('');
  const [program, setProgram] = useState('default');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [copied, setCopied] = useState(false);
  const [programs, setPrograms] = useState([]);

  useEffect(() => {
    fetchPrograms();
  }, []);

  const fetchPrograms = async () => {
    try {
      const response = await fetch('/api/referral-programs');
      const data = await response.json();
      setPrograms(data.programs || []);
    } catch (err) {
      // Use default program if fetch fails
      setPrograms([{ id: 'default', name: 'Default Program' }]);
    }
  };

  const generateLink = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/referrals/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          program_id: program
        })
      });
      
      const data = await response.json();
      
      if (data.success && data.referral_code) {
        setReferralCode(data.referral_code);
        setSuccess(true);
      } else {
        setError(data.error || 'Failed to generate referral link');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (referralCode) {
      navigator.clipboard.writeText(`https://example.com/referral/${referralCode}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const referralLink = referralCode ? `https://example.com/referral/${referralCode}` : '';

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        <LinkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Generate Referral Link
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Referral Program</InputLabel>
              <Select
                value={program}
                onChange={(e) => setProgram(e.target.value)}
                label="Referral Program"
              >
                {programs.map((prog) => (
                  <MenuItem key={prog.id} value={prog.id}>
                    {prog.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={generateLink}
                disabled={loading}
                size="large"
              >
                {loading ? <CircularProgress size={20} /> : 'Generate Referral Link'}
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
      
      {success && referralCode && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Your Referral Link
            </Typography>
            
            <TextField
              fullWidth
              value={referralLink}
              InputProps={{
                readOnly: true,
              }}
              sx={{ mb: 2 }}
            />
            
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={copied ? <CheckIcon /> : <CopyIcon />}
                onClick={copyToClipboard}
              >
                {copied ? 'Copied!' : 'Copy Link'}
              </Button>
              
              <Chip 
                label="Share this link with friends to earn rewards!" 
                color="primary" 
                variant="outlined" 
              />
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ReferralLinkGenerator;'''
    
    def _generate_get_wallet_endpoint(self) -> str:
        """Generate get wallet endpoint"""
        return '''@app.route('/api/wallet', methods=['GET'])
def get_wallet():
    """Get user's wallet information"""
    try:
        # In a real implementation, get user_id from session/auth
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get wallet manager from app context
        wallet_manager = current_app.wallet_manager
        
        # Get user's wallet
        wallet = wallet_manager.get_user_wallet(user_id)
        if not wallet:
            # Create wallet if it doesn't exist
            wallet = wallet_manager.create_wallet(user_id)
        
        return jsonify({
            'success': True,
            'wallet': {
                'id': wallet.id,
                'user_id': wallet.user_id,
                'balance': float(wallet.balance),
                'currency': wallet.currency,
                'status': wallet.status,
                'created_at': wallet.created_at.isoformat() if wallet.created_at else None,
                'updated_at': wallet.updated_at.isoformat() if wallet.updated_at else None
            }
        })
    except Exception as e:
        logger.error(f"Error getting wallet: {e}")
        return jsonify({'error': 'Failed to get wallet'}), 500'''
    
    def _generate_deposit_funds_endpoint(self) -> str:
        """Generate deposit funds endpoint"""
        return '''@app.route('/api/wallet/deposit', methods=['POST'])
def deposit_funds():
    """Deposit funds into wallet"""
    try:
        # In a real implementation, get user_id from session/auth
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description', '')
        reference_id = data.get('reference_id', '')
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Get wallet manager from app context
        wallet_manager = current_app.wallet_manager
        
        # Get user's wallet
        wallet = wallet_manager.get_user_wallet(user_id)
        if not wallet:
            wallet = wallet_manager.create_wallet(user_id)
        
        # Process deposit
        transaction = wallet_manager.deposit(wallet.id, amount, description, reference_id)
        
        return jsonify({
            'success': True,
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'type': transaction.type,
                'status': transaction.status,
                'description': transaction.description,
                'created_at': transaction.created_at.isoformat() if transaction.created_at else None
            }
        })
    except Exception as e:
        logger.error(f"Error depositing funds: {e}")
        return jsonify({'error': 'Failed to deposit funds'}), 500'''
    
    def _generate_withdraw_funds_endpoint(self) -> str:
        """Generate withdraw funds endpoint"""
        return '''@app.route('/api/wallet/withdraw', methods=['POST'])
def withdraw_funds():
    """Withdraw funds from wallet"""
    try:
        # In a real implementation, get user_id from session/auth
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        amount = data.get('amount')
        description = data.get('description', '')
        reference_id = data.get('reference_id', '')
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Get wallet manager from app context
        wallet_manager = current_app.wallet_manager
        
        # Get user's wallet
        wallet = wallet_manager.get_user_wallet(user_id)
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404
        
        # Process withdrawal
        transaction = wallet_manager.withdraw(wallet.id, amount, description, reference_id)
        
        return jsonify({
            'success': True,
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'type': transaction.type,
                'status': transaction.status,
                'description': transaction.description,
                'created_at': transaction.created_at.isoformat() if transaction.created_at else None
            }
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error withdrawing funds: {e}")
        return jsonify({'error': 'Failed to withdraw funds'}), 500'''
    
    def _generate_transfer_funds_endpoint(self) -> str:
        """Generate transfer funds endpoint"""
        return '''@app.route('/api/wallet/transfer', methods=['POST'])
def transfer_funds():
    """Transfer funds between wallets"""
    try:
        # In a real implementation, get user_id from session/auth
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        amount = data.get('amount')
        to_wallet_id = data.get('to_wallet')
        description = data.get('description', '')
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        if not to_wallet_id:
            return jsonify({'error': 'Destination wallet required'}), 400
        
        # Get wallet manager from app context
        wallet_manager = current_app.wallet_manager
        
        # Get user's wallet
        from_wallet = wallet_manager.get_user_wallet(user_id)
        if not from_wallet:
            return jsonify({'error': 'Source wallet not found'}), 404
        
        # Process transfer
        transactions = wallet_manager.transfer(from_wallet.id, to_wallet_id, amount, description)
        
        return jsonify({
            'success': True,
            'transactions': [{
                'id': tx.id,
                'amount': float(tx.amount),
                'currency': tx.currency,
                'type': tx.type,
                'status': tx.status,
                'description': tx.description,
                'created_at': tx.created_at.isoformat() if tx.created_at else None
            } for tx in transactions]
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error transferring funds: {e}")
        return jsonify({'error': 'Failed to transfer funds'}), 500'''
    
    def _generate_get_transactions_endpoint(self) -> str:
        """Generate get transactions endpoint"""
        return '''@app.route('/api/wallet/transactions', methods=['GET'])
def get_wallet_transactions():
    """Get wallet transaction history"""
    try:
        # In a real implementation, get user_id from session/auth
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get filter parameter
        filter_type = request.args.get('filter', 'all')
        
        # Get wallet manager from app context
        wallet_manager = current_app.wallet_manager
        
        # Get user's wallet
        wallet = wallet_manager.get_user_wallet(user_id)
        if not wallet:
            return jsonify({'transactions': []})
        
        # Get transactions
        transactions = wallet_manager.get_wallet_transactions(wallet.id)
        
        # Apply filter if needed
        if filter_type != 'all':
            transactions = [tx for tx in transactions if tx.type == filter_type]
        
        return jsonify({
            'success': True,
            'transactions': [{
                'id': tx.id,
                'wallet_id': tx.wallet_id,
                'amount': float(tx.amount),
                'currency': tx.currency,
                'type': tx.type,
                'status': tx.status,
                'description': tx.description,
                'reference_id': tx.reference_id,
                'fee': float(tx.fee),
                'created_at': tx.created_at.isoformat() if tx.created_at else None,
                'updated_at': tx.updated_at.isoformat() if tx.updated_at else None
            } for tx in transactions]
        })
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return jsonify({'error': 'Failed to get transactions'}), 500'''
    
    def _generate_create_referral_endpoint(self) -> str:
        """Generate create referral endpoint"""
        return '''@app.route('/api/referrals/create', methods=['POST'])
def create_referral():
    """Create a new referral"""
    try:
        # In a real implementation, get user_id from session/auth
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        program_id = data.get('program_id', 'default')
        
        # Get managers from app context
        wallet_manager = current_app.wallet_manager
        referral_manager = current_app.referral_manager
        
        # Create referral
        referral = referral_manager.create_referral(user_id, f"referee_{uuid.uuid4().hex[:8]}", program_id)
        
        return jsonify({
            'success': True,
            'referral_id': referral.id,
            'referral_code': referral.referral_code
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating referral: {e}")
        return jsonify({'error': 'Failed to create referral'}), 500'''
    
    def _generate_get_referrals_endpoint(self) -> str:
        """Generate get referrals endpoint"""
        return '''@app.route('/api/referrals', methods=['GET'])
def get_referrals():
    """Get user's referrals"""
    try:
        # In a real implementation, get user_id from session/auth
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get referral manager from app context
        referral_manager = current_app.referral_manager
        
        # Get user's referrals
        referrals = referral_manager.get_user_referrals(user_id)
        
        return jsonify({
            'success': True,
            'referrals': [{
                'id': r.id,
                'referrer_id': r.referrer_id,
                'referee_id': r.referee_id,
                'status': r.status,
                'reward_amount': float(r.reward_amount),
                'currency': r.currency,
                'referral_code': r.referral_code,
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'converted_at': r.converted_at.isoformat() if r.converted_at else None,
                'expired_at': r.expired_at.isoformat() if r.expired_at else None
            } for r in referrals]
        })
    except Exception as e:
        logger.error(f"Error getting referrals: {e}")
        return jsonify({'error': 'Failed to get referrals'}), 500'''
    
    def _generate_convert_referral_endpoint(self) -> str:
        """Generate convert referral endpoint"""
        return '''@app.route('/api/referrals/convert', methods=['POST'])
def convert_referral():
    """Mark a referral as converted"""
    try:
        # In a real implementation, get user_id from session/auth
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        referral_id = data.get('referral_id')
        purchase_amount = data.get('purchase_amount')
        
        if not referral_id:
            return jsonify({'error': 'Referral ID required'}), 400
        
        # Get referral manager from app context
        referral_manager = current_app.referral_manager
        
        # Convert referral
        result = referral_manager.mark_referral_converted(referral_id, purchase_amount)
        
        return jsonify({
            'success': True,
            'converted': result
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error converting referral: {e}")
        return jsonify({'error': 'Failed to convert referral'}), 500'''
