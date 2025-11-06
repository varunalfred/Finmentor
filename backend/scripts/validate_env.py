"""
Environment Variables Validation Script
Checks if all required environment variables are properly configured
Run this before starting the server to ensure everything is set up correctly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def validate_env():
    """Validate all environment variables"""
    print("\n" + "="*70)
    print("ENVIRONMENT VARIABLES VALIDATION")
    print("="*70 + "\n")
    
    all_valid = True
    
    # ============= CRITICAL SECURITY VARIABLES =============
    print("🔒 CRITICAL SECURITY VARIABLES:")
    print("-" * 70)
    
    # JWT Secret Key
    jwt_key = os.getenv("JWT_SECRET_KEY")
    if jwt_key:
        if len(jwt_key) < 32:
            print_warning(f"JWT_SECRET_KEY is too short ({len(jwt_key)} chars, need 32+)")
            all_valid = False
        else:
            print_success(f"JWT_SECRET_KEY is set ({len(jwt_key)} characters)")
    else:
        print_error("JWT_SECRET_KEY is NOT set - REQUIRED!")
        print("   Generate one using: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        all_valid = False
    
    # Database URL
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        if "password" in db_url.lower() and db_url.count("password") > 1:
            print_warning("DATABASE_URL contains literal 'password' - use a strong password!")
            all_valid = False
        else:
            # Mask password in output
            masked_url = db_url.split("@")[0].split(":")[0:2]
            print_success(f"DATABASE_URL is set (postgresql://...)")
    else:
        print_error("DATABASE_URL is NOT set - REQUIRED!")
        print("   Example: DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/finmentor")
        all_valid = False
    
    print()
    
    # ============= REQUIRED AI API KEYS =============
    print("🤖 AI API KEYS (At least one required):")
    print("-" * 70)
    
    has_ai_key = False
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print_success("GEMINI_API_KEY is set ⭐ (Recommended)")
        has_ai_key = True
    else:
        print_warning("GEMINI_API_KEY is not set")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print_success("OPENAI_API_KEY is set")
        has_ai_key = True
    else:
        print_warning("OPENAI_API_KEY is not set")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print_success("ANTHROPIC_API_KEY is set")
        has_ai_key = True
    else:
        print_warning("ANTHROPIC_API_KEY is not set")
    
    if not has_ai_key:
        print_error("NO AI API KEY SET - At least one is required!")
        all_valid = False
    
    print()
    
    # ============= CORS CONFIGURATION =============
    print("🌐 CORS CONFIGURATION:")
    print("-" * 70)
    
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
    origins_list = [o.strip() for o in allowed_origins.split(",")]
    
    if "*" in allowed_origins:
        print_error("ALLOWED_ORIGINS contains wildcard '*' - SECURITY RISK!")
        all_valid = False
    elif allowed_origins == "http://localhost:3000,http://localhost:5173":
        print_warning("Using default development origins")
        print(f"   {origins_list}")
    else:
        print_success(f"ALLOWED_ORIGINS configured with {len(origins_list)} origins")
        for origin in origins_list:
            print(f"   - {origin}")
    
    print()
    
    # ============= OPTIONAL CONFIGURATION =============
    print("⚙️  OPTIONAL CONFIGURATION:")
    print("-" * 70)
    
    model = os.getenv("DEFAULT_MODEL", "gemini-pro")
    print_success(f"DEFAULT_MODEL: {model}")
    
    temp = os.getenv("DEFAULT_TEMPERATURE", "0.7")
    print_success(f"DEFAULT_TEMPERATURE: {temp}")
    
    max_tokens = os.getenv("DEFAULT_MAX_TOKENS", "1000")
    print_success(f"DEFAULT_MAX_TOKENS: {max_tokens}")
    
    access_expire = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    print_success(f"ACCESS_TOKEN_EXPIRE_MINUTES: {access_expire}")
    
    refresh_expire = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    print_success(f"REFRESH_TOKEN_EXPIRE_DAYS: {refresh_expire}")
    
    print()
    
    # ============= OPTIONAL SERVICES =============
    print("🔧 OPTIONAL SERVICES:")
    print("-" * 70)
    
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        print_success(f"REDIS_URL is set")
    else:
        print_warning("REDIS_URL is not set (optional)")
    
    alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if alpha_key:
        print_success("ALPHA_VANTAGE_API_KEY is set")
    else:
        print_warning("ALPHA_VANTAGE_API_KEY is not set (optional - Yahoo Finance used as fallback)")
    
    news_key = os.getenv("NEWS_API_KEY")
    if news_key:
        print_success("NEWS_API_KEY is set")
    else:
        print_warning("NEWS_API_KEY is not set (optional)")
    
    print()
    
    # ============= SUMMARY =============
    print("="*70)
    if all_valid:
        print_success("ALL REQUIRED ENVIRONMENT VARIABLES ARE PROPERLY CONFIGURED! ✨")
        print("\nYou can now start the server:")
        print("  uvicorn main:app --reload")
    else:
        print_error("SOME REQUIRED VARIABLES ARE MISSING OR INVALID!")
        print("\nPlease fix the issues above before starting the server.")
        print("\nQuick Fix Steps:")
        print("1. Copy .env.example to .env if you haven't already")
        print("2. Generate JWT secret: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        print("3. Set DATABASE_URL with your PostgreSQL credentials")
        print("4. Add at least one AI API key (GEMINI_API_KEY recommended)")
        print("5. Run this script again to validate")
    print("="*70 + "\n")
    
    return all_valid

if __name__ == "__main__":
    sys.exit(0 if validate_env() else 1)
