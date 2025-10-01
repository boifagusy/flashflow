"""
Intelligent Search Services for FlashFlow
Provides advanced search functionality with multiple backends and AI-powered features
"""

import os
import json
import re
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Search result item"""
    id: str
    title: str
    content: str
    type: str
    score: float
    highlights: List[str]
    metadata: Dict[str, Any]
    url: Optional[str] = None

@dataclass
class SearchQuery:
    """Search query parameters"""
    query: str
    filters: Dict[str, Any]
    sort: str
    page: int
    per_page: int
    facets: List[str]
    suggest: bool

@dataclass
class SearchStats:
    """Search analytics data"""
    total_results: int
    query_time: float
    facets: Dict[str, List[Dict[str, Any]]]
    suggestions: List[str]
    related_queries: List[str]

class SearchEngineBase:
    """Base class for search engines"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "base"
    
    def index_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index a single document"""
        raise NotImplementedError
    
    def bulk_index(self, documents: List[Dict[str, Any]]) -> bool:
        """Index multiple documents"""
        raise NotImplementedError
    
    def search(self, query: SearchQuery) -> Tuple[List[SearchResult], SearchStats]:
        """Perform search"""
        raise NotImplementedError
    
    def suggest(self, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions"""
        raise NotImplementedError
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from index"""
        raise NotImplementedError

class SQLiteSearchEngine(SearchEngineBase):
    """SQLite-based search engine with FTS support"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "sqlite"
        self.db_path = config.get('db_path', 'search.db')
        self.setup_database()
    
    def setup_database(self):
        """Initialize SQLite FTS database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create FTS virtual table
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS search_index 
                USING fts5(id, title, content, type, metadata, tokenize='porter')
            ''')
            
            # Create suggestions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_suggestions (
                    query TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    results_count INTEGER,
                    query_time REAL,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("SQLite search database initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup SQLite search database: {e}")
            raise
    
    def index_document(self, doc_id: str, document: Dict[str, Any]) -> bool:
        """Index a single document"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO search_index 
                (id, title, content, type, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                doc_id,
                document.get('title', ''),
                document.get('content', ''),
                document.get('type', 'document'),
                json.dumps(document.get('metadata', {}))
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}")
            return False
    
    def bulk_index(self, documents: List[Dict[str, Any]]) -> bool:
        """Index multiple documents"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            data = []
            for doc in documents:
                data.append((
                    doc.get('id', ''),
                    doc.get('title', ''),
                    doc.get('content', ''),
                    doc.get('type', 'document'),
                    json.dumps(doc.get('metadata', {}))
                ))
            
            cursor.executemany('''
                INSERT OR REPLACE INTO search_index 
                (id, title, content, type, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', data)
            
            conn.commit()
            conn.close()
            logger.info(f"Bulk indexed {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to bulk index documents: {e}")
            return False
    
    def search(self, query: SearchQuery) -> Tuple[List[SearchResult], SearchStats]:
        """Perform search with FTS"""
        start_time = datetime.now()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build FTS query
            fts_query = self._build_fts_query(query.query)
            
            # Execute search
            cursor.execute('''
                SELECT id, title, content, type, metadata, rank
                FROM search_index
                WHERE search_index MATCH ?
                ORDER BY rank
                LIMIT ? OFFSET ?
            ''', (fts_query, query.per_page, query.page * query.per_page))
            
            rows = cursor.fetchall()
            
            # Convert to SearchResult objects
            results = []
            for row in rows:
                doc_id, title, content, doc_type, metadata_json, rank = row
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                # Generate highlights
                highlights = self._generate_highlights(query.query, title + " " + content)
                
                results.append(SearchResult(
                    id=doc_id,
                    title=title,
                    content=content[:200] + "..." if len(content) > 200 else content,
                    type=doc_type,
                    score=1.0 / (rank + 1),  # Convert rank to score
                    highlights=highlights,
                    metadata=metadata
                ))
            
            # Get total count
            cursor.execute('''
                SELECT COUNT(*) FROM search_index WHERE search_index MATCH ?
            ''', (fts_query,))
            total_count = cursor.fetchone()[0]
            
            # Generate facets
            facets = self._generate_facets(cursor, fts_query)
            
            # Get suggestions
            suggestions = self.suggest(query.query) if query.suggest else []
            
            conn.close()
            
            # Record analytics
            query_time = (datetime.now() - start_time).total_seconds()
            self._record_analytics(query.query, total_count, query_time)
            
            stats = SearchStats(
                total_results=total_count,
                query_time=query_time,
                facets=facets,
                suggestions=suggestions,
                related_queries=[]
            )
            
            return results, stats
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return [], SearchStats(
                total_results=0,
                query_time=0.0,
                facets={},
                suggestions=[],
                related_queries=[]
            )
    
    def suggest(self, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update suggestion count
            cursor.execute('''
                INSERT OR REPLACE INTO search_suggestions (query, count, last_used)
                VALUES (?, COALESCE((SELECT count + 1 FROM search_suggestions WHERE query = ?), 1), CURRENT_TIMESTAMP)
            ''', (query, query))
            
            # Get popular suggestions
            cursor.execute('''
                SELECT query FROM search_suggestions
                WHERE query LIKE ? AND query != ?
                ORDER BY count DESC, last_used DESC
                LIMIT ?
            ''', (f"{query}%", query, limit))
            
            suggestions = [row[0] for row in cursor.fetchall()]
            conn.commit()
            conn.close()
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from index"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM search_index WHERE id = ?', (doc_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def _build_fts_query(self, query: str) -> str:
        """Build FTS query from user input"""
        # Clean and escape query
        query = re.sub(r'[^\w\s]', ' ', query)
        terms = query.split()
        
        if not terms:
            return "*"
        
        # Build FTS query with OR logic
        fts_terms = []
        for term in terms:
            if len(term) > 2:
                fts_terms.append(f"{term}*")
        
        return " OR ".join(fts_terms) if fts_terms else "*"
    
    def _generate_highlights(self, query: str, text: str, max_highlights: int = 3) -> List[str]:
        """Generate text highlights"""
        highlights = []
        terms = query.lower().split()
        text_lower = text.lower()
        
        for term in terms[:max_highlights]:
            if len(term) > 2:
                start = text_lower.find(term)
                if start != -1:
                    # Extract context around the term
                    context_start = max(0, start - 50)
                    context_end = min(len(text), start + len(term) + 50)
                    highlight = text[context_start:context_end]
                    
                    # Add ellipsis if needed
                    if context_start > 0:
                        highlight = "..." + highlight
                    if context_end < len(text):
                        highlight = highlight + "..."
                    
                    highlights.append(highlight)
        
        return highlights
    
    def _generate_facets(self, cursor, fts_query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Generate search facets"""
        facets = {}
        
        try:
            # Type facets
            cursor.execute('''
                SELECT type, COUNT(*) as count
                FROM search_index
                WHERE search_index MATCH ?
                GROUP BY type
                ORDER BY count DESC
            ''', (fts_query,))
            
            type_facets = []
            for row in cursor.fetchall():
                type_facets.append({
                    'value': row[0],
                    'count': row[1]
                })
            
            if type_facets:
                facets['type'] = type_facets
            
        except Exception as e:
            logger.error(f"Failed to generate facets: {e}")
        
        return facets
    
    def _record_analytics(self, query: str, results_count: int, query_time: float):
        """Record search analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO search_analytics (query, results_count, query_time)
                VALUES (?, ?, ?)
            ''', (query, results_count, query_time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to record analytics: {e}")

class IntelligentSearchManager:
    """Main search management class"""
    
    def __init__(self):
        self.engines = {}
        self.default_engine = None
        self.config = {}
        self.analytics = SearchAnalytics()
    
    def add_engine(self, name: str, engine: SearchEngineBase, is_default: bool = False):
        """Add search engine"""
        self.engines[name] = engine
        if is_default or not self.default_engine:
            self.default_engine = engine
        logger.info(f"Added search engine: {name}")
    
    def configure(self, config: Dict[str, Any]):
        """Configure search system"""
        self.config = config
        
        # Setup default SQLite engine
        sqlite_config = config.get('sqlite', {'db_path': 'search.db'})
        sqlite_engine = SQLiteSearchEngine(sqlite_config)
        self.add_engine('sqlite', sqlite_engine, is_default=True)
        
        logger.info("Search system configured")
    
    def index_content(self, content_type: str, items: List[Dict[str, Any]]) -> bool:
        """Index content of specified type"""
        if not self.default_engine:
            logger.error("No search engine configured")
            return False
        
        # Prepare documents for indexing
        documents = []
        for item in items:
            doc = {
                'id': f"{content_type}_{item.get('id', '')}",
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'type': content_type,
                'metadata': {
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at'),
                    'author': item.get('author'),
                    'tags': item.get('tags', []),
                    **item.get('metadata', {})
                }
            }
            documents.append(doc)
        
        return self.default_engine.bulk_index(documents)
    
    def search(self, 
               query: str,
               content_types: Optional[List[str]] = None,
               filters: Optional[Dict[str, Any]] = None,
               sort: str = "relevance",
               page: int = 0,
               per_page: int = 20,
               facets: Optional[List[str]] = None,
               suggest: bool = True) -> Tuple[List[SearchResult], SearchStats]:
        """Perform intelligent search"""
        
        if not self.default_engine:
            logger.error("No search engine configured")
            return [], SearchStats(0, 0.0, {}, [], [])
        
        search_query = SearchQuery(
            query=query,
            filters=filters or {},
            sort=sort,
            page=page,
            per_page=per_page,
            facets=facets or ['type'],
            suggest=suggest
        )
        
        # Record search intent
        self.analytics.record_search(query, content_types)
        
        return self.default_engine.search(search_query)
    
    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions"""
        if not self.default_engine:
            return []
        return self.default_engine.suggest(query, limit)
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular search queries"""
        return self.analytics.get_popular_searches(limit)
    
    def get_search_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get search analytics"""
        return self.analytics.get_analytics(days)

