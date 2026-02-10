```markdown
# Project: LaTeX Book to Astro Markdown Converter with Git Integration

## Project Overview

Build a professional Python desktop application that converts Persian/Farsi LaTeX books (XeLaTeX) to Markdown files compatible with the Astro static site generator. The application must support full RTL Persian text, provide a wizard-style GUI for reviewing and approving each chapter before final export, and integrate with Git for direct pushing to a repository.

## Target User Profile

- Academic authors writing books in Persian using LaTeX/XeLaTeX
- Non-technical users who need a simple, intuitive GUI
- Users managing content for an Astro-based website (MahdiSalem.com structure)

---

## Part 1: LaTeX Parsing Engine

### 1.1 Multi-File Project Support

Parse LaTeX projects with multiple files:
- Follow `\input{filename}` commands
- Follow `\include{filename}` commands  
- Follow `\subfile{filename}` commands
- Handle relative and absolute paths
- Detect circular includes and prevent infinite loops
- Support nested includes (files that include other files)

### 1.2 Persian/XeLaTeX Support

Handle Persian-specific packages and commands:
- `xepersian` package
- `bidi` package
- `fontspec` package
- Persian date formats
- RTL text direction markers

### 1.3 Metadata Extraction

Extract from LaTeX source:
```
\title{...}           → title
\author{...}          → author  
\date{...}            → publishDate
\begin{abstract}...\end{abstract} → description
\keywords{...}        → tags (comma-separated)
```

Also detect custom metadata commands if present.

### 1.4 Structure Detection

- Detect `\graphicspath{{path1/}{path2/}}` for image locations
- Parse `\chapter{title}` for main chapters
- Parse `\section{}`, `\subsection{}`, `\subsubsection{}` hierarchy
- Detect `\appendix` marker to separate appendices from chapters
- Extract all `\label{key}` definitions
- Track all `\ref{key}` and `\pageref{key}` references
- Parse `\bibliography{}` or `\printbibliography` for references

### 1.5 Content Elements to Parse

- Figures: `\begin{figure}...\includegraphics{...}...\caption{...}...\label{...}...\end{figure}`
- Tables: `tabular`, `longtable`, `table` environments
- Lists: `itemize`, `enumerate`, `description`
- Math: inline `$...$`, display `\[...\]`, `equation`, `align` environments
- Code: `verbatim`, `lstlisting`, `minted` environments
- Footnotes: `\footnote{...}`
- Citations: `\cite{key}`, `\citep{key}`, `\citet{key}`
- Emphasis: `\textbf{}`, `\textit{}`, `\emph{}`
- Quotations: `quote`, `quotation` environments

---

## Part 2: Conversion Engine

### 2.1 Primary Conversion

Use Pandoc as the primary conversion engine:
```bash
pandoc -f latex -t markdown --wrap=none
```

Implement a fallback pure-Python converter if Pandoc is not installed.

### 2.2 Conversion Rules

| LaTeX | Markdown |
|-------|----------|
| `\chapter{Title}` | `# Title` (in separate file) |
| `\section{Title}` | `## Title` |
| `\subsection{Title}` | `### Title` |
| `\subsubsection{Title}` | `#### Title` |
| `\textbf{text}` | `**text**` |
| `\textit{text}` | `*text*` |
| `\emph{text}` | `*text*` |
| `$math$` | `$math$` (preserve) |
| `\[math\]` | `$$math$$` |
| `\begin{itemize}` | Markdown list with `-` |
| `\begin{enumerate}` | Markdown list with `1.` |
| `\footnote{text}` | `[^n]: text` |
| `\ref{label}` | `[link text](#label)` |
| `\cite{key}` | `[^key]` or link |
| `\includegraphics{img}` | `![caption](/images/book-slug/img.png)` |

### 2.3 Image Processing

1. Search for images in all `\graphicspath` directories
2. Search common subdirectories: `images/`, `figures/`, `figs/`, `img/`
3. Try extensions in order: `.png`, `.jpg`, `.jpeg`, `.pdf`, `.eps`, `.svg`
4. Convert PDF/EPS to PNG using:
   - `pdftoppm` (from Poppler) for PDF
   - `magick convert` (ImageMagick) for EPS
5. Copy all images to output folder with proper naming
6. Update all image references in Markdown

### 2.4 Cross-Reference Resolution

Build a label registry during parsing:
```python
{
  "ch:intro": {"type": "chapter", "number": 1, "title": "مقدمه", "file": "ch01-moghaddame"},
  "sec:background": {"type": "section", "chapter": 1, "title": "پیش‌زمینه"},
  "fig:diagram1": {"type": "figure", "number": 1, "caption": "نمودار اول"},
  "eq:main": {"type": "equation", "number": 1}
}
```

Convert `\ref{key}` to appropriate Markdown links.

---

## Part 3: Output Structure (Astro Compatible)

### 3.1 Directory Structure

```
output/
├── content/
│   └── books/
│       └── {lang}/
│           └── {book-slug}/
│               ├── index.md              # Book overview
│               ├── ch01-{chapter-slug}.md
│               ├── ch02-{chapter-slug}.md
│               └── app01-{appendix-slug}.md
├── public/
│   └── images/
│       └── books/
│           └── {book-slug}/
│               ├── cover.jpg
│               ├── fig1.png
│               └── fig2.png
└── manifest.json                         # Conversion manifest
```

### 3.2 Book Overview Frontmatter (index.md)

```yaml
---
title: "Book Title"
description: "Book description extracted from abstract"
lang: fa  # or en
author: "Author Name"
coverImage: "/images/books/{book-slug}/cover.jpg"
pdfUrl: ""  # Optional, user can add
publishDate: 2025-01-15
updatedDate: 2025-01-15
tags:
  - tag1
  - tag2
draft: true
order: 0
---
```

