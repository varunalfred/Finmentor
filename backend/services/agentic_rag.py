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
            return OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=embedding_key)
        elif embedding_key and embedding_key.startswith("AIza"):
            # Gemini key format
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            logger.info("Using Gemini embeddings (via EMBEDDING_API_KEY)")
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=embedding_key
            )
        else:
            # Use FREE local embeddings by default - unlimited queries!
            # This separates embeddings from LLM API keys
            from sentence_transformers import SentenceTransformer
            logger.info("Using LOCAL SentenceTransformer embeddings (unlimited, no API key needed)")
            return SentenceTransformer('all-MiniLM-L6-v2')

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
            plan["sources"] = ["education", "conversations"]
            plan["strategy"] = RetrievalStrategy.SIMILARITY
            plan["filters"]["level"] = user_context.get("education_level", "beginner")

        elif intent == QueryIntent.MARKET_ANALYSIS:
            plan["sources"] = ["market", "conversations"]
            plan["strategy"] = RetrievalStrategy.MULTI_SOURCE
            plan["filters"]["recency"] = 24  # Last 24 hours for market data

        elif intent == QueryIntent.PORTFOLIO_ADVICE:
            plan["sources"] = ["conversations", "education", "market"]
            plan["strategy"] = RetrievalStrategy.MULTI_SOURCE
            plan["filters"]["user_id"] = user_context.get("user_id")
            plan["needs_verification"] = True
            plan["k"] = 10  # Get more context for critical decisions

        elif intent == QueryIntent.RISK_ASSESSMENT:
            plan["sources"] = ["conversations", "education"]
            plan["strategy"] = RetrievalStrategy.MULTI_SOURCE
            plan["filters"]["user_id"] = user_context.get("user_id")
            plan["filters"]["risk_profile"] = user_context.get("risk_tolerance")
            plan["needs_verification"] = True

        else:  # GENERAL_CHAT
            plan["sources"] = ["conversations"]
            plan["strategy"] = RetrievalStrategy.SIMILARITY
            plan["filters"]["user_id"] = user_context.get("user_id")
            plan["k"] = 3

        return plan

    # ============= Retrieval Execution =============

    async def retrieve_from_conversations(
        self,
        query_embedding: List[float],
        filters: Dict[str, Any],
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve from conversation history using PGVector"""
        try:
            # Convert embedding list to proper vector string format for PGVector
            # Format: '[0.1,0.2,0.3]' (no spaces, wrapped in brackets)
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Build base query with vector similarity
            # CAST the string to vector type explicitly
            query_text = """
                SELECT
                    m.id,
                    m.content,
                    m.role,
                    m.confidence_score,
                    m.created_at,
                    c.topic,
                    m.embedding <-> CAST(:embedding AS vector) as distance
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE 1=1
            """

            # Add filters
            params = {"embedding": embedding_str}

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
            result = await self.db.execute(text(query_text), params)
            rows = result.fetchall()

            # Format results
            results = []
            for row in rows:
                results.append({
                    "id": row.id,
                    "content": row.content,
                    "role": row.role,
                    "confidence_score": row.confidence_score,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "topic": row.topic,
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
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve from educational content using PGVector"""
        try:
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

            result = await self.db.execute(text(query_text), params)
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

    async def execute_retrieval(
        self,
        query: str,
        plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute retrieval based on plan"""
        try:
            # Generate embedding for query
            if hasattr(self.embedding_service, 'embed_query'):
                query_embedding = await self.embedding_service.aembed_query(query)
            else:
                # For sentence transformers
                query_embedding = self.embedding_service.encode(query).tolist()

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
            # Generate embedding
            if hasattr(self.embedding_service, 'embed_query'):
                embedding = await self.embedding_service.aembed_query(content)
            else:
                embedding = self.embedding_service.encode(content).tolist()

            # Convert embedding list to string format for pgvector
            embedding_str = str(embedding)

            # Update message with embedding
            await self.db.execute(
                text("""
                    UPDATE messages
                    SET embedding = :embedding::vector
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
            # Generate query embedding
            if hasattr(self.embedding_service, 'embed_query'):
                query_embedding = await self.embedding_service.aembed_query(query)
            else:
                query_embedding = self.embedding_service.encode(query).tolist()

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