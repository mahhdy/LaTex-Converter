from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

@dataclass
class ImageInfo:
    original_name: str
    original_path: Path
    output_name: str
    output_path: Path
    needs_conversion: bool
    caption: str = ""

@dataclass
class LabelInfo:
    label_type: str  # 'chapter', 'section', 'figure', 'table', 'equation'
    number: str
    title: str = ""
    file: str = ""

@dataclass
class Chapter:
    number: int
    title: str
    slug: str
    filename: str
    description: str = ""
    content_latex: str = ""
    content_markdown: str = ""
    is_appendix: bool = False
    is_included: bool = True
    is_approved: bool = False
    is_draft: bool = False
    images: List[ImageInfo] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

@dataclass
class BookMetadata:
    title: str = ""
    author: str = "مهدی سالم"
    description: str = ""
    lang: str = "fa"  # 'fa' or 'en'
    type: str = "Book" # 'Book', 'Article', 'Markdown'
    slug: str = ""
    publish_date: str = ""  # YYYY-MM-DD
    updated_date: str = ""
    draft: bool = True
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    cover_image: str = ""
    pdf_url: str = ""
    order: int = 0

@dataclass
class Book:
    metadata: BookMetadata
    chapters: List[Chapter] = field(default_factory=list)
    appendices: List[Chapter] = field(default_factory=list)
    images: Dict[str, ImageInfo] = field(default_factory=dict)
    source_dir: Optional[Path] = None
    label_registry: Dict[str, LabelInfo] = field(default_factory=dict)