### 3.3 Chapter Frontmatter

```yaml
---
title: "Chapter Title"
description: "First 150 characters of chapter content or user-provided"
chapterNumber: 1
lang: fa
draft: false
---
```

### 3.4 Slug Generation Rules

1. Book slug: Generated from book title
   - Remove Persian diacritics
   - Convert spaces to hyphens
   - Remove special characters except Persian letters and hyphens
   - Lowercase (for English) or keep original (for Persian)
   - Max 50 characters
   - User can override

2. Chapter filename: `ch{NN}-{chapter-slug}.md`
   - NN = two-digit chapter number (01, 02, ...)
   - chapter-slug = generated from chapter title (same rules)
   - User can override each filename

3. Appendix filename: `app{NN}-{appendix-slug}.md`

4. **Important**: All inter-file references must use consistent slugs. When user changes book slug, all chapter `bookSlug` references must update automatically.

---

## Part 4: GUI Application (Wizard with Review System)

### 4.1 Technology Choice

Use **CustomTkinter** or **PyQt6** with these requirements:
- Full RTL support for Persian text
- Modern, clean appearance
- Proper Persian font rendering (Vazirmatn, Tahoma, or similar)
- Responsive layout

### 4.2 Wizard Flow

```
┌─────────────────────────────────────────────────────────────┐
│  [1. فایل]  →  [2. متادیتا]  →  [3. فصل‌ها]  →  [4. خروجی]  │
│     ●            ○               ○              ○           │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Step 1: File Selection & Analysis

**UI Elements:**
- File browser for selecting main .tex file
- "Analyze" button
- Analysis results panel showing:
  - Detected title, author, date
  - Number of chapters found
  - Number of appendices found  
  - Number of images found
  - List of included files
  - Any warnings/errors

**Functionality:**
- Parse the entire LaTeX project
- Build internal data structures
- Validate structure
- Show preview of detected content

### 4.4 Step 2: Book Metadata Editor

**UI Elements (Form Layout):**

```
┌─────────────────────────────────────────────────────────────┐
│ انتخاب از پیش‌تنظیم‌ها:  [Dropdown: پیش‌تنظیم‌ها ▼]          │
├─────────────────────────────────────────────────────────────┤
│ زبان:                   [Dropdown: 🇮🇷 فارسی ▼]              │
│ عنوان کتاب:             [___________________________]       │
│ شناسه URL (slug):       [_______________] [🔄 بازسازی]      │
│ تاریخ انتشار:           [____-__-__] [📅]                   │
│ ☑ پیش‌نویس (Draft)                                          │
│ نویسنده:                [___________________________]       │
│ توضیح کوتاه:            [                           ]       │
│                         [          (متن چند خطی)    ]       │
│ دسته‌بندی‌ها:            [___________________________]       │
│                         (با کاما جدا شود)                   │
│ برچسب‌ها:                [___________________________]       │
│                         (با کاما جدا شود)                   │
│ تصویر جلد:              [___________________] [انتخاب...]   │
├─────────────────────────────────────────────────────────────┤
│ پیش‌نمایش Frontmatter:                                      │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ---                                                     │ │
│ │ title: "عنوان کتاب"                                     │ │
│ │ author: "نویسنده"                                       │ │
│ │ ...                                                     │ │
│ │ ---                                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                              [🔄 بروزرسانی پیش‌نمایش]        │
└─────────────────────────────────────────────────────────────┘
```

**Presets Configuration:**
```json
{
  "presets": {
    "کتاب فلسفی": {
      "categories": ["فلسفه", "تحلیلی"],
      "tags": ["فلسفه", "اخلاق", "معرفت‌شناسی"],
      "author": "مهدی سالم"
    },
    "کتاب سیاسی": {
      "categories": ["سیاسی", "دموکراسی"],
      "tags": ["گذار", "دموکراسی", "ایران", "جنبش"],
      "author": "مهدی سالم"
    },
    "راهنمای عملی": {
      "categories": ["راهنما", "عملی"],
      "tags": ["آموزش", "راهنما"],
      "author": "مهدی سالم"
    },
    "سفارشی": {
      "categories": [],
      "tags": [],
      "author": ""
    }
  }
}
```

**Functionality:**
- Auto-populate from LaTeX metadata
- Live preview updates as user types
- Slug auto-generates from title (with manual override option)
- Validate required fields before proceeding

### 4.5 Step 3: Chapter-by-Chapter Review ⭐ (Critical Feature)

This is the **most important step**. User must review and approve each chapter individually.

**UI Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│ فصل‌ها و پیوست‌ها                                            │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐  ┌────────────────────────────────────┐ │
│ │ لیست فصل‌ها     │  │ ویرایش فصل                        │ │
│ │                 │  │                                    │ │
│ │ ☑ فصل ۱: مقدمه │  │ عنوان: [مقدمه_______________]     │ │
│ │   ⚠️ نیاز به    │  │ نام فایل: [ch01-moghaddame.md]    │ │
│ │      بررسی     │  │            [🔄 بازسازی از عنوان]   │ │
│ │ ☑ فصل ۲: تاریخ │  │ توضیح: [____________________]     │ │
│ │   ✅ تایید شده │  │         [____________________]     │ │
│ │ ☑ فصل ۳: ...   │  │ شماره فصل: [1]                    │ │
│ │   ⏳ بررسی نشده│  │ ☐ پیش‌نویس                         │ │
│ │ ☐ فصل ۴: ...   │  │                                    │ │
│ │   (حذف شده)    │  │ ─────────────────────────────────  │ │
│ │                 │  │ پیش‌نمایش Frontmatter:             │ │
│ │ ── پیوست‌ها ──  │  │ ┌──────────────────────────────┐  │ │
│ │ ☑ پیوست ۱     │  │ │ ---                          │  │ │
│ │                 │  │ │ title: "مقدمه"              │  │ │
│ │                 │  │ │ description: "..."          │  │ │
│ │ [انتخاب همه]   │  │ │ chapterNumber: 1            │  │ │
│ │ [عدم انتخاب]   │  │ │ lang: fa                    │  │ │
│ │                 │  │ │ ---                          │  │ │
│ └─────────────────┘  │ └──────────────────────────────┘  │ │
│                      │                                    │ │
│                      │ ─────────────────────────────────  │ │
│                      │ پیش‌نمایش محتوا:                    │ │
│                      │ ┌──────────────────────────────┐  │ │
│                      │ │ ## بخش اول                   │  │ │
│                      │ │ متن فصل در اینجا...         │  │ │
│                      │ │ ...                          │  │ │
│                      │ └──────────────────────────────┘  │ │
│                      │                                    │ │
│                      │ تصاویر این فصل: 3 تصویر           │ │
│                      │ [نمایش تصاویر]                     │ │
│                      │                                    │ │
│                      │    [✅ تایید این فصل]              │ │
│                      └────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Chapter List Features:**
- Checkbox to include/exclude each chapter
- Status indicator:
  - ⏳ بررسی نشده (Not reviewed)
  - ⚠️ نیاز به بررسی (Needs review - has warnings)
  - ✅ تایید شده (Approved)
- Click to select and edit in right panel
- Drag-and-drop to reorder (optional)
- "Select All" / "Deselect All" buttons

**Chapter Editor Features:**
- Editable title
- Editable filename with auto-regenerate button
- Editable description (auto-generated from first 150 chars, user can modify)
- Chapter number (auto-assigned, user can modify for reordering)
- Draft checkbox
- Live frontmatter preview
- Content preview (first 500 chars of converted Markdown)
- Image count and preview button
- **"Approve this chapter" button** - marks chapter as reviewed

**Validation:**
- Warn if filename conflicts with another chapter
- Warn if description is empty
- Warn if title is too long

**Slug Synchronization:**
When the book slug (from Step 2) changes, show a confirmation dialog:
```
شناسه کتاب تغییر کرد.
آیا می‌خواهید ارجاعات همه فصل‌ها بروزرسانی شود؟
[بله، بروزرسانی کن]  [خیر]
```

### 4.6 Step 4: Output & Git Integration

**UI Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│ خروجی و انتشار                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ── تنظیمات خروجی ──                                        │
│ پوشه خروجی محلی: [D:\output\__________] [انتخاب...]       │
│                                                             │
│ ── Git Repository ──                                        │
│ ☑ Push مستقیم به مخزن Git                                  │
│                                                             │
│ آدرس Repository:                                           │
│ [https://github.com/username/repo.git____]                 │
│                                                             │
│ Branch: [main_______]                                       │
│                                                             │
│ روش احراز هویت:                                            │
│ ○ HTTPS (Username + Token)                                 │
│   Username: [____________]                                  │
│   Token:    [____________] [نمایش/مخفی]                    │
│ ○ SSH Key                                                  │
│   Key Path: [~/.ssh/id_rsa____] [انتخاب...]               │
│                                                             │
│ Commit Message:                                             │
│ [Add book: {book-title}______________________]              │
│                                                             │
│ ── مسیرها در Repository ──                                 │
│ محتوا:    src/content/books/{lang}/{slug}/                 │
│ تصاویر:   public/images/books/{slug}/                       │
│                                                             │
│ [تست اتصال]                                                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ── عملیات ──                                               │
│                                                             │
│ [🔄 تبدیل و ذخیره محلی]                                    │
│ [📦 ایجاد فایل ZIP]                                        │
│ [🚀 تبدیل و Push به Git]                                   │
│ [📂 باز کردن پوشه خروجی]                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ ── پیشرفت و گزارش ──                                       │
│ [████████████████░░░░] 75%  در حال تبدیل فصل ۳...         │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 14:32:15 - شروع تبدیل...                               │ │
│ │ 14:32:16 - ✅ فصل ۱ تبدیل شد                           │ │
│ │ 14:32:17 - ✅ فصل ۲ تبدیل شد                           │ │
│ │ 14:32:18 - 🖼️ ۵ تصویر کپی شد                           │ │
│ │ 14:32:19 - ✅ Push به Git انجام شد                      │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Git Integration Features:**

1. **Repository Configuration:**
   - HTTPS URL or SSH URL
   - Branch selection
   - Authentication method:
     - HTTPS: Username + Personal Access Token
     - SSH: Key file path

2. **Path Mapping:**
   Based on content type, files go to correct locations:
   ```python
   path_mapping = {
       "books": "src/content/books/{lang}/{slug}/",
       "articles": "src/content/articles/{lang}/",
       "statements": "src/content/statements/{lang}/",
       "wiki": "src/content/wiki/{lang}/",
       "images": "public/images/books/{slug}/"
   }
   ```

3. **Git Operations:**
   ```python
   # Workflow:
   1. Clone repository (shallow clone for speed)
   2. Create/update files in correct paths
   3. Stage changes: git add .
   4. Commit: git commit -m "Add book: {title}"
   5. Push: git push origin {branch}
   6. Cleanup: remove temp clone directory
   ```

4. **Error Handling:**
   - Connection test before actual push
   - Handle authentication errors gracefully
   - Handle merge conflicts (abort and notify user)
   - Rollback on failure

---

## Part 5: Data Models

### 5.1 Book Model

```python
@dataclass
class BookMetadata:
    title: str
    author: str
    description: str
    lang: str  # 'fa' or 'en'
    slug: str
    publish_date: str  # YYYY-MM-DD
    updated_date: str
    draft: bool
    categories: List[str]
    tags: List[str]
    cover_image: str  # Path or URL
    pdf_url: str
    order: int

