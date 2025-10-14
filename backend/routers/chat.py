"""
Unified Chat Router - Supports Text, Voice, and Multimodal inputs
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import base64
import io
from PIL import Image
import PyPDF2
import logging

from agents.hybrid_core import HybridFinMentorSystem
from services.data_sources import DataSourcesManager
from services.database import db_service, get_db
from services.agentic_rag import rag_service
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()

# ============= Request/Response Models =============

class ChatRequest(BaseModel):
    """Unified chat request supporting multiple input types"""
    message: str = Field(..., description="User's message/query")

    # Input modality
    input_type: str = Field(
        default="text",
        description="Input type: text, voice, image, document"
    )

    # Optional data for different modalities
    voice_data: Optional[str] = Field(default=None, description="Base64 encoded audio")
    image_data: Optional[str] = Field(default=None, description="Base64 encoded image")
    document_data: Optional[str] = Field(default=None, description="Base64 encoded document")

    # User profile for personalization
    user_profile: Dict[str, Any] = Field(
        default={
            "type": "beginner",
            "education_level": "basic",
            "preferred_language": "en",
            "preferred_output": "text"  # text, voice, visual
        }
    )

    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Unified response with multimodal output options"""
    success: bool
    response: str  # Always include text response

    # Optional outputs
    voice_response: Optional[str] = None  # Base64 audio
    visual_data: Optional[Dict[str, Any]] = None  # Charts, graphs

    # Data and metadata
    data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

# ============= System Initialization with Singletons =============

hybrid_system = None
data_manager = None

def get_hybrid_system(db: AsyncSession = None) -> HybridFinMentorSystem:
    """Get or create hybrid system instance (singleton pattern)"""
    global hybrid_system
    if hybrid_system is None:
        config = {
            "model": "gemini-pro",  # Will auto-detect available API
            "temperature": 0.7,
            "max_tokens": 1000,
            "verbose": True
        }
        hybrid_system = HybridFinMentorSystem(config, db_session=db)
    elif db:
        # Update DB session if provided
        hybrid_system.agentic_rag.set_db_session(db)
    return hybrid_system

def get_data_manager() -> DataSourcesManager:
    """Get or create data manager instance (singleton pattern)"""
    global data_manager
    if data_manager is None:
        data_manager = DataSourcesManager()
    return data_manager

# ============= Processing Functions =============

async def process_voice_input(voice_data: str) -> str:
    """Process voice input using speech-to-text"""
    try:
        # TODO: Implement actual STT
        # Options: Whisper API, Google Speech-to-Text
        audio_bytes = base64.b64decode(voice_data)
        logger.info(f"Processing voice input: {len(audio_bytes)} bytes")

        # Placeholder - in production use actual STT
        return "Voice input received (implement STT)"

    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        return "Could not process voice input"

async def generate_voice_response(text: str) -> Optional[str]:
    """Generate voice response using text-to-speech"""
    try:
        # TODO: Implement actual TTS
        # Options: Google TTS, Amazon Polly
        logger.info(f"Generating voice for: {text[:50]}...")

        # Placeholder - return None for now
        return None

    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None

async def process_image_input(image_data: str, message: str) -> Dict[str, Any]:
    """Process image input (charts, documents, etc.)"""
    try:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))

        # TODO: Implement image analysis
        # Options: Gemini Vision, GPT-4 Vision, OCR

        return {
            "type": "image",
            "dimensions": f"{image.width}x{image.height}",
            "format": image.format,
            "analysis": "Image analysis pending implementation"
        }

    except Exception as e:
        logger.error(f"Image processing error: {e}")
        return {"error": str(e)}

