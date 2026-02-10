import customtkinter as ct
from pathlib import Path
from tkinter import filedialog
from gui.wizard import WizardStep
from core.parser import LatexParser

class AnalysisStep(WizardStep):
    def __init__(self, master, wizard):
        super().__init__(master, wizard)
        
        self.label = ct.CTkLabel(self, text="Step 1: File Analysis", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)
        
        self.file_frame = ct.CTkFrame(self)
        self.file_frame.pack(fill="x", padx=40, pady=10)
        
        self.file_path_var = ct.StringVar(value="No file selected")
        self.file_label = ct.CTkLabel(self.file_frame, textvariable=self.file_path_var, text_color="gray")
        self.file_label.pack(side="left", padx=10)
        
        self.browse_btn = ct.CTkButton(self.file_frame, text="Browse File", command=self.browse_file)
        self.browse_btn.pack(side="right", padx=10)

        # Content Type Selection
        self.type_frame = ct.CTkFrame(self)
        self.type_frame.pack(fill="x", padx=40, pady=5)
        
        ct.CTkLabel(self.type_frame, text="نوع محتوا (Content Type):").pack(side="left", padx=10)
        self.content_type_var = ct.StringVar(value="Book")
        self.type_menu = ct.CTkOptionMenu(self.type_frame, values=["Book", "Article", "Markdown"], variable=self.content_type_var)
        self.type_menu.pack(side="left", padx=10)
        
        self.status_box = ct.CTkTextbox(self, height=180)
        self.status_box.pack(fill="both", padx=40, pady=10)
        self.status_box.insert("0.0", "Select a LaTeX or Markdown file to begin analysis...\n")

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[
            ("Support files", "*.tex *.md"),
            ("LaTeX files", "*.tex"),
            ("Markdown files", "*.md")
        ])
        if filename:
            path = Path(filename)
            self.file_path_var.set(str(path))
            
            # Auto-detect type if it's .md
            if path.suffix == ".md":
                self.content_type_var.set("Markdown")
                
            self.run_analysis(path)

    def run_analysis(self, path: Path):
        content_type = self.content_type_var.get()
        self.status_box.insert("end", f"Analyzing {path.name} as {content_type}...\n")
        
        try:
            if content_type == "Markdown":
                from models.book import Book, BookMetadata, Chapter
                # Create a simple book structure for a single MD file
                metadata = BookMetadata(title=path.stem, slug=path.stem)
                content = path.read_text(encoding="utf-8")
                chapter = Chapter(number=1, title=path.stem, slug=path.stem, filename=path.name, content_markdown=content)
                book = Book(metadata=metadata, chapters=[chapter], source_dir=path.parent)
            else:
                from core.parser import LatexParser
                parser = LatexParser(path)
                book = parser.parse()
            
            self.wizard.context["main_tex"] = path
            self.wizard.context["book"] = book
            self.wizard.context["content_type"] = content_type
            
            self.status_box.insert("end", "✓ Analysis complete.\n")
            self.status_box.insert("end", f"Title: {book.metadata.title}\n")
            if content_type == "Book":
                self.status_box.insert("end", f"Chapters found: {len(book.chapters)}\n")
            else:
                self.status_box.insert("end", "Content treated as single document.\n")
                
        except Exception as e:
            self.status_box.insert("end", f"❌ Error: {str(e)}\n")

    def on_next(self) -> bool:
        if not self.wizard.context["book"]:
            self.status_box.insert("end", "Please select and analyze a file first.\n")
            return False
        return True
