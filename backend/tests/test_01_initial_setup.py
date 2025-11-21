"""
Test 01: Initial Setup Verification
Tests database connection, environment variables, and basic configuration
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

# ============= Test 1: Environment Variables =============

def test_environment_variables():
    """Test if required environment variables are set"""
    print_test_header("Environment Variables")
    
    required_vars = {
        "DATABASE_URL": "Database connection string",
        "JWT_SECRET_KEY": "JWT secret for authentication"
    }
    
    optional_vars = {
        "GEMINI_API_KEY": "Google Gemini API (Primary LLM)",
        "OPENAI_API_KEY": "OpenAI API (Alternative LLM)",
        "ANTHROPIC_API_KEY": "Anthropic Claude API (Alternative LLM)",
        "ALPHA_VANTAGE_API_KEY": "Alpha Vantage (Market data)",
        "NEWS_API_KEY": "NewsAPI (Financial news)",
        "GOOGLE_CSE_ID": "Google Custom Search",
        "REDIS_URL": "Redis cache",
        "ALLOWED_ORIGINS": "CORS allowed origins"
    }
    
    all_ok = True
    
    # Check required variables
    print(f"{Colors.BOLD}Required Variables:{Colors.RESET}")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print_success(f"{var}: Set ({description})")
        else:
            print_error(f"{var}: NOT SET ({description})")
            all_ok = False
    
    # Check optional variables
    print(f"\n{Colors.BOLD}Optional Variables:{Colors.RESET}")
    llm_count = 0
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here" and value != "your_" + var.lower().replace('_', '_') + "_here":
            print_success(f"{var}: Set ({description})")
            if "API_KEY" in var and any(x in var for x in ["GEMINI", "OPENAI", "ANTHROPIC"]):
                llm_count += 1
        else:
            print_warning(f"{var}: Not set ({description})")
    
    # Check if at least one LLM is configured
    print(f"\n{Colors.BOLD}LLM Configuration:{Colors.RESET}")
    if llm_count > 0:
        print_success(f"LLM APIs configured: {llm_count}")
    else:
        print_error("No LLM API key configured! System needs at least one LLM.")
        all_ok = False
    
    return all_ok

# ============= Test 2: Python Dependencies =============

def test_dependencies():
    """Test if required Python packages are installed"""
    print_test_header("Python Dependencies")
    
    required_packages = {
        "fastapi": "FastAPI framework",
        "uvicorn": "ASGI server",
        "sqlalchemy": "ORM for database",
        "asyncpg": "PostgreSQL async driver",
        "dspy": "DSPy framework",
        "langchain": "LangChain framework",
        "yfinance": "Yahoo Finance data",
        "pandas": "Data manipulation",
        "numpy": "Numerical computing"
    }
    
    all_ok = True
    
    for package, description in required_packages.items():
        try:
            if package == "dspy":
                __import__("dspy")
            else:
                __import__(package)
            print_success(f"{package}: Installed ({description})")
        except ImportError:
            print_error(f"{package}: NOT INSTALLED ({description})")
            all_ok = False
    
    return all_ok

# ============= Test 3: Database Connection =============

async def test_database_connection():
    """Test database connection"""
    print_test_header("Database Connection")
    
    try:
        from services.database import db_service
        
        # Get DATABASE_URL directly from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print_error("DATABASE_URL environment variable is not set!")
            print_info("Set it in your .env file")
            return False
        
        # Mask password in URL for display
        display_url = database_url.split('@')[1] if '@' in database_url else database_url
        print_info(f"Database: {display_url}")
        
        # Test async connection
        try:
            from sqlalchemy import text
            async with db_service.engine.connect() as conn:
                result = await conn.execute(text("SELECT version();"))
                version = result.fetchone()
                print_success(f"Database connection successful!")
                print_info(f"PostgreSQL version: {version[0][:50]}...")
                
                # Check if PGVector is available
                try:
                    result = await conn.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector';"))
                    vector_version = result.fetchone()
                    if vector_version:
                        print_success(f"PGVector extension installed (version {vector_version[0]})")
                    else:
                        print_warning("PGVector extension not installed - semantic search will use fallback")
                except Exception as e:
                    print_warning(f"PGVector check failed: {str(e)[:50]}")
                
            # Properly dispose of connections
            await db_service.engine.dispose()
            return True
            
        except Exception as e:
            print_error(f"Database connection failed: {str(e)}")
            print_info("Troubleshooting:")
            print_info("  • Make sure PostgreSQL is running")
            print_info("  • Check DATABASE_URL in .env is correct")
            print_info("  • Stop the server if it's running (it may hold connections)")
            return False
            
    except Exception as e:
        print_error(f"Failed to import database service: {str(e)}")
        return False

# ============= Test 4: Database Models =============

async def test_database_models():
    """Test if database models are properly defined"""
    print_test_header("Database Models")
    
    try:
        from models.database import (
            Base, User, Conversation, Message, 
            Portfolio, Holding, Transaction,
            EducationalContent, LearningProgress
        )
        
        models = [
            ("User", User),
            ("Conversation", Conversation),
            ("Message", Message),
            ("Portfolio", Portfolio),
            ("Holding", Holding),
            ("Transaction", Transaction),
            ("EducationalContent", EducationalContent),
            ("LearningProgress", LearningProgress)
        ]
        
        all_ok = True
        for name, model in models:
            try:
                # Check if model has __tablename__
                if hasattr(model, '__tablename__'):
                    print_success(f"{name} model: Defined (table: {model.__tablename__})")
                else:
                    print_error(f"{name} model: Missing __tablename__")
                    all_ok = False
            except Exception as e:
                print_error(f"{name} model: Error - {str(e)}")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print_error(f"Failed to import models: {str(e)}")
        return False

# ============= Test 5: Initialize Database Tables =============

async def test_database_initialization():
    """Test database table creation"""
    print_test_header("Database Initialization")
    
    try:
        from services.database import init_db
        from models.database import Base
        
        print_info("Creating database tables...")
        await init_db()
        print_success("Database tables created successfully!")
        
        # List created tables
        from sqlalchemy import text
        from services.database import db_service
        
        async with db_service.engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            
            if tables:
                print_info(f"Created {len(tables)} tables:")
                for table in tables:
                    print(f"  • {table[0]}")
                return True
            else:
                print_warning("No tables found - this might be an issue")
                return False
                
    except Exception as e:
        print_error(f"Database initialization failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

# ============= Test 6: DSPy Configuration =============

def test_dspy_setup():
    """Test DSPy framework setup"""
    print_test_header("DSPy Framework")
    
    try:
        import dspy
        print_success("DSPy imported successfully")
        
        # Check if we can configure DSPy with available LLM (using new dspy.LM API)
        if os.getenv("GEMINI_API_KEY"):
            try:
                # Set environment variable for LiteLLM
                api_key = os.getenv("GEMINI_API_KEY")
                os.environ["GEMINI_API_KEY"] = api_key
                
                lm = dspy.LM(model="gemini/gemini-1.5-flash")
                dspy.configure(lm=lm)
                print_success("DSPy configured with Gemini (using dspy.LM)")
                return True
            except Exception as e:
                print_warning(f"Gemini configuration failed: {str(e)[:50]}")
        
        if os.getenv("OPENAI_API_KEY"):
            try:
                lm = dspy.LM(model="openai/gpt-3.5-turbo")
                dspy.configure(lm=lm)
                print_success("DSPy configured with OpenAI (using dspy.LM)")
                return True
            except Exception as e:
                print_warning(f"OpenAI configuration failed: {str(e)[:50]}")
        
        print_error("No LLM configured for DSPy - add GEMINI_API_KEY or OPENAI_API_KEY")
        return False
        
    except Exception as e:
        print_error(f"DSPy setup failed: {str(e)}")
        return False

# ============= Test 7: Agents Setup =============

def test_agents_import():
    """Test if agent modules can be imported"""
    print_test_header("Agent Modules")
    
    agent_modules = {
        "hybrid_core": "Hybrid DSPy+LangChain system",
        "orchestrator": "Multi-agent orchestrator",
        "specialized_signatures": "Specialized agent signatures",
        "financial_tools": "Financial calculation tools",
        "langchain_tools": "LangChain tool integration"
    }
    
    all_ok = True
    for module, description in agent_modules.items():
        try:
            __import__(f"agents.{module}")
            print_success(f"{module}: Imported ({description})")
        except Exception as e:
            print_error(f"{module}: Failed to import - {str(e)[:50]}")
            all_ok = False
    
    return all_ok

# ============= Test 8: Data Sources =============

async def test_data_sources():
    """Test data sources integration"""
    print_test_header("Data Sources")
    
    try:
        from services.data_sources import DataSourcesManager
        
        data_manager = DataSourcesManager()
        print_success("DataSourcesManager initialized")
        
        # Test Yahoo Finance
        try:
            import yfinance as yf
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            if info:
                print_success(f"Yahoo Finance working (AAPL: ${info.get('currentPrice', 'N/A')})")
        except Exception as e:
            print_warning(f"Yahoo Finance test failed: {str(e)[:50]}")
        
        # Test DuckDuckGo Search
        try:
            from ddgs import DDGS
            ddg = DDGS()
            print_success("DuckDuckGo Search available (no API key needed)")
        except Exception as e:
            print_warning(f"DuckDuckGo import failed: {str(e)[:50]}")
        
        return True
        
    except Exception as e:
        print_error(f"Data sources test failed: {str(e)}")
        return False

# ============= Main Test Runner =============

async def run_all_tests():
    """Run all setup tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("  FinMentor AI - Initial Setup Verification")
    print("=" * 60)
    print(f"{Colors.RESET}\n")
    
    results = {}
    
    # Run tests in order
    results['Environment Variables'] = test_environment_variables()
    results['Python Dependencies'] = test_dependencies()
    results['Database Connection'] = await test_database_connection()
    results['Database Models'] = await test_database_models()
    results['Database Initialization'] = await test_database_initialization()
    results['DSPy Setup'] = test_dspy_setup()
    results['Agent Modules'] = test_agents_import()
    results['Data Sources'] = await test_data_sources()
    
    # Print summary
    print_test_header("Test Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed! Your setup is complete.{Colors.RESET}\n")
        return True
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Please fix the issues above.{Colors.RESET}\n")
        return False

if __name__ == "__main__":
    asyncio.run(run_all_tests())
