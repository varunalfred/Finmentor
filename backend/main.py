"""
FinMentor AI - Backend API
Multi-agent financial advisory system with voice support
"""
# Hey I am in christ university

from fastapi import FastAPI, HTTPException  # FastAPI framework and exception handling
from fastapi.middleware.cors import CORSMiddleware  # For cross-origin requests (browser access)
from contextlib import asynccontextmanager  # For managing app lifecycle
import logging  # For logging events and errors
from typing import Dict, Any  # Type hints for better code clarity
import os  # For environment variables
from dotenv import load_dotenv  # Load .env file

# Load environment variables from .env file
load_dotenv()

# Import what we actually have
from routers import chat, auth, rag  # API route handlers
from services.database import init_db, db_service  # Database initialization and service
from agents.hybrid_core import HybridFinMentorSystem  # Main AI system (DSPy + LangChain)
from agents.orchestrator import MultiAgentOrchestrator  # Manages multiple agents

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set log level to INFO (shows important events)
logger = logging.getLogger(__name__)  # Create logger for this module

# Initialize our actual system
hybrid_system = None  # Will hold the main AI system instance
orchestrator = None  # Will hold the multi-agent orchestrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - runs on startup and shutdown"""
    global hybrid_system, orchestrator  # Access global system instances

    # === Startup code (runs when server starts) ===
    logger.info("Starting FinMentor AI Backend...")  # Log startup

    # Initialize database
    await init_db()  # Create tables, setup connections
    logger.info("Database initialized")  # Confirm DB ready

    # Initialize hybrid system
    config = {
        "model": os.getenv("DEFAULT_MODEL", "gemini-pro"),  # Get model from env or use gemini-pro
        "temperature": 0.7,  # Creativity level (0=deterministic, 1=creative)
        "max_tokens": 1000  # Max response length
    }
    hybrid_system = HybridFinMentorSystem(config)  # Create main AI system
    orchestrator = MultiAgentOrchestrator(hybrid_system)  # Create agent manager
    logger.info("Multi-agent system initialized")  # Confirm AI ready

    logger.info("Backend started successfully!")  # All systems go!

    yield  # App runs here - this pauses until shutdown

    # === Shutdown code (runs when server stops) ===
    logger.info("Shutting down FinMentor AI Backend...")  # Log shutdown
    # Cleanup if needed (close connections, save state, etc.)
    logger.info("Backend stopped.")  # Final log

# Create FastAPI app
app = FastAPI(
    title="FinMentor AI API",  # API title shown in docs
    description="Multi-agent financial advisory system with voice support",  # Description in docs
    version="1.0.0",  # API version
    lifespan=lifespan  # Attach lifecycle manager for startup/shutdown
)

# Get allowed CORS origins from environment
# For development: http://localhost:3000,http://localhost:5173
# For production: https://yourdomain.com,https://app.yourdomain.com
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"  # Development defaults only
).split(",")

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,  # Middleware to handle browser security
    allow_origins=ALLOWED_ORIGINS,  # Specific origins only (not wildcard!)
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers (attach API endpoints)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])  # Auth endpoints at /api/auth/*
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])  # Chat endpoints at /api/chat/*
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])  # RAG endpoints at /api/rag/*

# Note: All financial queries (market, education, portfolio) go through
# the chat endpoint which uses multi-agent processing to handle them

@app.get("/")  # Handle GET requests to root URL
async def root():
    """Root endpoint - shows API info"""
    return {
        "message": "Welcome to FinMentor AI API",  # Welcome message
        "version": "1.0.0",  # API version
        "docs": "/docs",  # Link to auto-generated API docs
        "health": "/health",  # Link to health check endpoint
        "architecture": "DSPy + LangChain Multi-Agent System",  # System architecture
        "capabilities": [  # List of what the system can do
            "Multi-modal input (text, voice, image, document)",
            "13 specialized financial agents",
            "Parallel agent execution",
            "Intelligent context retrieval with RAG",
            "Portfolio analysis and optimization",
            "Market analysis and sentiment",
            "Tax and risk assessment",
            "Personalized education"
        ]
    }

@app.get("/health")  # Health check endpoint
async def health_check():
    """Health check endpoint - monitors system status"""
    global hybrid_system  # Access global system instance

    agent_status = {
        "dspy_agents": 13,  # Number of specialized DSPy signatures available
        "orchestrator": "active" if orchestrator else "inactive",  # Check if orchestrator is running
        "hybrid_system": "active" if hybrid_system else "inactive"  # Check if main system is running
    }

    return {
        "status": "healthy",  # Overall system status
        "agents": agent_status,  # Status of agent systems
        "services": {  # Status of supporting services
            "database": "connected" if db_service else "disconnected",  # DB connection status
            "rag": "active",  # RAG system status (always active)
            "rag_kb_loaded": "check /api/rag/check",  # Link to check if KB is loaded
            "data_sources": "available"  # Data sources status
        }
    }