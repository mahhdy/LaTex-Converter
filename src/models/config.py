from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class PresetConfig:
    author: str
    categories: List[str]
    tags: List[str]

@dataclass
class GitConfig:
    enabled: bool = False
    repo_path: str = ""
    repo_url: str = ""
    branch: str = "main"
    auth_method: str = "https"  # 'https' or 'ssh'
    username: str = ""
    token: str = ""  # Should be handled via keyring in actual usage
    ssh_key_path: str = ""
    auto_push: bool = False
    commit_message_template: str = "Add book: {title}"

@dataclass
class AppConfig:
    last_input_dir: str = ""
    last_output_dir: str = ""
    default_author: str = "مهدی سالم"
    default_lang: str = "fa"
    presets: Dict[str, PresetConfig] = field(default_factory=dict)
    git: GitConfig = field(default_factory=lambda: GitConfig())
    ui_language: str = "fa"
