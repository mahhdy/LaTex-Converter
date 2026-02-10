import customtkinter as ct
from gui.wizard import WizardStep

class MetadataStep(WizardStep):
    def __init__(self, master, wizard):
        super().__init__(master, wizard)
        
        self.label = ct.CTkLabel(self, text="Step 2: Book Metadata", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)
        
        self.form_frame = ct.CTkScrollableFrame(self)
        self.form_frame.pack(fill="both", expand=True, padx=40, pady=10)
        
        self.auto_btn = ct.CTkButton(self, text="استخراج خودکار از متن (AI/Regex)", command=self.auto_fill)
        self.auto_btn.pack(pady=10)
        
        self.fields = {}
        self._create_field("عنوان کتاب (Persian)", "title")
        self._create_field("English Slug (Folder Name)", "slug")
        self._create_field("نویسنده (Author)", "author")
        self._create_field("زبان (fa/en)", "lang")
        self._create_field("توضیحات (Description)", "description", multiline=True)
        self._create_field("برچسب‌ها (Tags)", "tags")

    def _create_field(self, label_text: str, attr_name: str, multiline=False):
        lbl = ct.CTkLabel(self.form_frame, text=label_text, anchor="e")
        lbl.pack(fill="x", padx=10, pady=(10, 0))
        
        if multiline:
            entry = ct.CTkTextbox(self.form_frame, height=80, activate_scrollbars=True)
        else:
            entry = ct.CTkEntry(self.form_frame, width=400, justify="right")
            
        entry.pack(fill="x", padx=10, pady=(0, 10))
        self.fields[attr_name] = entry

    def auto_fill(self):
        # Trigger smarter extraction
        main_tex = self.wizard.context.get("main_tex")
        if main_tex:
            from core.parser import LatexParser
            parser = LatexParser(main_tex)
            # Re-parse to get fresh metadata from the source
            parser.parse()
            self.wizard.context["book"] = parser.book
            # Refresh fields
            self.on_show()

    def on_show(self):
        book = self.wizard.context.get("book")
        if not book: return
        
        metadata = book.metadata
        for attr, entry in self.fields.items():
            value = getattr(metadata, attr)
            if isinstance(value, list):
                value = ", ".join(value)
            
            if isinstance(entry, ct.CTkTextbox):
                entry.delete("0.0", "end")
                entry.insert("0.0", str(value))
            else:
                entry.delete(0, "end")
                entry.insert(0, str(value or ""))

    def on_next(self) -> bool:
        book = self.wizard.context.get("book")
        if not book: return False
        
        metadata = book.metadata
        for attr, entry in self.fields.items():
            if isinstance(entry, ct.CTkTextbox):
                value = entry.get("0.0", "end-1c")
            else:
                value = entry.get()
                
            if attr == "tags":
                value = [t.strip() for t in value.split(",") if t.strip()]
                
            setattr(metadata, attr, value)
        
        metadata.type = self.wizard.context.get("content_type", "Book")
        return True
