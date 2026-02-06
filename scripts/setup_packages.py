#!/usr/bin/env python3
"""
Package Setup Script - Creates hard links for package files

This script ensures that package files are hard linked to source files
instead of being copied, preventing code duplication and sync issues.

Usage:
    python3 setup_packages.py
"""

import os
import sys
from pathlib import Path

# Package configuration
PACKAGES = {
    "cloudbrain-server": {
        "source_dir": "server",
        "package_dir": "packages/cloudbrain-server/cloudbrain_server",
        "files": [
            "db_config.py",
            "rest_api.py",
            "start_server.py",
            "token_manager.py",
            "logging_config.py",
            "env_config.py",
            "jwt_manager.py",
            "websocket_api.py",
        ]
    },
}

def create_hard_link(source_path: Path, target_path: Path):
    """Create a hard link from source to target"""
    try:
        if target_path.exists():
            if target_path.stat().st_ino == source_path.stat().st_ino:
                print(f"✅ Already hard linked: {target_path.name}")
                return True
            print(f"🔄 Removing existing file: {target_path.name}")
            target_path.unlink()
        
        os.link(str(source_path), str(target_path))
        print(f"✅ Created hard link: {target_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to create hard link for {target_path.name}: {e}")
        return False

def setup_package(package_name: str, config: dict):
    """Setup a single package"""
    print(f"\n{'='*60}")
    print(f"📦 Setting up {package_name}")
    print(f"{'='*60}")
    
    source_dir = Path(config["source_dir"])
    package_dir = Path(config["package_dir"])
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return False
    
    package_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    for file_name in config["files"]:
        source_path = source_dir / file_name
        target_path = package_dir / file_name
        
        if not source_path.exists():
            print(f"⚠️  Source file not found: {source_path}")
            continue
        
        if create_hard_link(source_path, target_path):
            success_count += 1
    
    print(f"\n📊 Summary: {success_count}/{len(config['files'])} files hard linked")
    return success_count == len(config["files"])

def main():
    """Main setup function"""
    print("🔗 CloudBrain Package Setup - Hard Link Manager")
    print("="*60)
    
    total_packages = len(PACKAGES)
    success_packages = 0
    
    for package_name, config in PACKAGES.items():
        if setup_package(package_name, config):
            success_packages += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Final Summary: {success_packages}/{total_packages} packages setup")
    print(f"{'='*60}")
    
    if success_packages == total_packages:
        print("\n✅ All packages setup successfully!")
        return 0
    else:
        print(f"\n⚠️  {total_packages - success_packages} package(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())