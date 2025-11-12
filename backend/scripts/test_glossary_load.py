"""
Simple test script to verify glossary CSV can be read correctly
"""

import pandas as pd
from pathlib import Path

def test_glossary_reading():
    """Test reading the glossary CSV file"""
    
    # Get path to glossary
    base_path = Path(__file__).parent.parent
    glossary_path = base_path / "RAG" / "glossary_clean.csv"
    
    print(f"Testing glossary at: {glossary_path}")
    print(f"File exists: {glossary_path.exists()}")
    
    if not glossary_path.exists():
        print("❌ Glossary file not found!")
        return False
    
    try:
        # Read CSV
        df = pd.read_csv(glossary_path)
        print(f"\n✅ CSV loaded successfully")
        print(f"Total rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Normalize column names
        df.columns = df.columns.str.lower()
        print(f"Normalized columns: {list(df.columns)}")
        
        # Check required columns
        if 'term' not in df.columns or 'definition' not in df.columns:
            print(f"❌ Missing required columns!")
            print(f"   Expected: 'term', 'definition'")
            print(f"   Found: {list(df.columns)}")
            return False
        
        print(f"\n✅ Required columns found")
        
        # Test processing first 5 rows
        print(f"\nTesting first 5 rows:")
        valid_count = 0
        for idx, row in df.head(5).iterrows():
            term = str(row['term']).strip()
            definition = str(row['definition']).strip()
            
            if term and definition and term != 'nan' and definition != 'nan':
                print(f"  ✅ Row {idx}: {term[:30]}... (def length: {len(definition)})")
                valid_count += 1
            else:
                print(f"  ⚠️  Row {idx}: Invalid (term={term[:20]}, def={definition[:20]})")
        
        print(f"\n✅ Valid rows in sample: {valid_count}/5")
        
        # Check all rows
        valid_total = 0
        for idx, row in df.iterrows():
            term = str(row['term']).strip()
            definition = str(row['definition']).strip()
            
            if term and definition and term != 'nan' and definition != 'nan':
                valid_total += 1
        
        print(f"\n✅ Total valid rows: {valid_total}/{len(df)}")
        print(f"✅ All tests passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_glossary_reading()
    exit(0 if success else 1)