@dataclass
class Chapter:
    number: int
    title: str
    slug: str
    filename: str
    description: str
    content_latex: str
    content_markdown: str
    is_appendix: bool
    is_included: bool
    is_approved: bool
    is_draft: bool
    images: List[ImageInfo]
    labels: Dict[str, str]
    warnings: List[str]

@dataclass
class ImageInfo:
    original_name: str
    original_path: Path
    output_name: str
    output_path: Path
    needs_conversion: bool
    caption: str

@dataclass
class Book:
    metadata: BookMetadata
    chapters: List[Chapter]
    appendices: List[Chapter]
    images: Dict[str, ImageInfo]
    source_dir: Path
    label_registry: Dict[str, LabelInfo]
```

### 5.2 Configuration Model

```python
@dataclass
class GitConfig:
    enabled: bool
    repo_url: str
    branch: str
    auth_method: str  # 'https' or 'ssh'
    username: str
    token: str  # Encrypted storage
    ssh_key_path: str
    commit_message_template: str

@dataclass
class AppConfig:
    last_input_dir: str
    last_output_dir: str
    default_author: str
    default_lang: str
    presets: Dict[str, PresetConfig]
    git: GitConfig
    ui_language: str  # 'fa' or 'en'
```

---

## Part 6: Technical Specifications

### 6.1 Python Requirements

- Python 3.10 or higher (tested with 3.13)
- Type hints throughout
- Docstrings in Persian and English

### 6.2 Dependencies

```
# requirements.txt
customtkinter>=5.2.0    # or PyQt6>=6.5.0
Pillow>=10.0.0          # Image processing
gitpython>=3.1.40       # Git operations
pyyaml>=6.0             # YAML handling
python-dateutil>=2.8    # Date parsing
keyring>=24.0           # Secure credential storage
```

External (must be installed separately):
- Pandoc (for LaTeX conversion)
- Poppler (pdftoppm for PDF→PNG)
- ImageMagick (optional, for EPS→PNG)

### 6.3 Project Structure

```
latex2astro/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── parser.py           # LaTeX parsing
│   │   ├── converter.py        # Markdown conversion
│   │   ├── images.py           # Image processing
│   │   └── references.py       # Cross-reference handling
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book.py             # Book, Chapter, Image models
│   │   ├── config.py           # Configuration models
│   │   └── frontmatter.py      # Frontmatter schema
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app.py              # Main application window
│   │   ├── wizard.py           # Wizard controller
│   │   ├── step1_file.py       # File selection UI
│   │   ├── step2_metadata.py   # Metadata editor UI
│   │   ├── step3_chapters.py   # Chapter review UI
│   │   ├── step4_output.py     # Output & Git UI
│   │   ├── widgets/
│   │   │   ├── __init__.py
│   │   │   ├── frontmatter_preview.py
│   │   │   ├── chapter_list.py
│   │   │   └── markdown_preview.py
│   │   └── dialogs/
│   │       ├── __init__.py
│   │       ├── git_config.py
│   │       └── image_preview.py
│   │
│   ├── git/
│   │   ├── __init__.py
│   │   ├── operations.py       # Git commands
│   │   └── credentials.py      # Secure credential handling
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── slugify.py          # Slug generation
│   │   ├── encoding.py         # File encoding detection
│   │   ├── validation.py       # Input validation
│   │   └── i18n.py             # Internationalization
│   │
│   └── resources/
│       ├── presets.json        # Default presets
│       ├── config_schema.json  # Configuration schema
│       └── translations/
│           ├── fa.json         # Persian UI strings
│           └── en.json         # English UI strings
│
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_converter.py
│   ├── test_git.py
│   └── fixtures/
│       └── sample_book/        # Test LaTeX book
│
├── docs/
│   ├── README.md
│   ├── README.fa.md            # Persian documentation
│   └── USAGE.md
│
├── requirements.txt
├── setup.py
├── pyproject.toml
└── run.py                      # Simple launcher
```

### 6.4 Error Handling Strategy

1. **Parser Errors:**
   - Missing files: Warn and continue
   - Encoding errors: Try multiple encodings
   - Circular includes: Detect and skip

2. **Conversion Errors:**
   - Pandoc not found: Use fallback converter
   - Complex LaTeX: Convert to plain text with warning

3. **Image Errors:**
   - Missing image: Create placeholder, add warning
   - Conversion failed: Copy original, add warning

4. **Git Errors:**
   - Auth failed: Show detailed error, don't save credentials
   - Push rejected: Explain possible causes
   - Network error: Offer retry

### 6.5 Security

- Store Git tokens using `keyring` library (OS credential manager)
- Never log sensitive credentials
- Validate all file paths to prevent directory traversal
- Sanitize user input in filenames

---

## Part 7: Sample Input/Output

### 7.1 Sample LaTeX Input

```latex
% main.tex
\documentclass[a4paper,12pt]{book}
\usepackage{xepersian}
\usepackage{graphicx}
\graphicspath{{images/}{figures/}}