async def process_document_input(document_data: str) -> Dict[str, Any]:
    """Process document input (PDFs, etc.)"""
    try:
        doc_bytes = base64.b64decode(document_data)

        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(doc_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        return {
            "type": "pdf",
            "pages": len(pdf_reader.pages),
            "text_preview": text[:500],
            "full_text": text
        }

    except Exception as e:
        logger.error(f"Document processing error: {e}")
        return {"error": str(e)}

# ============= Main Chat Endpoint =============

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)  # Database session injection
):
    """
    THE MAIN ENDPOINT - All queries come here!
    Handles: text, voice, images, documents
    This is the single entry point for ALL financial queries
    """
    try:
        # Log incoming request for debugging
        logger.info(f"Chat request ({request.input_type}): {request.message[:100]}...")

        # Start with the original message
        processed_message = request.message
        extracted_context = {}  # Will store additional context from multimodal inputs

        # === STEP 1: Process different input types ===

        # Voice input - convert speech to text
        if request.input_type == "voice" and request.voice_data:
            # TODO: Implement actual STT (Whisper/Google Speech)
            transcribed = await process_voice_input(request.voice_data)
            processed_message = transcribed  # Use transcribed text
            extracted_context["original_input"] = "voice"  # Remember it was voice

        # Image input - extract visual information
        elif request.input_type == "image" and request.image_data:
            # TODO: Use multimodal LLM to analyze image
            image_analysis = await process_image_input(request.image_data, request.message)
            extracted_context.update(image_analysis)
            # Append image context to the message
            processed_message = f"{request.message} [Image context: {image_analysis}]"

        # Document input - extract text from PDFs
        elif request.input_type == "document" and request.document_data:
            doc_analysis = await process_document_input(request.document_data)
            extracted_context.update(doc_analysis)
            # Append document preview to message
            processed_message = f"{request.message} [Document: {doc_analysis.get('text_preview', '')[:200]}]"

        # === STEP 2: Get AI system and retrieve context ===

        # Get the hybrid AI system (singleton instance)
        system = get_hybrid_system(db)  # Returns existing instance or creates new one

        # Extract user ID for personalization
        user_id = request.user_profile.get('user_id', 'default')  # Default ID if not provided

        # Use Agentic RAG to understand intent and retrieve relevant context
        # This fetches: past conversations, educational content, relevant data
        rag_context = await rag_service.retrieve_and_generate_context(
            query=processed_message,  # The user's query (possibly transcribed from voice)
            user_id=user_id,  # For retrieving user-specific history
            user_context=request.user_profile  # User's education level, preferences, etc.
        )
        # rag_context now contains:
        # - intent (what user wants: MARKET_ANALYSIS, PORTFOLIO_ADVICE, etc.)
        # - context (relevant past conversations, similar queries)
        # - confidence score (how confident RAG is about the intent)

        # Add RAG context for processing
        extracted_context['rag_context'] = rag_context  # Store for later use

        # === STEP 3: Process through multi-agent system ===

        # Send to hybrid system for processing
        # This will: classify complexity, select agents, execute, synthesize
        result = await system.process_query(
            query=processed_message,  # User's processed query
            user_profile=request.user_profile,  # User's preferences and level
            voice_input=(request.input_type == "voice"),  # True if user spoke the query
            rag_context=rag_context  # Context from RAG (intent, history, etc.)
        )
        # result contains:
        # - response: The text response to show the user
        # - data: Any structured data (stock prices, calculations)
        # - metadata: Processing details (agents used, confidence)
        # - success: Whether processing succeeded
        # - error: Any error message if failed

        # === STEP 4: Store conversation in database ===

        from models.database import Conversation, Message  # Import database models
        import uuid  # For generating unique IDs
        from datetime import datetime, timezone  # For timestamps

        # Get existing conversation ID or create new one
        conversation_id = extracted_context.get('conversation_id', str(uuid.uuid4()))  # Continue or start new convo

        # Create user message record
        user_message = Message(
            id=str(uuid.uuid4()),  # Generate unique message ID
            conversation_id=conversation_id,  # Link to conversation thread
            user_id=user_id,  # Who sent this message
            role="user",  # Mark as user message (not assistant)
            content=processed_message,  # The actual message text
            input_type=request.input_type,  # Was it text/voice/image/document?
            created_at=datetime.now(timezone.utc)  # When message was sent
        )
        db.add(user_message)  # Add to database session (not saved yet)

        # Create assistant response record
        assistant_message = Message(
            id=str(uuid.uuid4()),  # Generate unique ID for response
            conversation_id=conversation_id,  # Same conversation thread
            user_id=user_id,  # Response is for this user
            role="assistant",  # Mark as AI response
            content=result.get("response", ""),  # The AI's response text
            confidence_score=result.get("confidence", 0.0),  # How confident AI is
            model_used="gemini-pro",  # Which LLM generated this
            created_at=datetime.now(timezone.utc)  # Response timestamp
        )
        db.add(assistant_message)  # Add to session

        await db.commit()  # Save both messages to database

        # Store embeddings asynchronously for future RAG retrieval
        await rag_service.store_message_embedding(user_message.id, processed_message)  # Embed user's query
        await rag_service.store_message_embedding(assistant_message.id, result.get("response", ""))  # Embed AI response

        # Generate voice response if user prefers audio output
        voice_response = None  # Default to no voice
        if request.user_profile.get("preferred_output") == "voice":  # Check user preference
            voice_response = await generate_voice_response(result.get("response", ""))  # Convert text to speech

        return ChatResponse(
            success=result.get("success", True),  # Did processing succeed?
            response=result.get("response", ""),  # Text response to show user
            voice_response=voice_response,  # Base64 audio if generated
            data={**result.get("data", {}), **extracted_context},  # Merge all data (prices, analysis, etc.)
            metadata={  # Additional info about processing
                **result.get("metadata", {}),  # Metadata from agents
                "input_type": request.input_type  # Record how user inputted query
            },
            error=result.get("error")  # Any error message
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")  # Log the error for debugging
        return ChatResponse(
            success=False,  # Mark as failed
            response="I encountered an error processing your request.",  # Generic error message
            error=str(e)  # Include actual error for debugging
        )

# ============= Simple/Test Endpoints =============

@router.post("/simple")
async def simple_chat(message: str):
    """Simplified chat endpoint for quick testing"""
    try:
        dm = get_data_manager()  # Get data manager singleton
        message_lower = message.lower()  # Convert to lowercase for matching

        # Stock price queries
        if "price" in message_lower or "stock" in message_lower:  # Check for stock-related keywords
            import re  # For regex pattern matching
            symbols = re.findall(r'\b[A-Z]{1,5}\b', message)  # Find 1-5 uppercase letters (stock symbols)

            if symbols:  # If we found any symbols
                stock_data = await dm.get_stock_data(symbols[0])  # Get data for first symbol
                if "error" not in stock_data:  # If data fetch succeeded
                    return {
                        "response": f"{stock_data['symbol']}: ${stock_data['price']['current']:.2f} ({stock_data['price']['change_percent']:.2f}%)",  # Format price info
                        "data": stock_data  # Include full data
                    }

        # Market overview
        if "market" in message_lower:  # Check for market keywords
            indicators = await dm.get_economic_indicators()  # Fetch economic indicators
            response = "Market Overview:\n"  # Start building response
            for key, value in indicators["data"].items():  # Loop through each indicator
                if isinstance(value, dict):  # If indicator has structured data
                    response += f"• {key}: {value.get('value', 'N/A')}\n"  # Format as bullet point
            return {"response": response, "data": indicators}  # Return formatted overview

        # News
        if "news" in message_lower:  # Check for news keywords
            news = await dm.get_market_news()  # Fetch latest news
            if news:  # If news items found
                response = "Latest News:\n"  # Start response
                for item in news[:3]:  # Show top 3 news items
                    response += f"• {item['title']}\n"  # Format as bullet
                return {"response": response, "data": news}  # Return news summary

        # Default response if no patterns matched
        return {
            "response": "Ask me about stock prices, market data, or financial news!",  # Help message
            "examples": [  # Show example queries
                "What's AAPL price?",
                "Show market overview",
                "Latest financial news"
            ]
        }

    except Exception as e:
        return {"error": str(e)}  # Return error as JSON

@router.get("/test")
async def test_chat():
    """Test endpoint to verify system is working"""
    try:
        dm = get_data_manager()  # Get data manager to test connections
        market_data = await dm.get_economic_indicators()  # Test market data fetch

        return {
            "status": "operational",  # System is working
            "market_sample": market_data,  # Show sample market data
            "supported_inputs": ["text", "voice", "image", "document"],  # List input types
            "available_llms": ["gemini", "openai", "anthropic"]  # List LLM options
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}  # Return error status

# ============= File Upload Endpoints =============

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),  # Required image file upload
    message: str = Form("Analyze this image")  # Optional message with image
):
    """Upload and analyze an image"""
    try:
        contents = await file.read()  # Read file bytes
        image_data = base64.b64encode(contents).decode()  # Convert to base64 string

        request = ChatRequest(
            message=message,  # User's question about the image
            input_type="image",  # Mark as image input
            image_data=image_data  # Include base64 image data
        )

        return await chat(request)  # Process through main chat endpoint

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))  # Return 400 error

