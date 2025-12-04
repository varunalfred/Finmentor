-- ============================================
-- Migration: Add Document Storage System
-- Date: 2024-11-27
-- Version: 001
-- Safe: YES - Only adding new tables and columns
-- ============================================

BEGIN;

-- Step 1: Add public/private fields to conversations
-- SAFE: Just adding new columns with defaults
ALTER TABLE conversations 
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS visibility VARCHAR(20) DEFAULT 'private',
ADD COLUMN IF NOT EXISTS shared_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS view_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS upvote_count INTEGER DEFAULT 0;

-- Index for public conversations feed
CREATE INDEX IF NOT EXISTS idx_public_conversations 
ON conversations(is_public, shared_at DESC) 
WHERE is_public = TRUE;

-- Step 2: Create user_documents table
CREATE TABLE IF NOT EXISTS user_documents (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    is_public BOOLEAN DEFAULT FALSE,
    total_pages INTEGER,
    total_chunks INTEGER,
    upload_date TIMESTAMP DEFAULT NOW(),
    doc_metadata JSON
);

-- Indexes for user_documents
CREATE INDEX IF NOT EXISTS idx_user_docs_user 
ON user_documents(user_id, upload_date DESC);

CREATE INDEX IF NOT EXISTS idx_user_docs_public 
ON user_documents(is_public, upload_date DESC) 
WHERE is_public = TRUE;

CREATE INDEX IF NOT EXISTS idx_user_docs_conversation 
ON user_documents(conversation_id);

-- Step 3: Create document_chunks table with PGVector
CREATE TABLE IF NOT EXISTS document_chunks (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) REFERENCES user_documents(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL,
    conversation_id VARCHAR(36) REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Content
    chunk_text TEXT NOT NULL,
    chunk_embedding vector(384),  -- Sentence Transformers dimension
    
    -- Position
    page_number INTEGER,
    chunk_index INTEGER,
   
   -- Privacy
    is_public BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    doc_metadata JSON,
    created_at TIMESTAMP DEFAULT NOW()
);

-- PGVector index for similarity search (all chunks)
CREATE INDEX IF NOT EXISTS idx_chunk_embedding 
ON document_chunks 
USING ivfflat (chunk_embedding vector_cosine_ops)
WITH (lists = 100);

-- Separate PGVector index for public chunks only
CREATE INDEX IF NOT EXISTS idx_public_chunk_embedding 
ON document_chunks 
USING ivfflat (chunk_embedding vector_cosine_ops)
WITH (lists = 50)
WHERE is_public = TRUE;

-- Regular indexes
CREATE INDEX IF NOT EXISTS idx_chunk_user 
ON document_chunks(user_id);

CREATE INDEX IF NOT EXISTS idx_chunk_conversation 
ON document_chunks(conversation_id);

CREATE INDEX IF NOT EXISTS idx_chunk_document 
ON document_chunks(document_id);

-- Step 4: Create user storage tracking table
CREATE TABLE IF NOT EXISTS user_storage_usage (
    user_id VARCHAR(36) PRIMARY KEY,
    total_storage_bytes BIGINT DEFAULT 0,
    document_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

COMMIT;