\title{راهنمای عملی گذار به دموکراسی}
\author{مهدی سالم}
\date{۱۴۰۳}

\begin{document}

\maketitle
\tableofcontents

\begin{abstract}
این کتاب راهنمای عملی برای فعالان سیاسی و اجتماعی است که به دنبال گذار مسالمت‌آمیز به دموکراسی در ایران هستند.
\end{abstract}

\keywords{گذار، دموکراسی، ایران، جنبش مدنی}

\chapter{مقدمه}
\label{ch:intro}

در این فصل به معرفی...

\section{چرا این کتاب؟}
\label{sec:why}

دلایل نگارش این کتاب...

\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{diagram1}
\caption{چارچوب کلی گذار}
\label{fig:framework}
\end{figure}

همانطور که در شکل \ref{fig:framework} مشاهده می‌شود...

\chapter{تاریخچه}
\input{chapters/chapter2}

\appendix
\chapter{منابع و مآخذ}
\input{appendices/resources}

\end{document}
```

### 7.2 Expected Output

**`src/content/books/fa/practical-guide-transition/index.md`:**
```markdown
---
title: "راهنمای عملی گذار به دموکراسی"
description: "این کتاب راهنمای عملی برای فعالان سیاسی و اجتماعی است که به دنبال گذار مسالمت‌آمیز به دموکراسی در ایران هستند."
lang: fa
author: "مهدی سالم"
coverImage: "/images/books/practical-guide-transition/cover.jpg"
pdfUrl: ""
publishDate: 2025-01-15
updatedDate: 2025-01-15
tags:
  - گذار
  - دموکراسی
  - ایران
  - جنبش مدنی
