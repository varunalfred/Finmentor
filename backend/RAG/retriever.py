"""
Retriever for RAG system
Handles intelligent retrieval with query processing and re-ranking
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .embeddings import EmbeddingService
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """
    Intelligent retriever for RAG system
    Handles query processing, retrieval, and result re-ranking
    """
    
    def __init__(
        self,
        session: AsyncSession,
        embedding_service: EmbeddingService,
        top_k: int = 5
    ):
        """
        Initialize retriever
        
        Args:
            session: Database session
            embedding_service: Embedding service instance
            top_k: Number of documents to retrieve
        """
        self.session = session
        self.embedding_service = embedding_service
        self.top_k = top_k
        self.vector_store = VectorStore(
            session,
            embedding_dim=embedding_service.get_dimension()
        )
    
    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_score: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query text
            top_k: Number of results (overrides default)
            filters: Optional filters (topic, level, etc.)
            include_score: Whether to include similarity scores
            
        Returns:
            List of relevant documents
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        k = top_k or self.top_k
        
        # Generate query embedding
        logger.info(f"Retrieving documents for query: '{query[:50]}...'")
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Search vector store
        results = await self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=k,
            filters=filters
        )
        
        # Filter by score threshold if needed
        filtered_results = [
            doc for doc in results 
            if doc.get('score', 0) > 0.3  # Minimum similarity threshold
        ]
        
        if not include_score:
            for doc in filtered_results:
                doc.pop('score', None)
        
        logger.info(f"Retrieved {len(filtered_results)} relevant documents")
        return filtered_results
    
    async def retrieve_by_topic(
        self,
        query: str,
        topic: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents filtered by topic
        
        Args:
            query: User query
            topic: Topic to filter by
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters={'topic': topic}
        )
    
    async def retrieve_by_level(
        self,
        query: str,
        level: str,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents filtered by difficulty level
        
        Args:
            query: User query
            level: Level to filter by (beginner, intermediate, advanced)
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        return await self.retrieve(
            query=query,
            top_k=top_k,
            filters={'level': level}
        )
    
    async def retrieve_multi_query(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using multiple queries and merge results
        Useful for complex questions that can be broken down
        
        Args:
            queries: List of query strings
            top_k: Total number of unique results to return
            filters: Optional filters
            
        Returns:
            Merged list of relevant documents
        """
        k = top_k or self.top_k
        
        all_results = []
        seen_ids = set()
        
        # Retrieve for each query
        for query in queries:
            results = await self.retrieve(
                query=query,
                top_k=k,
                filters=filters,
                include_score=True
            )
            
            # Add unique results
            for doc in results:
                if doc['id'] not in seen_ids:
                    all_results.append(doc)
                    seen_ids.add(doc['id'])
        
        # Sort by score and take top k
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return all_results[:k]
    
    async def retrieve_with_context(
        self,
        query: str,
        conversation_history: Optional[List[str]] = None,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve with conversation context
        
        Args:
            query: Current query
            conversation_history: Previous conversation turns
            top_k: Number of results
            filters: Optional filters
            
        Returns:
            List of relevant documents
        """
        # Combine current query with recent context
        if conversation_history:
            # Use last 2 turns for context
            recent_history = conversation_history[-2:]
            context_query = " ".join(recent_history + [query])
        else:
            context_query = query
        
        return await self.retrieve(
            query=context_query,
            top_k=top_k,
            filters=filters
        )
    
    def format_context(
        self,
        documents: List[Dict[str, Any]],
        max_length: int = 2000
    ) -> str:
        """
        Format retrieved documents into context string for LLM
        
        Args:
            documents: List of retrieved documents
            max_length: Maximum character length
            
        Returns:
            Formatted context string
        """
        if not documents:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(documents, 1):
            # Format document
            doc_text = f"[Document {i}]\n"
            doc_text += f"Title: {doc.get('title', 'Untitled')}\n"
            doc_text += f"Topic: {doc.get('topic', 'General')}\n"
            doc_text += f"Content: {doc.get('content', '')}\n"
            
            # Add summary if available
            if doc.get('summary'):
                doc_text += f"Summary: {doc['summary']}\n"
            
            # Add key points if available
            if doc.get('key_points'):
                points = doc['key_points']
                if isinstance(points, list) and points:
                    doc_text += "Key Points:\n"
                    for point in points[:3]:  # Max 3 points
                        doc_text += f"- {point}\n"
            
            doc_text += "\n"
            
            # Check if adding this document exceeds max length
            if current_length + len(doc_text) > max_length:
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "\n".join(context_parts)
    
    async def get_available_topics(self) -> List[str]:
        """Get list of all available topics in the knowledge base"""
        return await self.vector_store.get_all_topics()
    
    async def get_document_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total document count with optional filters"""
        return await self.vector_store.get_document_count(filters)
