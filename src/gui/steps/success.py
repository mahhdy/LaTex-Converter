import customtkinter as ct
from gui.wizard import WizardStep

class SuccessStep(WizardStep):
    def __init__(self, master, wizard):
        super().__init__(master, wizard)
        
        self.label = ct.CTkLabel(self, text="✓ عملیات با موفقیت انجام شد", font=("Arial", 24, "bold"), text_color="green")
        self.label.pack(pady=40)
        
        self.report_box = ct.CTkTextbox(self, height=300, font=("Courier New", 12))
        self.report_box.pack(fill="both", padx=40, pady=10)
        
        self.btn_open = ct.CTkButton(self, text="باز کردن پوشه خروجی", command=self.open_output)
        self.btn_open.pack(pady=20)

    def on_show(self):
        # Hide navigation buttons on final step
        self.wizard.prev_btn.pack_forget()
        self.wizard.next_btn.configure(text="بستن برنامه", command=self.wizard.master.destroy)
        
        book = self.wizard.context.get("book")
        output_root = self.wizard.context.get("output_root")
        
        report = []
        report.append(f"کتاب: {book.metadata.title}")
        report.append(f"مسیر خروجی: {output_root}")
        report.append("-" * 30)
        report.append("عملیات انجام شده:")
        report.append("- پارس لاتک و استخراج ساختار")
        report.append("- تبدیل به مارک‌داون (Astro-compatible)")
        report.append("- انتقال تصاویر")
        report.append("- ایجاد فایل manifest.json")
        
        if self.wizard.context.get("git_pushed"):
            report.append("- ارسال به مخزن گیت (Push successful)")
        
        self.report_box.delete("0.0", "end")
        self.report_box.insert("0.0", "\n".join(report))

    def open_output(self):
        import os
        os.startfile(self.wizard.context.get("output_root"))
