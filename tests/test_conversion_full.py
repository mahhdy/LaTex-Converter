import sys
import os
from pathlib import Path

# Set UTF-8 encoding for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from core.orchestrator import ConversionOrchestrator

def test_full_conversion():
    main_tex = Path(__file__).parent / 'fixtures' / 'sample_book' / 'main.tex'
    output_root = Path(__file__).parent / 'output_test'
    
    # Clean up previous test output
    if output_root.exists():
        import shutil
        shutil.rmtree(output_root)
    
    orchestrator = ConversionOrchestrator(main_tex, output_root)
    orchestrator.run()
    
    print(f"Conversion complete. Output directory: {output_root}")
    
    # Check generated files
    book_slug = orchestrator.book.metadata.slug
    lang = orchestrator.book.metadata.lang
    book_content_dir = output_root / "src" / "content" / "books" / lang / book_slug
    
    print(f"Checking content directory: {book_content_dir}")
    if book_content_dir.exists():
        files = list(book_content_dir.glob("*.md"))
        print(f"Found {len(files)} Markdown files:")
        for f in files:
            print(f"  - {f.name}")
            # Read first few lines
            with open(f, 'r', encoding='utf-8') as content:
                print(f"    First 3 lines:\n{content.readlines()[:3]}")
    else:
        print("Error: Content directory not found!")

if __name__ == "__main__":
    test_full_conversion()