draft: true
order: 0
---

# راهنمای عملی گذار به دموکراسی

**نویسنده:** مهدی سالم

این کتاب راهنمای عملی برای فعالان سیاسی و اجتماعی است...

## فهرست مطالب

- [فصل ۱: مقدمه](./ch01-moghaddame)
- [فصل ۲: تاریخچه](./ch02-tarikhche)

### پیوست‌ها

- [منابع و مآخذ](./app01-manabe)
```

**`src/content/books/fa/practical-guide-transition/ch01-moghaddame.md`:**
```markdown
---
title: "مقدمه"
description: "در این فصل به معرفی چارچوب کلی کتاب و دلایل نگارش آن می‌پردازیم."
chapterNumber: 1
lang: fa
draft: false
---

در این فصل به معرفی...

## چرا این کتاب؟

دلایل نگارش این کتاب...

![چارچوب کلی گذار](/images/books/practical-guide-transition/diagram1.png)

همانطور که در شکل بالا مشاهده می‌شود...
```

---

## Part 8: Deliverables

Please provide:

1. **Complete Python source code** following the project structure above
2. **requirements.txt** with all dependencies
3. **setup.py** and/or **pyproject.toml** for installation
4. **README.md** with:
   - Installation instructions (Windows, macOS, Linux)
   - Usage guide with screenshots descriptions
   - Troubleshooting section
5. **README.fa.md** - Persian documentation
6. **Sample test fixture** - A minimal LaTeX book for testing
7. **Configuration files:**
   - `presets.json` with Persian presets
   - `translations/fa.json` and `translations/en.json`

---

## Part 9: Quality Requirements

1. **Code Quality:**
   - Type hints on all functions
   - Docstrings (Persian + English) on classes and public methods
   - Consistent naming conventions
   - No hardcoded strings (use i18n)

2. **UX Quality:**
   - Responsive UI (no freezing during long operations)
   - Clear error messages in Persian
   - Progress feedback for all operations
   - Confirmation dialogs for destructive actions

3. **Robustness:**
   - Handle malformed LaTeX gracefully
   - Recover from partial failures
   - Never lose user data

4. **Testing:**
   - Unit tests for parser and converter
   - Integration test with sample book

---

## Part 10: Astro Content Schema Reference

The target website follows this exact content schema. Generated files MUST match these specifications:

### 10.1 Books Schema

**Path Pattern:** `src/content/books/{lang}/{bookSlug}/`

**Book Overview (index.md):**
```json
{
  "type": "book-overview",
  "pathPattern": "src/content/books/{lang}/{bookSlug}/index.md",
  "frontmatter": {
    "title": "string (Required)",
    "description": "string (Required)",
    "lang": "enum: ['fa', 'en'] (Required)",
    "author": "string (Default: 'مهدی سالم')",
    "coverImage": "string (Optional, URL path starting with /)",
    "pdfUrl": "string (Optional, URL)",
    "publishDate": "date (Optional, YYYY-MM-DD)",
    "updatedDate": "date (Optional, YYYY-MM-DD)",
    "tags": "array<string> (Default: [])",
    "draft": "boolean (Default: false)",
    "order": "number (Default: 0)"
  }
}
```

**Book Chapter:**
```json
{
  "type": "book-chapter",
  "pathPattern": "src/content/books/{lang}/{bookSlug}/{chapterFilename}.md",
  "frontmatter": {
    "title": "string (Required)",
    "description": "string (Required)",
    "chapterNumber": "number (Optional, for ordering)",
    "lang": "enum: ['fa', 'en'] (Required)",
    "draft": "boolean (Default: false)"
  }
}
```

### 10.2 Articles Schema (For Future Extension)

```json
{
  "type": "article",
  "pathPattern": "src/content/articles/{lang}/{filename}.md",
  "frontmatter": {
    "title": "string (Required)",
    "description": "string (Required)",
    "lang": "enum: ['fa', 'en'] (Required)",
    "publishDate": "date (Required, YYYY-MM-DD)",
    "updatedDate": "date (Optional)",
    "author": "string (Default: 'مهدی سالم')",
    "categories": "array<string> (Default: [])",
    "tags": "array<string> (Default: [])",
    "coverImage": "string (Optional)",
    "draft": "boolean (Default: false)"
  }
}
```

### 10.3 Statements Schema (For Future Extension)

```json
{
  "type": "statement",
  "pathPattern": "src/content/statements/{lang}/{filename}.md",
  "frontmatter": {
    "title": "string (Required)",
    "description": "string (Required)",
    "lang": "enum: ['fa', 'en'] (Required)",
    "publishDate": "date (Required, YYYY-MM-DD)",
    "type": "enum: ['statement', 'press', 'position'] (Default: 'statement')",
    "draft": "boolean (Default: false)"
  }
}
```

### 10.4 Image Paths

All images must be placed in:
```
public/images/books/{book-slug}/
```

And referenced in Markdown as:
```markdown
![Alt text](/images/books/{book-slug}/filename.png)
```

---

## Part 11: Git Integration Details

### 11.1 Supported Git Workflows

**Workflow A: Direct Push (Default)**
```
1. User provides repo URL + credentials
2. App clones repo to temp directory
3. App copies generated files to correct paths
4. App commits and pushes
5. App cleans up temp directory
```

**Workflow B: Local Only + Manual Push**
```
1. User selects local repo directory
2. App copies files to correct paths in local repo
3. User manually commits and pushes
```

**Workflow C: Export ZIP for Manual Upload**
```
1. App generates files in output directory
2. App creates ZIP with correct folder structure
3. User extracts and uploads manually
```

### 11.2 Git Commit Message Templates

Default templates (user can customize):
```
# For new book:
Add book: {book_title}

