import customtkinter as ct
from gui.wizard import WizardStep

class RepositoryStep(WizardStep):
    def __init__(self, master, wizard):
        super().__init__(master, wizard)
        
        self.label = ct.CTkLabel(self, text="Step 4: Repository Configuration", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)
        
        self.form_frame = ct.CTkFrame(self)
        self.form_frame.pack(fill="both", expand=True, padx=40, pady=10)
        
        # Git Sync Toggle
        self.sync_var = ct.BooleanVar(value=False)
        self.sync_cb = ct.CTkCheckBox(self.form_frame, text="فعال‌سازی همگام‌سازی با گیت (Enable Git Sync)", variable=self.sync_var, command=self.toggle_sync)
        self.sync_cb.pack(pady=20)
        
        self.fields_frame = ct.CTkFrame(self.form_frame, fg_color="transparent")
        self.fields_frame.pack(fill="both", expand=True, padx=20)
        
        self.fields = {}
        self._create_field("آدرس مخزن (Remote URL)", "git_url", placeholder="https://github.com/user/repo.git")
        self._create_field("توکن امنیتی (Personal Access Token)", "git_token", placeholder="ghp_XXXXXXXXXXXXXXXXXXXX", secret=True)
        self._create_field("نام شاخه (Branch Name)", "git_branch", placeholder="main")
        
        self.toggle_sync() # Initial state

    def _create_field(self, label_text: str, attr_name: str, placeholder: str = "", secret=False):
        lbl = ct.CTkLabel(self.fields_frame, text=label_text, anchor="e")
        lbl.pack(fill="x", padx=10, pady=(10, 0))
        
        entry = ct.CTkEntry(self.fields_frame, width=400, justify="right", placeholder_text=placeholder)
        if secret:
            entry.configure(show="*")
            
        entry.pack(fill="x", padx=10, pady=(0, 10))
        self.fields[attr_name] = entry

    def toggle_sync(self):
        state = "normal" if self.sync_var.get() else "disabled"
        for entry in self.fields.values():
            entry.configure(state=state)

    def on_show(self):
        # Default values from context if present
        self.sync_var.set(self.wizard.context.get("git_enabled", False))
        self.fields["git_url"].insert(0, self.wizard.context.get("git_url", ""))
        self.fields["git_token"].insert(0, self.wizard.context.get("git_token", ""))
        self.fields["git_branch"].insert(0, self.wizard.context.get("git_branch", "main"))
        self.toggle_sync()

    def on_next(self) -> bool:
        self.wizard.context["git_enabled"] = self.sync_var.get()
        self.wizard.context["git_url"] = self.fields["git_url"].get()
        self.wizard.context["git_token"] = self.fields["git_token"].get()
        self.wizard.context["git_branch"] = self.fields["git_branch"].get() or "main"
        return True
