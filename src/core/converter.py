import re
import pypandoc
from typing import List, Dict, Optional
from models.book import Book, Chapter, LabelInfo, BookMetadata
from utils.slugify import slugify

class MarkdownConverter:
    def __init__(self, book: Book):
        self.book = book
        self.label_registry = book.label_registry

    def convert_all(self):
        """Converts all chapters and appendices in the book."""
        for chapter in self.book.chapters:
            chapter.content_markdown = self.convert_latex_to_markdown(chapter.content_latex)
            chapter.description = self._generate_description(chapter.content_markdown)
        
        for appendix in self.book.appendices:
            appendix.content_markdown = self.convert_latex_to_markdown(appendix.content_latex)
            appendix.description = self._generate_description(appendix.content_markdown)

    def convert_latex_to_markdown(self, latex_content: str) -> str:
        """Primary conversion using Pandoc with a regex-based fallback."""
        try:
            # Check if pandoc is installed
            pypandoc.get_pandoc_version()
            markdown = pypandoc.convert_text(latex_content, 'markdown', format='latex', extra_args=['--wrap=none'])
        except Exception as e:
            # Fallback to basic regex-based conversion
            markdown = self._fallback_convert(latex_content)
        
        # Post-processing: Resolve references
        markdown = self._resolve_references(markdown)
        
        return markdown

    def _fallback_convert(self, latex: str) -> str:
        """Basic regex-based LaTeX to Markdown conversion."""
        text = latex
        
        # Sections
        text = re.sub(r'\\section\*?\{([^}]+)\}', r'## \1', text)
        text = re.sub(r'\\subsection\*?\{([^}]+)\}', r'### \1', text)
        text = re.sub(r'\\subsubsection\*?\{([^}]+)\}', r'#### \1', text)
        
        # Bold/Italic
        text = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', text)
        text = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', text)
        text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)
        
        # Math
        text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
        text = re.sub(r'\$(.*?)\$', r'$\1$', text)
        
        # Lists (very basic)
        text = re.sub(r'\\begin\{itemize\}', '', text)
        text = re.sub(r'\\end\{itemize\}', '', text)
        text = re.sub(r'\\item\s+', '- ', text)
        
        # Remove remaining LaTeX commands (aggressive)
        text = re.sub(r'\\[a-zA-Z]+\*?(\{.*?\})?', '', text)
        
        return text.strip()

    def _resolve_references(self, markdown: str) -> str:
        """Converts \ref{key} to Markdown links using the label registry."""
        
        def replace_ref(match):
            key = match.group(1)
            if key in self.label_registry:
                label = self.label_registry[key]
                # In Astro, we might want to link to files or anchors
                if label.file:
                    return f'[LINK](#{key})' # Simplified for now
                return f'[REF:{key}](#{key})'
            return f'[MISSING-REF:{key}]'

        return re.sub(r'\\ref\{([^}]+)\}', replace_ref, markdown)

    def _generate_description(self, markdown: str, fallback: str = "توضیحات این بخش بزودی اضافه خواهد شد.") -> str:
        """Generates a short description from the first 150 characters of content."""
        # Strip markdown headers and formatting
        text = re.sub(r'[#*`\[\]]', '', markdown)
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            return fallback
            
        return text[:150] + "..." if len(text) > 150 else text

    def generate_frontmatter(self, chapter: Chapter) -> str:
        """Generates YAML frontmatter for a chapter file."""
        lines = [
            "---",
            f'title: "{chapter.title}"',
            f'description: "{chapter.description}"',
            f'chapterNumber: {chapter.number}',
            f'lang: {self.book.metadata.lang}',
            f'draft: {str(chapter.is_draft).lower()}',
            "---"
        ]
        return "\n".join(lines)

    def generate_frontmatter_from_metadata(self, metadata: BookMetadata) -> str:
        """Generates YAML frontmatter for the book index.md file."""
        desc = metadata.description or "توضیحات این کتاب بزودی اضافه خواهد شد."
        lines = [
            "---",
            f'title: "{metadata.title}"',
            f'description: "{desc}"',
            f'lang: {metadata.lang}',
            f'author: "{metadata.author}"',
            f'coverImage: "{metadata.cover_image}"',
            f'pdfUrl: "{metadata.pdf_url}"',
            f'publishDate: {metadata.publish_date or "2025-01-01"}',
            f'draft: {str(metadata.draft).lower()}',
            f'order: {metadata.order}',
            "---"
        ]
        return "\n".join(lines)
