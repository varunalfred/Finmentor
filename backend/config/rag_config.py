"""
RAG Configuration Module
Centralized configuration for the RAG system
"""

import os
from typing import Optional, Literal
from dataclasses import dataclass, field


@dataclass
class EmbeddingConfig:
    """Embedding service configuration"""
    
    # Provider selection
    provider: Literal['gemini', 'openai', 'local', 'auto'] = 'auto'
    
    # API Keys (read from environment)
    gemini_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv('GEMINI_API_KEY') or os.getenv('EMBEDDING_API_KEY')
    )
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv('OPENAI_API_KEY')
    )
    
    # Model configurations
    gemini_model: str = 'models/embedding-001'
    gemini_dimension: int = 768
    
    openai_model: str = 'text-embedding-3-small'
    openai_dimension: int = 1536
    
    local_model: str = 'sentence-transformers/all-MiniLM-L6-v2'
    local_dimension: int = 384
    
    # Performance settings
    batch_size: int = 50
    max_retries: int = 3
    timeout: int = 30
    
    def get_provider_priority(self) -> list[str]:
        """
        Get provider selection priority
        
        Returns:
            List of providers in order of preference
        """
        if self.provider != 'auto':
            return [self.provider]
        
        priority = []
        if self.gemini_api_key:
            priority.append('gemini')
        if self.openai_api_key:
            priority.append('openai')
        priority.append('local')  # Always available as fallback
        
        return priority
    
    def get_dimension(self, provider: str) -> int:
        """Get embedding dimension for provider"""
        dimensions = {
            'gemini': self.gemini_dimension,
            'openai': self.openai_dimension,
            'local': self.local_dimension
        }
        return dimensions.get(provider, self.local_dimension)


@dataclass
class VectorStoreConfig:
    """Vector store configuration"""
    
    # Search settings
    default_top_k: int = 5
    max_top_k: int = 20
    min_top_k: int = 1
    
    # Similarity settings
    similarity_metric: str = 'cosine'  # cosine, euclidean, inner_product
    min_similarity_threshold: float = 0.3
    
    # Performance settings
    batch_insert_size: int = 50
    use_fallback: bool = True  # Use numpy fallback if PGVector fails
    
    # Database settings
    table_name: str = 'educational_content'
    vector_column: str = 'embedding'


@dataclass
class RetrieverConfig:
    """Retriever configuration"""
    
    # Retrieval settings
    default_top_k: int = 5
    max_top_k: int = 20
    
    # Context settings
    max_context_length: int = 2000
    include_metadata: bool = True
    include_scores: bool = True
    
    # Multi-query settings
    enable_multi_query: bool = True
    max_queries: int = 5
    
    # Context formatting
    context_separator: str = "\n\n---\n\n"
    truncate_method: Literal['char', 'word', 'sentence'] = 'word'
    
    # Filtering
    available_topics: list[str] = field(default_factory=lambda: [
        'Stocks', 'Bonds', 'Options', 'ETFs', 'Mutual Funds', 
        'Portfolio Management', 'Risk Management', 'Technical Analysis',
        'Fundamental Analysis', 'Market Indicators', 'Trading Strategies'
    ])
    
    available_levels: list[str] = field(default_factory=lambda: [
        'beginner', 'intermediate', 'advanced'
    ])


@dataclass
class RAGPipelineConfig:
    """RAG Pipeline configuration"""
    
    # Pipeline settings
    default_top_k: int = 5
    max_context_length: int = 2000
    
    # Prompt settings
    default_system_instructions: str = (
        "You are a knowledgeable financial advisor assistant. "
        "Use the provided context to answer questions accurately and concisely. "
        "If the context doesn't contain relevant information, acknowledge the limitation. "
        "Always cite specific information from the context when available."
    )
    
    # Response settings
    include_sources: bool = True
    include_metadata: bool = True
    
    # Performance settings
    enable_caching: bool = False
    cache_ttl: int = 3600  # seconds


@dataclass
class GlossaryConfig:
    """Glossary loading configuration"""
    
    # File settings
    default_path: str = 'RAG/glossary_clean.csv'
    encoding: str = 'utf-8'
    
    # Required columns
    required_columns: list[str] = field(default_factory=lambda: [
        'Term', 'Definition', 'Category'
    ])
    
    # Processing settings
    batch_size: int = 50
    skip_duplicates: bool = True
    
    # Metadata mapping
    term_column: str = 'Term'
    definition_column: str = 'Definition'
    category_column: str = 'Category'
    level_column: str = 'Level'
    
    # Default metadata
    default_topic: str = 'Financial Terms'
    default_level: str = 'intermediate'
    default_content_type: str = 'glossary'


