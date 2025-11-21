# Quick Start Guide: Expanding the Knowledge Base

## Adding Your Financial Terms Repository

### Step 1: Prepare Your Data

Your financial terms can be in any of these formats:

#### Option A: CSV File (Recommended)
```csv
term,definition,category,examples,related_terms
Sharpe Ratio,"Risk-adjusted return metric...",performance_metrics,"Fund with return 12%, volatility 8% and risk-free 2% has Sharpe of 1.25","Alpha, Beta, Standard Deviation"
```

#### Option B: JSON File
```json
[
  {
    "term": "Sharpe Ratio",
    "definition": "Risk-adjusted return metric...",
    "category": "performance_metrics",
    "examples": "Fund with return 12%...",
    "related_terms": "Alpha, Beta, Standard Deviation"
  }
]
```

#### Option C: Directory of Text Files
```
financial_terms/
  ├── sharpe_ratio.txt
  ├── sortino_ratio.txt
  └── treynor_ratio.txt
```

Each file contains:
```
Risk-adjusted return metric that measures excess return per unit of risk.

Examples:
A fund with 12% return, 8% volatility, 2% risk-free rate has Sharpe of 1.25.
Higher Sharpe ratio indicates better risk-adjusted performance.
```

### Step 2: Run the Expansion Tool

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
venv1\Scripts\activate  # Windows
# or
source venv1/bin/activate  # Mac/Linux

# Run expansion script
python scripts/expand_knowledge_base.py --source path/to/your/terms.csv --format csv
```

### Step 3: Verify Addition

```bash
# Check knowledge base statistics
python scripts/expand_knowledge_base.py --stats
```

Expected output:
```
==============================================================
KNOWLEDGE BASE STATISTICS
==============================================================
Total terms in database: 643  # (538 original + 105 new)

Breakdown by category:
  general: 245
  performance_metrics: 128
  risk_metrics: 95
  income_metrics: 75
  financial_metrics: 100

Session statistics:
  Processed: 105
  Added: 105
  Duplicates skipped: 0
  Errors: 0
==============================================================
```

## Examples

### Example 1: Add Single Term

```bash
python scripts/expand_knowledge_base.py \
    --add-term "Sharpe Ratio" \
    --definition "A risk-adjusted return metric that measures excess return per unit of total risk" \
    --category "performance_metrics" \
    --examples "A fund with 12% return, 8% volatility, 2% risk-free rate has Sharpe of 1.25" \
    --related "Alpha, Beta, Standard Deviation, Sortino Ratio"
```

### Example 2: Batch Add from CSV

```bash
python scripts/expand_knowledge_base.py \
    --source data/new_financial_terms.csv \
    --format csv
```

### Example 3: Add from Directory

```bash
python scripts/expand_knowledge_base.py \
    --source data/financial_glossary/ \
    --format directory
```

## Testing New Terms

After adding terms, test that they're being used:

```bash
# Run RAG-first test
python tests/test_rag_first.py
```

Or test manually in Python:

```python
import asyncio
from agents.hybrid_core import HybridFinMentorSystem
from models.database import SessionLocal

async def test_new_term():
    config = {"model": "gemini-2.5-flash", "max_tokens": 2500}
    db = SessionLocal()
    
    try:
        system = HybridFinMentorSystem(config=config, db_session=db)
        
        response = await system.process_query(
            query="What is the Sharpe Ratio?",  # Your new term
            user_profile={"user_id": 1, "type": "beginner"}
        )
        
        print(response)
        
        # Should show: 📖 Sources: Knowledge Base
        if "Knowledge Base" in response:
            print("\n✓ New term is being used from KB!")
        
    finally:
        db.close()

asyncio.run(test_new_term())
```

## Template Files

We've provided templates in `data/`:

### template_new_terms.csv
Contains 5 sample terms with proper formatting. Use this as a reference for your own CSV files.

Fields:
- `term` (required): The financial term name
- `definition` (required): Clear, concise definition
- `category` (optional): Category for organization (default: "general")
- `examples` (optional): Practical examples for clarity
- `related_terms` (optional): Comma-separated related concepts

## Best Practices

### 1. Clear Definitions
✅ Good: "A measure of risk-adjusted returns calculated as (return - risk-free rate) / standard deviation"
❌ Bad: "It's like a thing that measures stuff"

### 2. Practical Examples
✅ Good: "A fund with 15% return, 10% volatility, and 3% risk-free rate has Sharpe of 1.2"
❌ Bad: "You calculate it with numbers"

### 3. Meaningful Categories
Use categories for organization:
- `performance_metrics`: Alpha, Beta, Sharpe Ratio
- `risk_metrics`: Standard Deviation, VaR, Beta
- `income_metrics`: Dividend Yield, Payout Ratio
- `financial_metrics`: EPS, P/E Ratio, ROE
- `valuation_metrics`: P/B Ratio, EV/EBITDA
- `technical_indicators`: RSI, MACD, Moving Averages

### 4. Link Related Concepts
Help users discover related terms:
- "Alpha" → related: "Beta, Sharpe Ratio, Jensen's Alpha"
- "P/E Ratio" → related: "EPS, Valuation, PEG Ratio"

## Troubleshooting

### Issue: Duplicate entries
**Error**: `⚠ Skipping duplicate: [term name]`
**Solution**: Term already exists. Update manually or use different term name.

### Issue: Missing required fields
**Error**: `⚠ Skipping row: missing term or definition`
**Solution**: Ensure CSV has both `term` and `definition` columns filled.

### Issue: Encoding errors
**Error**: `UnicodeDecodeError`
**Solution**: Save CSV with UTF-8 encoding.

### Issue: Database connection failed
**Error**: `DatabaseError: connection refused`
**Solution**: Check `DATABASE_URL` in `.env` file.

## Monitoring KB Usage

Track how often KB is being used:

```bash
# Check logs for KB usage
cat logs/system.log | grep "Knowledge Base"

# Expected output:
# Retrieved 5 documents from KB (relevance: 0.92)
# Concept explanation completed using: Knowledge Base
# Retrieved 3 documents from KB (relevance: 0.68)
# Financial analysis completed using: Knowledge Base + Market Data
```

## Next Steps

1. **Prepare your financial terms repository** as CSV/JSON
2. **Run the expansion script** to add terms
3. **Test** that terms are being retrieved
4. **Monitor** KB hit rate and user satisfaction
5. **Iterate** - add missing terms based on usage

Your system is now ready to grow its knowledge base continuously!
