import customtkinter as ct
from typing import List, Type, Dict
from pathlib import Path

class WizardStep(ct.CTkFrame):
    def __init__(self, master, wizard):
        super().__init__(master)
        self.wizard = wizard
        self.pack_fill = "both"
        self.pack_expand = True

    def on_show(self):
        """Called when the step is displayed."""
        pass

    def on_next(self) -> bool:
        """Called when Next is clicked. Return True to proceed."""
        return True

class ConversionWizard(ct.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Content
        self.grid_rowconfigure(1, weight=0) # Navigation

        self.steps: List[Type[WizardStep]] = []
        self.step_instances: Dict[int, WizardStep] = {}
        self.current_step_idx = 0
        
        self.content_container = ct.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.nav_frame = ct.CTkFrame(self, height=60)
        self.nav_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        self.prev_btn = ct.CTkButton(self.nav_frame, text="Back", command=self.prev_step)
        self.prev_btn.pack(side="left", padx=10)
        
        self.next_btn = ct.CTkButton(self.nav_frame, text="Next", command=self.next_step)
        self.next_btn.pack(side="right", padx=10)
        
        # Shared data
        self.context = {
            "main_tex": None,
            "book": None,
            "output_root": Path.cwd() / "output"
        }

    def add_steps(self, step_classes: List[Type[WizardStep]]):
        self.steps = step_classes
        self.show_step(0)

    def show_step(self, idx: int):
        if idx not in self.step_instances:
            self.step_instances[idx] = self.steps[idx](self.content_container, self)
        
        # Hide current
        for inst in self.step_instances.values():
            inst.pack_forget()
            
        # Show new
        step = self.step_instances[idx]
        step.pack(fill="both", expand=True)
        step.on_show()
        
        self.current_step_idx = idx
        self.update_navigation()

    def next_step(self):
        if self.step_instances[self.current_step_idx].on_next():
            if self.current_step_idx < len(self.steps) - 1:
                self.show_step(self.current_step_idx + 1)
            else:
                self.finish()

    def prev_step(self):
        if self.current_step_idx > 0:
            self.show_step(self.current_step_idx - 1)

    def update_navigation(self):
        self.prev_btn.configure(state="normal" if self.current_step_idx > 0 else "disabled")
        if self.current_step_idx == len(self.steps) - 1:
            self.next_btn.configure(text="Convert & Finish")
        else:
            self.next_btn.configure(text="Next")

    def finish(self):
        print("Starting conversion pipeline...")
        main_tex = self.context.get("main_tex")
        output_root = self.context.get("output_root")
        
        if not main_tex or not output_root:
            print("Error: Missing configuration.")
            return

        # Disable button to prevent double-click
        self.next_btn.configure(state="disabled", text="Processing...")
        self.update() # Force UI update

        try:
            from core.orchestrator import ConversionOrchestrator
            
            orchestrator = ConversionOrchestrator(main_tex, output_root)
            orchestrator.run()
            
            # --- Git Integration ---
            self.context["git_pushed"] = False
            if self.context.get("git_enabled", False):
                from git.manager import GitManager
                git_mgr = GitManager(output_root)
                
                if git_mgr.is_dirty():
                    git_mgr.add_all()
                    git_mgr.commit(f"Add converted content: {self.context['book'].metadata.title}")
                    
                    # Prepare Authenticated URL
                    git_url = self.context.get("git_url")
                    git_token = self.context.get("git_token")
                    git_branch = self.context.get("git_branch", "main")
                    
                    if git_url and git_token and git_url.startswith("https://"):
                        # Inject token into URL: https://token@github.com/...
                        auth_url = git_url.replace("https://", f"https://{git_token}@")
                    else:
                        auth_url = git_url

                    if git_mgr.push(remote_url=auth_url, branch=git_branch):
                        self.context["git_pushed"] = True
            
            # Transition to Success Step (the next step in the list)
            if self.current_step_idx < len(self.steps) - 1:
                self.show_step(self.current_step_idx + 1)
            else:
                from tkinter import messagebox
                messagebox.showinfo("Success", "Conversion completed successfully!")
                
        except Exception as e:
            print(f"Conversion failed: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
            self.next_btn.configure(state="normal", text="Convert & Finish")
