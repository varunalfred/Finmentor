"""
RAG System Tests
Comprehensive test suite for RAG components
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import numpy as np

from RAG.embeddings import EmbeddingService, GeminiEmbeddings, OpenAIEmbeddings, LocalEmbeddings
from RAG.vector_store import VectorStore
from RAG.retriever import Retriever
from RAG.rag_pipeline import RAGPipeline
from services.rag_service import RAGService
from models.database import Base, EducationalContent


# ============= Fixtures =============

@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    yield async_session
    
    await engine.dispose()


@pytest.fixture
async def session(test_db):
    """Create test session"""
    async with test_db() as session:
        yield session


@pytest.fixture
def sample_embedding():
    """Sample embedding vector"""
    return np.random.rand(384).tolist()


@pytest.fixture
async def sample_document(session, sample_embedding):
    """Create sample document"""
    doc = EducationalContent(
        title="Test Document",
        summary="Test summary",
        content="Test content with financial information",
        topic="Stocks",
        level="beginner",
        embedding=sample_embedding
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc


# ============= Embedding Service Tests =============

class TestEmbeddingService:
    """Test embedding service"""
    
    @pytest.mark.asyncio
    async def test_local_embeddings_initialization(self):
        """Test local embeddings can be initialized"""
        embeddings = LocalEmbeddings()
        assert embeddings.get_dimension() == 384
        assert embeddings.model_name == "sentence-transformers/all-MiniLM-L6-v2"
    
    @pytest.mark.asyncio
    async def test_local_embeddings_single_text(self):
        """Test local embeddings for single text"""
        embeddings = LocalEmbeddings()
        embedding = await embeddings.embed_text("Test financial term")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_local_embeddings_batch(self):
        """Test local embeddings for batch"""
        embeddings = LocalEmbeddings()
        texts = ["Stock market", "Bond yield", "P/E ratio"]
        embeddings_list = await embeddings.embed_texts(texts)
        
        assert len(embeddings_list) == 3
        assert all(len(emb) == 384 for emb in embeddings_list)
    
    @pytest.mark.asyncio
    async def test_embedding_service_auto_selection(self):
        """Test embedding service auto-selects local provider"""
        with patch.dict('os.environ', {}, clear=True):
            service = await EmbeddingService.get_service()
            assert service.provider_name == 'local'
            assert service.embedding_dimension == 384


# ============= Vector Store Tests =============

class TestVectorStore:
    """Test vector store"""
    
    @pytest.mark.asyncio
    async def test_add_document(self, session, sample_embedding):
        """Test adding document to vector store"""
        vector_store = VectorStore(session)
        
        doc_id = await vector_store.add_document(
            content="Test content",
            embedding=sample_embedding,
            metadata={
                'title': 'Test',
                'topic': 'Stocks',
                'level': 'beginner'
            }
        )
        
        assert doc_id is not None
        
        # Verify document was added
        doc = await vector_store.get_document_by_id(doc_id)
        assert doc is not None
        assert doc.content == "Test content"
        assert doc.topic == "Stocks"
    
    @pytest.mark.asyncio
    async def test_similarity_search(self, session, sample_document, sample_embedding):
        """Test similarity search"""
        vector_store = VectorStore(session)
        
        results = await vector_store.similarity_search(
            query_embedding=sample_embedding,
            top_k=5
        )
        
        assert len(results) > 0
        assert all('document' in r and 'score' in r for r in results)
    
    @pytest.mark.asyncio
    async def test_delete_document(self, session, sample_document):
        """Test deleting document"""
        vector_store = VectorStore(session)
        
        success = await vector_store.delete_document(sample_document.id)
        assert success is True
        
        # Verify deletion
        doc = await vector_store.get_document_by_id(sample_document.id)
        assert doc is None
    
    @pytest.mark.asyncio
    async def test_get_document_count(self, session, sample_document):
        """Test getting document count"""
        vector_store = VectorStore(session)
        
        count = await vector_store.get_document_count()
        assert count >= 1
        
        # Test with filters
        count_stocks = await vector_store.get_document_count(filters={'topic': 'Stocks'})
        assert count_stocks >= 1


# ============= Retriever Tests =============

class TestRetriever:
    """Test retriever"""
    
    @pytest.mark.asyncio
    async def test_retrieve(self, session, sample_document):
        """Test basic retrieval"""
        embedding_service = await EmbeddingService.get_service('local')
        retriever = Retriever(session, embedding_service)
        
        results = await retriever.retrieve("financial information", top_k=5)
        
        assert 'documents' in results
        assert isinstance(results['documents'], list)
    
    @pytest.mark.asyncio
    async def test_retrieve_with_filters(self, session, sample_document):
        """Test retrieval with filters"""
        embedding_service = await EmbeddingService.get_service('local')
        retriever = Retriever(session, embedding_service)
        
        results = await retriever.retrieve(
            "test query",
            top_k=5,
            filters={'topic': 'Stocks'}
        )
        
        assert 'documents' in results
        # All results should match filter
        for doc in results['documents']:
            assert doc['topic'] == 'Stocks'
    
    @pytest.mark.asyncio
    async def test_format_context(self, session):
        """Test context formatting"""
        embedding_service = await EmbeddingService.get_service('local')
        retriever = Retriever(session, embedding_service)
        
        mock_docs = [
            {
                'title': 'Doc 1',
                'summary': 'Summary 1',
                'content': 'Content 1',
                'key_points': ['Point 1', 'Point 2']
            },
            {
                'title': 'Doc 2',
                'summary': 'Summary 2',
                'content': 'Content 2',
                'key_points': []
            }
        ]
        
        context = retriever.format_context(mock_docs, max_length=500)
        
        assert isinstance(context, str)
        assert 'Doc 1' in context
        assert 'Doc 2' in context
        assert len(context) <= 500


# ============= RAG Pipeline Tests =============

class TestRAGPipeline:
    """Test RAG pipeline"""
    
    @pytest.mark.asyncio
    async def test_pipeline_initialization(self, session):
        """Test pipeline initialization"""
        pipeline = await RAGPipeline.get_pipeline(session)
        
        assert pipeline is not None
        assert pipeline.session == session
        assert pipeline.embedding_service is not None
    
    @pytest.mark.asyncio
    async def test_query(self, session, sample_document):
        """Test RAG query"""
        pipeline = await RAGPipeline.get_pipeline(session)
        
        result = await pipeline.query("What is a stock?", top_k=5)
        
        assert 'context' in result
        assert 'num_sources' in result
        assert 'has_context' in result
        assert isinstance(result['context'], str)
    
    @pytest.mark.asyncio
    async def test_query_with_sources(self, session, sample_document):
        """Test query with source documents"""
        pipeline = await RAGPipeline.get_pipeline(session)
        
        result = await pipeline.query(
            "financial term",
            top_k=5,
            return_sources=True
        )
        
        assert 'sources' in result
        assert isinstance(result['sources'], list)
    
    @pytest.mark.asyncio
    async def test_verify_knowledge_base(self, session, sample_document):
        """Test knowledge base verification"""
        pipeline = await RAGPipeline.get_pipeline(session)
        
        is_valid = await pipeline.verify_knowledge_base()
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, session, sample_document):
        """Test getting statistics"""
        pipeline = await RAGPipeline.get_pipeline(session)
        
        stats = await pipeline.get_statistics()
        
        assert 'total_documents' in stats
        assert 'embedding_provider' in stats
        assert 'embedding_dimension' in stats
        assert stats['total_documents'] >= 1


# ============= RAG Service Tests =============

class TestRAGService:
    """Test RAG service"""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, session):
        """Test service initialization"""
        service = await RAGService.get_service(session)
        
        assert service is not None
        assert service.pipeline is not None
    
    @pytest.mark.asyncio
    async def test_search(self, session, sample_document):
        """Test search"""
        service = await RAGService.get_service(session)
        
        result = await service.search("test query", top_k=5)
        
        assert 'context' in result
        assert 'num_sources' in result
        assert 'has_context' in result
    
    @pytest.mark.asyncio
    async def test_get_status(self, session):
        """Test getting status"""
        service = await RAGService.get_service(session)
        
        status = await service.get_status()
        
        assert 'embedding_provider' in status
        assert 'total_documents' in status
        assert 'topics' in status
    
    @pytest.mark.asyncio
    async def test_get_topics(self, session, sample_document):
        """Test getting topics"""
        service = await RAGService.get_service(session)
        
        topics = await service.get_topics()
        
        assert isinstance(topics, list)
        assert 'Stocks' in topics
    
    @pytest.mark.asyncio
    async def test_check_knowledge_base(self, session, sample_document):
        """Test checking knowledge base"""
        service = await RAGService.get_service(session)
        
        is_loaded = await service.check_knowledge_base_loaded()
        assert is_loaded is True


# ============= Integration Tests =============

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_search(self, session, sample_document):
        """Test end-to-end search flow"""
        # Initialize service
        service = await RAGService.get_service(session)
        
        # Perform search
        result = await service.search("financial information", top_k=5)
        
        # Verify result structure
        assert result['has_context'] is True
        assert result['num_sources'] > 0
        assert len(result['context']) > 0
        
        # Verify sources if included
        if 'sources' in result:
            assert len(result['sources']) > 0
            assert all('title' in s for s in result['sources'])
    
    @pytest.mark.asyncio
    async def test_multiple_documents(self, session, sample_embedding):
        """Test with multiple documents"""
        # Add multiple documents
        vector_store = VectorStore(session)
        
        topics = ['Stocks', 'Bonds', 'Options']
        for i, topic in enumerate(topics):
            await vector_store.add_document(
                content=f"Content about {topic}",
                embedding=sample_embedding,
                metadata={
                    'title': f'{topic} Guide',
                    'topic': topic,
                    'level': 'beginner'
                }
            )
        
        # Search
        service = await RAGService.get_service(session)
        result = await service.search("investment options", top_k=5)
        
        assert result['num_sources'] >= len(topics)
    
    @pytest.mark.asyncio
    async def test_filtered_search(self, session, sample_embedding):
        """Test filtered search"""
        # Add documents with different topics
        vector_store = VectorStore(session)
        
        await vector_store.add_document(
            content="Stock market information",
            embedding=sample_embedding,
            metadata={'title': 'Stocks', 'topic': 'Stocks', 'level': 'beginner'}
        )
        
        await vector_store.add_document(
            content="Bond market information",
            embedding=sample_embedding,
            metadata={'title': 'Bonds', 'topic': 'Bonds', 'level': 'beginner'}
        )
        
        # Search with filter
        service = await RAGService.get_service(session)
        result = await service.search(
            "market information",
            top_k=5,
            filters={'topic': 'Stocks'}
        )
        
        # Verify only Stocks documents returned
        if 'sources' in result:
            assert all(s['topic'] == 'Stocks' for s in result['sources'])


# ============= Performance Tests =============

class TestPerformance:
    """Performance tests"""
    
    @pytest.mark.asyncio
    async def test_batch_embedding(self):
        """Test batch embedding performance"""
        embeddings = LocalEmbeddings()
        
        texts = [f"Test text {i}" for i in range(100)]
        
        import time
        start = time.time()
        embeddings_list = await embeddings.embed_texts(texts)
        end = time.time()
        
        assert len(embeddings_list) == 100
        assert (end - start) < 10  # Should complete in under 10 seconds
    
    @pytest.mark.asyncio
    async def test_search_performance(self, session):
        """Test search performance"""
        # Add multiple documents
        vector_store = VectorStore(session)
        embedding_service = await EmbeddingService.get_service('local')
        
        for i in range(50):
            embedding = await embedding_service.embed_text(f"Test content {i}")
            await vector_store.add_document(
                content=f"Test content {i}",
                embedding=embedding,
                metadata={
                    'title': f'Doc {i}',
                    'topic': 'Stocks',
                    'level': 'beginner'
                }
            )
        
        # Perform search
        service = await RAGService.get_service(session)
        
        import time
        start = time.time()
        result = await service.search("test query", top_k=5)
        end = time.time()
        
        assert (end - start) < 5  # Should complete in under 5 seconds


# ============= Error Handling Tests =============

class TestErrorHandling:
    """Test error handling"""
    
    @pytest.mark.asyncio
    async def test_empty_query(self, session):
        """Test handling of empty query"""
        service = await RAGService.get_service(session)
        
        with pytest.raises(ValueError):
            await service.search("", top_k=5)
    
    @pytest.mark.asyncio
    async def test_invalid_top_k(self, session):
        """Test handling of invalid top_k"""
        service = await RAGService.get_service(session)
        
        # Should clamp to valid range
        result = await service.search("test", top_k=0)
        assert result is not None
        
        result = await service.search("test", top_k=1000)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_missing_document(self, session):
        """Test handling of missing document"""
        vector_store = VectorStore(session)
        
        doc = await vector_store.get_document_by_id(99999)
        assert doc is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
