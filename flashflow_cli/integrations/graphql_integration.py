"""
GraphQL Integration for FlashFlow
Provides automatic GraphQL API generation integration with React components and Flask routes
"""

import os
import json
from typing import Dict, Any, List
from ..services.graphql_services import GraphQLServiceManager, GraphQLPlaygroundService, GraphQLIntrospectionService
import logging

logger = logging.getLogger(__name__)

class GraphQLIntegration:
    """Main GraphQL integration class for FlashFlow"""
    
    def __init__(self):
        self.graphql_manager = None
        self.playground_service = None
        self.introspection_service = None
        self.generated_components = {}
        self.generated_routes = {}
    
    def initialize(self, models: Dict[str, Any], database_url: str = "sqlite:///app.db"):
        """Initialize GraphQL services with FlashFlow models"""
        try:
            self.graphql_manager = GraphQLServiceManager(database_url)
            schema = self.graphql_manager.generate_schema_from_models(models)
            
            self.playground_service = GraphQLPlaygroundService(schema)
            self.introspection_service = GraphQLIntrospectionService(schema)
            
            # Create database tables
            self.graphql_manager.create_tables()
            
            logger.info("GraphQL integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize GraphQL integration: {e}")
            return False
    
    def generate_react_components(self) -> Dict[str, str]:
        """Generate React components for GraphQL operations"""
        components = {}
        
        try:
            if not self.graphql_manager:
                raise Exception("GraphQL manager not initialized")
            
            # Generate Apollo Client setup
            components['ApolloProvider'] = self._generate_apollo_provider()
            
            # Generate query components for each model
            for model_name, type_info in self.graphql_manager.generated_types.items():
                model_config = type_info['config']
                
                # List component
                components[f"{model_name}List"] = self._generate_list_component(model_name, model_config)
                
                # Form component
                components[f"{model_name}Form"] = self._generate_form_component(model_name, model_config)
                
                # Query hooks
                components[f"use{model_name}Query"] = self._generate_query_hook(model_name, model_config)
            
            # GraphQL Playground component
            components['GraphQLPlayground'] = self._generate_playground_component()
            
            self.generated_components = components
            logger.info(f"Generated {len(components)} React components")
            return components
            
        except Exception as e:
            logger.error(f"Failed to generate React components: {e}")
            return {}
    
    def generate_flask_routes(self) -> Dict[str, str]:
        """Generate Flask routes for GraphQL API"""
        routes = {}
        
        try:
            if not self.graphql_manager:
                raise Exception("GraphQL manager not initialized")
            
            # Main GraphQL endpoint
            routes['graphql_endpoint'] = self._generate_graphql_endpoint()
            
            # GraphQL Playground route
            routes['playground_route'] = self._generate_playground_route()
            
            # Schema introspection route
            routes['introspection_route'] = self._generate_introspection_route()
            
            self.generated_routes = routes
            logger.info(f"Generated {len(routes)} Flask routes")
            return routes
            
        except Exception as e:
            logger.error(f"Failed to generate Flask routes: {e}")
            return {}
    
    def _generate_apollo_provider(self) -> str:
        """Generate Apollo Client provider setup"""
        return '''import React from 'react';
import { ApolloClient, InMemoryCache, ApolloProvider as Provider, createHttpLink } from '@apollo/client';

const httpLink = createHttpLink({
  uri: '/api/graphql',
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
});

export const ApolloProvider = ({ children }) => {
  return <Provider client={client}>{children}</Provider>;
};

export default ApolloProvider;'''
    
    def _generate_list_component(self, model_name: str, model_config: Dict[str, Any]) -> str:
        """Generate list component for a model"""
        fields = model_config.get('fields', {})
        field_names = list(fields.keys())[:3]  # Limit to first 3 fields
        
        return f'''import React from 'react';
import {{ useQuery, gql }} from '@apollo/client';

const LIST_{model_name.upper()}S = gql`
  query List{model_name}s {{
    list_{model_name.lower()}s {{
      id
      {chr(10).join(['      ' + field for field in field_names])}
    }}
  }}
`;

export const {model_name}List = () => {{
  const {{ loading, error, data }} = useQuery(LIST_{model_name.upper()}S);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {{error.message}}</div>;

  const items = data?.list_{model_name.lower()}s || [];

  return (
    <div>
      <h2>{model_name}s</h2>
      {{items.map(item => (
        <div key={{item.id}}>
          <h3>{{item.{field_names[0] if field_names else 'id'}}}</h3>
          {chr(10).join([f'          <p>{{item.{field}}}</p>' for field in field_names[1:]])}
        </div>
      ))}}
    </div>
  );
}};

export default {model_name}List;'''
    
    def _generate_form_component(self, model_name: str, model_config: Dict[str, Any]) -> str:
        """Generate form component for a model"""
        fields = model_config.get('fields', {})
        
        return f'''import React, {{ useState }} from 'react';
import {{ useMutation, gql }} from '@apollo/client';

const CREATE_{model_name.upper()} = gql`
  mutation Create{model_name}({', '.join([f'${field}: String' for field in fields.keys()])}) {{
    create_{model_name.lower()}({', '.join([f'{field}: ${field}' for field in fields.keys()])}) {{
      id
      {chr(10).join(['      ' + field for field in fields.keys()])}
    }}
  }}
`;

export const {model_name}Form = () => {{
  const [formData, setFormData] = useState({{}});
  const [createMutation, {{ loading, error }}] = useMutation(CREATE_{model_name.upper()});

  const handleSubmit = async (e) => {{
    e.preventDefault();
    await createMutation({{ variables: formData }});
    setFormData({{}});
  }};

  return (
    <form onSubmit={{handleSubmit}}>
      <h3>Create {model_name}</h3>
      {chr(10).join([f'''      <input
        placeholder="{field}"
        value={{formData.{field} || ''}}
        onChange={{e => setFormData({{...formData, {field}: e.target.value}})}}
      />''' for field in fields.keys()])}
      <button type="submit" disabled={{loading}}>
        {{loading ? 'Creating...' : 'Create'}}
      </button>
      {{error && <div>Error: {{error.message}}</div>}}
    </form>
  );
}};

export default {model_name}Form;'''
    
    def _generate_query_hook(self, model_name: str, model_config: Dict[str, Any]) -> str:
        """Generate custom query hooks for a model"""
        return f'''import {{ useQuery, gql }} from '@apollo/client';

const GET_{model_name.upper()} = gql`
  query Get{model_name}($id: Int!) {{
    get_{model_name.lower()}(id: $id) {{
      id
      {chr(10).join(['      ' + field for field in model_config.get('fields', {}).keys()])}
    }}
  }}
`;

export const use{model_name}Query = () => {{
  const useGet = (id) => useQuery(GET_{model_name.upper()}, {{
    variables: {{ id: parseInt(id) }},
    skip: !id
  }});
  
  return {{ useGet }};
}};

export default use{model_name}Query;'''
    
    def _generate_playground_component(self) -> str:
        """Generate GraphQL Playground React component"""
        return '''import React from 'react';

export const GraphQLPlayground = () => {
  return (
    <div>
      <h2>GraphQL Playground</h2>
      <iframe
        src="/api/graphql/playground"
        width="100%"
        height="600px"
        frameBorder="0"
        title="GraphQL Playground"
      />
    </div>
  );
};

export default GraphQLPlayground;'''
    
    def _generate_graphql_endpoint(self) -> str:
        """Generate main GraphQL endpoint"""
        return '''from flask import Blueprint, request, jsonify
from graphql import execute
import json

graphql_bp = Blueprint('graphql', __name__)

@graphql_bp.route('/graphql', methods=['GET', 'POST'])
def graphql_endpoint():
    try:
        from flashflow_cli.integrations.graphql_integration import get_graphql_schema
        schema = get_graphql_schema()
        
        if request.method == 'GET':
            query = request.args.get('query')
            variables = request.args.get('variables')
        else:
            data = request.get_json()
            query = data.get('query')
            variables = data.get('variables')
        
        result = execute(schema, query, variable_values=variables)
        
        response_data = {'data': result.data}
        if result.errors:
            response_data['errors'] = [str(error) for error in result.errors]
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register_graphql_routes(app):
    app.register_blueprint(graphql_bp, url_prefix='/api')'''
    
    def _generate_playground_route(self) -> str:
        """Generate GraphQL Playground route"""
        return '''from flask import Blueprint, Response

playground_bp = Blueprint('playground', __name__)

@playground_bp.route('/playground')
def graphql_playground():
    try:
        from flashflow_cli.integrations.graphql_integration import get_playground_html
        html = get_playground_html()
        return Response(html, mimetype='text/html')
    except Exception as e:
        return f"Error: {str(e)}", 500

def register_playground_routes(app):
    app.register_blueprint(playground_bp, url_prefix='/api/graphql')'''
    
    def _generate_introspection_route(self) -> str:
        """Generate schema introspection route"""
        return '''from flask import Blueprint, jsonify

introspection_bp = Blueprint('introspection', __name__)

@introspection_bp.route('/introspection')
def graphql_introspection():
    try:
        from flashflow_cli.integrations.graphql_integration import get_introspection_data
        data = get_introspection_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def register_introspection_routes(app):
    app.register_blueprint(introspection_bp, url_prefix='/api/graphql')'''
    
    def _get_graphql_input_type(self, flow_type: str) -> str:
        """Map FlashFlow types to GraphQL input types"""
        type_mapping = {
            'string': 'String',
            'integer': 'Int',
            'boolean': 'Boolean',
            'datetime': 'String',  # Simplified for input
            'float': 'Float'
        }
        return type_mapping.get(flow_type, 'String')

# Global functions for Flask integration
_integration_instance = None

def initialize_graphql_integration(models: Dict[str, Any], database_url: str = "sqlite:///app.db"):
    """Initialize global GraphQL integration"""
    global _integration_instance
    _integration_instance = GraphQLIntegration()
    return _integration_instance.initialize(models, database_url)

def get_graphql_schema():
    """Get GraphQL schema from global integration"""
    if _integration_instance and _integration_instance.graphql_manager:
        return _integration_instance.graphql_manager.schema
    return None

def get_playground_html():
    """Get GraphQL Playground HTML"""
    if _integration_instance and _integration_instance.playground_service:
        return _integration_instance.playground_service.generate_playground_html()
    return "GraphQL integration not initialized"

def get_introspection_data():
    """Get GraphQL introspection data"""
    if _integration_instance and _integration_instance.introspection_service:
        return _integration_instance.introspection_service.get_schema_introspection()
    return {}

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