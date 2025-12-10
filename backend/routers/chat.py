"""
Unified Chat Router - Supports Text, Voice, and Multimodal inputs
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
import base64
import io
import os
from PIL import Image
import PyPDF2
import logging

from agents.smart_orchestrator import SmartMultiAgentOrchestrator
from agents.hybrid_core import HybridFinMentorSystem
from services.agentic_rag import AgenticRAG
from services.database import get_db
from models.database import User
from models.document import UserDocument, DocumentChunk
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from routers.auth import get_current_user  # Import from routers.auth


# ============= Helper Functions =============




async def process_image_input(image_data: str, message: str) -> dict:
    """
    Placeholder for image analysis - to be implemented later
    """
    return {
        "description": "[Image analysis not yet implemented - coming soon]",
        "success": False
    }


# ============= Data Manager Singleton =============
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
    context: Optional[Dict[str, Any]] = None
    voice_data: Optional[str] = Field(None, description="Base64 encoded voice data")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    document_data: Optional[str] = Field(None, description="Base64 encoded PDF data")
    filename: Optional[str] = Field(None, description="Filename for document")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="User profile context")

class ChatResponse(BaseModel):
    """Unified response with multimodal output options"""
    response: str
    metadata: Dict[str, Any] = {}

class UploadRequest(BaseModel):
    document_data: str = Field(..., description="Base64 encoded document content")
    filename: str = Field(..., description="Original filename")
    conversation_id: Optional[str] = Field(None, description="Conversation ID if known")

class UploadResponse(BaseModel):
    success: bool
    document_id: Optional[str] = None
    filename: str
    message: str

# ============= System Initialization with Singletons =============

hybrid_system = None

def get_hybrid_system(db_session: AsyncSession):
    """Singleton accessor for HybridFinMentorSystem"""
    global hybrid_system
    if hybrid_system is None:
        # Initialize with database session
        hybrid_system = HybridFinMentorSystem(db_session=db_session)
    return hybrid_system
# data_manager = None  # REMOVED: DataSourcesManager class doesn't exist

# ============= Background Task Functions =============

async def store_embeddings_background(user_msg_id: str, assistant_msg_id: str, user_content: str, assistant_content: str):
    """
    Background task to store message embeddings using sentence-transformers (all-MiniLM-L6-v2)
    Runs after response is sent to user, doesn't block the response
    """
    from services.agentic_rag import rag_service
    from services.database import get_db
    
    try:
        # Get a new database session for this background task
        async for db in get_db():
            try:
                # Update RAG service with this session
                rag_service.set_db_session(db)
               
                # Store user message embedding
                await rag_service.store_message_embedding(user_msg_id, user_content)
                logger.info(f"✅ Stored embedding for user message {user_msg_id[:8]}")
                
                # Store assistant message embedding
                await rag_service.store_message_embedding(assistant_msg_id, assistant_content)
                logger.info(f"✅ Stored embedding for assistant message {assistant_msg_id[:8]}")
                break  # Break after first (and only) iteration
            except Exception as e:
                logger.error(f"❌ Background embedding storage failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
                break
    except Exception as e:
        logger.error(f"❌ Failed to get database session for background task: {e}")



def get_hybrid_system(db: AsyncSession = None) -> HybridFinMentorSystem:
    """Get or create hybrid system instance (singleton pattern)"""
    global hybrid_system
    if hybrid_system is None:
        config = {
            "model": os.getenv("DEFAULT_MODEL", "gemini-2.0-flash-exp"),  # Configurable via env
            "temperature": float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("DEFAULT_MAX_TOKENS", "4000")),
            "verbose": os.getenv("VERBOSE_LOGGING", "false").lower() == "true"
        }
        hybrid_system = HybridFinMentorSystem(config, db_session=db)
    elif db:
        # Update DB session if provided
        hybrid_system.agentic_rag.set_db_session(db)
    return hybrid_system

# REMOVED: DataSourcesManager class doesn't exist
# def get_data_manager() -> DataSourcesManager:
#     """Get or create data manager instance (singleton pattern)"""
#     global data_manager
#     if data_manager is None:
#         data_manager = DataSourcesManager()
#     return data_manager

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

async def process_document_input(
    document_data: str,
    filename: str,
    user_id: str,
    conversation_id: str,
    is_public: bool = False,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Process document input (PDFs) - NOW WITH PERSISTENT STORAGE
    Stores document in PGVector for future RAG retrieval
    """
    try:
        from services.document_storage import DocumentStorageService
        
        # Quick extraction for immediate response
        doc_bytes = base64.b64decode(document_data)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(doc_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Store in PGVector for future retrieval (if db provided)
        storage_result = None
        if db:
            doc_service = DocumentStorageService(db)
            storage_result = await doc_service.store_pdf(
                pdf_data=document_data,
                filename=filename,
                user_id=user_id,
                conversation_id=conversation_id,
                is_public=is_public
            )
            logger.info(f"Document storage result: {storage_result}")
        
        return {
            "type": "pdf",
            "pages": len(pdf_reader.pages),
            "text_preview": text[:500],
            "full_text": text,
            "stored": storage_result is not None and storage_result.get("success", False),
            "storage_info": storage_result
        }

    except Exception as e:
        logger.error(f"Document processing error: {e}")
        return {"error": str(e)}

# ============= Upload Endpoint =============

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    request: UploadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and process a document in the background.
    Returns a document_id that can be used in chat.
    """
    try:
        user_id = str(current_user.id)
        conversation_id = request.conversation_id or f"{user_id}_temp"
        
        result = await process_document_input(
            document_data=request.document_data,
            filename=request.filename,
            user_id=user_id,
            conversation_id=conversation_id,
            db=db
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        # Extract document_id from storage_info if available
        document_id = None
        if result.get("stored") and result.get("storage_info"):
            document_id = result["storage_info"].get("document_id")
            
        return UploadResponse(
            success=True,
            document_id=str(document_id) if document_id else None,
            filename=request.filename,
            message="Document processed successfully"
        )
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= Main Chat Endpoint =============

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)  # Database session injection
):
    """
    THE MAIN ENDPOINT - All queries come here!
    Handles: text, voice, images, documents
    This is the single entry point for ALL financial queries
    """


@router.post("", response_model=None)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with FinMentor AI (Streaming + Persistence)
    """
    try:
        # === 1. Setup Conversation & User Message ===
        from models.database import Conversation, Message
        import uuid
        from sqlalchemy import select
        import json

        # Get user profile
        user_profile = {
            "user_id": current_user.id,
            "username": current_user.username,
            "risk_tolerance": current_user.risk_tolerance,
            "investment_goals": current_user.financial_goals,
            "education_level": current_user.education_level,
            "user_type": current_user.user_type
        }

        processed_message = request.message
        logger.info(f"Chat request ({request.input_type}): {processed_message[:50]}...")

        # Initialize Hybrid System
        global hybrid_system
        if hybrid_system is None:
            hybrid_system = get_hybrid_system(db)

        # Get/Create Conversation
        conversation_id = request.conversation_id or str(uuid.uuid4())
        result_query = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        existing_conversation = result_query.scalar_one_or_none()
        
        if not existing_conversation:
            conversation = Conversation(
                id=conversation_id,
                user_id=current_user.id,
                title=processed_message[:100],
                topic="general",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(conversation)
            await db.flush()

        # Create User Message
        user_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            user_id=current_user.id,
            role="user",
            content=processed_message,
            input_type=request.input_type,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user_message)
        await db.commit() # Commit user message immediately

        # === 2. Streaming Generator with Persistence ===
        async def response_generator():
            full_response = ""
            completion_data = {}
            
            try:
                # Stream from Hybrid System
                async for chunk_str in hybrid_system.stream_query(
                    query=processed_message,
                    user_profile=user_profile,
                    voice_input=(request.input_type == "voice")
                ):
                    # Yield chunk to client immediately
                    yield chunk_str
                    
                    # Process chunk for persistence
                    try:
                        chunk = json.loads(chunk_str)
                        if chunk["type"] == "token":
                            full_response += chunk["content"]
                        elif chunk["type"] == "complete":
                            completion_data = chunk["data"]
                    except:
                        pass

                # === 3. Save Assistant Response on Completion ===
                # Create Assistant Message
                assistant_message = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conversation_id,
                    user_id=current_user.id,
                    role="assistant",
                    content=full_response,
                    created_at=datetime.now(timezone.utc),
                    confidence_score=completion_data.get("metadata", {}).get("confidence", 0.0),
                    processing_time=completion_data.get("metadata", {}).get("processing_time"),
                    response_data=completion_data.get("metrics", {})
                )
                db.add(assistant_message)
                
                # Update Conversation
                # We need to re-fetch or merge because session might be different/expired in generator? 
                # Actually, we are in the same request scope, so 'db' session is still valid until response closes.
                
                # Update conversation stats
                if existing_conversation:
                    existing_conversation.updated_at = datetime.now(timezone.utc)
                    existing_conversation.last_message_at = datetime.now(timezone.utc)
                    existing_conversation.total_messages = (existing_conversation.total_messages or 0) + 2
                    db.add(existing_conversation)
                else:
                    # If we created it earlier, we might need to re-fetch if not attached? 
                    # But db.add(conversation) was done.
                    # To be safe, let's just update via SQL update if object not attached
                    pass 

                await db.commit()
                logger.info(f"Saved streaming response for conversation {conversation_id}")
                
                # Yield conversation ID update to frontend if needed (as a metadata chunk)
                # The frontend already handles conversation_id from the first response if we sent it?
                # Actually, we can send a final metadata chunk if we want.
                yield json.dumps({
                    "type": "metadata", 
                    "content": {
                        "conversation_id": conversation_id,
                        "saved": True
                    }
                }) + "\n"

            except Exception as e:
                logger.error(f"Error in streaming generator: {e}")
                yield json.dumps({"type": "error", "content": str(e)}) + "\n"

        # Use StreamingResponse
        return StreamingResponse(
            response_generator(),
            media_type="application/x-ndjson"
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= Simple/Test Endpoints =============



# REMOVED: This endpoint uses non-existent DataSourcesManager
# @router.get("/test")
# async def test_chat():
#     """Test endpoint to verify system is working"""
#     try:
#         dm = get_data_manager()  # Get data manager to test connections
#         market_data = await dm.get_economic_indicators()  # Test market data fetch
#
#         return {
#             "status": "operational",  # System is working
#             "market_sample": market_data,  # Show sample market data
#             "supported_inputs": ["text", "voice", "image", "document"],  # List input types
#             "available_llms": ["gemini", "openai", "anthropic"]  # List LLM options
#         }
#     except Exception as e:
#         return {"status": "error", "message": str(e)}  # Return error status


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


# ============= Conversation History Endpoints =============

@router.get("/conversations")
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get list of user's conversations with titles and metadata
    Returns conversations ordered by most recent first
    """
    try:
        from models.database import Conversation
        from sqlalchemy import select, desc
        
        logger.info(f"Fetching conversations for user: {current_user.id} ({current_user.username})")
        
        # Query conversations ordered by most recent
        query = select(Conversation).where(
            Conversation.user_id == current_user.id
        ).order_by(desc(Conversation.updated_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        conversations = result.scalars().all()
        logger.info(f"Found {len(conversations)} conversations for user {current_user.id}")
        
        # Format response
        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                "id": conv.id,
                "user_id": conv.user_id,
                "title": conv.title,
                "topic": conv.topic,
                "total_messages": conv.total_messages,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None
            })
        
        return {
            "success": True,
            "conversations": conversation_list,
            "total": len(conversation_list),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 100
):
    """
    Get all messages from a specific conversation
    Returns messages ordered chronologically (oldest first)
    """
    try:
        from models.database import Message, Conversation
        from sqlalchemy import select
        
        # Verify conversation exists
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages for this conversation
        messages_query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).limit(limit)
        
        result = await db.execute(messages_query)
        messages = result.scalars().all()
        
        # Format messages
        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "input_type": msg.input_type,
                "confidence_score": msg.confidence_score,
                "model_used": msg.model_used,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        return {
            "success": True,
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat() if conversation.created_at else None
            },
            "messages": message_list,
            "total": len(message_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading conversation messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/rating")
async def submit_satisfaction_rating(
    conversation_id: str,
    rating: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit satisfaction rating for a conversation (1-5 stars)
    Called when user is prompted (every 50 conversations)
    """
    try:
        from models.database import Conversation
        from sqlalchemy import select
        
        # Validate rating
        if not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Get conversation
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update satisfaction rating
        conversation.satisfaction_rating = rating
        await db.commit()
        
        logger.info(f"Satisfaction rating {rating} submitted for conversation {conversation_id}")
        
        return {
            "success": True,
            "message": "Thank you for your feedback!",
            "rating": rating
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting rating: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages
    """
    try:
        from models.database import Conversation, Message
        from sqlalchemy import select, delete
        
        # Verify conversation exists
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete all messages first (foreign key constraint)
        await db.execute(delete(Message).where(Message.conversation_id == conversation_id))
        
        # Delete conversation
        await db.execute(delete(Conversation).where(Conversation.id == conversation_id))
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Conversation deleted successfully",
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============= Public/Private Conversation & Document Management =============

@router.post("/conversations/{conversation_id}/make-public")
async def make_conversation_public(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Make a conversation and all its documents public"""
    try:
        from models.database import Conversation
        from models.document import UserDocument, DocumentChunk
        from sqlalchemy import select, update
        
        # Get conversation  
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update conversation
        conversation.is_public = True
        conversation.visibility = "public"
        conversation.shared_at = datetime.utcnow()
        
        # Update all documents in this conversation
        await db.execute(
            update(UserDocument).where(
                UserDocument.conversation_id == conversation_id
            ).values(is_public=True)
        )
        
        # Update all document chunks
        await db.execute(
            update(DocumentChunk).where(
                DocumentChunk.conversation_id == conversation_id
            ).values(is_public=True)
        )
        
        await db.commit()
        
        logger.info(f"Conversation {conversation_id} made public")
        
        return {
            "success": True,
            "message": "Conversation is now public",
            "conversation_id": conversation_id,
            "shared_at": conversation.shared_at.isoformat() if conversation.shared_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making conversation public: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/make-private")
async def make_conversation_private(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Make a conversation private"""
    try:
        from models.database import Conversation
        from models.document import UserDocument, DocumentChunk
        from sqlalchemy import select, update
        
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation.is_public = False
        conversation.visibility = "private"
        
        await db.execute(
            update(UserDocument).where(
                UserDocument.conversation_id == conversation_id
            ).values(is_public=False)
        )
        
        await db.execute(
            update(DocumentChunk).where(
                DocumentChunk.conversation_id == conversation_id
            ).values(is_public=False)
        )
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Conversation is now private"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making conversation private: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/public")
async def get_public_conversations(
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "recent",
    db: AsyncSession = Depends(get_db)
):
    """Get public conversation feed"""
    try:
        from models.database import Conversation, User
        from models.document import UserDocument
        from sqlalchemy import select, func, desc
        
        query = select(
            Conversation.id,
            Conversation.title,
            Conversation.topic,
            Conversation.shared_at,
            Conversation.view_count,
            Conversation.upvote_count,
            User.username,
            func.count(UserDocument.id).label('document_count')
        ).join(
            User, Conversation.user_id == User.id
        ).outerjoin(
            UserDocument, Conversation.id == UserDocument.conversation_id
        ).where(
            Conversation.is_public == True
        ).group_by(
            Conversation.id, User.username
        )
        
        # Sort
        if sort_by == "popular":
            query = query.order_by(desc(Conversation.view_count))
        elif sort_by == "upvoted":
            query = query.order_by(desc(Conversation.upvote_count))
        else:
            query = query.order_by(desc(Conversation.shared_at))
        
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        conversations = result.fetchall()
        
        return {
            "success": True,
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "topic": conv.topic,
                    "shared_at": conv.shared_at.isoformat() if conv.shared_at else None,
                    "view_count": conv.view_count or 0,
                    "upvote_count": conv.upvote_count or 0,
                    "author": conv.username,
                    "document_count": conv.document_count or 0
                }
                for conv in conversations
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching public conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/mine")
async def get_my_documents(
    db: AsyncSession = Depends(get_db)
):
    """Get all documents uploaded by current user"""
    try:
        from models.document import UserDocument
        from sqlalchemy import select
        
        # TODO: Get user_id from authenticated user
        # For now, this will return all documents
        # You should add authentication to get the actual user_id
        
        query = select(UserDocument).order_by(UserDocument.upload_date.desc())
        
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return {
            "success": True,
            "documents": [
                {
                    "id": str(doc.id),
                    "filename": doc.filename,
                    "file_size": doc.file_size,
                    "total_pages": doc.total_pages,
                    "is_public": doc.is_public,
                    "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
                    "conversation_id": str(doc.conversation_id) if doc.conversation_id else None
                }
                for doc in documents
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching user documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/public")
async def get_public_documents(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get public documents"""
    try:
        from models.document import UserDocument
        from sqlalchemy import select
        
        query = select(UserDocument).where(
            UserDocument.is_public == True
        ).order_by(UserDocument.upload_date.desc()).limit(limit)
        
        result = await db.execute(query)
        documents = result.scalars().all()
        
        return {
            "success": True,
            "documents": [doc.to_dict() for doc in documents]
        }
        
    except Exception as e:
        logger.error(f"Error fetching public documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    user_id: str,  # Pass from auth
    db: AsyncSession = Depends(get_db)
):
    """Delete a document"""
    try:
        from services.document_storage import DocumentStorageService
        
        doc_service = DocumentStorageService(db)
        success = await doc_service.delete_document(document_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "message": "Document deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/upvote")
async def upvote_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Upvote a public conversation"""
    try:
        from models.database import Conversation
        from sqlalchemy import select
        
        conv_query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.is_public == True
        )
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Public conversation not found")
        
        conversation.upvote_count = (conversation.upvote_count or 0) + 1
        await db.commit()
        
        return {
            "success": True,
            "upvote_count": conversation.upvote_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upvoting: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
