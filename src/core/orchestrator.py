import re
from pathlib import Path
from core.parser import LatexParser
from core.converter import MarkdownConverter
from core.images import ImageProcessor
from models.book import Book
from utils.slugify import slugify
from core.manifest import ManifestGenerator

class ConversionOrchestrator:
    """Orchestrates the entire conversion process from LaTeX to Astro."""
    
    def __init__(self, main_tex: Path, output_root: Path):
        self.main_tex = main_tex
        self.output_root = output_root
        self.parser = LatexParser(main_tex)
        self.manifest = ManifestGenerator(output_root)
        self.book: Book = None
        
    def run(self):
        # 1. Parse LaTeX
        self.book = self.parser.parse()
        
        # 2. Refine Slugs (Respect user input if available)
        if not self.book.metadata.slug:
            self.book.metadata.slug = slugify(self.book.metadata.title)
            
        for ch in self.book.chapters:
            if not ch.slug:
                ch.slug = slugify(ch.title)
            ch.filename = f"ch{ch.number:02d}-{ch.slug}.md"
            
        for app in self.book.appendices:
            if not app.slug:
                app.slug = slugify(app.title)
            app.filename = f"app{app.number:02d}-{app.slug}.md"
        
        # 3. Setup Image Processor
        image_out_dir = self.output_root / "public" / "images" / "books" / self.book.metadata.slug
        self.img_processor = ImageProcessor(self.main_tex.parent, image_out_dir)
        
        # 4. Convert Content
        self.converter = MarkdownConverter(self.book)
        self.converter.convert_all()
        
        # 5. Save Files and Manifest
        self.save_markdown_files()
        self.manifest.set_metadata({
            "title": self.book.metadata.title,
            "slug": self.book.metadata.slug,
            "chapters_count": len(self.book.chapters)
        })
        self.manifest.save()
        
    def save_markdown_files(self):
        content_type = self.book.metadata.type or "Book"
        
        if content_type == "Book":
            base_dir = self.output_root / "src" / "content" / "books" / self.book.metadata.lang / self.book.metadata.slug
        else:
            base_dir = self.output_root / "src" / "content" / "articles" / self.book.metadata.lang
            
        base_dir.mkdir(parents=True, exist_ok=True)
        
        if content_type == "Book":
            # Save index.md (Overview)
            index_fm = self.converter.generate_frontmatter_from_metadata(self.book.metadata)
            index_path = base_dir / "index.md"
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_fm + "\n\n# " + self.book.metadata.title + "\n")
            self.manifest.add_file("overview", "main.tex", str(index_path.relative_to(self.output_root)))
                
            # Save Chapters
            for chapter in self.book.chapters:
                filepath = base_dir / chapter.filename
                fm = self.converter.generate_frontmatter(chapter)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(fm + "\n\n" + chapter.content_markdown)
                self.manifest.add_file("chapter", "mixed", str(filepath.relative_to(self.output_root)))

            # Save Appendices
            for app in self.book.appendices:
                filepath = base_dir / app.filename
                fm = self.converter.generate_frontmatter(app)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(fm + "\n\n" + app.content_markdown)
                self.manifest.add_file("appendix", "mixed", str(filepath.relative_to(self.output_root)))
        else:
            # Article or Markdown: Single File
            filepath = base_dir / f"{self.book.metadata.slug}.md"
            # We can use the same frontmatter generator for articles for now, 
            # or refine it if schemas differ significantly.
            fm = self.converter.generate_frontmatter_from_metadata(self.book.metadata)
            # Add the content (assuming it's in the first chapter for single-file types)
            content = self.book.chapters[0].content_markdown if self.book.chapters else ""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fm + "\n\n" + content)
            self.manifest.add_file("article", "mixed", str(filepath.relative_to(self.output_root)))

        # Handle PDF Publishing (Relevant for books mostly, but can apply to articles)
        self._publish_pdf(base_dir if content_type == "Book" else base_dir)

    def _publish_pdf(self, book_dir: Path):
        """Looks for a PDF in source and copies it to the book folder."""
        import shutil
        source_pdf = list(self.main_tex.parent.glob("*.pdf"))
        if source_pdf:
            # Pick the largest or the first one
            pdf_file = source_pdf[0]
            target_pdf = book_dir / "book.pdf"
            shutil.copy2(pdf_file, target_pdf)
            self.book.metadata.pdf_url = "/books/" + self.book.metadata.slug + "/book.pdf"
            # Update index.md with the new PDF URL
            self._update_index_pdf_url(book_dir / "index.md")
            self.manifest.add_file("pdf", str(pdf_file), str(target_pdf.relative_to(self.output_root)))

    def _update_index_pdf_url(self, index_path: Path):
        """Updates the frontmatter of index.md with the actual PDF URL."""
        if not index_path.exists(): return
        content = index_path.read_text(encoding="utf-8")
        # Simple regex swap for pdfUrl
        new_content = re.sub(r'pdfUrl: ".*"', f'pdfUrl: "{self.book.metadata.pdf_url}"', content)
        index_path.write_text(new_content, encoding="utf-8")
