import os
from git import Repo, GitCommandError
from pathlib import Path
from typing import Optional

class GitManager:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.repo: Optional[Repo] = None
        
        if (repo_path / ".git").exists():
            self.repo = Repo(repo_path)
        else:
            self.repo = Repo.init(repo_path)

    def add_all(self):
        self.repo.git.add(A=True)

    def commit(self, message: str):
        try:
            self.repo.index.commit(message)
            return True
        except Exception as e:
            print(f"Commit failed: {e}")
            return False

    def push(self, remote_url: Optional[str] = None, branch: str = "main"):
        try:
            if remote_url:
                if "origin" in self.repo.remotes:
                    origin = self.repo.remote("origin")
                    origin.set_url(remote_url)
                else:
                    self.repo.create_remote("origin", remote_url)
            
            origin = self.repo.remote("origin")
            origin.push(branch)
            return True
        except GitCommandError as e:
            print(f"Push failed: {e}")
            return False
        except Exception as e:
            print(f"Error during push: {e}")
            return False

    def is_dirty(self) -> bool:
        return self.repo.is_dirty(untracked_files=True)