@router.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),  # Required document file
    message: str = Form("Analyze this document")  # Optional analysis request
):
    """Upload and analyze a document (PDF)"""
    try:
        contents = await file.read()  # Read document bytes
        document_data = base64.b64encode(contents).decode()  # Encode as base64

        request = ChatRequest(
            message=message,  # User's question about document
            input_type="document",  # Mark as document input
            document_data=document_data  # Include encoded document
        )

        return await chat(request)  # Process through main endpoint

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))  # Return HTTP 400 error

@router.post("/upload/audio")
async def upload_audio(
    file: UploadFile = File(...),  # Required audio file
    user_profile: str = Form("{}")  # Optional user profile as JSON string
):
    """Upload audio for voice input"""
    try:
        import json  # For parsing user profile JSON

        contents = await file.read()  # Read audio bytes
        voice_data = base64.b64encode(contents).decode()  # Encode audio as base64

        # Transcribe audio first
        transcribed = await process_voice_input(voice_data)  # Convert speech to text

        request = ChatRequest(
            message=transcribed,  # Use transcribed text as message
            input_type="voice",  # Mark as voice input
            voice_data=voice_data,  # Include original audio
            user_profile=json.loads(user_profile)  # Parse user profile from JSON
        )

        return await chat(request)  # Process through main chat

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))  # Return error

