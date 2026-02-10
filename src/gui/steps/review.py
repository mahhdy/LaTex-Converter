import customtkinter as ct
from gui.wizard import WizardStep

class ReviewStep(WizardStep):
    def __init__(self, master, wizard):
        super().__init__(master, wizard)
        
        self.label = ct.CTkLabel(self, text="مرحله ۳: بازبینی و تایید فصل‌ها", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)
        
        self.list_frame = ct.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=40, pady=10)
        
        self.chapter_vars = []

    def on_show(self):
        book = self.wizard.context.get("book")
        if not book: return
        
        # Clear previous
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.chapter_vars = []
        
        is_book = book.metadata.type == "Book"
        self.label.configure(text="مرحله ۳: بازبینی و تایید نهایی" if not is_book else "مرحله ۳: بازبینی و تایید فصل‌ها")
        
        for idx, chapter in enumerate(book.chapters):
            row = ct.CTkFrame(self.list_frame)
            row.pack(fill="x", pady=5)
            
            # Use a dict instead of just a bool var to store reference
            var = ct.BooleanVar(value=not chapter.is_draft)
            text = f"فصل {idx+1}: {chapter.title}" if is_book else f"سند: {chapter.title}"
            cb = ct.CTkCheckBox(row, text=text, variable=var, font=("Arial", 14))
            cb.pack(side="right", padx=10)
            
            self.chapter_vars.append((chapter, var))
            
            if is_book:
                # Reorder buttons
                dn_btn = ct.CTkButton(row, text="بیا پایین ↓", width=80, command=lambda i=idx: self.move_down(i))
                dn_btn.pack(side="left", padx=2)
                
                up_btn = ct.CTkButton(row, text="برو بالا ↑", width=80, command=lambda i=idx: self.move_up(i))
                up_btn.pack(side="left", padx=2)

    def move_up(self, idx):
        if idx > 0:
            chapters = self.wizard.context["book"].chapters
            chapters[idx], chapters[idx-1] = chapters[idx-1], chapters[idx]
            self.on_show()

    def move_down(self, idx):
        chapters = self.wizard.context["book"].chapters
        if idx < len(chapters) - 1:
            chapters[idx], chapters[idx+1] = chapters[idx+1], chapters[idx]
            self.on_show()

    def on_next(self) -> bool:
        # Final approval check
        for chapter, var in self.chapter_vars:
            chapter.is_draft = not var.get()
        return True
