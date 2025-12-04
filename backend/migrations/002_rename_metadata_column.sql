-- ============================================
-- Migration: Rename metadata to doc_metadata
-- Date: 2024-11-27
-- Version: 002
-- Safe: YES - Just renaming columns
-- Reason: 'metadata' is a reserved name in SQLAlchemy
-- ============================================

BEGIN;

-- Rename metadata column in user_documents table
ALTER TABLE user_documents 
RENAME COLUMN metadata TO doc_metadata;

-- Rename metadata column in document_chunks table
ALTER TABLE document_chunks 
RENAME COLUMN metadata TO doc_metadata;

COMMIT;

-- Verification queries (run these after migration)
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'user_documents';
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'document_chunks';
