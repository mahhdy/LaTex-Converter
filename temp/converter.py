#!/usr/bin/env python3
"""
LaTeX Book to Astro Markdown Converter - Professional Edition
مبدل حرفه‌ای کتاب LaTeX به Markdown برای Astro
"""

import os
import re
import shutil
import subprocess
import json
import zipfile
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ChapterInfo:
    """اطلاعات یک فصل"""
    number: int
    original_title: str
    title: str
    slug: str
    filename: str
    source_file: Path
    content: str = ""
    is_appendix: bool = False
    images: List[Path] = field(default_factory=list)
    include: bool = True  # آیا در خروجی باشد


@dataclass
class BookMetadata:
    """متادیتای کتاب (Frontmatter)"""
    title: str = ""
    author: str = ""
    description: str = ""
    lang: str = "fa"
    publish_date: str = ""
    slug: str = ""
    draft: bool = True
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    cover_image: str = ""


@dataclass
class BookStructure:
    """ساختار کامل کتاب"""
    metadata: BookMetadata
    source_dir: Path
    chapters: List[ChapterInfo] = field(default_factory=list)
    appendices: List[ChapterInfo] = field(default_factory=list)
    images: Dict[str, Path] = field(default_factory=dict)
    preamble: str = ""


# =============================================================================
# Presets / پیش‌تنظیم‌ها
# =============================================================================

PRESETS = {
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
    "مقاله علمی": {
        "categories": ["مقاله", "پژوهشی"],
        "tags": ["تحقیق", "علمی"],
        "author": "مهدی سالم"
    },
    "راهنمای عملی": {
        "categories": ["راهنما", "عملی"],
        "tags": ["آموزش", "راهنما", "گام‌به‌گام"],
        "author": "مهدی سالم"
    },
    "خالی": {
        "categories": [],
        "tags": [],
        "author": ""
    }
}

LANGUAGES = {
    "fa": "🇮🇷 فارسی",
    "en": "🇬🇧 English",
    "ar": "🇸🇦 العربية"
}


# =============================================================================
# LaTeX Parser
# =============================================================================

