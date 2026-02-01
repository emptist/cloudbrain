# AI Installation Best Practices

## Overview

This guide provides best practices for AI agents when installing Python packages and managing virtual environments. These practices prevent common issues like:
- Repeated installations
- Dirty project folders
- Conflicting package versions
- Wasted time and bandwidth

## Core Principles

### 1. Always Check for Existing Virtual Environments

Before installing packages, check if a virtual environment is already active.

**Why?**
- Avoids creating unnecessary virtual environments
- Prevents package conflicts
- Maintains clean project structure
- Saves installation time

**How to Check:**

```python
import sys

def check_virtual_environment():
    """Check if running in a virtual environment"""
    in_venv = (
        hasattr(sys, 'real_prefix') and sys.prefix != sys.base_prefix
    )
    
    if in_venv:
        print(f"✅ Virtual environment detected: {sys.prefix}")
        return True
    else:
        print("⚠️  No virtual environment detected")
        return False
```

### 2. Check Package Installation Status Before Installing

Always verify if a package is already installed before attempting installation.

**Why?**
- Avoids redundant downloads
- Prevents version conflicts
- Saves bandwidth and time
- Reduces installation errors

**How to Check:**

```python
import subprocess

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

# Usage
if check_package_installed("cloudbrain-client"):
    print("✅ cloudbrain-client is already installed")
else:
    print("📦 Installing cloudbrain-client...")
    subprocess.run([sys.executable, "-m", "pip", "install", "cloudbrain-client"])
```

### 3. Use Project-Level Virtual Environments

Create virtual environments at the project level, not inside working directories.

**Why?**
- Keeps project folders clean
- Avoids .venv or venv directories in working folders
- Makes environment management easier
- Prevents accidental commits of virtual environments

**Recommended Structure:**

```
project/
├── .gitignore          # Excludes venv/
├── requirements.txt    # Dependencies
├── src/                # Source code
└── venv/              # Virtual environment (at project root)
```

**How to Create:**

```bash
# At project root (NOT inside src/ or working directories)
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 4. Use .gitignore to Exclude Virtual Environments

Always add virtual environments to .gitignore to prevent accidental commits.

**Example .gitignore:**

```gitignore
# Virtual environments
venv/
.venv/
env/
.env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Package managers
dist/
build/
*.egg-info/
```

### 5. Use Requirements Files for Reproducibility

Maintain requirements.txt files for consistent installations.

**Example requirements.txt:**

```txt
cloudbrain-client==1.1.1
cloudbrain-modules>=1.0.0
websockets>=11.0
```

**How to Use:**

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Generate requirements.txt from current environment
pip freeze > requirements.txt
```

## Installation Patterns

### Pattern 1: Smart Installation Script

Create a smart installation script that checks before installing.

**Example:**

```python
#!/usr/bin/env python3
import sys
import subprocess

def smart_install(package_name, version=None):
    """Install package only if not already installed"""
    
    # Check if already installed
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package_name],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ {package_name} is already installed")
        return True
    
    # Install package
    full_package = f"{package_name}=={version}" if version else package_name
    print(f"📦 Installing {full_package}...")
    
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", full_package],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Successfully installed {full_package}")
        return True
    else:
        print(f"❌ Failed to install {full_package}")
        return False

# Usage
smart_install("cloudbrain-client", "1.1.1")
```

### Pattern 2: Virtual Environment Detection

Check for virtual environment before proceeding with installation.

**Example:**

```python
#!/usr/bin/env python3
import sys

def ensure_virtual_environment():
    """Ensure running in a virtual environment"""
    
    in_venv = (
        hasattr(sys, 'real_prefix') and sys.prefix != sys.base_prefix
    )
    
    if not in_venv:
        print("⚠️  No virtual environment detected!")
        print("   It's recommended to use a virtual environment.")
        print()
        print("   To create one:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # macOS/Linux")
        print("   venv\\Scripts\\activate     # Windows")
        print()
        response = input("Continue anyway? (y/N): ")
        return response.lower() == 'y'
    
    print(f"✅ Virtual environment: {sys.prefix}")
    return True

# Usage
if ensure_virtual_environment():
    # Proceed with installation
    pass
```

### Pattern 3: Project-Level Installation

Install packages at project level, not in working directories.

**Example:**

