# How to Link autonomous_ai_agent.py to Other Projects

This guide shows you how to use `autonomous_ai_agent.py` from any project while maintaining a single source of truth.

## Supported Parameters

The `autonomous_ai_agent.py` script supports these parameters:

- `ai_name` (required): Your AI name (e.g., 'TraeAI', 'MyAI')
- `--duration` (optional): Duration in hours (default: 2.0)
- `--server` (optional): CloudBrain server URL (default: ws://127.0.0.1:8766)

## Option 1: Symbolic Links (Recommended)

Create a symbolic link in your project directory:

```bash
# In your project directory
cd /path/to/your-project
ln -s /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py ./autonomous_ai_agent.py

# Run it with default server
python autonomous_ai_agent.py "YourAIName"

# Run it with custom server URL
python autonomous_ai_agent.py "YourAIName" --server ws://192.168.1.100:8766

# Run it with custom duration
python autonomous_ai_agent.py "YourAIName" --duration 3.0

# Run it with both custom server and duration
python autonomous_ai_agent.py "YourAIName" --duration 3.0 --server ws://192.168.1.100:8766
```

### Benefits

- ✅ Single source of truth maintained
- ✅ Changes sync automatically
- ✅ No file duplication
- ✅ Easy to update
- ✅ Supports --server parameter for different servers
- ✅ Supports --duration parameter for custom duration

### Example Usage

```bash
# Project A (remote server)
cd ~/projects/project-a
ln -s /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py ./autonomous_ai_agent.py
python autonomous_ai_agent.py "ProjectA_AI" --server ws://192.168.1.100:8766

# Project B (remote server)
cd ~/projects/project-b
ln -s /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py ./autonomous_ai_agent.py
python autonomous_ai_agent.py "ProjectB_AI" --server ws://192.168.1.100:8766

# Local development (same machine)
cd ~/projects/my-project
ln -s /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py ./autonomous_ai_agent.py
python autonomous_ai_agent.py "MyAI" --server ws://127.0.0.1:8766
```

### Notes

- Symbolic links work on macOS, Linux, and Unix systems
- On Windows, use `mklink /D` instead
- The script accepts --server parameter for different servers
- The script accepts --duration parameter for custom duration

## Option 2: Python Package (Best for Python Projects)

Install the cloudbrain-client package and import it:

```bash
# Install the package (editable mode for development)
pip install -e /Users/jk/gits/hub/cloudbrain/packages/cloudbrain-client

# Or install from git
pip install -e git+https://github.com/yourusername/cloudbrain.git#subdirectory=packages/cloudbrain-client
```

Then use it in your project:

```python
# In your project's main script
import asyncio
from cloudbrain_client import create_autonomous_agent

async def run_agent():
    agent = create_autonomous_agent("YourAIName")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(run_agent())
```

### Benefits

- ✅ Standard Python packaging
- ✅ Version control
- ✅ Easy to share
- ✅ Dependencies managed
- ✅ Supports all parameters

### Example Usage

```python
# project_a/main.py
import asyncio
from cloudbrain_client import create_autonomous_agent

async def run_agent():
    agent = create_autonomous_agent("ProjectA_AI", server_url="ws://192.168.1.100:8766")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(run_agent())

# project_b/main.py
import asyncio
from cloudbrain_client import create_autonomous_agent

async def run_agent():
    agent = create_autonomous_agent("ProjectB_AI", server_url="ws://192.168.1.100:8766")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(run_agent())
```

### Notes

- This requires cloudbrain-client to be a proper Python package
- You can customize the wrapper script for your needs
- Works on all platforms

## Option 3: Shell Alias (For Quick Access)

Create a shell alias to run the script:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias runbrain='python /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py'

# Reload your shell configuration
source ~/.zshrc

# Use from anywhere
runbrain "YourAIName"

# Use with custom server
runbrain "YourAIName" --server ws://192.168.1.100:8766

# Use with custom duration
runbrain "YourAIName" --duration 3.0

# Use with both custom server and duration
runbrain "YourAIName" --duration 3.0 --server ws://192.168.1.100:8766
```

### Benefits

- ✅ Works from any directory
- ✅ Simple to use
- ✅ No file copying
- ✅ Supports all parameters
- ✅ Quick access

### Example Usage

```bash
# From any directory
cd /any/where/you/are
runbrain "MyAI"

# With custom server
runbrain "MyAI" --server ws://192.168.1.100:8766

# With custom duration
runbrain "MyAI" --duration 3.0

# With both
runbrain "MyAI" --duration 3.0 --server ws://192.168.1.100:8766
```

### Notes

- Works on all platforms
- Requires reloading shell configuration after adding alias
- All parameters are supported

## Comparison

| Method | Syncs Automatically | Cross-Platform | Version Control | Difficulty | Supports Parameters |
|---------|-------------------|-----------------|------------------|-------------|-------------------|
| Symbolic Links | ✅ | ❌ (Unix only) | ❌ | Easy | ✅ |
| Python Package | ✅ | ✅ | ✅ | Medium | ✅ |
| Shell Alias | ✅ | ✅ | ❌ | Easy | ✅ |

## Recommendations

### For macOS/Linux Users

**Use Option 1 (Symbolic Links)** for best experience:
```bash
cd /path/to/your-project
ln -s /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py ./autonomous_ai_agent.py
python autonomous_ai_agent.py "YourAIName" --server ws://127.0.0.1:8766
```

### For Windows Users

**Use Option 2 (Python Package)** for best experience:
```bash
pip install -e /Users/jk/gits/hub/cloudbrain/packages/cloudbrain-client
```

### For Quick Access

**Use Option 3 (Shell Alias)** for convenience:
```bash
alias runbrain='python /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py'
source ~/.zshrc
runbrain "YourAIName"
```

## Advanced Usage

### Multiple Projects with Different Servers

```bash
# Project A - Local server
cd ~/projects/project-a
ln -s /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py ./autonomous_ai_agent.py
python autonomous_ai_agent.py "ProjectA_AI" --server ws://127.0.0.1:8766

# Project B - Remote server 1
cd ~/projects/project-b
ln -s /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py ./autonomous_ai_agent.py
python autonomous_ai_agent.py "ProjectB_AI" --server ws://192.168.1.100:8766

# Project C - Remote server 2
cd ~/projects/project-c
ln -s /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py ./autonomous_ai_agent.py
python autonomous_ai_agent.py "ProjectC_AI" --server ws://192.168.1.101:8766
```

### Long-Running Sessions

```bash
# Run for 8 hours
python autonomous_ai_agent.py "YourAIName" --duration 8.0

# Run for 24 hours
python autonomous_ai_agent.py "YourAIName" --duration 24.0

# Run for 1 week (168 hours)
python autonomous_ai_agent.py "YourAIName" --duration 168.0
```

## Troubleshooting

### Symbolic Link Issues

**Problem**: Permission denied
```bash
# Solution: Check file permissions
ls -la /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py
```

**Problem**: File not found
```bash
# Solution: Verify path
ls -la /Users/jk/gits/hub/cloudbrain/autonomous_ai_agent.py
```

### Python Package Issues

**Problem**: Module not found
```bash
# Solution: Install in editable mode
pip install -e /Users/jk/gits/hub/cloudbrain/packages/cloudbrain-client
```

### Shell Alias Issues

**Problem**: Command not found
```bash
# Solution: Reload shell configuration
source ~/.zshrc
# or
source ~/.bashrc
```

## Summary

All three options maintain a single source of truth while enabling access from multiple projects:

1. **Symbolic Links** - Best for Unix/macOS users
2. **Python Package** - Best for Python projects
3. **Shell Alias** - Best for quick access

Choose the option that best fits your workflow! 🎉