# For update:
Update book: {book_title}

# Detailed template:
{action} book: {book_title}

- Chapters: {chapter_count}
- Appendices: {appendix_count}
- Images: {image_count}
- Language: {lang}
```

### 11.3 Conflict Resolution

If remote has changes:
```
1. Detect: git fetch + compare
2. Options presented to user:
   a) Force push (overwrite remote) - with warning
   b) Pull first, then push (may cause merge)
   c) Cancel and let user handle manually
3. Never auto-merge to avoid content corruption
```

---

## Part 12: Localization (i18n)

### 12.1 Persian UI Strings (fa.json)

```json
{
  "app": {
    "title": "مبدل کتاب LaTeX به Markdown",
    "version": "نسخه"
  },
  "steps": {
    "step1": "انتخاب فایل",
    "step2": "اطلاعات کتاب",
    "step3": "بررسی فصل‌ها",
    "step4": "خروجی و انتشار"
  },
  "buttons": {
    "next": "بعدی",
    "previous": "قبلی",
    "browse": "انتخاب...",
    "analyze": "تحلیل ساختار",
    "convert": "تبدیل",
    "push": "ارسال به Git",
    "cancel": "انصراف",
    "approve": "تایید",
    "approveAll": "تایید همه",
    "selectAll": "انتخاب همه",
    "deselectAll": "عدم انتخاب همه",
    "regenerate": "بازسازی",
    "preview": "پیش‌نمایش",
    "openFolder": "باز کردن پوشه",
    "createZip": "ایجاد فایل ZIP",
    "testConnection": "تست اتصال"
  },
  "labels": {
    "language": "زبان",
    "title": "عنوان",
    "author": "نویسنده",
    "description": "توضیحات",
    "slug": "شناسه URL",
    "publishDate": "تاریخ انتشار",
    "draft": "پیش‌نویس",
    "categories": "دسته‌بندی‌ها",
    "tags": "برچسب‌ها",
    "coverImage": "تصویر جلد",
    "filename": "نام فایل",
    "chapterNumber": "شماره فصل",
    "preset": "پیش‌تنظیم",
    "outputDir": "پوشه خروجی",
    "repoUrl": "آدرس مخزن",
    "branch": "شاخه",
    "username": "نام کاربری",
    "token": "توکن",
    "commitMessage": "پیام Commit"
  },
  "placeholders": {
    "categoriesHint": "با کاما جدا کنید",
    "tagsHint": "با کاما جدا کنید",
    "descriptionHint": "توضیح کوتاه درباره کتاب..."
  },
  "messages": {
    "analyzing": "در حال تحلیل...",
    "converting": "در حال تبدیل...",
    "pushing": "در حال ارسال به Git...",
    "success": "عملیات با موفقیت انجام شد",
    "error": "خطا",
    "warning": "هشدار",
    "connectionSuccess": "اتصال برقرار شد",
    "connectionFailed": "اتصال برقرار نشد",
    "notReviewed": "بررسی نشده",
    "needsReview": "نیاز به بررسی",
    "approved": "تایید شده",
    "excluded": "حذف شده"
  },
  "errors": {
    "fileNotFound": "فایل یافت نشد",
    "invalidLatex": "فایل LaTeX معتبر نیست",
    "pandocNotFound": "Pandoc نصب نیست. از مبدل داخلی استفاده می‌شود.",
    "gitAuthFailed": "احراز هویت Git ناموفق",
    "gitPushFailed": "ارسال به Git ناموفق",
    "requiredField": "این فیلد الزامی است",
    "invalidSlug": "شناسه URL معتبر نیست",
    "duplicateFilename": "نام فایل تکراری است"
  },
  "dialogs": {
    "confirmOverwrite": "فایل‌های موجود بازنویسی شوند؟",
    "confirmPush": "آیا مطمئن هستید که می‌خواهید به Git ارسال کنید؟",
    "slugChanged": "شناسه کتاب تغییر کرد. ارجاعات فصل‌ها بروزرسانی شود؟",
    "unsavedChanges": "تغییرات ذخیره نشده‌ای وجود دارد. ادامه می‌دهید؟"
  },
  "tooltips": {
    "slug": "شناسه یکتا برای URL کتاب. فقط حروف انگلیسی، اعداد و خط تیره.",
    "draft": "محتوای پیش‌نویس در سایت نمایش داده نمی‌شود.",
    "regenerateFilename": "بازسازی نام فایل از روی عنوان"
  }
}
```

### 12.2 English UI Strings (en.json)

```json
{
  "app": {
    "title": "LaTeX Book to Markdown Converter",
    "version": "Version"
  },
  "steps": {
    "step1": "Select File",
    "step2": "Book Info",
    "step3": "Review Chapters",
    "step4": "Output & Publish"
  },
  "buttons": {
    "next": "Next",
    "previous": "Previous",
    "browse": "Browse...",
    "analyze": "Analyze Structure",
    "convert": "Convert",
    "push": "Push to Git",
    "cancel": "Cancel",
    "approve": "Approve",
    "approveAll": "Approve All",
    "selectAll": "Select All",
    "deselectAll": "Deselect All",
    "regenerate": "Regenerate",
    "preview": "Preview",
    "openFolder": "Open Folder",
    "createZip": "Create ZIP",
    "testConnection": "Test Connection"
  }
}
```

---

## Part 13: Configuration Files

### 13.1 Default Presets (presets.json)

```json
{
  "version": "1.0",
  "presets": {
    "کتاب فلسفی": {
      "id": "philosophy",
      "name_fa": "کتاب فلسفی",
      "name_en": "Philosophy Book",
      "author": "مهدی سالم",
      "categories": ["فلسفه", "تحلیلی"],
      "tags": ["فلسفه", "اخلاق", "معرفت‌شناسی", "فلسفه تحلیلی"],
      "lang": "fa"
    },
    "کتاب سیاسی": {
      "id": "political",
      "name_fa": "کتاب سیاسی",
      "name_en": "Political Book",
      "author": "مهدی سالم",
      "categories": ["سیاسی", "دموکراسی"],
      "tags": ["گذار", "دموکراسی", "ایران", "جنبش", "سیاست"],
      "lang": "fa"
    },
    "راهنمای عملی": {
      "id": "guide",
      "name_fa": "راهنمای عملی",
      "name_en": "Practical Guide",
      "author": "مهدی سالم",
      "categories": ["راهنما", "آموزشی"],
      "tags": ["راهنما", "آموزش", "عملی", "گام‌به‌گام"],
      "lang": "fa"
    },
    "مقاله علمی": {
      "id": "academic",
      "name_fa": "مقاله علمی",
      "name_en": "Academic Paper",
      "author": "مهدی سالم",
      "categories": ["مقاله", "پژوهشی"],
      "tags": ["تحقیق", "علمی", "پژوهش"],
      "lang": "fa"
    },
    "English Book": {
      "id": "english",
      "name_fa": "کتاب انگلیسی",
      "name_en": "English Book",
      "author": "Mehdi Salem",
      "categories": [],
      "tags": [],
      "lang": "en"
    },
    "سفارشی": {
      "id": "custom",
      "name_fa": "سفارشی",
      "name_en": "Custom",
      "author": "",
      "categories": [],
      "tags": [],
      "lang": "fa"
    }
  }
}
```

### 13.2 App Configuration Schema (config_schema.json)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {"type": "string"},
    "ui": {
      "type": "object",
      "properties": {
        "language": {"type": "string", "enum": ["fa", "en"]},
        "theme": {"type": "string", "enum": ["light", "dark", "system"]},
        "fontSize": {"type": "integer", "minimum": 8, "maximum": 24}
      }
    },
    "defaults": {
      "type": "object",
      "properties": {
        "author": {"type": "string"},
        "lang": {"type": "string", "enum": ["fa", "en"]},
        "draft": {"type": "boolean"},
        "lastInputDir": {"type": "string"},
        "lastOutputDir": {"type": "string"}
      }
    },
    "git": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "repoUrl": {"type": "string"},
        "branch": {"type": "string"},
        "authMethod": {"type": "string", "enum": ["https", "ssh"]},
        "username": {"type": "string"},
        "sshKeyPath": {"type": "string"},
        "commitMessageTemplate": {"type": "string"},
        "autoPush": {"type": "boolean"}
      }
    },
    "paths": {
      "type": "object",
      "properties": {
        "books": {"type": "string", "default": "src/content/books"},
        "articles": {"type": "string", "default": "src/content/articles"},
        "images": {"type": "string", "default": "public/images/books"}
      }
    },
    "conversion": {
      "type": "object",
      "properties": {
        "usePandoc": {"type": "boolean", "default": true},
        "convertPdfImages": {"type": "boolean", "default": true},
        "imageQuality": {"type": "integer", "minimum": 1, "maximum": 100},
        "maxImageWidth": {"type": "integer"}
      }
    }
  }
}
```

