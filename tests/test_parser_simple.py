import sys
from pathlib import Path

# Set UTF-8 encoding for stdout to handle Persian characters in terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from core.parser import LatexParser

def test_parser():
    main_tex = Path(__file__).parent / 'fixtures' / 'sample_book' / 'main.tex'
    parser = LatexParser(main_tex)
    book = parser.parse()
    
    print(f"Title: {book.metadata.title}")
    print(f"Author: {book.metadata.author}")
    print(f"Chapters found: {len(book.chapters)}")
    for i, ch in enumerate(book.chapters):
        print(f"  Chapter {i+1}: {ch.title} (Slug: {ch.slug})")
    
    print(f"Labels found: {len(book.label_registry)}")
    for lbl in book.label_registry:
        print(f"  Label: {lbl}")

if __name__ == "__main__":
    test_parser()