@dataclass
class RAGConfig:
    """
    Master RAG configuration
    Combines all sub-configurations
    """
    
    # Sub-configurations
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    pipeline: RAGPipelineConfig = field(default_factory=RAGPipelineConfig)
    glossary: GlossaryConfig = field(default_factory=GlossaryConfig)
    
    # Global settings
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    
    # Feature flags
    enable_auto_refresh: bool = False
    auto_refresh_interval_days: int = 15
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate top_k settings
        if self.vector_store.default_top_k > self.vector_store.max_top_k:
            raise ValueError("default_top_k cannot exceed max_top_k")
        
        if self.vector_store.default_top_k < self.vector_store.min_top_k:
            raise ValueError("default_top_k cannot be less than min_top_k")
        
        # Validate similarity threshold
        if not 0 <= self.vector_store.min_similarity_threshold <= 1:
            raise ValueError("min_similarity_threshold must be between 0 and 1")
        
        # Validate batch sizes
        if self.embedding.batch_size < 1:
            raise ValueError("embedding.batch_size must be positive")
        
        if self.vector_store.batch_insert_size < 1:
            raise ValueError("vector_store.batch_insert_size must be positive")
        
        # Validate context length
        if self.retriever.max_context_length < 100:
            raise ValueError("max_context_length must be at least 100")
        
        return True
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary
        
        Returns:
            Configuration as dictionary
        """
        return {
            'embedding': {
                'provider': self.embedding.provider,
                'batch_size': self.embedding.batch_size,
                'providers_available': {
                    'gemini': bool(self.embedding.gemini_api_key),
                    'openai': bool(self.embedding.openai_api_key),
                    'local': True
                }
            },
            'vector_store': {
                'default_top_k': self.vector_store.default_top_k,
                'similarity_metric': self.vector_store.similarity_metric,
                'min_similarity_threshold': self.vector_store.min_similarity_threshold
            },
            'retriever': {
                'max_context_length': self.retriever.max_context_length,
                'available_topics': self.retriever.available_topics,
                'available_levels': self.retriever.available_levels
            },
            'pipeline': {
                'default_top_k': self.pipeline.default_top_k,
                'include_sources': self.pipeline.include_sources
            },
            'glossary': {
                'batch_size': self.glossary.batch_size,
                'default_path': self.glossary.default_path
            },
            'debug': self.debug,
            'log_level': self.log_level
        }


# ============= Global Configuration Instance =============

# Create global configuration instance
_rag_config: Optional[RAGConfig] = None


def get_rag_config() -> RAGConfig:
    """
    Get global RAG configuration instance
    
    Returns:
        RAG configuration
    """
    global _rag_config
    
    if _rag_config is None:
        _rag_config = RAGConfig()
        _rag_config.validate()
    
    return _rag_config


def reload_rag_config() -> RAGConfig:
    """
    Reload configuration from environment
    
    Returns:
        New RAG configuration
    """
    global _rag_config
    _rag_config = RAGConfig()
    _rag_config.validate()
    return _rag_config


def update_rag_config(**kwargs) -> RAGConfig:
    """
    Update configuration with new values
    
    Args:
        **kwargs: Configuration values to update
        
    Returns:
        Updated configuration
    """
    config = get_rag_config()
    
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    config.validate()
    return config


# ============= Environment Variable Helpers =============

def get_embedding_provider() -> str:
    """
    Get embedding provider from environment
    
    Returns:
        Provider name: 'gemini', 'openai', 'local', or 'auto'
    """
    provider = os.getenv('EMBEDDING_PROVIDER', 'auto').lower()
    if provider not in ['gemini', 'openai', 'local', 'auto']:
        return 'auto'
    return provider


def get_glossary_path() -> str:
    """
    Get glossary path from environment
    
    Returns:
        Path to glossary file
    """
    return os.getenv('GLOSSARY_PATH', 'RAG/glossary_clean.csv')


def get_top_k() -> int:
    """
    Get default top_k from environment
    
    Returns:
        Default top_k value
    """
    try:
        top_k = int(os.getenv('RAG_TOP_K', '5'))
        return max(1, min(top_k, 20))
    except ValueError:
        return 5


def get_max_context_length() -> int:
    """
    Get max context length from environment
    
    Returns:
        Max context length
    """
    try:
        length = int(os.getenv('RAG_MAX_CONTEXT_LENGTH', '2000'))
        return max(100, length)
    except ValueError:
        return 2000