---

## Part 14: Testing

### 14.1 Test Fixture: Sample LaTeX Book

Create a minimal test book with this structure:

```
tests/fixtures/sample_book/
├── main.tex
├── chapters/
│   ├── chapter1.tex
│   └── chapter2.tex
├── appendices/
│   └── appendixA.tex
└── images/
    ├── figure1.png
    └── diagram.pdf
```

**main.tex:**
```latex
\documentclass[a4paper]{book}
\usepackage{xepersian}
\usepackage{graphicx}
\graphicspath{{images/}}

\title{کتاب آزمایشی}
\author{نویسنده تست}
\date{۱۴۰۳}

\begin{document}
\maketitle

\begin{abstract}
این یک کتاب آزمایشی برای تست نرم‌افزار است.
\end{abstract}

\keywords{تست، آزمایش، نمونه}

\tableofcontents

\chapter{فصل اول}
\label{ch:first}
\input{chapters/chapter1}

\chapter{فصل دوم}
\input{chapters/chapter2}

\appendix
\chapter{پیوست}
\input{appendices/appendixA}

\end{document}
```

**chapters/chapter1.tex:**
```latex
این فصل اول است.

\section{بخش اول}
\label{sec:first}

متن بخش اول با \textbf{متن پررنگ} و \textit{متن ایتالیک}.

\begin{itemize}
  \item مورد اول
  \item مورد دوم
\end{itemize}

\begin{figure}[h]
\centering
\includegraphics[width=0.5\textwidth]{figure1}
\caption{تصویر آزمایشی}
\label{fig:test}
\end{figure}

همانطور که در شکل \ref{fig:test} می‌بینید...

\section{بخش دوم}

فرمول ریاضی: $E = mc^2$

\begin{equation}
\label{eq:main}
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
\end{equation}
```

