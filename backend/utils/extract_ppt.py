from pptx import Presentation
import sys

ppt_path = r"D:\Christ University\MSc\5MDS\ProjectFinance\ProjectPPT.pptx"

try:
    prs = Presentation(ppt_path)
    print(f"Total slides: {len(prs.slides)}\n")
    print("="*80)
    
    for i, slide in enumerate(prs.slides):
        print(f"\n--- SLIDE {i+1} ---")
        print("-"*80)
        
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                print(shape.text)
        
        # Check for tables
        if slide.shapes:
            for shape in slide.shapes:
                if shape.shape_type == 19:  # Table
                    print("\n[TABLE DETECTED]")
                    try:
                        for row in shape.table.rows:
                            row_text = " | ".join([cell.text for cell in row.cells])
                            print(row_text)
                    except:
                        pass
        
        print("-"*80)
    
    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
