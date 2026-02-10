import shutil
from pathlib import Path
from typing import List, Dict, Optional
from models.book import ImageInfo

class ImageProcessor:
    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.graphics_paths: List[Path] = [source_dir]
        self.common_subdirs = ['images', 'figures', 'figs', 'img']

    def set_graphics_paths(self, paths: List[str]):
        """Sets additional paths to search for images."""
        for p in paths:
            path = self.source_dir / p.strip('{}')
            if path.exists():
                self.graphics_paths.append(path)

    def find_image(self, name: str) -> Optional[Path]:
        """Searches for an image file in all registered graphics paths and root."""
        extensions = ['', '.png', '.jpg', '.jpeg', '.pdf', '.eps', '.svg']
        
        # Search in all graphics paths
        for base_path in self.graphics_paths:
            for ext in extensions:
                img_path = base_path / (name + ext)
                if img_path.exists() and img_path.is_file():
                    return img_path
            
            # Search in common subdirectories of this path
            for subdir in self.common_subdirs:
                subdir_path = base_path / subdir
                if subdir_path.exists():
                    for ext in extensions:
                        img_path = subdir_path / (name + ext)
                        if img_path.exists() and img_path.is_file():
                            return img_path
                            
        return None

    def process_image(self, img_info: ImageInfo) -> bool:
        """Copies or converts the image to the output directory."""
        if not img_info.original_path.exists():
            return False
            
        # Ensure output directory exists
        img_info.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle conversion if needed
        if img_info.needs_conversion:
            return self._convert_image(img_info)
        
        # Simple copy
        try:
            shutil.copy2(img_info.original_path, img_info.output_path)
            return True
        except Exception:
            return False

    def _convert_image(self, img_info: ImageInfo) -> bool:
        """Converts PDF/EPS to PNG. (Placeholder for actual conversion logic)"""
        # In a real implementation, this would use subprocess to call pdftoppm or magick
        # For now, we'll just copy if it's already a supported format or skip
        print(f"Warning: Conversion for {img_info.original_path.suffix} not fully implemented. Copying instead.")
        try:
            shutil.copy2(img_info.original_path, img_info.output_path)
            return True
        except Exception:
            return False
