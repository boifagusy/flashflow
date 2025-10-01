"""
Search Integration for FlashFlow
Provides intelligent search system integration with React components and Flask routes
"""

import os
import json
from typing import Dict, Any, List, Optional
from ..services.search_services import IntelligentSearchManager, SearchResult, SearchStats
import logging

logger = logging.getLogger(__name__)

class SearchIntegration:
    """Main search integration class for FlashFlow"""
    
    def __init__(self):
        self.search_manager = IntelligentSearchManager()
        self.generated_components = {}
        self.generated_routes = {}
        self.indexed_models = set()
    
    def initialize(self, models: Dict[str, Any], config: Dict[str, Any] = None):
        """Initialize search services with FlashFlow models"""
        try:
            # Configure search system
            search_config = config or {'sqlite': {'db_path': 'search.db'}}
            self.search_manager.configure(search_config)
            
            # Index models automatically
            for model_name, model_config in models.items():
                self._setup_model_indexing(model_name, model_config)
            
            logger.info("Search integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize search integration: {e}")
            return False
    
    def _setup_model_indexing(self, model_name: str, model_config: Dict[str, Any]):
        """Setup automatic indexing for a model"""
        try:
            # Create sample data for demonstration
            sample_data = self._generate_sample_data(model_name, model_config)
            
            # Index the sample data
            if sample_data:
                success = self.search_manager.index_content(model_name.lower(), sample_data)
                if success:
                    self.indexed_models.add(model_name)
                    logger.info(f"Indexed {len(sample_data)} {model_name} documents")
            
        except Exception as e:
            logger.error(f"Failed to setup indexing for {model_name}: {e}")
    
    def _generate_sample_data(self, model_name: str, model_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate sample data for indexing demonstration"""
        # Generate different sample data based on model type
        if model_name.lower() == 'user':
            return [
                {'id': '1', 'title': 'John Doe', 'content': 'Software engineer with React and Python experience'},
                {'id': '2', 'title': 'Jane Smith', 'content': 'Product manager specializing in AI and ML products'},
                {'id': '3', 'title': 'Bob Johnson', 'content': 'Full-stack developer with Node.js and GraphQL skills'}
            ]
        elif model_name.lower() == 'post':
            return [
                {'id': '1', 'title': 'Introduction to FlashFlow', 'content': 'FlashFlow framework for rapid development'},
                {'id': '2', 'title': 'GraphQL Best Practices', 'content': 'Design efficient GraphQL APIs with optimization'},
                {'id': '3', 'title': 'Search Implementation', 'content': 'Full-text search with faceting and analytics'}
            ]
        else:
            # Generic sample data
            return [
                {'id': '1', 'title': f'Sample {model_name} 1', 'content': f'First sample {model_name.lower()} item'},
                {'id': '2', 'title': f'Sample {model_name} 2', 'content': f'Second sample {model_name.lower()} item'},
                {'id': '3', 'title': f'Sample {model_name} 3', 'content': f'Third sample {model_name.lower()} item'}
            ]
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for search functionality"""
        components = {}
        
        try:
            # Search input component
            components['SearchInput'] = self._generate_search_input_component()
            
            # Search results component
            components['SearchResults'] = self._generate_search_results_component()
            
            # Search page component
            components['SearchPage'] = self._generate_search_page_component()
            
            # Search hooks
            components['useSearch'] = self._generate_search_hooks()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} search React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for search API"""
        routes = {}
        
        try:
            # Main search endpoint
            routes['search_endpoint'] = self._generate_search_endpoint()
            
            # Search suggestions endpoint
            routes['suggestions_endpoint'] = self._generate_suggestions_endpoint()
            
            # Search analytics endpoint
            routes['analytics_endpoint'] = self._generate_analytics_endpoint()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} search Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_search_input_component(self) -> str:
        """Generate search input component"""
        return '''import React, { useState } from 'react';
import { TextField, InputAdornment, IconButton } from '@mui/material';
import { Search as SearchIcon, Clear as ClearIcon } from '@mui/icons-material';

export const SearchInput = ({ onSearch, placeholder = "Search..." }) => {
  const [query, setQuery] = useState('');

  const handleSearch = (searchQuery = query) => {
    if (searchQuery.trim()) {
      onSearch(searchQuery.trim());
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const handleClear = () => {
    setQuery('');
    onSearch('');
  };

  return (
    <TextField
      fullWidth
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      onKeyPress={handleKeyPress}
      placeholder={placeholder}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <IconButton onClick={() => handleSearch()}>
              <SearchIcon />
            </IconButton>
          </InputAdornment>
        ),
        endAdornment: query && (
          <InputAdornment position="end">
            <IconButton onClick={handleClear} size="small">
              <ClearIcon />
            </IconButton>
          </InputAdornment>
        ),
      }}
    />
  );
};

export default SearchInput;'''
    
    def _generate_search_results_component(self) -> str:
        """Generate search results component"""
        return '''import React from 'react';
import { Card, CardContent, Typography, Chip, Box, Skeleton } from '@mui/material';

export const SearchResults = ({ results, loading, query, stats }) => {
  if (loading) {
    return (
      <Box>
        {[...Array(5)].map((_, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Skeleton variant="text" width="60%" height={32} />
              <Skeleton variant="text" width="100%" />
              <Skeleton variant="text" width="80%" />
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  if (!results.length) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="h6" color="textSecondary">
          No results found for "{query}"
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {stats && (
        <Typography variant="body2" color="textSecondary" mb={2}>
          {stats.total_results} results found in {stats.query_time?.toFixed(3)}s
        </Typography>
      )}
      
      {results.map((result) => (
        <Card key={result.id} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
              <Typography variant="h6">{result.title}</Typography>
              <Chip label={result.type} size="small" variant="outlined" />
            </Box>
            
            <Typography variant="body2" color="textSecondary" paragraph>
              {result.content}
            </Typography>
            
            {result.highlights && result.highlights.length > 0 && (
              <Box mt={1}>
                {result.highlights.map((highlight, index) => (
                  <Typography 
                    key={index} 
                    variant="body2" 
                    sx={{ backgroundColor: 'yellow', display: 'inline', mx: 0.5, px: 0.5 }}
                  >
                    {highlight}
                  </Typography>
                ))}
              </Box>
            )}
            
            <Typography variant="caption" color="textSecondary">
              Score: {result.score?.toFixed(2)}
            </Typography>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default SearchResults;'''
    
    def _generate_search_page_component(self) -> str:
        """Generate complete search page component"""
        return '''import React from 'react';
import { Container, Grid, Box } from '@mui/material';
import SearchInput from './SearchInput';
import SearchResults from './SearchResults';
import { useSearch } from './useSearch';

export const SearchPage = () => {
  const { query, results, stats, loading, search } = useSearch();

  const handleSearch = (searchQuery) => {
    search(searchQuery);
  };

  return (
    <Container maxWidth="lg">
      <Box py={3}>
        <SearchInput onSearch={handleSearch} placeholder="Search across all content..." />
        
        <Box mt={3}>
          <SearchResults results={results} loading={loading} query={query} stats={stats} />
        </Box>
      </Box>
    </Container>
  );
};

export default SearchPage;'''
    
    def _generate_search_hooks(self) -> str:
        """Generate search hooks"""
        return '''import { useState } from 'react';

export const useSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const search = async (searchQuery) => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setQuery(searchQuery);
    
    try {
      const params = new URLSearchParams({ q: searchQuery });
      const response = await fetch(`/api/search?${params}`);
      const data = await response.json();
      
      setResults(data.results || []);
      setStats(data.stats || null);
      
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  return { query, results, stats, loading, search };
};

export default useSearch;'''
    
    def _generate_search_endpoint(self) -> str:
        """Generate main search endpoint"""
        return '''from flask import Blueprint, request, jsonify
import json

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search():
    """Main search endpoint"""
    try:
        from flashflow_cli.integrations.search_integration import get_search_manager
        
        search_manager = get_search_manager()
        if not search_manager:
            return jsonify({'error': 'Search system not initialized'}), 500
        
        query = request.args.get('q', '')
        page = int(request.args.get('page', 0))
        per_page = int(request.args.get('per_page', 20))
        
        # Perform search
        results, stats = search_manager.search(query=query, page=page, per_page=per_page)
        
        # Convert results to JSON
        results_data = []
        for result in results:
            results_data.append({
                'id': result.id,
                'title': result.title,
                'content': result.content,
                'type': result.type,
                'score': result.score,
                'highlights': result.highlights,
                'metadata': result.metadata,
                'url': result.url
            })
        
        stats_data = {
            'total_results': stats.total_results,
            'query_time': stats.query_time,
            'facets': stats.facets
        }
        
        return jsonify({
            'results': results_data,
            'stats': stats_data,
            'query': query
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

def register_search_routes(app):
    app.register_blueprint(search_bp, url_prefix='/api')'''
    
    def _generate_suggestions_endpoint(self) -> str:
        """Generate search suggestions endpoint"""
        return '''from flask import Blueprint, request, jsonify

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('/suggestions', methods=['GET'])
def get_suggestions():
    try:
        from flashflow_cli.integrations.search_integration import get_search_manager
        
        search_manager = get_search_manager()
        if not search_manager:
            return jsonify({'error': 'Search system not initialized'}), 500
        
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 5))
        
        suggestions = search_manager.get_suggestions(query, limit)
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        return jsonify({'error': f'Suggestions failed: {str(e)}'}), 500

def register_suggestions_routes(app):
    app.register_blueprint(suggestions_bp, url_prefix='/api/search')'''
    
    def _generate_analytics_endpoint(self) -> str:
        """Generate search analytics endpoint"""
        return '''from flask import Blueprint, jsonify

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics', methods=['GET'])
def get_analytics():
    try:
        from flashflow_cli.integrations.search_integration import get_search_manager
        
        search_manager = get_search_manager()
        if not search_manager:
            return jsonify({'error': 'Search system not initialized'}), 500
        
        analytics = search_manager.get_search_analytics()
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({'error': f'Analytics failed: {str(e)}'}), 500

def register_analytics_routes(app):
    app.register_blueprint(analytics_bp, url_prefix='/api/search')'''

# Global functions for Flask integration
_integration_instance = None

def initialize_search_integration(models: Dict[str, Any], config: Dict[str, Any] = None):
    """Initialize global search integration"""
    global _integration_instance
    _integration_instance = SearchIntegration()
    return _integration_instance.initialize(models, config)

def get_search_manager():
    """Get search manager from global integration"""
    if _integration_instance:
        return _integration_instance.search_manager
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