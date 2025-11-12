"""
Embedding Service for RAG
Handles text-to-vector embedding generation using multiple providers
"""

import os
import logging
from typing import List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        pass


class GeminiEmbeddings(EmbeddingProvider):
    """Google Gemini embeddings provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                google_api_key=self.api_key,
                model="models/embedding-001"
            )
            self.dimension = 768
            logger.info("Initialized Gemini embeddings")
        except ImportError:
            raise ImportError("langchain-google-genai not installed. Run: pip install langchain-google-genai")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        return await self.embeddings.aembed_query(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return await self.embeddings.aembed_documents(texts)
    
    def get_dimension(self) -> int:
        return self.dimension


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI embeddings provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found")
        
        try:
            from langchain_openai import OpenAIEmbeddings as LCOpenAIEmbeddings
            self.embeddings = LCOpenAIEmbeddings(
                api_key=self.api_key,
                model="text-embedding-3-small"
            )
            self.dimension = 1536
            logger.info("Initialized OpenAI embeddings")
        except ImportError:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        return await self.embeddings.aembed_query(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return await self.embeddings.aembed_documents(texts)
    
    def get_dimension(self) -> int:
        return self.dimension


class LocalEmbeddings(EmbeddingProvider):
    """Local HuggingFace embeddings (free, no API key needed)"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
            self.dimension = 384  # for all-MiniLM-L6-v2
            logger.info(f"Initialized local embeddings: {model_name}")
        except ImportError:
            raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        # HuggingFace embeddings are synchronous, wrap in async
        return self.embeddings.embed_query(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return self.embeddings.embed_documents(texts)
    
    def get_dimension(self) -> int:
        return self.dimension


class EmbeddingService:
    """
    Unified embedding service that automatically selects the best available provider
    Priority: 1. Gemini, 2. OpenAI, 3. Local (free fallback)
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize embedding service
        
        Args:
            provider: Force specific provider ('gemini', 'openai', 'local')
                     If None, auto-selects based on available API keys
        """
        self.provider_name = provider
        self.provider = self._initialize_provider()
        logger.info(f"Embedding service initialized with: {self.provider_name}")
    
    def _initialize_provider(self) -> EmbeddingProvider:
        """Initialize the embedding provider"""
        
        # If provider specified, use it
        if self.provider_name:
            if self.provider_name.lower() == 'gemini':
                return GeminiEmbeddings()
            elif self.provider_name.lower() == 'openai':
                return OpenAIEmbeddings()
            elif self.provider_name.lower() == 'local':
                return LocalEmbeddings()
            else:
                raise ValueError(f"Unknown provider: {self.provider_name}")
        
        # Auto-select based on available API keys
        # Try Gemini first
        if os.getenv("GEMINI_API_KEY") or os.getenv("EMBEDDING_API_KEY", "").startswith("AIza"):
            try:
                self.provider_name = "gemini"
                return GeminiEmbeddings()
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        
        # Try OpenAI
        if os.getenv("OPENAI_API_KEY") or os.getenv("EMBEDDING_API_KEY", "").startswith("sk-"):
            try:
                self.provider_name = "openai"
                return OpenAIEmbeddings()
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Fallback to local (always works)
        logger.info("No API keys found, using free local embeddings")
        self.provider_name = "local"
        return LocalEmbeddings()
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        return await self.provider.embed_text(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Filter out empty strings
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("No valid texts to embed")
        
        return await self.provider.embed_texts(valid_texts)
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings from current provider"""
        return self.provider.get_dimension()
    
    def get_provider_name(self) -> str:
        """Get the name of current provider"""
        return self.provider_name


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(provider: Optional[str] = None) -> EmbeddingService:
    """
    Get or create singleton embedding service instance
    
    Args:
        provider: Optional provider name to force ('gemini', 'openai', 'local')
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    
    # Check environment variable if provider not specified
    if provider is None:
        provider = os.getenv("EMBEDDING_PROVIDER", "").lower()
        if provider and provider in ['local', 'gemini', 'openai']:
            logger.info(f"Using EMBEDDING_PROVIDER from environment: {provider}")
    
    if _embedding_service is None or (provider and provider != _embedding_service.provider_name):
        _embedding_service = EmbeddingService(provider if provider else None)
    
    return _embedding_service
