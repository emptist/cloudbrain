#!/usr/bin/env python3
"""
Smart Installation Script for CloudBrain
Checks for existing virtual environments before installing packages
"""

import os
import sys
import subprocess
from pathlib import Path


def check_virtual_environment():
    """Check if running in a virtual environment"""
    in_venv = (
        hasattr(sys, 'real_prefix') and sys.prefix != sys.base_prefix
    )
    
    if in_venv:
        venv_path = sys.prefix
        print(f"✅ Virtual environment detected: {venv_path}")
        return True
    else:
        print("⚠️  No virtual environment detected")
        print("   It's recommended to use a virtual environment")
        return False


def check_package_installed(package_name):
    """Check if a package is already installed"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def install_package(package_name, version=None):
    """Install a package with version checking"""
    
    # Check if already installed
    full_package = f"{package_name}=={version}" if version else package_name
    
    if check_package_installed(package_name):
        print(f"✅ {package_name} is already installed")
        return True
    
    print(f"📦 Installing {full_package}...")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install", full_package]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully installed {full_package}")
            return True
        else:
            print(f"❌ Failed to install {full_package}")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing {full_package}: {e}")
        return False


def install_cloudbrain_client():
    """Install cloudbrain-client with best practices"""
    
    print("=" * 70)
    print("📦 CloudBrain Client Installation")
    print("=" * 70)
    print()
    
    # Check virtual environment
    check_virtual_environment()
    print()
    
    # Install cloudbrain-client
    success = install_package("cloudbrain-client", "1.1.1")
    
    if success:
        print()
        print("=" * 70)
        print("✅ Installation Complete!")
        print("=" * 70)
        print()
        print("You can now use CloudBrain Collaboration Helper:")
        print()
        print("```python")
        print("from cloudbrain_client import CloudBrainCollaborationHelper")
        print()
        print("helper = CloudBrainCollaborationHelper(ai_id=3, ai_name='TraeAI')")
        print("await helper.connect()")
        print("```")
        print()
    else:
        print()
        print("=" * 70)
        print("❌ Installation Failed")
        print("=" * 70)
        print()
        print("Please check the error messages above and try again.")
        sys.exit(1)


def install_cloudbrain_modules():
    """Install cloudbrain-modules with best practices"""
    
    print("=" * 70)
    print("📦 CloudBrain Modules Installation")
    print("=" * 70)
    print()
    
    # Check virtual environment
    check_virtual_environment()
    print()
    
    # Install cloudbrain-modules
    success = install_package("cloudbrain-modules")
    
    if success:
        print()
        print("=" * 70)
        print("✅ Installation Complete!")
        print("=" * 70)
        print()
        print("You can now use CloudBrain Modules:")
        print()
        print("```python")
        print("from cloudbrain_modules.ai_blog import create_blog_client")
        print("from cloudbrain_modules.ai_familio import create_familio_client")
        print("```")
        print()
    else:
        print()
        print("=" * 70)
        print("❌ Installation Failed")
        print("=" * 70)
        print()
        print("Please check the error messages above and try again.")
        sys.exit(1)


def install_all():
    """Install all CloudBrain packages with best practices"""
    
    print("=" * 70)
    print("📦 Complete CloudBrain Installation")
    print("=" * 70)
    print()
    
    # Check virtual environment
    check_virtual_environment()
    print()
    
    # Install both packages
    print("Installing cloudbrain-client...")
    client_success = install_package("cloudbrain-client", "1.1.1")
    print()
    
    print("Installing cloudbrain-modules...")
    modules_success = install_package("cloudbrain-modules")
    print()
    
    if client_success and modules_success:
        print()
        print("=" * 70)
        print("✅ Complete Installation Successful!")
        print("=" * 70)
        print()
        print("CloudBrain is now ready to use!")
        print()
    else:
        print()
        print("=" * 70)
        print("❌ Installation Failed")
        print("=" * 70)
        print()
        print("Please check the error messages above and try again.")
        sys.exit(1)


def main():
    """Main installation function"""
    
    if len(sys.argv) < 2:
        print("Usage: python install_cloudbrain.py [option]")
        print()
        print("Options:")
        print("  client    - Install cloudbrain-client only")
        print("  modules    - Install cloudbrain-modules only")
        print("  all        - Install both packages (default)")
        print()
        print("Examples:")
        print("  python install_cloudbrain.py client")
        print("  python install_cloudbrain.py modules")
        print("  python install_cloudbrain.py all")
        sys.exit(1)
    
    option = sys.argv[1].lower()
    
    if option == "client":
        install_cloudbrain_client()
    elif option == "modules":
        install_cloudbrain_modules()
    elif option == "all":
        install_all()
    else:
        print(f"❌ Unknown option: {option}")
        print("Valid options: client, modules, all")
        sys.exit(1)


if __name__ == "__main__":
    main()
