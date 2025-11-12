"""
RAG Pipeline - Complete RAG orchestration
Combines retrieval and generation for question answering
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .embeddings import EmbeddingService, get_embedding_service
from .retriever import Retriever

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline for question answering
    Handles retrieval, context formatting, and response generation
    """
    
    def __init__(
        self,
        session: AsyncSession,
        embedding_service: Optional[EmbeddingService] = None,
        top_k: int = 5,
        max_context_length: int = 2000
    ):
        """
        Initialize RAG pipeline
        
        Args:
            session: Database session
            embedding_service: Optional embedding service (auto-creates if None)
            top_k: Number of documents to retrieve
            max_context_length: Maximum context length for LLM
        """
        self.session = session
        self.embedding_service = embedding_service or get_embedding_service()
        self.top_k = top_k
        self.max_context_length = max_context_length
        
        self.retriever = Retriever(
            session=session,
            embedding_service=self.embedding_service,
            top_k=top_k
        )
        
        logger.info("RAG Pipeline initialized")
    
    async def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[str]] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            filters: Optional filters (topic, level)
            conversation_history: Previous conversation for context
            return_sources: Whether to return source documents
            
        Returns:
            Dict with 'context', 'sources', and metadata
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        logger.info(f"RAG query: '{question[:50]}...'")
        
        # Retrieve relevant documents
        if conversation_history:
            documents = await self.retriever.retrieve_with_context(
                query=question,
                conversation_history=conversation_history,
                top_k=top_k,
                filters=filters
            )
        else:
            documents = await self.retriever.retrieve(
                query=question,
                top_k=top_k,
                filters=filters
            )
        
        # Format context
        context = self.retriever.format_context(
            documents=documents,
            max_length=self.max_context_length
        )
        
        # Prepare response
        response = {
            'context': context,
            'num_sources': len(documents),
            'has_context': len(context) > 0
        }
        
        if return_sources:
            response['sources'] = [
                {
                    'id': doc['id'],
                    'title': doc['title'],
                    'topic': doc['topic'],
                    'level': doc['level'],
                    'summary': doc.get('summary', ''),
                    'score': doc.get('score', 0)
                }
                for doc in documents
            ]
        
        logger.info(f"RAG retrieved {len(documents)} sources with {len(context)} chars of context")
        return response
    
    async def query_by_topic(
        self,
        question: str,
        topic: str,
        top_k: Optional[int] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query filtered by specific topic
        
        Args:
            question: User question
            topic: Topic to filter by
            top_k: Number of results
            return_sources: Include source documents
            
        Returns:
            RAG response dict
        """
        return await self.query(
            question=question,
            top_k=top_k,
            filters={'topic': topic},
            return_sources=return_sources
        )
    
    async def query_by_level(
        self,
        question: str,
        level: str,
        top_k: Optional[int] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query filtered by difficulty level
        
        Args:
            question: User question
            level: Level (beginner, intermediate, advanced)
            top_k: Number of results
            return_sources: Include source documents
            
        Returns:
            RAG response dict
        """
        return await self.query(
            question=question,
            top_k=top_k,
            filters={'level': level},
            return_sources=return_sources
        )
    
    async def get_context_only(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get formatted context without full response
        
        Args:
            question: User question
            top_k: Number of documents
            filters: Optional filters
            
        Returns:
            Formatted context string
        """
        documents = await self.retriever.retrieve(
            query=question,
            top_k=top_k,
            filters=filters
        )
        
        return self.retriever.format_context(
            documents=documents,
            max_length=self.max_context_length
        )
    
    async def get_relevant_documents(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        include_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get relevant documents without formatting
        
        Args:
            question: User question
            top_k: Number of documents
            filters: Optional filters
            include_scores: Include similarity scores
            
        Returns:
            List of document dicts
        """
        return await self.retriever.retrieve(
            query=question,
            top_k=top_k,
            filters=filters,
            include_score=include_scores
        )
    
    async def verify_knowledge_base(self) -> Dict[str, Any]:
        """
        Verify knowledge base status
        
        Returns:
            Status information
        """
        total_docs = await self.retriever.get_document_count()
        topics = await self.retriever.get_available_topics()
        
        return {
            'total_documents': total_docs,
            'topics': topics,
            'embedding_provider': self.embedding_service.get_provider_name(),
            'embedding_dimension': self.embedding_service.get_dimension(),
            'retriever_top_k': self.top_k,
            'max_context_length': self.max_context_length
        }
    
    def create_prompt_with_context(
        self,
        question: str,
        context: str,
        system_instructions: Optional[str] = None
    ) -> str:
        """
        Create a formatted prompt with RAG context
        
        Args:
            question: User question
            context: Retrieved context
            system_instructions: Optional system instructions
            
        Returns:
            Formatted prompt string
        """
        if not system_instructions:
            system_instructions = """You are a helpful financial advisor AI assistant. 
Use the provided context to answer questions accurately and helpfully.
If the context doesn't contain relevant information, say so clearly."""
        
        prompt = f"""{system_instructions}

Context Information:
{context}

User Question: {question}

Please provide a clear, accurate, and helpful answer based on the context provided."""
        
        return prompt
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get RAG system statistics
        
        Returns:
            Statistics dict
        """
        status = await self.verify_knowledge_base()
        
        # Add per-topic counts
        topic_counts = {}
        for topic in status['topics']:
            count = await self.retriever.get_document_count({'topic': topic})
            topic_counts[topic] = count
        
        status['documents_by_topic'] = topic_counts
        
        return status


# Singleton instance management
_rag_pipeline: Optional[RAGPipeline] = None


async def get_rag_pipeline(
    session: AsyncSession,
    embedding_service: Optional[EmbeddingService] = None,
    top_k: int = 5
) -> RAGPipeline:
    """
    Get or create RAG pipeline instance
    
    Args:
        session: Database session
        embedding_service: Optional embedding service
        top_k: Number of documents to retrieve
        
    Returns:
        RAGPipeline instance
    """
    global _rag_pipeline
    
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(
            session=session,
            embedding_service=embedding_service,
            top_k=top_k
        )
    
    return _rag_pipeline
