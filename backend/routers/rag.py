"""
RAG Router - API endpoints for RAG system
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import db_service
from services.rag_service import get_rag_service, RAGService
from routers.auth import get_current_user
from models.database import User

router = APIRouter()


# ============= Request/Response Models =============

class SearchQuery(BaseModel):
    """Search query request"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    topic: Optional[str] = Field(None, description="Filter by topic")
    level: Optional[str] = Field(None, description="Filter by level (beginner, intermediate, advanced)")
    include_sources: bool = Field(True, description="Include source documents")


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    context: str
    num_sources: int
    has_context: bool
    sources: Optional[List[Dict[str, Any]]] = None


class LoadGlossaryResponse(BaseModel):
    """Glossary loading response"""
    success: bool
    message: str
    stats: Dict[str, Any]


# ============= Endpoints =============

@router.get("/status")
async def get_rag_status(
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Get RAG system status
    
    Returns:
        - System configuration
        - Knowledge base statistics
        - Available topics
    """
    try:
        rag_service = await get_rag_service(session)
        status = await rag_service.get_status()
        
        return JSONResponse(content={
            'status': 'active',
            **status
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.get("/statistics")
async def get_statistics(
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Get detailed RAG system statistics
    
    Returns:
        - Total documents
        - Documents by topic
        - Embedding provider info
    """
    try:
        rag_service = await get_rag_service(session)
        stats = await rag_service.get_statistics()
        
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting statistics: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(
    query: SearchQuery,
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Search the knowledge base using RAG
    
    Args:
        query: Search parameters
        
    Returns:
        Relevant context and source documents
    """
    try:
        rag_service = await get_rag_service(session)
        
        # Build filters
        filters = {}
        if query.topic:
            filters['topic'] = query.topic
        if query.level:
            filters['level'] = query.level
        
        # Search
        result = await rag_service.search(
            query=query.query,
            top_k=query.top_k,
            filters=filters if filters else None
        )
        
        response = {
            'query': query.query,
            'context': result['context'],
            'num_sources': result['num_sources'],
            'has_context': result['has_context']
        }
        
        if query.include_sources:
            response['sources'] = result.get('sources', [])
        
        return JSONResponse(content=response)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/search")
async def search_knowledge_base_get(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    level: Optional[str] = Query(None, description="Filter by level"),
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Search knowledge base (GET method)
    
    Query parameters:
        - q: Search query
        - top_k: Number of results (1-20)
        - topic: Filter by topic
        - level: Filter by level
        
    Returns:
        Search results with context and sources
    """
    try:
        rag_service = await get_rag_service(session)
        
        filters = {}
        if topic:
            filters['topic'] = topic
        if level:
            filters['level'] = level
        
        result = await rag_service.search(
            query=q,
            top_k=top_k,
            filters=filters if filters else None
        )
        
        return JSONResponse(content={
            'query': q,
            **result
        })
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/topics")
async def get_topics(
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Get list of available topics
    
    Returns:
        List of topic names
    """
    try:
        rag_service = await get_rag_service(session)
        topics = await rag_service.get_topics()
        
        return JSONResponse(content={
            'topics': topics,
            'count': len(topics)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting topics: {str(e)}")


@router.post("/load-glossary", response_model=LoadGlossaryResponse)
async def load_glossary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Load financial glossary into knowledge base
    
    Requires authentication.
    
    Returns:
        Loading statistics
    """
    try:
        rag_service = await get_rag_service(session)
        
        # Check if already loaded
        is_loaded = await rag_service.check_knowledge_base_loaded()
        if is_loaded:
            return JSONResponse(content={
                'success': False,
                'message': 'Knowledge base already loaded. Use /reload-glossary to reload.',
                'stats': {}
            })
        
        # Load glossary
        stats = await rag_service.load_glossary()
        
        return JSONResponse(content={
            'success': True,
            'message': f"Successfully loaded {stats['loaded']} terms into knowledge base",
            'stats': stats
        })
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading glossary: {str(e)}")


@router.post("/reload-glossary", response_model=LoadGlossaryResponse)
async def reload_glossary(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Reload financial glossary (updates existing entries)
    
    Requires authentication.
    
    Returns:
        Loading statistics
    """
    try:
        rag_service = await get_rag_service(session)
        stats = await rag_service.load_glossary()
        
        return JSONResponse(content={
            'success': True,
            'message': f"Successfully reloaded glossary. Processed {stats['total']} terms.",
            'stats': stats
        })
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading glossary: {str(e)}")


@router.get("/check")
async def check_knowledge_base(
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Check if knowledge base is loaded
    
    Returns:
        Status of knowledge base
    """
    try:
        rag_service = await get_rag_service(session)
        is_loaded = await rag_service.check_knowledge_base_loaded()
        stats = await rag_service.get_status()
        
        return JSONResponse(content={
            'loaded': is_loaded,
            'document_count': stats['total_documents'],
            'topics_available': len(stats['topics']),
            'ready': is_loaded and stats['total_documents'] > 0
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking knowledge base: {str(e)}")


@router.get("/context/{query}")
async def get_context(
    query: str,
    top_k: int = Query(5, ge=1, le=20),
    topic: Optional[str] = Query(None),
    session: AsyncSession = Depends(db_service.get_session)
) -> Dict[str, Any]:
    """
    Get formatted context for a query (without full search response)
    
    Path parameters:
        - query: Search query
        
    Query parameters:
        - top_k: Number of documents
        - topic: Filter by topic
        
    Returns:
        Formatted context string
    """
    try:
        rag_service = await get_rag_service(session)
        
        filters = {'topic': topic} if topic else None
        
        context = await rag_service.get_context_for_question(
            question=query,
            top_k=top_k,
            filters=filters
        )
        
        return JSONResponse(content={
            'query': query,
            'context': context,
            'has_context': len(context) > 0
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting context: {str(e)}")
