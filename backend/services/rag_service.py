"""
RAG Service - High-level service for RAG operations
Integrates with the rest of the application
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from pathlib import Path

from RAG.embeddings import get_embedding_service, EmbeddingService
from RAG.rag_pipeline import RAGPipeline
from RAG.vector_store import VectorStore
from models.database import EducationalContent

logger = logging.getLogger(__name__)


class RAGService:
    """
    High-level service for RAG operations
    Handles initialization, data loading, and query processing
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize RAG service
        
        Args:
            session: Database session
        """
        self.session = session
        self.embedding_service = get_embedding_service()
        self.pipeline = RAGPipeline(
            session=session,
            embedding_service=self.embedding_service
        )
        self.vector_store = VectorStore(
            session=session,
            embedding_dim=self.embedding_service.get_dimension()
        )
        logger.info("RAG Service initialized")
    
    async def load_glossary(self, glossary_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load financial glossary from CSV into vector store
        
        Args:
            glossary_path: Path to glossary CSV (defaults to RAG/glossary_clean.csv)
            
        Returns:
            Statistics about loading process
        """
        if glossary_path is None:
            # Default path
            base_path = Path(__file__).parent.parent
            glossary_path = base_path / "RAG" / "glossary_clean.csv"
        
        logger.info(f"Loading glossary from: {glossary_path}")
        
        if not Path(glossary_path).exists():
            raise FileNotFoundError(f"Glossary file not found: {glossary_path}")
        
        # Read CSV
        df = pd.read_csv(glossary_path)
        logger.info(f"Found {len(df)} terms in glossary")
        
        # Normalize column names to handle both lowercase and capitalized versions
        df.columns = df.columns.str.lower()
        
        stats = {
            'total': len(df),
            'loaded': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }
        
        # Process in batches
        batch_size = 50
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            batch_docs = []
            
            for idx, row in batch.iterrows():
                term = None
                try:
                    term = str(row['term']).strip()
                    definition = str(row['definition']).strip()
                    
                    if not term or not definition or term == 'nan' or definition == 'nan':
                        stats['skipped'] += 1
                        continue
                    
                    # Combine for embedding
                    content_text = f"{term}: {definition}"
                    
                    # Generate embedding
                    embedding = await self.embedding_service.embed_text(content_text)
                    
                    # Prepare document
                    batch_docs.append({
                        'content': definition,
                        'embedding': embedding,
                        'metadata': {
                            'title': term,
                            'topic': 'Financial Glossary',
                            'level': 'beginner',
                            'content_type': 'definition',
                            'summary': definition[:200] if len(definition) > 200 else definition
                        }
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing term at index {idx} {f'({term})' if term else ''}: {e}")
                    stats['errors'] += 1
            
            # Add batch to vector store
            if batch_docs:
                try:
                    await self.vector_store.add_documents_batch(batch_docs)
                    stats['loaded'] += len(batch_docs)
                except Exception as e:
                    logger.error(f"Error adding batch: {e}")
                    stats['errors'] += len(batch_docs)
            
            logger.info(f"Processed batch {i//batch_size + 1}: {stats}")
        
        logger.info(f"Glossary loading complete: {stats}")
        return stats
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search knowledge base with RAG
        
        Args:
            query: User query
            top_k: Number of results
            filters: Optional filters
            conversation_history: Conversation context
            
        Returns:
            RAG response with context and sources
        """
        return await self.pipeline.query(
            question=query,
            top_k=top_k,
            filters=filters,
            conversation_history=conversation_history,
            return_sources=True
        )
    
    async def get_context_for_question(
        self,
        question: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get formatted context for a question
        
        Args:
            question: User question
            top_k: Number of documents
            filters: Optional filters
            
        Returns:
            Formatted context string
        """
        return await self.pipeline.get_context_only(
            question=question,
            top_k=top_k,
            filters=filters
        )
    
    async def answer_question(
        self,
        question: str,
        llm_service: Any,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Answer question using RAG + LLM
        
        Args:
            question: User question
            llm_service: LLM service for generation
            top_k: Number of documents
            filters: Optional filters
            conversation_history: Conversation context
            
        Returns:
            Answer with sources and metadata
        """
        # Get RAG context
        rag_result = await self.search(
            query=question,
            top_k=top_k,
            filters=filters,
            conversation_history=conversation_history
        )
        
        context = rag_result['context']
        sources = rag_result.get('sources', [])
        
        if not context:
            return {
                'answer': "I don't have enough information in my knowledge base to answer this question.",
                'sources': [],
                'has_context': False
            }
        
        # Create prompt with context
        prompt = self.pipeline.create_prompt_with_context(
            question=question,
            context=context
        )
        
        # Generate answer (this would call your LLM service)
        # For now, return the context and sources
        return {
            'answer': context,  # Replace with LLM generated answer
            'sources': sources,
            'has_context': True,
            'num_sources': len(sources)
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get RAG system status
        
        Returns:
            Status information
        """
        return await self.pipeline.verify_knowledge_base()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get detailed statistics
        
        Returns:
            Statistics dict
        """
        return await self.pipeline.get_statistics()
    
    async def check_knowledge_base_loaded(self) -> bool:
        """
        Check if knowledge base has content
        
        Returns:
            True if KB has documents
        """
        count = await self.vector_store.get_document_count()
        return count > 0
    
    async def get_topics(self) -> List[str]:
        """Get list of available topics"""
        return await self.vector_store.get_all_topics()
    
    async def search_by_topic(
        self,
        query: str,
        topic: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Search within specific topic"""
        return await self.pipeline.query_by_topic(
            question=query,
            topic=topic,
            top_k=top_k
        )
    
    async def search_by_level(
        self,
        query: str,
        level: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Search by difficulty level"""
        return await self.pipeline.query_by_level(
            question=query,
            level=level,
            top_k=top_k
        )


# Singleton management
_rag_service: Optional[RAGService] = None


async def get_rag_service(session: AsyncSession) -> RAGService:
    """
    Get or create RAG service singleton
    
    Args:
        session: Database session
        
    Returns:
        RAGService instance
    """
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RAGService(session)
    
    return _rag_service
