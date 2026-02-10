import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from models.book import Book, BookMetadata, Chapter, ImageInfo, LabelInfo

class LatexParser:
    def __init__(self, main_file: Path):
        self.main_file = main_file
        self.project_dir = main_file.parent
        self.book = Book(metadata=BookMetadata())
        self.processed_files: Set[Path] = set()
        self.label_registry: Dict[str, LabelInfo] = {}

    def parse(self) -> Book:
        """Main entry point for parsing the LaTeX project."""
        content = self._read_file_recursive(self.main_file)
        
        # 1. Extract Metadata
        self._extract_metadata(content)
        
        # 2. Extract Graphics Path
        self._extract_graphics_path(content)
        
        # 3. Split into Chapters
        self._split_chapters(content)
        
        # 4. Process Labels and References
        self._process_labels(content)
        
        return self.book

    def _read_file_recursive(self, file_path: Path) -> str:
        """Reads a LaTeX file and recursively includes content from \\input, \\include, and \\subfile."""
        if file_path in self.processed_files:
            return f"% Circular include detected: {file_path}\n"
        
        self.processed_files.add(file_path)
        
        if not file_path.exists():
            if not file_path.suffix:
                file_path = file_path.with_suffix('.tex')
            if not file_path.exists():
                return f"% File not found: {file_path}\n"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='utf-16') as f:
                    content = f.read()
            except Exception:
                return f"% Error reading file: {file_path}\n"

        # Regex for includes
        include_pattern = re.compile(r'\\(?:input|include|subfile)\s*\{([^}]+)\}')
        
        def replace_include(match):
            inc_filename = match.group(1)
            inc_path = self.project_dir / inc_filename
            return self._read_file_recursive(inc_path)

        return include_pattern.sub(replace_include, content)

    def _extract_metadata(self, content: str):
        """Extracts title, author, date, abstract, and keywords."""
        patterns = {
            'title': r'\\title\s*\{([^}]+)\}',
            'author': r'\\author\s*\{([^}]+)\}',
            'date': r'\\date\s*\{([^}]+)\}',
            'keywords': r'\\keywords\s*\{([^}]+)\}',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1).strip()
                if key == 'keywords':
                    self.book.metadata.tags = [t.strip() for t in value.split(',')]
                else:
                    setattr(self.book.metadata, key if key != 'date' else 'publish_date', value)

        # Abstract extraction
        abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
        if abstract_match:
            self.book.metadata.description = abstract_match.group(1).strip()

    def _extract_graphics_path(self, content: str):
        """Extracts graphicspath from the LaTeX project."""
        # Simple extraction, can be improved to handle multiple paths
        match = re.search(r'\\graphicspath\s*\{\{([^}]+)\}\}', content)
        if match:
            # TODO: Store graphics paths for image searching
            pass

    def _split_chapters(self, content: str):
        """Splits the content into chapters and appendices."""
        # Split by \appendix if present
        parts = re.split(r'\\appendix', content, maxsplit=1)
        main_content = parts[0]
        appendix_content = parts[1] if len(parts) > 1 else ""
        
        # 1. Process Chapters
        self._process_section_type(main_content, is_appendix=False)
        
        # 2. Process Appendices
        if appendix_content:
            self._process_section_type(appendix_content, is_appendix=True)

    def _process_section_type(self, content: str, is_appendix: bool):
        """Helper to extract chapters/appendices from a string section."""
        # Support \chapter and \chapter*
        parts = re.split(r'(\\chapter\*?\s*(?:\[[^\]]*\])?\s*\{[^}]+\})', content)
        chapter_idx = 1
        
        for i in range(1, len(parts), 2):
            chapter_cmd = parts[i]
            chapter_content = parts[i+1] if i+1 < len(parts) else ""
            
            title_match = re.search(r'\{([^}]+)\}', chapter_cmd)
            title = title_match.group(1) if title_match else f"{'Appendix' if is_appendix else 'Chapter'} {chapter_idx}"
            
            # Use letters for appendices (A, B, C)
            number_val = chr(64 + chapter_idx) if is_appendix else chapter_idx
            
            chapter = Chapter(
                number=chapter_idx,
                title=title,
                slug="", # Will be set by Orchestrator or MetadataStep
                filename="",
                content_latex=chapter_content,
                is_appendix=is_appendix
            )
            
            if is_appendix:
                self.book.appendices.append(chapter)
            else:
                self.book.chapters.append(chapter)
            chapter_idx += 1

    def _process_labels(self, content: str):
        """Extracts all \\label definitions and builds a registry."""
        label_pattern = re.compile(r'\\label\s*\{([^}]+)\}')
        # This will be more complex in final implementation to associate labels with numbers/types
        for match in label_pattern.finditer(content):
            label = match.group(1)
            self.label_registry[label] = LabelInfo(label_type="unknown", number="0", title=label)
        
        self.book.label_registry = self.label_registry
