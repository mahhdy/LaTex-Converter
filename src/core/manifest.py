import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

class ManifestGenerator:
    def __init__(self, output_root: Path):
        self.output_root = output_root
        self.data: Dict[str, Any] = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "files": [],
            "metadata": {}
        }

    def set_metadata(self, metadata: Dict[str, Any]):
        self.data["metadata"] = metadata

    def add_file(self, type: str, source: str, target: str):
        self.data["files"].append({
            "type": type,
            "source": source,
            "target": target
        })

    def save(self):
        manifest_path = self.output_root / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
