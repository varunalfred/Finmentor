import PyPDF2
import sys

pdf_path = r"D:\Christ University\MSc\5MDS\ProjectFinance\PortifolioBuilder\FINMentorProjectSRS.pdf"

try:
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        
        print(f"Total pages: {num_pages}\n")
        print("="*80)
        
        for page_num in range(num_pages):
            print(f"\n--- PAGE {page_num + 1} ---")
            print("-"*80)
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            print(text)
            print("-"*80)
        
        print("\n" + "="*80)
        print("EXTRACTION COMPLETE")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