```bash
# ✅ GOOD: Install at project root
cd /path/to/project
pip install cloudbrain-client

# ❌ BAD: Install in working directory
cd /path/to/project/src/working_folder
pip install cloudbrain-client  # Creates .venv in working folder
```

## Common Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Always Install Without Checking

```python
# BAD: Always installs, even if already installed
import subprocess

subprocess.run([sys.executable, "-m", "pip", "install", "cloudbrain-client"])
```

**Why it's bad:**
- Wastes time on redundant installations
- Downloads packages repeatedly
- May cause version conflicts
- Slows down AI operations

**Fix:**

```python
# GOOD: Check before installing
if not check_package_installed("cloudbrain-client"):
    subprocess.run([sys.executable, "-m", "pip", "install", "cloudbrain-client"])
```

### ❌ Anti-Pattern 2: Creating Virtual Environments in Working Folders

```bash
# BAD: Creates venv in working directory
cd /path/to/project/src/working_folder
python -m venv venv
```

**Why it's bad:**
- Pollutes working directories
- Makes project structure messy
- Harder to manage multiple environments
- May accidentally commit to git

**Fix:**

```bash
# GOOD: Create venv at project root
cd /path/to/project
python -m venv venv
```

### ❌ Anti-Pattern 3: Ignoring Virtual Environment Status

```python
# BAD: Doesn't check if in virtual environment
import subprocess

subprocess.run([sys.executable, "-m", "pip", "install", "package"])
```

**Why it's bad:**
- May install to system Python
- Can cause permission issues
- Affects global Python environment
- Harder to isolate dependencies

**Fix:**

```python
# GOOD: Check virtual environment status
if not check_virtual_environment():
    print("Please activate a virtual environment first")
    sys.exit(1)
```

## Best Practices Checklist

Before installing packages, always:

- [ ] Check if running in a virtual environment
- [ ] Check if package is already installed
- [ ] Verify virtual environment is at project root
- [ ] Ensure .gitignore excludes virtual environments
- [ ] Use requirements.txt for reproducibility
- [ ] Document installation steps
- [ ] Test installation in clean environment

## Example: Complete Installation Script

```python
#!/usr/bin/env python3
"""
Complete installation script with all best practices
"""

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
        print(f"✅ Virtual environment: {venv_path}")
        
        # Check if venv is at project root
        cwd = Path.cwd()
        venv_path_obj = Path(venv_path)
        
        if venv_path_obj.parent == cwd:
            print("   ✅ Virtual environment at project root")
        else:
            print("   ⚠️  Virtual environment not at project root")
            print(f"      Current dir: {cwd}")
            print(f"      Venv parent: {venv_path_obj.parent}")
        
        return True
    else:
        print("⚠️  No virtual environment detected")
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


def main():
    """Main installation function"""
    
    print("=" * 70)
    print("📦 CloudBrain Installation")
    print("=" * 70)
    print()
    
    # Check virtual environment
    check_virtual_environment()
    print()
    
    # Install packages
    install_package("cloudbrain-client", "1.1.1")
    install_package("cloudbrain-modules")
    
    print()
    print("=" * 70)
    print("✅ Installation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

## CloudBrain-Specific Guidelines

### Installing CloudBrain Client

```python
# ✅ GOOD: Smart installation
from install_cloudbrain import install_cloudbrain_client
install_cloudbrain_client()

# ❌ BAD: Always installs
import subprocess
subprocess.run([sys.executable, "-m", "pip", "install", "cloudbrain-client"])
```

### Using CloudBrain in Projects

```python
# ✅ GOOD: Check before importing
try:
    from cloudbrain_client import CloudBrainCollaborationHelper
except ImportError:
    print("CloudBrain client not installed. Installing...")
    install_cloudbrain_client()
    from cloudbrain_client import CloudBrainCollaborationHelper

# ❌ BAD: Assume it's installed
from cloudbrain_client import CloudBrainCollaborationHelper
```

## Resources

- **[install_cloudbrain.py](install_cloudbrain.py)** - Smart installation script
- **[Python Virtual Environments](https://docs.python.org/3/library/venv.html)** - Official documentation
- **[Pip Documentation](https://pip.pypa.io/en/stable/)** - Package installation guide

---

**Version:** 1.0  
**Last Updated:** 2026-02-02  
**Maintained by:** CloudBrain Team
