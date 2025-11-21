"""
Knowledge Base Expansion Utility

This script helps expand the financial knowledge base by:
1. Loading terms from CSV/JSON files
2. Batch importing from repositories
3. Adding individual terms programmatically
4. Validating and deduplicating entries

Usage:
    # From CSV
    python scripts/expand_knowledge_base.py --source terms.csv --format csv

    # From JSON
    python scripts/expand_knowledge_base.py --source terms.json --format json

    # From directory of text files
    python scripts/expand_knowledge_base.py --source /path/to/terms/ --format directory

    # Add single term
    python scripts/expand_knowledge_base.py --add-term "Term Name" --definition "..." --category "..."
"""

import asyncio
import asyncpg
import argparse
import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class KnowledgeBaseExpander:
    """Utility class for expanding the financial knowledge base"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        # Initialize embedding model (same as setup_rag.py)
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Embedding model loaded (384 dimensions)")
        
        self.conn = None
        self.stats = {
            "total_processed": 0,
            "added": 0,
            "duplicates": 0,
            "errors": 0
        }

    async def connect_db(self):
        """Connect to PostgreSQL database"""
        print(f"Connecting to database...")
        self.conn = await asyncpg.connect(self.db_url)
        print("✓ Connected to database")

    async def close_db(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            print("✓ Database connection closed")

    def generate_embedding(self, text: str) -> str:
        """Generate embedding vector for text"""
        embedding = self.model.encode(text)
        # Format as PostgreSQL vector string: '[0.1,0.2,0.3]'
        vector_str = '[' + ','.join(map(str, embedding.tolist())) + ']'
        return vector_str

    async def term_exists(self, term: str) -> bool:
        """Check if term already exists in database"""
        result = await self.conn.fetchval(
            "SELECT COUNT(*) FROM educational_content WHERE LOWER(term) = LOWER($1)",
            term
        )
        return result > 0

    async def add_term(
        self,
        term: str,
        definition: str,
        category: str = "general",
        examples: str = None,
        related_terms: str = None
    ) -> bool:
        """Add a single term to the knowledge base"""
        try:
            # Check for duplicates
            if await self.term_exists(term):
                print(f"⚠ Skipping duplicate: {term}")
                self.stats["duplicates"] += 1
                return False

            # Generate embedding from term + definition
            text_for_embedding = f"{term}. {definition}"
            if examples:
                text_for_embedding += f" Examples: {examples}"
            
            embedding = self.generate_embedding(text_for_embedding)

            # Insert into database
            await self.conn.execute("""
                INSERT INTO educational_content 
                (term, definition, category, examples, related_terms, embedding)
                VALUES ($1, $2, $3, $4, $5, CAST($6 AS vector))
            """, term, definition, category, examples, related_terms, embedding)

            print(f"✓ Added: {term} [{category}]")
            self.stats["added"] += 1
            return True

        except Exception as e:
            print(f"✗ Error adding {term}: {e}")
            self.stats["errors"] += 1
            return False

    async def load_from_csv(self, filepath: str):
        """Load terms from CSV file"""
        print(f"\nLoading from CSV: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"✗ File not found: {filepath}")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                self.stats["total_processed"] += 1
                
                term = row.get('term') or row.get('Term')
                definition = row.get('definition') or row.get('Definition')
                category = row.get('category') or row.get('Category') or 'general'
                examples = row.get('examples') or row.get('Examples')
                related_terms = row.get('related_terms') or row.get('Related')

                if not term or not definition:
                    print(f"⚠ Skipping row {self.stats['total_processed']}: missing term or definition")
                    self.stats["errors"] += 1
                    continue

                await self.add_term(term, definition, category, examples, related_terms)

    async def load_from_json(self, filepath: str):
        """Load terms from JSON file"""
        print(f"\nLoading from JSON: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"✗ File not found: {filepath}")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Support both array of objects and single object
        if isinstance(data, dict):
            data = [data]

        for item in data:
            self.stats["total_processed"] += 1

            term = item.get('term')
            definition = item.get('definition')
            category = item.get('category', 'general')
            examples = item.get('examples')
            related_terms = item.get('related_terms')

            if not term or not definition:
                print(f"⚠ Skipping item: missing term or definition")
                self.stats["errors"] += 1
                continue

            await self.add_term(term, definition, category, examples, related_terms)

    async def load_from_directory(self, dirpath: str):
        """Load terms from directory of text files"""
        print(f"\nLoading from directory: {dirpath}")
        
        if not os.path.isdir(dirpath):
            print(f"✗ Directory not found: {dirpath}")
            return

        # Look for .txt, .md files
        files = list(Path(dirpath).glob("*.txt")) + list(Path(dirpath).glob("*.md"))
        
        print(f"Found {len(files)} files to process")

        for filepath in files:
            self.stats["total_processed"] += 1
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Use filename as term (without extension)
                term = filepath.stem.replace('_', ' ').replace('-', ' ').title()
                
                # Try to split definition and examples
                parts = content.split('\n\n', 1)
                definition = parts[0].strip()
                examples = parts[1].strip() if len(parts) > 1 else None

                # Infer category from parent directory name
                category = filepath.parent.name if filepath.parent.name != dirpath else 'general'

                await self.add_term(term, definition, category, examples)

            except Exception as e:
                print(f"✗ Error processing {filepath}: {e}")
                self.stats["errors"] += 1

    async def print_statistics(self):
        """Print knowledge base statistics"""
        total = await self.conn.fetchval("SELECT COUNT(*) FROM educational_content")
        categories = await self.conn.fetch("""
            SELECT category, COUNT(*) as count 
            FROM educational_content 
            GROUP BY category 
            ORDER BY count DESC
        """)

        print("\n" + "="*60)
        print("KNOWLEDGE BASE STATISTICS")
        print("="*60)
        print(f"Total terms in database: {total}")
        print(f"\nBreakdown by category:")
        for row in categories:
            print(f"  {row['category']}: {row['count']}")
        
        print(f"\nSession statistics:")
        print(f"  Processed: {self.stats['total_processed']}")
        print(f"  Added: {self.stats['added']}")
        print(f"  Duplicates skipped: {self.stats['duplicates']}")
        print(f"  Errors: {self.stats['errors']}")
        print("="*60)


async def main():
    parser = argparse.ArgumentParser(description="Expand the financial knowledge base")
    
    # Input source options
    parser.add_argument('--source', help='Path to CSV, JSON, or directory')
    parser.add_argument('--format', choices=['csv', 'json', 'directory'], help='Input format')
    
    # Add single term option
    parser.add_argument('--add-term', help='Add a single term')
    parser.add_argument('--definition', help='Term definition')
    parser.add_argument('--category', default='general', help='Term category')
    parser.add_argument('--examples', help='Term examples')
    parser.add_argument('--related', help='Related terms (comma-separated)')
    
    # Statistics option
    parser.add_argument('--stats', action='store_true', help='Show knowledge base statistics')

    args = parser.parse_args()

    # Initialize expander
    expander = KnowledgeBaseExpander()
    await expander.connect_db()

    try:
        # Handle single term addition
        if args.add_term:
            if not args.definition:
                print("✗ Error: --definition required when using --add-term")
                return
            
            await expander.add_term(
                term=args.add_term,
                definition=args.definition,
                category=args.category,
                examples=args.examples,
                related_terms=args.related
            )

        # Handle file/directory import
        elif args.source and args.format:
            if args.format == 'csv':
                await expander.load_from_csv(args.source)
            elif args.format == 'json':
                await expander.load_from_json(args.source)
            elif args.format == 'directory':
                await expander.load_from_directory(args.source)

        # Show statistics
        if args.stats or args.source or args.add_term:
            await expander.print_statistics()

        # If no arguments, show help
        if not any([args.source, args.add_term, args.stats]):
            parser.print_help()

    finally:
        await expander.close_db()


if __name__ == "__main__":
    asyncio.run(main())
