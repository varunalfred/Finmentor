"""
Conversation Service
Handles conversation management, user activity logging, and statistics
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
import logging

from models.database import Conversation, Message, User

logger = logging.getLogger(__name__)

class ConversationService:
    """Service for managing conversations and user activity"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============= User Activity Logging =============

    async def log_user_activity(
        self,
        user_id: str,
        activity_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log user activity (login, logout, etc.)
        
        Args:
            user_id: User ID
            activity_type: Type of activity (login, logout, query, etc.)
            details: Additional activity details
        
        Returns:
            True if logged successfully
        """
        try:
            # For now, just log to console
            # In production, you'd save to a user_activity table
            logger.info(f"User activity: {user_id} - {activity_type} - {details}")
            return True
        except Exception as e:
            logger.error(f"Failed to log user activity: {e}")
            return False

    # ============= Conversation Management =============

    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Optional[Conversation]:
        """
        Create a new conversation
        
        Args:
            user_id: User ID
            title: Conversation title
            topic: Conversation topic
        
        Returns:
            Created conversation or None
        """
        try:
            conversation = Conversation(
                user_id=user_id,
                title=title or "New Conversation",
                topic=topic or "general",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)
            
            logger.info(f"Created conversation {conversation.id} for user {user_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            await self.db.rollback()
            return None

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Conversation]:
        """
        Get user's conversations
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations
            offset: Offset for pagination
        
        Returns:
            List of conversations
        """
        try:
            result = await self.db.execute(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(desc(Conversation.updated_at))
                .limit(limit)
                .offset(offset)
            )
            conversations = result.scalars().all()
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get user conversations: {e}")
            return []

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> Optional[Conversation]:
        """
        Get a specific conversation
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)
        
        Returns:
            Conversation or None
        """
        try:
            result = await self.db.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user_id
                    )
                )
            )
            conversation = result.scalar_one_or_none()
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None

    # ============= Message Management =============

    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        **kwargs
    ) -> Optional[Message]:
        """
        Add a message to a conversation
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            role: Message role (user, assistant, system)
            content: Message content
            **kwargs: Additional message fields
        
        Returns:
            Created message or None
        """
        try:
            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content,
                created_at=datetime.utcnow(),
                **kwargs
            )
            
            self.db.add(message)
            
            # Update conversation's last_message_at
            await self.db.execute(
                select(Conversation)
                .where(Conversation.id == conversation_id)
            )
            
            await self.db.commit()
            await self.db.refresh(message)
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            await self.db.rollback()
            return None

    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Message]:
        """
        Get messages from a conversation
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
        
        Returns:
            List of messages
        """
        try:
            result = await self.db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
                .limit(limit)
            )
            messages = result.scalars().all()
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    # ============= User Statistics =============

    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with user statistics
        """
        try:
            # Count conversations
            conv_result = await self.db.execute(
                select(func.count(Conversation.id))
                .where(Conversation.user_id == user_id)
            )
            conversation_count = conv_result.scalar() or 0
            
            # Count messages
            msg_result = await self.db.execute(
                select(func.count(Message.id))
                .where(
                    and_(
                        Message.user_id == user_id,
                        Message.role == "user"
                    )
                )
            )
            message_count = msg_result.scalar() or 0
            
            # Get last activity
            last_msg_result = await self.db.execute(
                select(Message.created_at)
                .where(Message.user_id == user_id)
                .order_by(desc(Message.created_at))
                .limit(1)
            )
            last_activity = last_msg_result.scalar_one_or_none()
            
            return {
                "total_conversations": conversation_count,
                "total_messages": message_count,
                "last_activity": last_activity.isoformat() if last_activity else None,
                "active_user": conversation_count > 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics: {e}")
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "last_activity": None,
                "active_user": False
            }

    # ============= Conversation Updates =============

    async def update_conversation(
        self,
        conversation_id: str,
        user_id: str,
        **updates
    ) -> bool:
        """
        Update conversation details
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)
            **updates: Fields to update
        
        Returns:
            True if updated successfully
        """
        try:
            result = await self.db.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user_id
                    )
                )
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return False
            
            for key, value in updates.items():
                if hasattr(conversation, key):
                    setattr(conversation, key, value)
            
            conversation.updated_at = datetime.utcnow()
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation: {e}")
            await self.db.rollback()
            return False

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a conversation
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)
        
        Returns:
            True if deleted successfully
        """
        try:
            result = await self.db.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user_id
                    )
                )
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return False
            
            await self.db.delete(conversation)
            await self.db.commit()
            
            logger.info(f"Deleted conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            await self.db.rollback()
            return False
