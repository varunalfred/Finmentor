"""
Agentic RAG Service with PGVector
Intelligent retrieval system that decides what and how to retrieve
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, text
from enum import Enum
import numpy as np
import logging
import json
import os

from models.database import Message, Conversation, EducationalContent, User
from models.document import DocumentChunk, UserDocument

logger = logging.getLogger(__name__)

# ============= Intent Classification =============

class QueryIntent(Enum):
    """Types of query intents for routing"""
    HISTORICAL_REFERENCE = "historical"      # "What did we discuss last time?"
    EDUCATIONAL_QUERY = "educational"        # "What is a P/E ratio?"
    MARKET_ANALYSIS = "market"              # "How is AAPL performing?"
    PORTFOLIO_ADVICE = "portfolio"          # "Should I buy more?"
    RISK_ASSESSMENT = "risk"                # "Is this too risky for me?"
    GENERAL_CHAT = "general"                # General conversation

class RetrievalStrategy(Enum):
    """Retrieval strategies based on intent"""
    MEMORY_ONLY = "memory"                  # Only past conversations
    EDUCATION_ONLY = "education"            # Only educational content
    MARKET_ONLY = "market"                  # Only market data
    MULTI_SOURCE = "multi"                  # Combine multiple sources
    TEMPORAL = "temporal"                   # Time-based retrieval
    SIMILARITY = "similarity"               # Pure semantic search

# ============= Agentic RAG Service =============

class EmbeddingServiceWrapper:
    """Wrapper to unify different embedding service interfaces"""
    def __init__(self, service, service_type):
        self.service = service
        self.service_type = service_type

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text, handling different provider methods"""
        try:
            if self.service_type == "sentence_transformer":
                # SentenceTransformer.encode returns numpy array, convert to list
                embedding = self.service.encode(text)
                return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
            elif self.service_type == "langchain":
                # LangChain embeddings use embed_query
                return await self.service.aembed_query(text)
            else:
                raise ValueError(f"Unknown service type: {self.service_type}")
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback to prevent crash
            return [0.0] * 384  # Assuming 384 dim for fallback