# ============= Specialized Endpoints =============

@router.post("/analyze-stock")
async def analyze_stock(symbol: str):
    """Quick stock analysis endpoint"""
    try:
        dm = get_data_manager()  # Get data manager
        stock_data = await dm.get_stock_data(symbol.upper())  # Fetch stock data (uppercase symbol)

        if "error" in stock_data:  # Check if data fetch failed
            return {"success": False, "error": stock_data["error"]}  # Return error

        # Get news
        news = await dm.get_market_news(symbol)  # Fetch news for this stock

        # Create analysis request
        request = ChatRequest(
            message=f"Analyze {symbol} stock with price ${stock_data['price']['current']:.2f}",  # Include price in query
            user_profile={"type": "investor"}  # Mark as investor query
        )

        response = await chat(request)  # Get AI analysis

        return {
            "symbol": symbol.upper(),  # Standardized symbol
            "current_data": stock_data,  # Current price and metrics
            "news": news[:3] if news else [],  # Top 3 news items
            "analysis": response.response  # AI's analysis
        }

    except Exception as e:
        return {"success": False, "error": str(e)}  # Return error response

@router.post("/education")
async def get_education(topic: str, level: str = "beginner"):
    """Educational content endpoint"""
    try:
        request = ChatRequest(
            message=f"Explain {topic} in simple terms",  # Request simple explanation
            user_profile={"education_level": level}  # Set education level (beginner/intermediate/advanced)
        )

        response = await chat(request)  # Get educational content

        return {
            "topic": topic,  # Topic being explained
            "level": level,  # Education level used
            "explanation": response.response  # The explanation
        }

    except Exception as e:
        return {"success": False, "error": str(e)}  # Return error