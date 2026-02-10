import os
import sys
from pathlib import Path

# Add the 'src' directory to sys.path to allow absolute imports of packages
# This ensures that 'gui', 'core', 'models', etc. are found regardless of the working directory.
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import customtkinter as ct
from gui.wizard import ConversionWizard
from gui.steps.analysis import AnalysisStep
from gui.steps.metadata import MetadataStep
from gui.steps.review import ReviewStep
from gui.steps.repository import RepositoryStep
from gui.steps.success import SuccessStep

class LatexConverterApp(ct.CTk):
    def __init__(self):
        super().__init__()

        self.title("LaTeX to Astro Converter")
        self.geometry("900x700")
        
        # Set theme
        ct.set_appearance_mode("dark")
        ct.set_default_color_theme("blue")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize Wizard
        self.wizard = ConversionWizard(self)
        self.wizard.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Add Steps
        self.wizard.add_steps([AnalysisStep, MetadataStep, ReviewStep, RepositoryStep, SuccessStep])

if __name__ == "__main__":
    app = LatexConverterApp()
    app.mainloop()