class LaTeXParser:
    """پارسر فایل‌های LaTeX"""
    
    def __init__(self, root_file: Path):
        self.root_file = Path(root_file)
        self.root_dir = self.root_file.parent
        self.processed_files: set = set()
        
        self.patterns = {
            'input': re.compile(r'\\input\{([^}]+)\}'),
            'include': re.compile(r'\\include\{([^}]+)\}'),
            'chapter': re.compile(r'\\chapter\{([^}]+)\}'),
            'section': re.compile(r'\\section\{([^}]+)\}'),
            'appendix': re.compile(r'\\appendix'),
            'label': re.compile(r'\\label\{([^}]+)\}'),
            'includegraphics': re.compile(r'\\includegraphics(?:$$[^$$]*\])?\{([^}]+)\}'),
            'title': re.compile(r'\\title\{([^}]+)\}'),
            'author': re.compile(r'\\author\{([^}]+)\}'),
            'date': re.compile(r'\\date\{([^}]+)\}'),
            'graphicspath': re.compile(r'\\graphicspath\{([^}]+)\}'),
            'begin_document': re.compile(r'\\begin\{document\}'),
            'end_document': re.compile(r'\\end\{document\}'),
            'abstract': re.compile(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', re.DOTALL),
            'keywords': re.compile(r'\\keywords\{([^}]+)\}'),
        }
        
        self.graphics_paths: List[Path] = [self.root_dir]
        
    def parse(self) -> BookStructure:
        """پارس کامل کتاب"""
        content = self._read_file(self.root_file)
        
        # استخراج متادیتا
        metadata = self._extract_metadata(content)
        
        # پیدا کردن مسیرهای تصویر
        self._find_graphics_paths(content)
        
        # جداسازی preamble و document
        preamble, document = self._split_document(content)
        
        # پردازش document
        full_document = self._expand_inputs(document)
        
        # استخراج فصل‌ها و پیوست‌ها
        chapters, appendices = self._extract_chapters(full_document)
        
        # جمع‌آوری تصاویر
        all_images = self._collect_all_images(full_document)
        
        return BookStructure(
            metadata=metadata,
            source_dir=self.root_dir,
            chapters=chapters,
            appendices=appendices,
            images=all_images,
            preamble=preamble
        )
    
    def _extract_metadata(self, content: str) -> BookMetadata:
        """استخراج متادیتا از فایل LaTeX"""
        title = self._extract_single(content, 'title') or "Untitled"
        author = self._extract_single(content, 'author') or ""
        date_str = self._extract_single(content, 'date') or ""
        
        # استخراج abstract به عنوان description
        abstract_match = self.patterns['abstract'].search(content)
        description = self._clean_latex(abstract_match.group(1)) if abstract_match else ""
        
        # استخراج keywords به عنوان tags
        keywords_match = self.patterns['keywords'].search(content)
        tags = []
        if keywords_match:
            tags = [t.strip() for t in keywords_match.group(1).split(',')]
        
        # تبدیل تاریخ
        publish_date = datetime.now().strftime("%Y-%m-%d")
        if date_str:
            # تلاش برای پارس تاریخ‌های مختلف
            date_str_clean = self._clean_latex(date_str)
            if re.match(r'\d{4}', date_str_clean):
                publish_date = date_str_clean[:10] if len(date_str_clean) >= 10 else f"{date_str_clean[:4]}-01-01"
        
        # ایجاد slug از عنوان
        slug = self._slugify(title)
        
        return BookMetadata(
            title=self._clean_latex(title),
            author=self._clean_latex(author),
            description=description[:500],  # حداکثر 500 کاراکتر
            lang="fa",
            publish_date=publish_date,
            slug=slug,
            draft=True,
            categories=[],
            tags=tags,
            cover_image=""
        )
    
    def _read_file(self, filepath: Path) -> str:
        """خواندن فایل"""
        filepath = Path(filepath)
        
        if not filepath.suffix:
            filepath = filepath.with_suffix('.tex')
        
        if not filepath.is_absolute():
            filepath = self.root_dir / filepath
        
        if not filepath.exists():
            return ""
        
        if str(filepath) in self.processed_files:
            return ""
        self.processed_files.add(str(filepath))
        
        encodings = ['utf-8', 'utf-8-sig', 'cp1256', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        return ""
    
    def _extract_single(self, content: str, pattern_name: str) -> Optional[str]:
        match = self.patterns[pattern_name].search(content)
        return match.group(1) if match else None
    
    def _find_graphics_paths(self, content: str):
        match = self.patterns['graphicspath'].search(content)
        if match:
            paths_str = match.group(1)
            paths = re.findall(r'\{([^}]+)\}', paths_str)
            for p in paths:
                path = self.root_dir / p
                if path.exists():
                    self.graphics_paths.append(path)
    
    def _split_document(self, content: str) -> Tuple[str, str]:
        begin_match = self.patterns['begin_document'].search(content)
        end_match = self.patterns['end_document'].search(content)
        
        if begin_match:
            preamble = content[:begin_match.start()]
            if end_match:
                document = content[begin_match.end():end_match.start()]
            else:
                document = content[begin_match.end():]
        else:
            preamble = ""
            document = content
        
        return preamble, document
    
    def _expand_inputs(self, content: str) -> str:
        r"""جایگزینی \input و \include"""
        def replace_input(match):
            filename = match.group(1)
            file_content = self._read_file(Path(filename))
            return self._expand_inputs(file_content)
        
        content = self.patterns['include'].sub(replace_input, content)
        content = self.patterns['input'].sub(replace_input, content)
        return content
    
    def _extract_chapters(self, content: str) -> Tuple[List[ChapterInfo], List[ChapterInfo]]:
        """استخراج فصل‌ها"""
        chapters = []
        appendices = []
        
        appendix_match = self.patterns['appendix'].search(content)
        appendix_pos = appendix_match.start() if appendix_match else len(content)
        
        chapter_matches = list(self.patterns['chapter'].finditer(content))
        
        for i, match in enumerate(chapter_matches):
            title = match.group(1)
            start = match.end()
            end = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(content)
            
            chapter_content = content[start:end]
            is_appendix = match.start() >= appendix_pos
            
            clean_title = self._clean_latex(title)
            slug = self._slugify(clean_title)
            num = len(appendices if is_appendix else chapters) + 1
            prefix = "app" if is_appendix else "ch"
            filename = f"{prefix}{num:02d}-{slug}.md"
            
            images = self._extract_images(chapter_content)
            
            chapter = ChapterInfo(
                number=num,
                original_title=title,
                title=clean_title,
                slug=slug,
                filename=filename,
                source_file=self.root_file,
                content=chapter_content,
                is_appendix=is_appendix,
                images=images,
                include=True
            )
            
            if is_appendix:
                appendices.append(chapter)
            else:
                chapters.append(chapter)
        
        return chapters, appendices
    
    def _extract_images(self, content: str) -> List[Path]:
        images = []
        for match in self.patterns['includegraphics'].finditer(content):
            img_name = match.group(1)
            img_path = self._find_image(img_name)
            if img_path:
                images.append(img_path)
        return images
    
    def _find_image(self, img_name: str) -> Optional[Path]:
        extensions = ['', '.png', '.jpg', '.jpeg', '.pdf', '.eps', '.svg']
        for graphics_path in self.graphics_paths:
            for ext in extensions:
                img_path = graphics_path / (img_name + ext)
                if img_path.exists():
                    return img_path
        return None
    
    def _collect_all_images(self, content: str) -> Dict[str, Path]:
        images = {}
        for match in self.patterns['includegraphics'].finditer(content):
            img_name = match.group(1)
            img_path = self._find_image(img_name)
            if img_path:
                images[img_name] = img_path
        return images
    
    def _clean_latex(self, text: str) -> str:
        text = re.sub(r'\$$a-zA-Z]+\{([^}]*)\}', r'\1', text)
        text = re.sub(r'\\[a-zA-Z]+', '', text)
        text = re.sub(r'[{}]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _slugify(self, text: str) -> str:
        text = self._clean_latex(text)
        text = text.lower().strip()
        # حفظ حروف فارسی و انگلیسی
        text = re.sub(r'[^\w\s\u0600-\u06FF-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        # حذف خط تیره از ابتدا و انتها
        text = text.strip('-')
        return text[:50]


# =============================================================================
# Markdown Converter
# =============================================================================

class MarkdownConverter:
    """تبدیل به Markdown"""
    
    def __init__(self, book: BookStructure, output_dir: Path):
        self.book = book
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        
    def convert(self) -> Path:
        book_dir = self.output_dir / "books" / self.book.metadata.lang
        book_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        self._copy_images()
        self._create_book_overview(book_dir)
        
        for chapter in self.book.chapters:
            if chapter.include:
                self._convert_chapter(book_dir, chapter)
        
        for appendix in self.book.appendices:
            if appendix.include:
                self._convert_chapter(book_dir, appendix)
        
        return book_dir
    
    def _copy_images(self):
        for img_name, img_path in self.book.images.items():
            dest = self.images_dir / img_path.name
            if img_path.suffix.lower() in ['.pdf', '.eps']:
                self._convert_image(img_path, dest.with_suffix('.png'))
            else:
                try:
                    shutil.copy2(img_path, dest)
                except Exception:
                    pass
    
    def _convert_image(self, src: Path, dest: Path):
        try:
            if src.suffix.lower() == '.pdf':
                subprocess.run(
                    ['pdftoppm', '-png', '-singlefile', str(src), str(dest.with_suffix(''))],
                    check=True, capture_output=True
                )
            else:
                subprocess.run(
                    ['magick', 'convert', str(src), str(dest)],
                    check=True, capture_output=True
                )
        except Exception:
            try:
                shutil.copy2(src, dest.with_suffix(src.suffix))
            except:
                pass
    
    def _create_book_overview(self, book_dir: Path):
        meta = self.book.metadata
        
        # ساخت frontmatter
        categories_yaml = "\n".join([f"  - {cat}" for cat in meta.categories]) if meta.categories else ""
        tags_yaml = "\n".join([f"  - {tag}" for tag in meta.tags]) if meta.tags else ""
        
        frontmatter = f'''---
title: "{meta.title}"
author: "{meta.author}"
description: "{meta.description}"
lang: {meta.lang}
publishDate: {meta.publish_date}
draft: {str(meta.draft).lower()}
coverImage: "{meta.cover_image or f'/images/books/{meta.slug}.jpg'}"
'''
        if categories_yaml:
            frontmatter += f"categories:\n{categories_yaml}\n"
        if tags_yaml:
            frontmatter += f"tags:\n{tags_yaml}\n"
        
        frontmatter += f'''---

# {meta.title}

**نویسنده:** {meta.author}

{meta.description}

## فهرست مطالب

'''
        for ch in self.book.chapters:
            if ch.include:
                frontmatter += f"- [فصل {ch.number}: {ch.title}](./{ch.filename.replace('.md', '')})\n"
        
        if any(app.include for app in self.book.appendices):
            frontmatter += "\n### پیوست‌ها\n\n"
            for app in self.book.appendices:
                if app.include:
                    frontmatter += f"- [پیوست {app.number}: {app.title}](./{app.filename.replace('.md', '')})\n"
        
        book_file = book_dir / f"{meta.slug}.md"
        with open(book_file, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
    
    def _convert_chapter(self, book_dir: Path, chapter: ChapterInfo):
        md_content = self._latex_to_markdown(chapter.content)
        md_content = self._fix_image_links(md_content)
        
        meta = self.book.metadata
        frontmatter = f'''---
title: "{chapter.title}"
bookSlug: "{meta.lang}/{meta.slug}"
order: {chapter.number}
lang: {meta.lang}
---

'''
        full_content = frontmatter + md_content
        
        chapter_file = book_dir / chapter.filename
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(full_content)
    
    def _latex_to_markdown(self, latex_content: str) -> str:
        try:
            result = subprocess.run(
                ['pandoc', '-f', 'latex', '-t', 'markdown', '--wrap=none'],
                input=latex_content,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except Exception:
            return self._basic_latex_to_md(latex_content)
    
    def _basic_latex_to_md(self, content: str) -> str:
        content = re.sub(r'\\section\{([^}]+)\}', r'## \1', content)
        content = re.sub(r'\\subsection\{([^}]+)\}', r'### \1', content)
        content = re.sub(r'\\subsubsection\{([^}]+)\}', r'#### \1', content)
        content = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', content)
        content = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', content)
        content = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', content)
        content = re.sub(r'\\begin\{itemize\}', '', content)
        content = re.sub(r'\\end\{itemize\}', '', content)
        content = re.sub(r'\\item\s*', '- ', content)
        return content
    
    def _fix_image_links(self, content: str) -> str:
        def replace_img(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            img_name = Path(img_path).stem
            for ext in ['.png', '.jpg', '.jpeg', '.svg', '.gif']:
                if (self.images_dir / (img_name + ext)).exists():
                    return f'![{alt_text}](/images/{img_name}{ext})'
            return match.group(0)
        
        content = re.sub(r'!\[([^$$]*)\]\(([^)]+)\)', replace_img, content)
        return content


# =============================================================================
# GUI Application - Wizard Style
# =============================================================================

class BookConverterWizard:
    """رابط کاربری Wizard"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("مبدل کتاب LaTeX به Markdown")
        self.root.geometry("1000x750")
        
        # تنظیم فونت فارسی
        self.setup_fonts()
        
        self.output_dir = Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        
        self.book_structure: Optional[BookStructure] = None
        self.current_step = 0
        
        # فریم‌های مراحل
        self.steps = []
        self.step_titles = [
            "۱. انتخاب فایل",
            "۲. اطلاعات کتاب",
            "۳. فصل‌ها و فایل‌ها",
            "۴. تبدیل و خروجی"
        ]
        
        self.create_main_layout()
        self.create_step1()
        self.create_step2()
        self.create_step3()
        self.create_step4()
        
        self.show_step(0)
    
    def setup_fonts(self):
        """تنظیم فونت"""
        try:
            import tkinter.font as tkfont
            default_font = tkfont.nametofont("TkDefaultFont")
            default_font.configure(family="Tahoma", size=10)
        except:
            pass
    
    def create_main_layout(self):
        """ایجاد لایه اصلی"""
        # هدر با نمایش مراحل
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(fill='x', padx=10, pady=10)
        
        self.step_labels = []
        for i, title in enumerate(self.step_titles):
            lbl = ttk.Label(self.header_frame, text=title, font=('Tahoma', 11))
            lbl.pack(side='left', padx=20)
            self.step_labels.append(lbl)
        
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=10)
        
        # محتوای اصلی
        self.content_frame = ttk.Frame(self.root, padding="20")
        self.content_frame.pack(fill='both', expand=True)
        
        # دکمه‌های پایین
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=10)
        self.button_frame = ttk.Frame(self.root, padding="10")
        self.button_frame.pack(fill='x')
        
        self.prev_btn = ttk.Button(self.button_frame, text="← قبلی", command=self.prev_step)
        self.prev_btn.pack(side='left', padx=5)
        
        self.next_btn = ttk.Button(self.button_frame, text="بعدی →", command=self.next_step)
        self.next_btn.pack(side='right', padx=5)
    
    def show_step(self, step_num):
        """نمایش مرحله"""
        self.current_step = step_num
        
        # آپدیت هدر
        for i, lbl in enumerate(self.step_labels):
            if i == step_num:
                lbl.configure(font=('Tahoma', 11, 'bold'), foreground='#0066cc')
            elif i < step_num:
                lbl.configure(font=('Tahoma', 11), foreground='#008800')
            else:
                lbl.configure(font=('Tahoma', 11), foreground='#888888')
        
        # نمایش فریم مناسب
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()
        
        self.steps[step_num].pack(fill='both', expand=True)
        
        # آپدیت دکمه‌ها
        self.prev_btn.configure(state='normal' if step_num > 0 else 'disabled')
        
        if step_num == len(self.steps) - 1:
            self.next_btn.configure(text="تبدیل ✓", command=self.do_convert)
        else:
            self.next_btn.configure(text="بعدی →", command=self.next_step)
    
    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def next_step(self):
        if self.current_step == 0:
            if not self.tex_file_var.get():
                messagebox.showerror("خطا", "لطفاً فایل LaTeX را انتخاب کنید")
                return
            if not self.book_structure:
                self.analyze_file()
                return
        
        if self.current_step == 1:
            self.save_metadata()
        
        if self.current_step == 2:
            self.save_chapters()
        
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
    
    # =========================================================================
    # Step 1: File Selection
    # =========================================================================
    
    def create_step1(self):
        """مرحله ۱: انتخاب فایل"""
        frame = ttk.Frame(self.content_frame)
        self.steps.append(frame)
        
        # عنوان
        ttk.Label(frame, text="انتخاب فایل LaTeX", font=('Tahoma', 14, 'bold')).pack(pady=20)
        ttk.Label(frame, text="فایل اصلی (.tex) کتاب خود را انتخاب کنید").pack()
        
        # انتخاب فایل
        file_frame = ttk.Frame(frame)
        file_frame.pack(pady=30, fill='x', padx=50)
        
        ttk.Label(file_frame, text="فایل:").pack(side='left')
        self.tex_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.tex_file_var, width=60).pack(side='left', padx=10)
        ttk.Button(file_frame, text="انتخاب...", command=self.browse_file).pack(side='left')
        
        # دکمه تحلیل
        ttk.Button(frame, text="🔍 تحلیل ساختار فایل", command=self.analyze_file).pack(pady=20)
        
        # نتیجه تحلیل
        self.analysis_frame = ttk.LabelFrame(frame, text="نتیجه تحلیل", padding="10")
        self.analysis_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.analysis_text = scrolledtext.ScrolledText(self.analysis_frame, height=15, state='disabled')
        self.analysis_text.pack(fill='both', expand=True)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("LaTeX files", "*.tex"), ("All files", "*.*")]
        )
        if filename:
            self.tex_file_var.set(filename)
    
    def analyze_file(self):
        """تحلیل فایل LaTeX"""
        tex_file = self.tex_file_var.get()
        if not tex_file:
            return
        
        self.log_analysis("در حال تحلیل...")
        
        try:
            parser = LaTeXParser(Path(tex_file))
            self.book_structure = parser.parse()
            
            # نمایش نتیجه
            info = f"""✅ تحلیل موفق!

📚 عنوان: {self.book_structure.metadata.title}
✍️ نویسنده: {self.book_structure.metadata.author}
📅 تاریخ: {self.book_structure.metadata.publish_date}

📖 تعداد فصل‌ها: {len(self.book_structure.chapters)}
📎 تعداد پیوست‌ها: {len(self.book_structure.appendices)}
🖼️ تعداد تصاویر: {len(self.book_structure.images)}

فصل‌ها:
"""
            for ch in self.book_structure.chapters:
                info += f"  - فصل {ch.number}: {ch.title}\n"
            
            if self.book_structure.appendices:
                info += "\nپیوست‌ها:\n"
                for app in self.book_structure.appendices:
                    info += f"  - پیوست {app.number}: {app.title}\n"
            
            self.log_analysis(info)
            
            # پر کردن فرم مرحله ۲
            self.populate_metadata_form()
            self.populate_chapters_list()
            
            # رفتن به مرحله بعد
            self.show_step(1)
            
        except Exception as e:
            self.log_analysis(f"❌ خطا: {e}")
    
    def log_analysis(self, text):
        self.analysis_text.configure(state='normal')
        self.analysis_text.delete('1.0', 'end')
        self.analysis_text.insert('end', text)
        self.analysis_text.configure(state='disabled')
    
    # =========================================================================
    # Step 2: Book Metadata
    # =========================================================================
    
    def create_step2(self):
        """مرحله ۲: اطلاعات کتاب"""
        frame = ttk.Frame(self.content_frame)
        self.steps.append(frame)
        
        # عنوان
        ttk.Label(frame, text="اطلاعات کتاب", font=('Tahoma', 14, 'bold')).pack(pady=10)
        ttk.Label(frame, text="مشخصات کتاب و فراداده‌ها را وارد کنید").pack()
        
        # فرم
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # ردیف ۱: پیش‌تنظیم و زبان
        row1 = ttk.Frame(form_frame)
        row1.pack(fill='x', pady=5)
        
        ttk.Label(row1, text="انتخاب از پیش‌تنظیم‌ها:", width=20, anchor='e').pack(side='left')
        self.preset_var = tk.StringVar()
        preset_combo = ttk.Combobox(row1, textvariable=self.preset_var, values=list(PRESETS.keys()), width=25)
        preset_combo.pack(side='left', padx=5)
        preset_combo.bind('<<ComboboxSelected>>', self.apply_preset)
        
        ttk.Label(row1, text="زبان:", width=10, anchor='e').pack(side='left', padx=(20, 0))
        self.lang_var = tk.StringVar(value='fa')
        lang_combo = ttk.Combobox(row1, textvariable=self.lang_var, width=15)
        lang_combo['values'] = [f"{code} - {name}" for code, name in LANGUAGES.items()]
        lang_combo.set("fa - 🇮🇷 فارسی")
        lang_combo.pack(side='left', padx=5)
        
        # ردیف ۲: عنوان
        row2 = ttk.Frame(form_frame)
        row2.pack(fill='x', pady=5)
        
        ttk.Label(row2, text="عنوان کتاب:", width=20, anchor='e').pack(side='left')
        self.title_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.title_var, width=60).pack(side='left', padx=5, fill='x', expand=True)
        
        # ردیف ۳: slug و تاریخ
        row3 = ttk.Frame(form_frame)
        row3.pack(fill='x', pady=5)
        
        ttk.Label(row3, text="شناسه URL (slug):", width=20, anchor='e').pack(side='left')
        self.slug_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.slug_var, width=30).pack(side='left', padx=5)
        
        ttk.Label(row3, text="تاریخ انتشار:", width=15, anchor='e').pack(side='left', padx=(20, 0))
        self.date_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.date_var, width=15).pack(side='left', padx=5)
        
        self.draft_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row3, text="پیش‌نویس (Draft)", variable=self.draft_var).pack(side='left', padx=20)
        
        # ردیف ۴: نویسنده
        row4 = ttk.Frame(form_frame)
        row4.pack(fill='x', pady=5)
        
        ttk.Label(row4, text="نویسنده:", width=20, anchor='e').pack(side='left')
        self.author_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.author_var, width=40).pack(side='left', padx=5)
        
        # ردیف ۵: توضیحات
        row5 = ttk.Frame(form_frame)
        row5.pack(fill='x', pady=5)
        
        ttk.Label(row5, text="توضیح کوتاه:", width=20, anchor='ne').pack(side='left')
        self.desc_text = tk.Text(row5, height=4, width=60)
        self.desc_text.pack(side='left', padx=5, fill='x', expand=True)
        
        # ردیف ۶: دسته‌بندی‌ها و برچسب‌ها
        row6 = ttk.Frame(form_frame)
        row6.pack(fill='x', pady=5)
        
        ttk.Label(row6, text="دسته‌بندی‌ها:", width=20, anchor='e').pack(side='left')
        self.categories_var = tk.StringVar()
        ttk.Entry(row6, textvariable=self.categories_var, width=30).pack(side='left', padx=5)
        ttk.Label(row6, text="(با کاما جدا شود)").pack(side='left')
        
        row7 = ttk.Frame(form_frame)
        row7.pack(fill='x', pady=5)
        
        ttk.Label(row7, text="برچسب‌ها:", width=20, anchor='e').pack(side='left')
        self.tags_var = tk.StringVar()
        ttk.Entry(row7, textvariable=self.tags_var, width=50).pack(side='left', padx=5)
        ttk.Label(row7, text="(با کاما جدا شود)").pack(side='left')
        
        # ردیف ۸: تصویر جلد
        row8 = ttk.Frame(form_frame)
        row8.pack(fill='x', pady=5)
        
        ttk.Label(row8, text="تصویر جلد:", width=20, anchor='e').pack(side='left')
        self.cover_var = tk.StringVar()
        ttk.Entry(row8, textvariable=self.cover_var, width=40).pack(side='left', padx=5)
        ttk.Button(row8, text="انتخاب...", command=self.browse_cover).pack(side='left')
        
        # پیش‌نمایش frontmatter
        preview_frame = ttk.LabelFrame(form_frame, text="پیش‌نمایش Frontmatter", padding="5")
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, state='disabled')
        self.preview_text.pack(fill='both', expand=True)
        
        # دکمه بروزرسانی پیش‌نمایش
        ttk.Button(form_frame, text="🔄 بروزرسانی پیش‌نمایش", command=self.update_preview).pack(pady=5)
        
        # Bind events for auto-update
        self.title_var.trace_add('write', lambda *args: self.auto_generate_slug())
    
    def apply_preset(self, event=None):
        """اعمال پیش‌تنظیم"""
        preset_name = self.preset_var.get()
        if preset_name in PRESETS:
            preset = PRESETS[preset_name]
            self.categories_var.set(", ".join(preset.get("categories", [])))
            self.tags_var.set(", ".join(preset.get("tags", [])))
            if preset.get("author"):
                self.author_var.set(preset["author"])
    
    def auto_generate_slug(self):
        """تولید خودکار slug از عنوان"""
        title = self.title_var.get()
        if title:
            # تبدیل ساده به slug
            slug = title.lower().strip()
            slug = re.sub(r'[^\w\s\u0600-\u06FF-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            slug = slug.strip('-')[:50]
            self.slug_var.set(slug)
    
    def browse_cover(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")]
        )
        if filename:
            self.cover_var.set(filename)
    
    def populate_metadata_form(self):
        """پر کردن فرم با داده‌های استخراج‌شده"""
        if not self.book_structure:
            return
        
        meta = self.book_structure.metadata
        self.title_var.set(meta.title)
        self.slug_var.set(meta.slug)
        self.author_var.set(meta.author)
        self.date_var.set(meta.publish_date)
        self.draft_var.set(meta.draft)
        self.desc_text.delete('1.0', 'end')
        self.desc_text.insert('1.0', meta.description)
        self.categories_var.set(", ".join(meta.categories))
        self.tags_var.set(", ".join(meta.tags))
    
    def update_preview(self):
        """بروزرسانی پیش‌نمایش"""
        self.save_metadata()
        
        meta = self.book_structure.metadata
        categories_yaml = "\n".join([f"  - {cat}" for cat in meta.categories]) if meta.categories else "  []"
        tags_yaml = "\n".join([f"  - {tag}" for tag in meta.tags]) if meta.tags else "  []"
        
        preview = f'''---
title: "{meta.title}"
author: "{meta.author}"
description: "{meta.description[:100]}..."
lang: {meta.lang}
publishDate: {meta.publish_date}
draft: {str(meta.draft).lower()}
coverImage: "{meta.cover_image or f'/images/books/{meta.slug}.jpg'}"
categories:
{categories_yaml}
tags:
{tags_yaml}
---'''
        
        self.preview_text.configure(state='normal')
        self.preview_text.delete('1.0', 'end')
        self.preview_text.insert('1.0', preview)
        self.preview_text.configure(state='disabled')
    
    def save_metadata(self):
        """ذخیره متادیتا"""
        if not self.book_structure:
            return
        
        lang_selection = self.lang_var.get()
        lang_code = lang_selection.split(' - ')[0] if ' - ' in lang_selection else lang_selection
        
        self.book_structure.metadata.title = self.title_var.get()
        self.book_structure.metadata.slug = self.slug_var.get()
        self.book_structure.metadata.author = self.author_var.get()
        self.book_structure.metadata.publish_date = self.date_var.get()
        self.book_structure.metadata.draft = self.draft_var.get()
        self.book_structure.metadata.description = self.desc_text.get('1.0', 'end').strip()
        self.book_structure.metadata.lang = lang_code
        self.book_structure.metadata.cover_image = self.cover_var.get()
        
        # پارس دسته‌بندی‌ها و برچسب‌ها
        cats = self.categories_var.get()
        self.book_structure.metadata.categories = [c.strip() for c in cats.split(',') if c.strip()]
        
        tags = self.tags_var.get()
        self.book_structure.metadata.tags = [t.strip() for t in tags.split(',') if t.strip()]
    
    # =========================================================================
    # Step 3: Chapters
    # =========================================================================
    
    def create_step3(self):
        """مرحله ۳: فصل‌ها و فایل‌ها"""
        frame = ttk.Frame(self.content_frame)
        self.steps.append(frame)
        
        # عنوان
        ttk.Label(frame, text="فصل‌ها و فایل‌ها", font=('Tahoma', 14, 'bold')).pack(pady=10)
        ttk.Label(frame, text="عنوان، نام فایل و ترتیب فصل‌ها را تنظیم کنید").pack()
        
        # فریم لیست با اسکرول
        list_container = ttk.Frame(frame)
        list_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Canvas و Scrollbar
        canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=canvas.yview)
        self.chapters_frame = ttk.Frame(canvas)
        
        self.chapters_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.chapters_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Mouse wheel scroll
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # لیست فصل‌ها (پر می‌شود در populate_chapters_list)
        self.chapter_widgets = []
    
    def populate_chapters_list(self):
        """پر کردن لیست فصل‌ها"""
        # پاک کردن قبلی
        for widget in self.chapters_frame.winfo_children():
            widget.destroy()
        self.chapter_widgets = []
        
        if not self.book_structure:
            return
        
        # هدر
        header = ttk.Frame(self.chapters_frame)
        header.pack(fill='x', pady=5)
        
        ttk.Label(header, text="شامل", width=6).pack(side='left', padx=2)
        ttk.Label(header, text="نوع", width=8).pack(side='left', padx=2)
        ttk.Label(header, text="شماره", width=6).pack(side='left', padx=2)
        ttk.Label(header, text="عنوان", width=30).pack(side='left', padx=2)
        ttk.Label(header, text="نام فایل", width=30).pack(side='left', padx=2)
        
        ttk.Separator(self.chapters_frame, orient='horizontal').pack(fill='x', pady=5)
        
        # فصل‌ها
        all_items = [(ch, 'chapter') for ch in self.book_structure.chapters] + \
                    [(app, 'appendix') for app in self.book_structure.appendices]
        
        for item, item_type in all_items:
            row = ttk.Frame(self.chapters_frame)
            row.pack(fill='x', pady=2)
            
            # Checkbox
            include_var = tk.BooleanVar(value=item.include)
            ttk.Checkbutton(row, variable=include_var).pack(side='left', padx=2)
            
            # نوع
            type_label = "فصل" if item_type == 'chapter' else "پیوست"
            ttk.Label(row, text=type_label, width=8).pack(side='left', padx=2)
            
            # شماره
            ttk.Label(row, text=str(item.number), width=6).pack(side='left', padx=2)
            
            # عنوان (قابل ویرایش)
            title_var = tk.StringVar(value=item.title)
            ttk.Entry(row, textvariable=title_var, width=30).pack(side='left', padx=2)
            
            # نام فایل (قابل ویرایش)
            filename_var = tk.StringVar(value=item.filename)
            ttk.Entry(row, textvariable=filename_var, width=30).pack(side='left', padx=2)
            
            # دکمه بازسازی نام فایل
            def regenerate_filename(title_v=title_var, filename_v=filename_var, ch=item):
                new_title = title_v.get()
                slug = re.sub(r'[^\w\s\u0600-\u06FF-]', '', new_title.lower())
                slug = re.sub(r'[-\s]+', '-', slug).strip('-')[:30]
                prefix = "app" if ch.is_appendix else "ch"
                filename_v.set(f"{prefix}{ch.number:02d}-{slug}.md")
            
            ttk.Button(row, text="🔄", width=3, command=regenerate_filename).pack(side='left', padx=2)
            
            # تعداد تصاویر
            ttk.Label(row, text=f"🖼️ {len(item.images)}").pack(side='left', padx=5)
            
            self.chapter_widgets.append({
                'item': item,
                'type': item_type,
                'include_var': include_var,
                'title_var': title_var,
                'filename_var': filename_var
            })
    
    def save_chapters(self):
        """ذخیره تغییرات فصل‌ها"""
        for widget_data in self.chapter_widgets:
            item = widget_data['item']
            item.include = widget_data['include_var'].get()
            item.title = widget_data['title_var'].get()
            item.filename = widget_data['filename_var'].get()
    
    # =========================================================================
    # Step 4: Convert
    # =========================================================================
    
    def create_step4(self):
        """مرحله ۴: تبدیل و خروجی"""
        frame = ttk.Frame(self.content_frame)
        self.steps.append(frame)
        
        # عنوان
        ttk.Label(frame, text="تبدیل و خروجی", font=('Tahoma', 14, 'bold')).pack(pady=10)
        
        # تنظیمات خروجی
        settings_frame = ttk.LabelFrame(frame, text="تنظیمات خروجی", padding="10")
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill='x', pady=5)
        
        ttk.Label(row1, text="پوشه خروجی:").pack(side='left')
        self.output_var = tk.StringVar(value=str(self.output_dir))
        ttk.Entry(row1, textvariable=self.output_var, width=50).pack(side='left', padx=10)
        ttk.Button(row1, text="انتخاب...", command=self.browse_output).pack(side='left')
        
        # دکمه‌های عملیات
        actions_frame = ttk.Frame(frame)
        actions_frame.pack(pady=20)
        
        ttk.Button(actions_frame, text="🔄 تبدیل به Markdown", command=self.do_convert).pack(side='left', padx=10)
        ttk.Button(actions_frame, text="📦 ایجاد فایل ZIP", command=self.create_zip).pack(side='left', padx=10)
        ttk.Button(actions_frame, text="📁 کپی به سایت", command=self.copy_to_site).pack(side='left', padx=10)
        ttk.Button(actions_frame, text="📂 باز کردن پوشه خروجی", command=self.open_output_folder).pack(side='left', padx=10)
        
        # Progress
        self.progress = ttk.Progressbar(frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=10)
        
        # لاگ
        log_frame = ttk.LabelFrame(frame, text="گزارش عملیات", padding="5")
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state='disabled')
        self.log_text.pack(fill='both', expand=True)
    
    def browse_output(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.output_var.set(dirname)
            self.output_dir = Path(dirname)
    
    def log(self, message: str):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see('end')
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()
    
    def do_convert(self):
        """انجام تبدیل"""
        if not self.book_structure:
            messagebox.showerror("خطا", "ابتدا فایل را تحلیل کنید")
            return
        
        self.save_metadata()
        self.save_chapters()
        
        self.progress.start()
        self.log("شروع تبدیل...")
        
        def convert():
            error_msg = None
            output_path = None
            try:
                output_dir = Path(self.output_var.get())
                converter = MarkdownConverter(self.book_structure, output_dir)
                output_path = converter.convert()
            except Exception as ex:
                error_msg = str(ex)
            
            def update_ui():
                self.progress.stop()
                if error_msg:
                    messagebox.showerror("خطا", error_msg)
                    self.log(f"❌ خطا: {error_msg}")
                else:
                    self.log(f"✅ تبدیل کامل شد!")
                    self.log(f"📁 خروجی: {output_path}")
                    
                    # نمایش خلاصه
                    ch_count = sum(1 for ch in self.book_structure.chapters if ch.include)
                    app_count = sum(1 for app in self.book_structure.appendices if app.include)
                    self.log(f"📖 فصل‌ها: {ch_count}")
                    self.log(f"📎 پیوست‌ها: {app_count}")
                    self.log(f"🖼️ تصاویر: {len(self.book_structure.images)}")
                    
                    messagebox.showinfo("موفق", f"تبدیل با موفقیت انجام شد!\n\n{output_path}")
            
            self.root.after(0, update_ui)
        
        threading.Thread(target=convert, daemon=True).start()
    
    def create_zip(self):
        """ایجاد ZIP"""
        output_dir = Path(self.output_var.get())
        if not output_dir.exists() or not any(output_dir.iterdir()):
            messagebox.showerror("خطا", "ابتدا تبدیل را انجام دهید")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = self.book_structure.metadata.slug if self.book_structure else "book"
        zip_name = f"{slug}_{timestamp}.zip"
        
        try:
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in output_dir.rglob('*'):
                    if file.is_file():
                        arcname = file.relative_to(output_dir)
                        zipf.write(file, arcname)
            
            self.log(f"📦 فایل ZIP ایجاد شد: {zip_name}")
            messagebox.showinfo("موفق", f"فایل فشرده ایجاد شد:\n{zip_name}")
        except Exception as e:
            messagebox.showerror("خطا", str(e))
    
    def copy_to_site(self):
        """کپی به سایت"""
        site_dir = filedialog.askdirectory(title="پوشه اصلی سایت را انتخاب کنید")
        if not site_dir:
            return
        
        output_dir = Path(self.output_var.get())
        
        try:
            site_path = Path(site_dir)
            content_dir = site_path / "src" / "content"
            public_dir = site_path / "public"
            
            copied = 0
            
            books_src = output_dir / "books"
            if books_src.exists():
                books_dest = content_dir / "books"
                for file in books_src.rglob('*.md'):
                    rel_path = file.relative_to(books_src)
                    target = books_dest / rel_path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, target)
                    self.log(f"📄 {target}")
                    copied += 1
            
            images_src = output_dir / "images"
            if images_src.exists():
                images_dest = public_dir / "images"
                images_dest.mkdir(parents=True, exist_ok=True)
                for file in images_src.rglob('*'):
                    if file.is_file():
                        shutil.copy2(file, images_dest / file.name)
                        self.log(f"🖼️ {file.name}")
                        copied += 1
            
            self.log(f"✅ {copied} فایل کپی شد")
            messagebox.showinfo("موفق", f"{copied} فایل به سایت کپی شد!")
        except Exception as e:
            messagebox.showerror("خطا", str(e))
    
    def open_output_folder(self):
        """باز کردن پوشه خروجی"""
        output_dir = Path(self.output_var.get())
        if output_dir.exists():
            os.startfile(str(output_dir))
        else:
            messagebox.showerror("خطا", "پوشه خروجی وجود ندارد")


# =============================================================================
# Main
# =============================================================================

def main():
    root = tk.Tk()
    
    # آیکون (اختیاری)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = BookConverterWizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()