class SearchAnalytics:
    """Search analytics and insights"""
    
    def __init__(self):
        self.search_log = []
        self.query_counts = Counter()
        self.no_results_queries = []
    
    def record_search(self, query: str, content_types: Optional[List[str]] = None):
        """Record search query"""
        self.search_log.append({
            'query': query,
            'content_types': content_types,
            'timestamp': datetime.now()
        })
        self.query_counts[query] += 1
    
    def record_no_results(self, query: str):
        """Record query with no results"""
        self.no_results_queries.append({
            'query': query,
            'timestamp': datetime.now()
        })
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular search queries"""
        popular = []
        for query, count in self.query_counts.most_common(limit):
            popular.append({
                'query': query,
                'count': count
            })
        return popular
    
    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get search analytics for specified period"""
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_searches = [
            log for log in self.search_log 
            if log['timestamp'] > cutoff
        ]
        
        recent_no_results = [
            log for log in self.no_results_queries
            if log['timestamp'] > cutoff
        ]
        
        return {
            'total_searches': len(recent_searches),
            'unique_queries': len(set(log['query'] for log in recent_searches)),
            'no_results_count': len(recent_no_results),
            'no_results_rate': len(recent_no_results) / max(len(recent_searches), 1),
            'top_queries': [log['query'] for log in recent_searches[:10]],
            'problematic_queries': [log['query'] for log in recent_no_results[:5]]
        }

def create_search_manager() -> IntelligentSearchManager:
    """Factory function to create search manager"""
    return IntelligentSearchManager()