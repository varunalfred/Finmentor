"""
Vector Store using PGVector
Handles storage and similarity search of embeddings in PostgreSQL
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, and_
import numpy as np

from models.database import EducationalContent

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for managing embeddings in PostgreSQL with PGVector
    """
    
    def __init__(self, session: AsyncSession, embedding_dim: int = 384):
        """
        Initialize vector store
        
        Args:
            session: SQLAlchemy async session
            embedding_dim: Dimension of embedding vectors (384 for local, 768 for Gemini, 1536 for OpenAI)
        """
        self.session = session
        self.embedding_dim = embedding_dim
    
    async def add_document(
        self,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a document with its embedding to the vector store
        
        Args:
            content: Document text content
            embedding: Embedding vector
            metadata: Optional metadata (title, topic, level, etc.)
            
        Returns:
            Document ID
        """
        if len(embedding) != self.embedding_dim:
            raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dim}, got {len(embedding)}")
        
        metadata = metadata or {}
        
        # Create educational content entry
        doc = EducationalContent(
            title=metadata.get('title', 'Untitled'),
            topic=metadata.get('topic', 'General'),
            level=metadata.get('level', 'beginner'),
            content_type=metadata.get('content_type', 'text'),
            content=content,
            summary=metadata.get('summary', content[:200]),
            embedding=embedding,
            key_points=metadata.get('key_points', [])
        )
        
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        
        logger.info(f"Added document: {doc.id} - {doc.title}")
        return doc.id
    
    async def add_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple documents in batch
        
        Args:
            documents: List of dicts with 'content', 'embedding', and 'metadata'
            
        Returns:
            List of document IDs
        """
        doc_ids = []
        
        for doc_data in documents:
            content = doc_data['content']
            embedding = doc_data['embedding']
            metadata = doc_data.get('metadata', {})
            
            doc = EducationalContent(
                title=metadata.get('title', 'Untitled'),
                topic=metadata.get('topic', 'General'),
                level=metadata.get('level', 'beginner'),
                content_type=metadata.get('content_type', 'text'),
                content=content,
                summary=metadata.get('summary', content[:200]),
                embedding=embedding,
                key_points=metadata.get('key_points', [])
            )
            
            self.session.add(doc)
            doc_ids.append(doc.id)
        
        await self.session.commit()
        logger.info(f"Added {len(doc_ids)} documents in batch")
        
        return doc_ids
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Optional filters (topic, level, etc.)
            
        Returns:
            List of matching documents with scores
        """
        if len(query_embedding) != self.embedding_dim:
            raise ValueError(f"Query embedding dimension mismatch: expected {self.embedding_dim}, got {len(query_embedding)}")
        
        try:
            # Use PGVector cosine distance operator
            # <=> is cosine distance (1 - cosine similarity)
            query = select(
                EducationalContent.id,
                EducationalContent.title,
                EducationalContent.content,
                EducationalContent.topic,
                EducationalContent.level,
                EducationalContent.summary,
                EducationalContent.key_points,
                # Calculate similarity score (1 - distance)
                (1 - EducationalContent.embedding.cosine_distance(query_embedding)).label('score')
            )
            
            # Apply filters
            if filters:
                conditions = []
                if 'topic' in filters:
                    conditions.append(EducationalContent.topic == filters['topic'])
                if 'level' in filters:
                    conditions.append(EducationalContent.level == filters['level'])
                if 'content_type' in filters:
                    conditions.append(EducationalContent.content_type == filters['content_type'])
                
                if conditions:
                    query = query.where(and_(*conditions))
            
            # Order by similarity and limit
            query = query.order_by(text('score DESC')).limit(top_k)
            
            result = await self.session.execute(query)
            rows = result.fetchall()
            
            documents = []
            for row in rows:
                documents.append({
                    'id': row.id,
                    'title': row.title,
                    'content': row.content,
                    'topic': row.topic,
                    'level': row.level,
                    'summary': row.summary,
                    'key_points': row.key_points,
                    'score': float(row.score)
                })
            
            logger.info(f"Found {len(documents)} similar documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            # Fallback to slower Python-based cosine similarity
            return await self._fallback_similarity_search(query_embedding, top_k, filters)
    
    async def _fallback_similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fallback similarity search using Python (if PGVector fails)
        """
        logger.warning("Using fallback similarity search (slower)")
        
        # Get all documents
        query = select(EducationalContent)
        
        # Apply filters
        if filters:
            conditions = []
            if 'topic' in filters:
                conditions.append(EducationalContent.topic == filters['topic'])
            if 'level' in filters:
                conditions.append(EducationalContent.level == filters['level'])
            
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        all_docs = result.scalars().all()
        
        # Calculate cosine similarity in Python
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        
        scored_docs = []
        for doc in all_docs:
            if doc.embedding:
                doc_vec = np.array(doc.embedding)
                doc_norm = np.linalg.norm(doc_vec)
                
                if query_norm > 0 and doc_norm > 0:
                    similarity = np.dot(query_vec, doc_vec) / (query_norm * doc_norm)
                    scored_docs.append((doc, float(similarity)))
        
        # Sort by similarity
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Take top k
        top_docs = scored_docs[:top_k]
        
        documents = []
        for doc, score in top_docs:
            documents.append({
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,
                'topic': doc.topic,
                'level': doc.level,
                'summary': doc.summary,
                'key_points': doc.key_points,
                'score': score
            })
        
        return documents
    
    async def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by its ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document dict or None
        """
        result = await self.session.execute(
            select(EducationalContent).where(EducationalContent.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            return None
        
        return {
            'id': doc.id,
            'title': doc.title,
            'content': doc.content,
            'topic': doc.topic,
            'level': doc.level,
            'summary': doc.summary,
            'key_points': doc.key_points
        }
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            select(EducationalContent).where(EducationalContent.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            return False
        
        await self.session.delete(doc)
        await self.session.commit()
        logger.info(f"Deleted document: {doc_id}")
        return True
    
    async def get_document_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Get total document count
        
        Args:
            filters: Optional filters
            
        Returns:
            Count of documents
        """
        query = select(text("COUNT(*)")).select_from(EducationalContent)
        
        if filters:
            conditions = []
            if 'topic' in filters:
                conditions.append(EducationalContent.topic == filters['topic'])
            if 'level' in filters:
                conditions.append(EducationalContent.level == filters['level'])
            
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        count = result.scalar()
        return count or 0
    
    async def get_all_topics(self) -> List[str]:
        """Get list of all unique topics"""
        result = await self.session.execute(
            select(EducationalContent.topic).distinct()
        )
        topics = [row[0] for row in result.fetchall()]
        return topics
