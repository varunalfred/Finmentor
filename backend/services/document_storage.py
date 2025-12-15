"""
Document Storage Service
Handles storage of uploaded PDFs with PGVector embeddings
"""

import base64
import io
import logging
from typing import List, Dict, Optional
from PyPDF2 import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.document import UserDocument, DocumentChunk, UserStorageUsage

logger = logging.getLogger(__name__)

# Storage limits
DEFAULT_USER_STORAGE_LIMIT_MB = 100
PREMIUM_USER_STORAGE_LIMIT_MB = 1000
MAX_CHUNK_SIZE = 500  # characters
OVERLAP_SIZE = 50  # characters overlap between chunks


class DocumentStorageService:
    """Service for storing and managing documents with PGVector"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_model = None
    
    def _get_embedding_model(self):
        """Lazy load Sentence Transformer model"""
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading Sentence Transformer model: all-MiniLM-L6-v2")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model
    
    async def check_storage_quota(self, user_id: str, file_size: int, is_premium: bool = False) -> bool:
        """
        Check if user has enough storage quota
        Returns: True if user can upload, False if quota exceeded
        """
        # Get user's current storage
        result = await self.db.execute(
            select(UserStorageUsage).where(UserStorageUsage.user_id == user_id)
        )
        usage = result.scalar_one_or_none()
        
        current_storage_mb = 0
        if usage:
            current_storage_mb = usage.storage_mb
        
        # Determine limit
        limit_mb = PREMIUM_USER_STORAGE_LIMIT_MB if is_premium else DEFAULT_USER_STORAGE_LIMIT_MB
        
        # Check if adding this file would exceed limit
        file_size_mb = file_size / (1024 * 1024)
        would_exceed = (current_storage_mb + file_size_mb) > limit_mb
        
        if would_exceed:
            logger.warning(f"User {user_id} would exceed storage quota: {current_storage_mb + file_size_mb:.2f}MB / {limit_mb}MB")
        
        return not would_exceed
    
    async def store_pdf(
        self,
        pdf_data: str,
        filename: str,
        user_id: str,
        conversation_id: str,
        is_public: bool = False,
        document_id: Optional[str] = None
    ) -> Dict:
        """
        Store PDF with chunks in PGVector
        
        Args:
            pdf_data: Base64 encoded PDF content
            filename: Original filename
            user_id: User ID
            conversation_id: Conversation ID
            is_public: Whether document is public
            document_id: Optional pre-generated ID
            
        Returns:
            Dict with document info and success status
        """
        try:
            # 1. Decode and extract text
            pdf_bytes = base64.b64decode(pdf_data)
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            file_size = len(pdf_bytes)
            
            # Check storage quota (assume not premium for now)
            has_quota = await self.check_storage_quota(user_id, file_size, is_premium=False)
            if not has_quota:
                return {
                    "success": False,
                    "error": "Storage quota exceeded. Please upgrade or delete old documents."
                }
            
            # 2. Create document record
            document = UserDocument(
                id=document_id, # Use provided ID if any (DB will generate if None)
                conversation_id=conversation_id,
                user_id=user_id,
                filename=filename,
                file_size=file_size,
                mime_type="application/pdf",
                is_public=is_public,
                total_pages=len(reader.pages)
            )
            self.db.add(document)
            await self.db.flush()  # Get document ID
            
            logger.info(f"Created document record: {document.id}, {len(reader.pages)} pages")
            
            # 3. Process pages and create chunks
            chunks = []
            chunk_index = 0
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if not page_text.strip():
                    continue
                
                # Split page into chunks
                page_chunks = self._split_into_chunks(page_text, page_num + 1)
                
                for chunk_text in page_chunks:
                    # Generate embedding
                    embedding = self._generate_embedding(chunk_text)
                    
                    chunk = DocumentChunk(
                        document_id=document.id,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        chunk_text=chunk_text,
                        chunk_embedding=embedding,
                        page_number=page_num + 1,
                        chunk_index=chunk_index,
                        is_public=is_public
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            
            # 4. Bulk insert chunks
            self.db.add_all(chunks)
            document.total_chunks = len(chunks)
            
            # 5. Update user storage usage
            await self._update_storage_usage(user_id, file_size)
            
            # 6. Commit transaction
            await self.db.commit()
            
            logger.info(f"Successfully stored document with {len(chunks)} chunks")
            
            return {
                "success": True,
                "document_id": document.id,
                "filename": filename,
                "pages": len(reader.pages),
                "chunks": len(chunks),
                "size_mb": round(file_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error storing PDF: {e}")
            await self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _split_into_chunks(self, text: str, page_num: int, max_size: int = MAX_CHUNK_SIZE) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to split
            page_num: Page number
            max_size: Maximum chunk size in characters
            
        Returns:
            List of text chunks
        """
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If paragraph alone exceeds max_size, split by sentences
            if len(para) > max_size:
                sentences = para.split('. ')
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > max_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += (" " if current_chunk else "") + sentence
            else:
                # Add paragraph to current chunk
                if len(current_chunk) + len(para) > max_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para
                else:
                    current_chunk += ("\n\n" if current_chunk else "") + para
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [c for c in chunks if len(c.strip()) > 50]  # Filter out very small chunks
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using Sentence Transformers
        
        Args:
            text: Text to embed
            
        Returns:
            384-dimensional embedding vector
        """
        model = self._get_embedding_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    async def _update_storage_usage(self, user_id: str, file_size: int):
        """Update user's storage usage"""
        result = await self.db.execute(
            select(UserStorageUsage).where(UserStorageUsage.user_id == user_id)
        )
        usage = result.scalar_one_or_none()
        
        if usage:
            usage.total_storage_bytes += file_size
            usage.document_count += 1
        else:
            usage = UserStorageUsage(
                user_id=user_id,
                total_storage_bytes=file_size,
                document_count=1
            )
            self.db.add(usage)
    
    async def make_document_public(self, document_id: str, user_id: str) -> bool:
        """
        Make a document and its chunks public
        
        Args:
            document_id: Document ID
            user_id: User ID (for verification)
            
        Returns:
            True if successful
        """
        try:
            # Get document
            result = await self.db.execute(
                select(UserDocument).where(
                    UserDocument.id == document_id,
                    UserDocument.user_id == user_id
                )
            )
            document = result.scalar_one_or_none()
            
            if not document:
                logger.warning(f"Document {document_id} not found for user {user_id}")
                return False
            
            # Update document
            document.is_public = True
            
            # Update all chunks
            await self.db.execute(
                f"UPDATE document_chunks SET is_public = TRUE WHERE document_id = '{document_id}'"
            )
            
            await self.db.commit()
            logger.info(f"Document {document_id} made public")
            return True
            
        except Exception as e:
            logger.error(f"Error making document public: {e}")
            await self.db.rollback()
            return False
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete document and all chunks (CASCADE)
        
        Args:
            document_id: Document ID
            user_id: User ID (for verification)
            
        Returns:
            True if successful
        """
        try:
            # Get document
            result = await self.db.execute(
                select(UserDocument).where(
                    UserDocument.id == document_id,
                    UserDocument.user_id == user_id
                )
            )
            document = result.scalar_one_or_none()
            
            if not document:
                return False
            
            file_size = document.file_size
            
            # Delete document (chunks delete automatically via CASCADE)
            await self.db.delete(document)
            
            # Update storage usage
            result = await self.db.execute(
                select(UserStorageUsage).where(UserStorageUsage.user_id == user_id)
            )
            usage = result.scalar_one_or_none()
            if usage:
                usage.total_storage_bytes -= file_size
                usage.document_count -= 1
            
            await self.db.commit()
            logger.info(f"Document {document_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            await self.db.rollback()
            return False