class AgenticRAG:
    """
    Singleton Agentic RAG that intelligently decides:
    1. What intent the query has
    2. Which sources to search
    3. How to retrieve (strategy)
    4. Whether to self-reflect
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AgenticRAG, cls).__new__(cls)
        return cls._instance

    def __init__(self, db: AsyncSession = None, embedding_service=None):
        if not self._initialized:
            self.db = db
            self.embedding_service = embedding_service or self._init_embedding_service()
            self._initialize()
            self.__class__._initialized = True

    def _initialize(self):

        # Intent patterns for classification
        self.intent_patterns = {
            QueryIntent.HISTORICAL_REFERENCE: [
                "last time", "previously", "we discussed", "you said",
                "earlier", "before", "remember when", "our last chat"
            ],
            QueryIntent.EDUCATIONAL_QUERY: [
                "what is", "explain", "how does", "teach me",
                "what are", "definition", "meaning of", "understand"
            ],
            QueryIntent.MARKET_ANALYSIS: [
                "price", "stock", "market", "performing", "trading",
                "chart", "technical", "fundamental", "earnings"
            ],
            QueryIntent.PORTFOLIO_ADVICE: [
                "should i buy", "should i sell", "invest", "portfolio",
                "recommend", "advice", "good investment", "worth buying"
            ],
            QueryIntent.RISK_ASSESSMENT: [
                "risk", "safe", "dangerous", "volatile", "stable",
                "conservative", "aggressive", "lose money", "risky"
            ]
        }

        # Critical intents that need self-reflection
        self.critical_intents = {
            QueryIntent.PORTFOLIO_ADVICE,
            QueryIntent.RISK_ASSESSMENT
        }



    def _init_embedding_service(self):
        """Initialize embedding service - use EMBEDDING_API_KEY or fall back to local"""
        # Check for dedicated embedding API key (allows choosing embedding provider)
        embedding_key = os.getenv("EMBEDDING_API_KEY")
        
        if embedding_key and embedding_key.startswith("sk-"):
            # OpenAI key format
            from langchain_openai import OpenAIEmbeddings
            logger.info("Using OpenAI embeddings (via EMBEDDING_API_KEY)")
            service = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=embedding_key)
            return EmbeddingServiceWrapper(service, "langchain")
        elif embedding_key and embedding_key.startswith("AIza"):
            # Gemini key format
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            logger.info("Using Gemini embeddings (via EMBEDDING_API_KEY)")
            service = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=embedding_key
            )
            return EmbeddingServiceWrapper(service, "langchain")
        else:
            # Use FREE local embeddings by default - unlimited queries!
            # This separates embeddings from LLM API keys
            from sentence_transformers import SentenceTransformer
            logger.info("Using LOCAL SentenceTransformer embeddings (unlimited, no API key needed)")
            service = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)
            return EmbeddingServiceWrapper(service, "sentence_transformer")

    # ============= Intent Classification =============

    def classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """
        Classify the intent of a query - what does the user REALLY want?
        Returns: (intent_type, confidence_score)
        Example: "What did we discuss about Apple?" → (HISTORICAL_REFERENCE, 0.75)
        """
        query_lower = query.lower()  # Convert to lowercase for matching
        intent_scores = {}  # Will store score for each intent type

        # Check how well each intent's patterns match the query
        for intent, patterns in self.intent_patterns.items():
            # Count matching patterns (e.g., "should i buy" in query)
            score = sum(1 for pattern in patterns if pattern in query_lower)
            if score > 0:
                # Normalize by total patterns (e.g., 2 matches out of 8 patterns = 0.25)
                intent_scores[intent] = score / len(patterns)

        if intent_scores:
            # Return the intent with highest confidence score
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            return best_intent, confidence
        else:
            # No patterns matched - default to general conversation
            return QueryIntent.GENERAL_CHAT, 0.5  # 50% confidence for default

    def plan_retrieval(
        self,
        intent: QueryIntent,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan retrieval strategy based on intent and context
        Returns a retrieval plan
        """
        plan = {
            "intent": intent,
            "sources": [],
            "strategy": RetrievalStrategy.SIMILARITY,
            "filters": {},
            "k": 5,  # Number of results
            "needs_verification": False
        }

        # Determine sources and strategy based on intent
        if intent == QueryIntent.HISTORICAL_REFERENCE:
            plan["sources"] = ["conversations"]
            plan["strategy"] = RetrievalStrategy.TEMPORAL
            plan["filters"]["user_id"] = user_context.get("user_id")
            plan["filters"]["time_range"] = 30  # Last 30 days

        elif intent == QueryIntent.EDUCATIONAL_QUERY:
            plan["sources"] = ["education", "documents", "conversations"]  # Add documents
            plan["strategy"] = RetrievalStrategy.SIMILARITY
            plan["filters"]["level"] = user_context.get("education_level", "beginner")
            plan["filters"]["user_id"] = user_context.get("user_id")  # For document search
            plan["filters"]["include_public"] = True  # Include public documents

        elif intent == QueryIntent.MARKET_ANALYSIS:
            plan["sources"] = ["market", "documents", "conversations"]  # Add documents
            plan["strategy"] = RetrievalStrategy.MULTI_SOURCE
            plan["filters"]["recency"] = 24  # Last 24 hours for market data
            plan["filters"]["user_id"] = user_context.get("user_id")
            plan["filters"]["include_public"] = True

        elif intent == QueryIntent.PORTFOLIO_ADVICE:
            plan["sources"] = ["conversations", "education", "documents", "market"]  # Add documents
            plan["strategy"] = RetrievalStrategy.MULTI_SOURCE
            plan["filters"]["user_id"] = user_context.get("user_id")
            plan["filters"]["include_public"] = True
            plan["needs_verification"] = True
            plan["k"] = 10  # Get more context for critical decisions

        elif intent == QueryIntent.RISK_ASSESSMENT:
            plan["sources"] = ["conversations", "education", "documents"]  # Add documents
            plan["strategy"] = RetrievalStrategy.MULTI_SOURCE
            plan["filters"]["user_id"] = user_context.get("user_id")
            plan["filters"]["risk_profile"] = user_context.get("risk_tolerance")
            plan["filters"]["include_public"] = True
            plan["needs_verification"] = True

        else:  # GENERAL_CHAT
            plan["sources"] = ["conversations", "documents"]  # Add documents for general queries too
            plan["strategy"] = RetrievalStrategy.SIMILARITY
            plan["filters"]["user_id"] = user_context.get("user_id")
            plan["filters"]["include_public"] = True
            plan["k"] = 3

        return plan

    # ============= Retrieval Execution =============

    async def retrieve_from_conversations(
        self,
        query_embedding: List[float],
        filters: Dict[str, Any],
        k: int = 5,
        db_session: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Retrieve from conversation history using PGVector"""
        try:
            session = db_session or self.db
            if not session:
                logger.warning("No database session available for retrieval")
                return []

            # Convert embedding list to proper vector string format for PGVector
            # Format: '[0.1,0.2,0.3]' (no spaces, wrapped in brackets)
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Base query
            query_text = """
                SELECT 
                    id, 
                    content, 
                    role, 
                    confidence_score, 
                    created_at, 
                    embedding <-> CAST(:embedding AS vector) as distance
                FROM messages m
                WHERE embedding IS NOT NULL
            """
            
            params = {"embedding": embedding_str}

            # Apply filters
            if "user_id" in filters:
                query_text += " AND m.user_id = :user_id"
                params["user_id"] = filters["user_id"]

            if "time_range" in filters:
                cutoff = datetime.now(timezone.utc) - timedelta(days=filters["time_range"])
                query_text += " AND m.created_at > :cutoff"
                params["cutoff"] = cutoff

            if "role" in filters:
                query_text += " AND m.role = :role"
                params["role"] = filters["role"]

            # Order by similarity and limit
            query_text += " ORDER BY distance LIMIT :k"
            params["k"] = k

            # Execute query
            result = await session.execute(text(query_text), params)
            rows = result.fetchall()

            # Format results
            results = []
            for row in rows:
                # Skip if distance is None (shouldn't happen with WHERE clause but check anyway)
                if row.distance is None:
                    continue
                results.append({
                    "id": row.id,
                    "content": row.content,
                    "role": row.role,
                    "confidence_score": row.confidence_score,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "topic": "general",  # Default topic since column doesn't exist on message
                    "distance": float(row.distance),
                    "source": "conversations"
                })

            return results

        except Exception as e:
            logger.error(f"Error retrieving from conversations: {e}")
            return []

    async def retrieve_from_education(
        self,
        query_embedding: List[float],
        filters: Dict[str, Any],
        k: int = 5,
        db_session: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """Retrieve from educational content using PGVector"""
        try:
            session = db_session or self.db
            if not session:
                logger.warning("No database session available for retrieval")
                return []

            # Convert embedding list to proper vector string format for PGVector
            # Format: '[0.1,0.2,0.3]' (no spaces, wrapped in brackets)
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            query_text = """
                SELECT
                    id,
                    title,
                    topic,
                    level,
                    content,
                    summary,
                    embedding <-> CAST(:embedding AS vector) as distance
                FROM educational_content
                WHERE embedding IS NOT NULL
            """

            params = {"embedding": embedding_str}

            if "level" in filters:
                query_text += " AND level = :level"
                params["level"] = filters["level"]

            if "topic" in filters:
                query_text += " AND topic = :topic"
                params["topic"] = filters["topic"]

            query_text += " ORDER BY distance LIMIT :k"
            params["k"] = k

            result = await session.execute(text(query_text), params)
            rows = result.fetchall()

            results = []
            for row in rows:
                results.append({
                    "id": row.id,
                    "title": row.title,
                    "topic": row.topic,
                    "level": row.level,
                    "content": row.content[:500],  # Truncate for context
                    "summary": row.summary,
                    "distance": float(row.distance),
                    "source": "education"
                })

            return results

        except Exception as e:
            logger.error(f"Error retrieving from education: {e}")
            return []

    async def retrieve_from_documents(
        self,
        query_embedding: List[float],
        user_id: str,
        filters: Dict[str, Any],
        include_public: bool = True,
        k: int = 5,
        db_session: AsyncSession = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve from user documents + public community documents using PGVector
        
        Args:
            query_embedding: Query vector
            user_id: Current user ID
            filters: Additional filters
            include_public: Whether to include public documents
            k: Number of results to return
            
        Returns:
            List of relevant document chunks with attribution
        """
        try:
            session = db_session or self.db
            if not session:
                logger.warning("No database session available for retrieval")
                return []

            # Convert embedding to PGVector format
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Build query for private + public documents
            if include_public:
                # Search user's private docs OR public docs
                query_text = """
                    SELECT
                        dc.id,
                        dc.chunk_text,
                        dc.page_number,
                        dc.chunk_index,
                        dc.is_public,
                        ud.filename,
                        ud.user_id as uploader_id,
                        dc.conversation_id,
                        (dc.chunk_embedding <=> :embedding) as distance
                    FROM document_chunks dc
                    JOIN user_documents ud ON dc.document_id = ud.id
                    WHERE (dc.user_id = :user_id OR dc.is_public = TRUE)
                    AND dc.chunk_embedding IS NOT NULL
                    ORDER BY dc.chunk_embedding <=> :embedding
                    LIMIT :k
                """
            else:
                # Only user's private docs
                query_text = """
                    SELECT
                        dc.id,
                        dc.chunk_text,
                        dc.page_number,
                        dc.chunk_index,
                        dc.is_public,
                        ud.filename,
                        ud.user_id as uploader_id,
                        dc.conversation_id,
                        (dc.chunk_embedding <=> :embedding) as distance
                    FROM document_chunks dc
                    JOIN user_documents ud ON dc.document_id = ud.id
                    WHERE dc.user_id = :user_id
                    AND dc.chunk_embedding IS NOT NULL
                    ORDER BY dc.chunk_embedding <=> :embedding
                    LIMIT :k
                """
            
            # Execute query with named parameters
            result = await session.execute(
                text(query_text),
                {"embedding": embedding_str, "user_id": user_id, "k": k}
            )
            rows = result.fetchall()
            
            # Format results with attribution
            results = []
            for row in rows:
                # Convert row to dict for easier access
                row_dict = dict(row._mapping) if hasattr(row, '_mapping') else {
                    'id': row[0],
                    'chunk_text': row[1],
                    'page_number': row[2],
                    'chunk_index': row[3],
                    'is_public': row[4],
                    'filename': row[5],
                    'uploader_id': row[6],
                    'conversation_id': row[7],
                    'distance': row[8]
                }
                
                # Determine attribution
                if row_dict['is_public'] and row_dict['uploader_id'] != user_id:
                    attribution = f"from {row_dict['filename']} (shared by user_{row_dict['uploader_id'][:8]})"
                    source_type = "public_document"
                else:
                    attribution = f"from your document: {row_dict['filename']}"
                    source_type = "private_document"
                
                results.append({
                    "id": row_dict['id'],
                    "content": row_dict['chunk_text'],
                    "filename": row_dict['filename'],
                    "page_number": row_dict['page_number'],
                    "chunk_index": row_dict['chunk_index'],
                    "is_public": row_dict['is_public'],
                    "uploader_id": row_dict['uploader_id'],
                    "conversation_id": row_dict['conversation_id'],
                    "distance": float(row_dict['distance']),
                    "similarity": 1 - float(row_dict['distance']),  # Convert distance to similarity score
                    "attribution": attribution,
                    "source": source_type
                })
            
            logger.info(f"Retrieved {len(results)} document chunks for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving from documents: {e}")
            return []

    async def execute_retrieval(
        self,
        query: str,
        plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute retrieval based on plan"""
        try:
            # Generate embedding for query using wrapper
            query_embedding = await self.embedding_service.get_embedding(query)

            all_results = []

            # Retrieve from each source
            for source in plan["sources"]:
                if source == "conversations":
                    results = await self.retrieve_from_conversations(
                        query_embedding,
                        plan["filters"],
                        plan["k"]
                    )
                    all_results.extend(results)

                elif source == "education":
                    results = await self.retrieve_from_education(
                        query_embedding,
                        plan["filters"],
                        plan["k"]
                    )
                    all_results.extend(results)

                elif source == "documents":
                    # Retrieve from uploaded documents (private + public)
                    user_id = plan["filters"].get("user_id", "default")
                    results = await self.retrieve_from_documents(
                        query_embedding,
                        user_id,
                        plan["filters"],
                        include_public=plan["filters"].get("include_public", True),
                        k=plan["k"]
                    )
                    all_results.extend(results)

                # Add more sources as needed (market, portfolio, etc.)

            # Sort by relevance (distance)
            all_results.sort(key=lambda x: x.get("distance", 1.0))

            # Return top k results
            return all_results[:plan["k"]]

        except Exception as e:
            logger.error(f"Error executing retrieval: {e}")
            return []

    # ============= Self-Reflection =============

    async def self_reflect(
        self,
        query: str,
        response: str,
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Self-reflection for critical queries
        Checks for consistency, accuracy, and completeness
        """
        reflection = {
            "needs_revision": False,
            "concerns": [],
            "suggestions": []
        }

        # Check for contradictions with past advice
        for ctx in context:
            if ctx.get("source") == "conversations" and ctx.get("role") == "assistant":
                # Simple contradiction check (in production, use LLM)
                if "buy" in ctx["content"].lower() and "sell" in response.lower():
                    reflection["needs_revision"] = True
                    reflection["concerns"].append(
                        "Potential contradiction with previous advice"
                    )
                    reflection["suggestions"].append(
                        "Review previous recommendation and explain any changes"
                    )

        # Check for risk warnings in portfolio advice
        if "buy" in response.lower() or "invest" in response.lower():
            if "risk" not in response.lower():
                reflection["needs_revision"] = True
                reflection["concerns"].append("Missing risk disclosure")
                reflection["suggestions"].append("Add risk warnings")

            if "not financial advice" not in response.lower():
                reflection["needs_revision"] = True
                reflection["concerns"].append("Missing disclaimer")
                reflection["suggestions"].append("Add disclaimer")

        # Check for personalization
        if len(context) > 0 and "your" not in response.lower():
            reflection["concerns"].append("Response may not be personalized")
            reflection["suggestions"].append("Consider user's specific situation")

        return reflection

    # ============= Main Agentic RAG Pipeline =============

    async def retrieve_and_generate_context(
        self,
        query: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main agentic RAG pipeline
        1. Classify intent
        2. Plan retrieval
        3. Execute retrieval
        4. Self-reflect if needed
        """
        try:
            # Prepare user context
            if not user_context:
                user_context = {"user_id": user_id}

            # Step 1: Classify intent
            intent, confidence = self.classify_intent(query)
            logger.info(f"Classified intent: {intent.value} (confidence: {confidence:.2f})")

            # Step 2: Plan retrieval
            plan = self.plan_retrieval(intent, user_context)
            logger.info(f"Retrieval plan: {plan['sources']} using {plan['strategy'].value}")

            # Step 3: Execute retrieval
            retrieved_context = await self.execute_retrieval(query, plan)
            logger.info(f"Retrieved {len(retrieved_context)} documents")

            # Step 4: Self-reflect for critical queries
            reflection = None
            if intent in self.critical_intents:
                # This would normally use the LLM-generated response
                # For now, we'll prepare the reflection structure
                reflection = {
                    "needed": True,
                    "intent": intent.name,  # Use enum name for consistency
                    "checks": ["consistency", "risk_disclosure", "personalization"]
                }

            # Prepare final context
            result = {
                "query": query,
                "intent": intent.name,  # Return enum name (e.g., "EDUCATIONAL_QUERY") instead of value
                "confidence": confidence,
                "retrieval_plan": plan,
                "context": retrieved_context,
                "reflection": reflection,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "user_id": user_id,
                    "num_sources": len(plan["sources"]),
                    "num_results": len(retrieved_context)
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error in agentic RAG pipeline: {e}")
            return {
                "query": query,
                "error": str(e),
                "context": [],
                "metadata": {"timestamp": datetime.now(timezone.utc).isoformat()}
            }

    # ============= Helper Functions =============

    async def store_message_embedding(
        self,
        message_id: str,
        content: str
    ) -> bool:
        """Store embedding for a message"""
        try:
            # Generate embedding using wrapper
            embedding = await self.embedding_service.get_embedding(content)

            # Convert embedding list to proper pgvector format
            # Format: '[0.1,0.2,0.3]' - pgvector accepts this directly
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'

            # Update message with embedding - use text() for raw SQL
            # pgvector will automatically cast the string to vector type
            await self.db.execute(
                text("""
                    UPDATE messages
                    SET embedding = :embedding
                    WHERE id = :message_id
                """),
                {"embedding": embedding_str, "message_id": message_id}
            )
            await self.db.commit()

            return True

        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            await self.db.rollback()
            return False

    async def find_similar_messages(
        self,
        query: str,
        user_id: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar messages for a user"""
        try:
            # Generate query embedding using wrapper
            query_embedding = await self.embedding_service.get_embedding(query)

            # Convert embedding list to proper vector string format for PGVector
            # Format: '[0.1,0.2,0.3]' (no spaces, wrapped in brackets)
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

            # Search using PGVector with explicit CAST
            result = await self.db.execute(
                text("""
                    SELECT
                        content,
                        created_at,
                        embedding <-> CAST(:embedding AS vector) as distance
                    FROM messages
                    WHERE user_id = :user_id
                        AND embedding IS NOT NULL
                        AND role = 'user'
                    ORDER BY distance
                    LIMIT :k
                """),
                {
                    "embedding": embedding_str,
                    "user_id": user_id,
                    "k": k
                }
            )

            similar = []
            for row in result.fetchall():
                similar.append({
                    "content": row.content,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "similarity": 1 - float(row.distance)  # Convert distance to similarity
                })

            return similar

        except Exception as e:
            logger.error(f"Error finding similar messages: {e}")
            return []

    def set_db_session(self, db: AsyncSession):
        """Update database session (useful for request-scoped sessions)"""
        self.db = db

# Create singleton instance
rag_service = AgenticRAG()

# Export for convenience
AgenticRAGService = AgenticRAG