#!/usr/bin/env python3
"""
Autonomous AI Agent Setup Script
Checks for virtual environment, server, and installs dependencies
"""

import os
import sys
import subprocess
import socket
from pathlib import Path

def print_step(step_num, message):
    print(f"\n📦 Step {step_num}: {message}")

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def check_server_running(host="127.0.0.1", port=8766):
    """Check if CloudBrain server is running"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result == 0
    except:
        return False

def main():
    print("🤖 Autonomous AI Agent Setup")
    print("=" * 40)
    
    # Step 1: Check virtual environment
    print_step(1, "Checking virtual environment...")
    
    venv_paths = [Path("./.venv"), Path("../.venv")]
    venv_found = False
    
    for venv_path in venv_paths:
        if venv_path.exists():
            print_success(f"Found virtual environment at {venv_path}")
            activate_script = venv_path / ("Scripts/activate" if os.name == 'nt' else "bin/activate")
            print(f"Activate with: source {activate_script}")
            venv_found = True
            break
    
    if not venv_found:
        print_warning("No virtual environment found at ./.venv or ../.venv")
        print("Creating virtual environment at ./.venv...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print_success("Virtual environment created at ./.venv")
        print(f"Activate with: source ./.venv/bin/activate")
    
    # Step 2: Check for running server
    print_step(2, "Checking for CloudBrain server...")
    
    if check_server_running():
        print_success("CloudBrain server is running on port 8766")
        print("You can connect to the existing server!")
    else:
        print_warning("No CloudBrain server detected on port 8766")
        print("Please start the CloudBrain server first")
        print("Or check if it's running on a different port")
        
        response = input("\nDo you want to continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print_error("Setup cancelled")
            sys.exit(1)
    
    # Step 3: Install package
    print_step(3, "Installing cloudbrain-client...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "cloudbrain-client==1.1.1"], check=True)
        print_success("Package installed successfully")
    except subprocess.CalledProcessError:
        print_error("Failed to install package")
        sys.exit(1)
    
    # Step 4: Check if code exists
    print_step(4, "Checking for autonomous agent code...")
    
    agent_file = Path("autonomous_ai_agent_esperanto.py")
    if agent_file.exists():
        print_success("Found autonomous_ai_agent_esperanto.py")
    else:
        print_warning("autonomous_ai_agent_esperanto.py not found")
        print("Please search CloudBrain for 'autonomous agent code' and save it")
        input("\nPress Enter after you've saved the code...")
    
    # Step 5: Run the agent
    print_step(5, "Running the autonomous agent...")
    
    try:
        subprocess.run([sys.executable, "autonomous_ai_agent_esperanto.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Agent stopped by user")
    except Exception as e:
        print_error(f"Error running agent: {e}")

if __name__ == "__main__":
    main()
