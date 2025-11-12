"""
RAG System Requirements Verification
Checks all dependencies and system requirements
"""

import sys
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)")
        return False


def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name} ({version})")
        return True
    except ImportError:
        print(f"❌ {package_name} - NOT INSTALLED")
        return False


def check_core_dependencies():
    """Check core dependencies"""
    print("\n=== Core Dependencies ===")
    
    packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('sqlalchemy', 'sqlalchemy'),
        ('asyncpg', 'asyncpg'),
        ('pydantic', 'pydantic'),
    ]
    
    results = [check_package(pkg, imp) for pkg, imp in packages]
    return all(results)


def check_ai_dependencies():
    """Check AI/LLM dependencies"""
    print("\n=== AI/LLM Dependencies ===")
    
    packages = [
        ('dspy-ai', 'dspy'),
        ('langchain', 'langchain'),
        ('langchain-openai', 'langchain_openai'),
        ('langchain-google-genai', 'langchain_google_genai'),
        ('langchain-community', 'langchain_community'),
    ]
    
    results = [check_package(pkg, imp) for pkg, imp in packages]
    return all(results)


def check_rag_dependencies():
    """Check RAG-specific dependencies"""
    print("\n=== RAG System Dependencies ===")
    
    packages = [
        ('sentence-transformers', 'sentence_transformers'),
        ('pgvector', 'pgvector'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
    ]
    
    results = [check_package(pkg, imp) for pkg, imp in packages]
    return all(results)


def check_files():
    """Check if required files exist"""
    print("\n=== Required Files ===")
    
    base_dir = Path(__file__).parent.parent
    
    files = [
        'RAG/__init__.py',
        'RAG/embeddings.py',
        'RAG/vector_store.py',
        'RAG/retriever.py',
        'RAG/rag_pipeline.py',
        'RAG/glossary_clean.csv',
        'services/rag_service.py',
        'routers/rag.py',
        'config/rag_config.py',
        'tests/test_rag.py',
    ]
    
    results = []
    for file_path in files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
            results.append(True)
        else:
            print(f"❌ {file_path} - NOT FOUND")
            results.append(False)
    
    return all(results)


def check_environment():
    """Check environment variables"""
    print("\n=== Environment Variables ===")
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Required
    required = {
        'DATABASE_URL': os.getenv('DATABASE_URL')
    }
    
    # Optional but recommended
    optional = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY') or os.getenv('EMBEDDING_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'EMBEDDING_PROVIDER': os.getenv('EMBEDDING_PROVIDER', 'auto')
    }
    
    print("Required:")
    all_required = True
    for key, value in required.items():
        if value:
            print(f"✅ {key}: {'*' * 20}...")
        else:
            print(f"❌ {key}: NOT SET")
            all_required = False
    
    print("\nOptional:")
    for key, value in optional.items():
        if value:
            if 'KEY' in key:
                print(f"✅ {key}: {'*' * 20}...")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"⚠️  {key}: NOT SET (will use defaults)")
    
    return all_required


def print_installation_instructions():
    """Print installation instructions for missing packages"""
    print("\n=== Installation Instructions ===")
    print("\nTo install missing packages, run:")
    print("\n  pip install -r requirements.txt")
    print("\nFor RAG-specific packages:")
    print("\n  pip install langchain-google-genai langchain-openai langchain-community sentence-transformers")


def print_next_steps():
    """Print next steps"""
    print("\n=== Next Steps ===")
    print("\n1. Install missing dependencies:")
    print("   pip install -r requirements.txt")
    print("\n2. Set up environment variables (optional):")
    print("   Create .env file with GEMINI_API_KEY or OPENAI_API_KEY")
    print("\n3. Run setup script:")
    print("   python scripts/setup_rag.py")
    print("\n4. Start API server:")
    print("   uvicorn main:app --reload")
    print("\n5. Test the system:")
    print("   curl http://localhost:8000/api/rag/status")


def main():
    """Main verification function"""
    print("=" * 60)
    print("RAG System Requirements Verification")
    print("=" * 60)
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check dependencies
    core_ok = check_core_dependencies()
    ai_ok = check_ai_dependencies()
    rag_ok = check_rag_dependencies()
    
    # Check files
    files_ok = check_files()
    
    # Check environment
    env_ok = check_environment()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_ok = python_ok and core_ok and ai_ok and rag_ok and files_ok and env_ok
    
    if all_ok:
        print("\n✅ All requirements satisfied!")
        print("\n🚀 Your RAG system is ready to use!")
        print("\nNext command:")
        print("  python scripts/setup_rag.py")
    else:
        print("\n⚠️  Some requirements are missing")
        print_installation_instructions()
        print_next_steps()
    
    return all_ok


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)
