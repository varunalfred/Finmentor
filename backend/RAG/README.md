# RAG System - Financial Education Knowledge Base

This directory contains the RAG (Retrieval-Augmented Generation) system for intelligent financial education content retrieval.

## 📁 Directory Contents

- **`__init__.py`** - Module initialization and exports
- **`embeddings.py`** - Multi-provider embedding service (Gemini/OpenAI/Local)
- **`vector_store.py`** - PGVector integration for similarity search
- **`retriever.py`** - Intelligent document retrieval with filtering
- **`rag_pipeline.py`** - Complete RAG pipeline orchestration
- **`glossary_clean.csv`** - Financial glossary with 538+ terms

## 🚀 Quick Start

### Load the Glossary

```python
from services.database import db_service
from services.rag_service import get_rag_service

async def load():
    async with db_service.get_session() as session:
        rag = await get_rag_service(session)
        stats = await rag.load_glossary()
        print(f"Loaded {stats['loaded']} terms")
```

### Search the Knowledge Base

```python
async def search():
    async with db_service.get_session() as session:
        rag = await get_rag_service(session)
        
        result = await rag.search("What is P/E ratio?", top_k=5)
        print(result['context'])
```

## 🔧 Configuration

The system uses three embedding providers:

1. **Gemini** (Google) - 768 dimensions, free tier: 1,500/day
2. **OpenAI** - 1536 dimensions, paid service
3. **Local** (HuggingFace) - 384 dimensions, completely free

Set provider via environment:
```bash
EMBEDDING_PROVIDER=auto  # auto, gemini, openai, or local
GEMINI_API_KEY=your-key  # for Gemini
OPENAI_API_KEY=your-key  # for OpenAI
```

If no API keys are provided, the system automatically uses free local embeddings.

## 📊 Glossary Format

The `glossary_clean.csv` file should have these columns:

- **Term** - Financial term name
- **Definition** - Detailed explanation
- **Category** - Topic category (e.g., "Stocks", "Bonds")
- **Level** - Difficulty level (beginner, intermediate, advanced)

## 🎯 Features

- ✅ Multi-provider embeddings with auto-fallback
- ✅ Vector similarity search using PGVector
- ✅ Context-aware retrieval with conversation history
- ✅ Topic and level filtering
- ✅ Batch processing for efficiency
- ✅ Comprehensive error handling
- ✅ Singleton pattern for resource management

## 📖 API Usage

The RAG system is exposed via REST API at `/api/rag/`:

```bash
# Search
curl "http://localhost:8000/api/rag/search?q=diversification"

# Get status
curl http://localhost:8000/api/rag/status

# List topics
curl http://localhost:8000/api/rag/topics
```

## 🧪 Testing

Run tests:
```bash
pytest ../tests/test_rag.py -v
```

## 📚 Documentation

See parent directory for:
- **RAG_SETUP_GUIDE.md** - Complete setup guide
- **RAG_IMPLEMENTATION_SUMMARY.md** - Implementation details

## 🔐 Security

- API keys stored in environment variables
- No keys committed to repository
- Local embeddings available for privacy
- SQL injection prevention via SQLAlchemy

## 🚀 Performance

| Provider | Speed (single) | Batch (538 terms) | Quality |
|----------|---------------|-------------------|---------|
| Gemini   | ~100ms        | 2-5 min          | High    |
| OpenAI   | ~150ms        | 3-7 min          | Highest |
| Local    | ~50ms*        | 10-15 min        | Good    |

*After initial model load

## 📞 Support

For help:
1. Run: `python ../scripts/verify_rag_requirements.py`
2. Check: `../RAG_SETUP_GUIDE.md`
3. Test: `pytest ../tests/test_rag.py -v`
