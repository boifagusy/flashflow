"""
GraphQL Services for FlashFlow
Provides automatic GraphQL API generation from FlashFlow models
"""

import os
import json
import graphene
from graphene import Schema, ObjectType, Mutation, Field, List, String, Int, Boolean, DateTime, Float
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String as SQLString, DateTime as SQLDateTime, Boolean as SQLBoolean, Float as SQLFloat
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Dict, Any, List as PyList, Optional
import logging

logger = logging.getLogger(__name__)

class GraphQLServiceManager:
    """Main GraphQL service management class"""
    
    def __init__(self, database_url: str = "sqlite:///app.db"):
        self.database_url = database_url
        self.engine = None
        self.session = None
        self.metadata = None
        self.base = declarative_base()
        self.generated_types = {}
        self.schema = None
        self.setup_database()
    
    def setup_database(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(self.database_url)
            self.metadata = MetaData(bind=self.engine)
            session_factory = sessionmaker(bind=self.engine)
            self.session = scoped_session(session_factory)
            logger.info("GraphQL database connection established")
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            raise
    
    def generate_schema_from_models(self, models: Dict[str, Any]) -> Schema:
        """Generate GraphQL schema from FlashFlow models"""
        try:
            # Generate GraphQL types from models
            self._generate_types_from_models(models)
            
            # Create query class
            query_class = self._create_query_class()
            
            # Create mutation class
            mutation_class = self._create_mutation_class()
            
            # Create subscription class
            subscription_class = self._create_subscription_class()
            
            # Generate schema
            self.schema = Schema(
                query=query_class,
                mutation=mutation_class,
                subscription=subscription_class
            )
            
            logger.info("GraphQL schema generated successfully")
            return self.schema
            
        except Exception as e:
            logger.error(f"Failed to generate GraphQL schema: {e}")
            raise
    
    def _generate_types_from_models(self, models: Dict[str, Any]):
        """Generate GraphQL types from model definitions"""
        for model_name, model_config in models.items():
            try:
                # Generate SQLAlchemy model
                sqlalchemy_model = self._create_sqlalchemy_model(model_name, model_config)
                
                # Generate GraphQL type
                graphql_type = self._create_graphql_type(model_name, sqlalchemy_model)
                
                self.generated_types[model_name] = {
                    'sqlalchemy_model': sqlalchemy_model,
                    'graphql_type': graphql_type,
                    'config': model_config
                }
                
            except Exception as e:
                logger.error(f"Failed to generate type for {model_name}: {e}")
                continue
    
    def _create_sqlalchemy_model(self, model_name: str, model_config: Dict[str, Any]):
        """Create SQLAlchemy model from configuration"""
        fields = model_config.get('fields', {})
        
        # Build table columns
        columns = {'id': Column(Integer, primary_key=True)}
        
        for field_name, field_config in fields.items():
            field_type = field_config.get('type', 'string')
            required = field_config.get('required', False)
            
            # Map FlashFlow types to SQLAlchemy types
            if field_type == 'string':
                column_type = SQLString(255)
            elif field_type == 'integer':
                column_type = Integer
            elif field_type == 'boolean':
                column_type = SQLBoolean
            elif field_type == 'datetime':
                column_type = SQLDateTime
            elif field_type == 'float':
                column_type = SQLFloat
            else:
                column_type = SQLString(255)  # Default fallback
            
            columns[field_name] = Column(column_type, nullable=not required)
        
        # Create dynamic model class
        model_class = type(
            model_name,
            (self.base,),
            {
                '__tablename__': model_name.lower(),
                **columns
            }
        )
        
        return model_class
    
    def _create_graphql_type(self, model_name: str, sqlalchemy_model):
        """Create GraphQL type from SQLAlchemy model"""
        
        class Meta:
            model = sqlalchemy_model
            interfaces = (graphene.relay.Node,)
        
        # Create dynamic GraphQL type
        graphql_type = type(
            f"{model_name}Type",
            (SQLAlchemyObjectType,),
            {'Meta': Meta}
        )
        
        return graphql_type
    
    def _create_query_class(self):
        """Create GraphQL Query class with all model queries"""
        query_fields = {}
        
        # Add individual queries for each type
        for model_name, type_info in self.generated_types.items():
            graphql_type = type_info['graphql_type']
            
            # Single item query
            query_fields[f"get_{model_name.lower()}"] = Field(
                graphql_type,
                id=Int(required=True),
                resolver=self._create_get_resolver(type_info['sqlalchemy_model'])
            )
            
            # List query
            query_fields[f"list_{model_name.lower()}s"] = List(
                graphql_type,
                resolver=self._create_list_resolver(type_info['sqlalchemy_model'])
            )
            
            # Search query
            query_fields[f"search_{model_name.lower()}s"] = List(
                graphql_type,
                query=String(),
                resolver=self._create_search_resolver(type_info['sqlalchemy_model'])
            )
        
        # Create dynamic Query class
        query_class = type('Query', (ObjectType,), query_fields)
        return query_class
    
    def _create_mutation_class(self):
        """Create GraphQL Mutation class with CRUD operations"""
        mutation_fields = {}
        
        for model_name, type_info in self.generated_types.items():
            sqlalchemy_model = type_info['sqlalchemy_model']
            graphql_type = type_info['graphql_type']
            model_config = type_info['config']
            
            # Create mutation
            mutation_fields[f"create_{model_name.lower()}"] = Field(
                graphql_type,
                resolver=self._create_create_resolver(sqlalchemy_model, model_config)
            )
            
            # Update mutation
            mutation_fields[f"update_{model_name.lower()}"] = Field(
                graphql_type,
                id=Int(required=True),
                resolver=self._create_update_resolver(sqlalchemy_model, model_config)
            )
            
            # Delete mutation
            mutation_fields[f"delete_{model_name.lower()}"] = Boolean(
                id=Int(required=True),
                resolver=self._create_delete_resolver(sqlalchemy_model)
            )
        
        # Create dynamic Mutation class
        mutation_class = type('Mutation', (ObjectType,), mutation_fields)
        return mutation_class
    
    def _create_subscription_class(self):
        """Create GraphQL Subscription class for real-time updates"""
        subscription_fields = {}
        
        for model_name, type_info in self.generated_types.items():
            graphql_type = type_info['graphql_type']
            
            # Model created subscription
            subscription_fields[f"{model_name.lower()}_created"] = Field(
                graphql_type,
                resolver=self._create_subscription_resolver(f"{model_name}_created")
            )
            
            # Model updated subscription
            subscription_fields[f"{model_name.lower()}_updated"] = Field(
                graphql_type,
                resolver=self._create_subscription_resolver(f"{model_name}_updated")
            )
            
            # Model deleted subscription
            subscription_fields[f"{model_name.lower()}_deleted"] = Field(
                graphql_type,
                resolver=self._create_subscription_resolver(f"{model_name}_deleted")
            )
        
        # Create dynamic Subscription class
        subscription_class = type('Subscription', (ObjectType,), subscription_fields)
        return subscription_class
    
    def _create_get_resolver(self, model_class):
        """Create resolver for getting single item"""
        def resolve_get(root, info, id):
            try:
                return self.session.query(model_class).filter(model_class.id == id).first()
            except Exception as e:
                logger.error(f"Error in get resolver: {e}")
                return None
        return resolve_get
    
    def _create_list_resolver(self, model_class):
        """Create resolver for listing items"""
        def resolve_list(root, info):
            try:
                return self.session.query(model_class).all()
            except Exception as e:
                logger.error(f"Error in list resolver: {e}")
                return []
        return resolve_list
    
    def _create_search_resolver(self, model_class):
        """Create resolver for searching items"""
        def resolve_search(root, info, query=None):
            try:
                if not query:
                    return self.session.query(model_class).all()
                
                # Simple text search on string fields
                filters = []
                for column in model_class.__table__.columns:
                    if isinstance(column.type, SQLString):
                        filters.append(getattr(model_class, column.name).ilike(f"%{query}%"))
                
                if filters:
                    from sqlalchemy import or_
                    return self.session.query(model_class).filter(or_(*filters)).all()
                else:
                    return self.session.query(model_class).all()
                    
            except Exception as e:
                logger.error(f"Error in search resolver: {e}")
                return []
        return resolve_search
    
    def _create_create_resolver(self, model_class, model_config):
        """Create resolver for creating items"""
        def resolve_create(root, info, **kwargs):
            try:
                # Filter valid fields
                valid_fields = {}
                for field_name, field_value in kwargs.items():
                    if hasattr(model_class, field_name):
                        valid_fields[field_name] = field_value
                
                # Create new instance
                instance = model_class(**valid_fields)
                self.session.add(instance)
                self.session.commit()
                
                return instance
                
            except Exception as e:
                logger.error(f"Error in create resolver: {e}")
                self.session.rollback()
                return None
        return resolve_create
    
    def _create_update_resolver(self, model_class, model_config):
        """Create resolver for updating items"""
        def resolve_update(root, info, id, **kwargs):
            try:
                # Find existing instance
                instance = self.session.query(model_class).filter(model_class.id == id).first()
                if not instance:
                    return None
                
                # Update fields
                for field_name, field_value in kwargs.items():
                    if hasattr(instance, field_name):
                        setattr(instance, field_name, field_value)
                
                self.session.commit()
                return instance
                
            except Exception as e:
                logger.error(f"Error in update resolver: {e}")
                self.session.rollback()
                return None
        return resolve_update
    
    def _create_delete_resolver(self, model_class):
        """Create resolver for deleting items"""
        def resolve_delete(root, info, id):
            try:
                instance = self.session.query(model_class).filter(model_class.id == id).first()
                if not instance:
                    return False
                
                self.session.delete(instance)
                self.session.commit()
                return True
                
            except Exception as e:
                logger.error(f"Error in delete resolver: {e}")
                self.session.rollback()
                return False
        return resolve_delete
    
    def _create_subscription_resolver(self, event_name):
        """Create resolver for subscriptions"""
        def resolve_subscription(root, info):
            # In a real implementation, this would use WebSocket connections
            # For now, return a placeholder
            return None
        return resolve_subscription
    
    def generate_schema_sdl(self) -> str:
        """Generate Schema Definition Language (SDL) string"""
        if not self.schema:
            return ""
        
        try:
            # Generate SDL from schema
            sdl_parts = ["# FlashFlow Auto-Generated GraphQL Schema\n"]
            
            # Add type definitions
            for model_name, type_info in self.generated_types.items():
                model_config = type_info['config']
                fields = model_config.get('fields', {})
                
                sdl_parts.append(f"type {model_name} {{")
                sdl_parts.append("  id: ID!")
                
                for field_name, field_config in fields.items():
                    field_type = self._map_type_to_graphql(field_config.get('type', 'string'))
                    required = "!" if field_config.get('required', False) else ""
                    sdl_parts.append(f"  {field_name}: {field_type}{required}")
                
                sdl_parts.append("}\n")
            
            # Add Query type
            sdl_parts.append("type Query {")
            for model_name in self.generated_types.keys():
                model_lower = model_name.lower()
                sdl_parts.append(f"  get_{model_lower}(id: ID!): {model_name}")
                sdl_parts.append(f"  list_{model_lower}s: [{model_name}]")
                sdl_parts.append(f"  search_{model_lower}s(query: String): [{model_name}]")
            sdl_parts.append("}\n")
            
            # Add Mutation type
            sdl_parts.append("type Mutation {")
            for model_name, type_info in self.generated_types.items():
                model_lower = model_name.lower()
                model_config = type_info['config']
                fields = model_config.get('fields', {})
                
                # Create mutation
                create_args = []
                update_args = ["id: ID!"]
                
                for field_name, field_config in fields.items():
                    field_type = self._map_type_to_graphql(field_config.get('type', 'string'))
                    required = "!" if field_config.get('required', False) else ""
                    create_args.append(f"{field_name}: {field_type}{required}")
                    update_args.append(f"{field_name}: {field_type}")
                
                sdl_parts.append(f"  create_{model_lower}({', '.join(create_args)}): {model_name}")
                sdl_parts.append(f"  update_{model_lower}({', '.join(update_args)}): {model_name}")
                sdl_parts.append(f"  delete_{model_lower}(id: ID!): Boolean")
            sdl_parts.append("}\n")
            
            # Add Subscription type
            sdl_parts.append("type Subscription {")
            for model_name in self.generated_types.keys():
                model_lower = model_name.lower()
                sdl_parts.append(f"  {model_lower}_created: {model_name}")
                sdl_parts.append(f"  {model_lower}_updated: {model_name}")
                sdl_parts.append(f"  {model_lower}_deleted: {model_name}")
            sdl_parts.append("}")
            
            return "\n".join(sdl_parts)
            
        except Exception as e:
            logger.error(f"Failed to generate SDL: {e}")
            return ""
    
    def _map_type_to_graphql(self, flow_type: str) -> str:
        """Map FlashFlow types to GraphQL types"""
        type_mapping = {
            'string': 'String',
            'integer': 'Int',
            'boolean': 'Boolean',
            'datetime': 'DateTime',
            'float': 'Float'
        }
        return type_mapping.get(flow_type, 'String')
    
    def create_tables(self):
        """Create database tables for all models"""
        try:
            self.base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise

class GraphQLPlaygroundService:
    """Service for GraphQL Playground interface"""
    
    def __init__(self, schema: Schema):
        self.schema = schema
    
    def generate_playground_html(self, endpoint: str = "/graphql") -> str:
        """Generate GraphQL Playground HTML"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>FlashFlow GraphQL Playground</title>
    <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/css/index.css"
    />
    <link
        rel="shortcut icon"
        href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/favicon.png"
    />
    <script
        src="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/middleware.js"
    ></script>
</head>
<body>
    <div id="root">
        <style>
            body {{
                background-color: rgb(23, 42, 58);
                font-family: Open Sans, sans-serif;
                height: 90vh;
            }}
            #root {{
                height: 100%;
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .loading {{
                font-size: 32px;
                font-weight: 200;
                color: rgba(255, 255, 255, .6);
                margin-left: 20px;
            }}
            img {{
                width: 78px;
                height: 78px;
            }}
            .title {{
                font-weight: 400;
            }}
        </style>
        <img
            src="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/logo.png"
            alt=""
        />
        <div class="loading">Loading FlashFlow GraphQL Playground...</div>
    </div>
    <script>
        window.addEventListener('load', function (event) {{
            GraphQLPlayground.init(document.getElementById('root'), {{
                endpoint: '{endpoint}',
                settings: {{
                    'editor.theme': 'dark'
                }},
                tabs: [
                    {{
                        endpoint: '{endpoint}',
                        query: `# Welcome to FlashFlow GraphQL Playground
# 
# Type queries in the left panel and see the results in the right panel.
#
# Example query:
query {{
  # Replace with your actual model queries
}}

# Example mutation:
mutation {{
  # Replace with your actual mutations
}}

# Example subscription:
subscription {{
  # Replace with your actual subscriptions
}}`
                    }}
                ]
            }})
        }})
    </script>
</body>
</html>
        """

class GraphQLIntrospectionService:
    """Service for GraphQL introspection and documentation"""
    
    def __init__(self, schema: Schema):
        self.schema = schema
    
    def get_schema_introspection(self) -> Dict[str, Any]:
        """Get full schema introspection data"""
        try:
            from graphql import get_introspection_query, build_client_schema, execute
            
            introspection_query = get_introspection_query()
            result = execute(self.schema, introspection_query)
            
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to generate introspection: {e}")
            return {}
    
    def generate_documentation(self) -> str:
        """Generate markdown documentation for the GraphQL API"""
        try:
            docs = ["# FlashFlow GraphQL API Documentation\n"]
            docs.append("This API was automatically generated from your FlashFlow models.\n")
            
            # Add queries section
            docs.append("## Queries\n")
            docs.append("Available query operations:\n")
            
            # Add mutations section  
            docs.append("## Mutations\n")
            docs.append("Available mutation operations:\n")
            
            # Add subscriptions section
            docs.append("## Subscriptions\n")
            docs.append("Available subscription operations:\n")
            
            # Add types section
            docs.append("## Types\n")
            docs.append("Available GraphQL types:\n")
            
            return "\n".join(docs)
            
        except Exception as e:
            logger.error(f"Failed to generate documentation: {e}")
            return "# Documentation generation failed"

def create_graphql_manager(database_url: str = "sqlite:///app.db") -> GraphQLServiceManager:
    """Factory function to create GraphQL service manager"""
    return GraphQLServiceManager(database_url)