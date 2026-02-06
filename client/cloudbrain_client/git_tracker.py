import subprocess
from typing import Dict, List, Optional

class GitTracker:
    """Track git changes for brain state"""
    
    def __init__(self):
        self.repo_path = None
    
    def get_status(self) -> Dict[str, List[str]]:
        """Get git status
        
        Returns:
            Dict with:
                - modified: List of modified files
                - added: List of added files
                - deleted: List of deleted files
                - output: Full git status output
        """
        try:
            output = subprocess.check_output(
                ['git', 'status', '--porcelain'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            modified = []
            added = []
            deleted = []
            
            for line in output.split('\n'):
                if not line:
                    continue
                    
                status = line[:2]
                filepath = line[3:]
                
                if 'M' in status:
                    modified.append(filepath)
                elif 'A' in status:
                    added.append(filepath)
                elif 'D' in status:
                    deleted.append(filepath)
            
            return {
                'modified': modified,
                'added': added,
                'deleted': deleted,
                'output': output
            }
            
        except Exception as e:
            return {
                'modified': [],
                'added': [],
                'deleted': [],
                'output': f'no git: {str(e)}'
            }
    
    def get_git_hash(self) -> str:
        """Get current git commit hash
        
        Returns:
            7-character git hash, or 'unknown' if not in git repo
        """
        try:
            output = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            return output[:7]
        except:
            return 'unknown'
    
    def get_project_id(self) -> str:
        """Get unique project ID (remote URL + git hash)
        
        Returns:
            Unique project identifier, or 'default' if not in git repo
        """
        try:
            remote_url = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            if remote_url:
                git_hash = self.get_git_hash()
                return f"{remote_url}#{git_hash}"
            else:
                repo_path = subprocess.check_output(
                    ['git', 'rev-parse', '--show-toplevel'],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                return repo_path
        except:
            return 'default'
    
    def get_project_name(self) -> str:
        """Get project name for display
        
        Returns:
            Project name, or 'default' if not in git repo
        """
        try:
            repo_path = subprocess.check_output(
                ['git', 'rev-parse', '--show-toplevel'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            return repo_path.split('/')[-1]
        except:
            return 'default'