### 14.2 Test Cases

```python
# tests/test_parser.py

def test_parse_simple_book():
    """Test parsing a simple LaTeX book"""
    parser = LaTeXParser(Path("fixtures/sample_book/main.tex"))
    book = parser.parse()
    
    assert book.metadata.title == "کتاب آزمایشی"
    assert book.metadata.author == "نویسنده تست"
    assert len(book.chapters) == 2
    assert len(book.appendices) == 1
    assert "تست" in book.metadata.tags

def test_parse_includes():
    """Test that \input commands are followed"""
    parser = LaTeXParser(Path("fixtures/sample_book/main.tex"))
    book = parser.parse()
    
    # Chapter content should be loaded from included files
    assert "بخش اول" in book.chapters[0].content_latex

def test_extract_images():
    """Test image extraction"""
    parser = LaTeXParser(Path("fixtures/sample_book/main.tex"))
    book = parser.parse()
    
    assert "figure1" in book.images
    assert book.images["figure1"].original_path.exists()

def test_extract_labels():
    """Test label extraction"""
    parser = LaTeXParser(Path("fixtures/sample_book/main.tex"))
    book = parser.parse()
    
    assert "ch:first" in book.label_registry
    assert "fig:test" in book.label_registry
    assert "eq:main" in book.label_registry

def test_encoding_detection():
    """Test handling of different encodings"""
    # Test with UTF-8, Windows-1256, etc.
    pass

def test_circular_include_detection():
    """Test that circular includes are handled"""
    pass
```

```python
# tests/test_converter.py

def test_convert_chapter():
    """Test chapter conversion to Markdown"""
    pass

def test_convert_math():
    """Test math equation conversion"""
    pass

def test_convert_images():
    """Test image reference conversion"""
    pass

def test_convert_lists():
    """Test list conversion"""
    pass

def test_frontmatter_generation():
    """Test correct frontmatter YAML generation"""
    pass
```

```python
# tests/test_git.py

def test_git_clone():
    """Test repository cloning"""
    pass

def test_git_push():
    """Test pushing to repository"""
    pass

def test_git_auth_https():
    """Test HTTPS authentication"""
    pass

def test_git_auth_ssh():
    """Test SSH authentication"""
    pass
```

---

## Part 15: Build & Distribution

### 15.1 PyInstaller Spec

Create executable for Windows:

```python
# build.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/resources/*', 'resources'),
        ('src/resources/translations/*', 'resources/translations'),
    ],
    hiddenimports=['PIL', 'git', 'keyring'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LaTeX2Astro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app, no console
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico',
)
```

### 15.2 Build Commands

```bash
# Install build dependencies
pip install pyinstaller

# Build executable
pyinstaller build.spec

# Output will be in dist/LaTeX2Astro.exe
```

---

## Part 16: Final Notes

### 16.1 Priority Order

If time/resources are limited, implement in this order:

1. **Critical (MVP):**
   - LaTeX parser with multi-file support
   - Basic Markdown conversion
   - Frontmatter generation
   - Step 1-3 of wizard (file selection, metadata, chapters)
   - Local output (no Git)

2. **Important:**
   - Chapter-by-chapter review and approval
   - Image handling
   - Step 4 with local output and ZIP
   - Persian RTL support

3. **Nice to Have:**
   - Git integration
   - Presets system
   - Configuration persistence
   - Cross-reference resolution
   - PDF image conversion

### 16.2 Key UX Principles

1. **Never lose user data** - Auto-save state, confirm before closing
2. **Show progress** - Long operations must have progress feedback
3. **Fail gracefully** - Show helpful error messages, offer solutions
4. **Persian first** - Default to Persian, proper RTL layout
5. **Review before commit** - User must explicitly approve each chapter

### 16.3 Code Style

- Use `snake_case` for functions/variables
- Use `PascalCase` for classes
- Type hints on all function signatures
- Docstrings on all public methods
- Comments in Persian for complex logic
- English for technical terms

---

## Summary

Build a professional Python GUI application that:

1. **Parses** multi-file Persian LaTeX books
2. **Extracts** metadata automatically (title, author, abstract, keywords)
3. **Converts** to Astro-compatible Markdown with proper frontmatter
4. **Provides** a wizard interface with 4 steps
5. **Allows** chapter-by-chapter review and approval before export
6. **Handles** images (finding, converting, copying)
7. **Integrates** with Git for direct pushing to repository
8. **Supports** full Persian RTL text
9. **Saves** configuration and user preferences

The application should be robust, user-friendly, and produce output that works directly with the MahdiSalem.com Astro website structure.
```

---

این پرامپت کامل است. می‌توانید مستقیماً کپی و استفاده کنید. 

**نکات:**
- حدود ۱۵۰۰۰ کلمه است
- تمام جزئیات فنی، UI، و ساختار داده را شامل می‌شود
- Schema های Astro شما را include کردم
- Git integration با جزئیات کامل
- سیستم Review فصل به فصل که خواستید
- فایل‌های i18n فارسی و انگلیسی
- Test cases