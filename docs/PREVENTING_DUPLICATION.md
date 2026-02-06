# Preventing File Duplication in Packages

## The Problem

When setting up package structures, it's common to accidentally **copy** files instead of creating **hard links**. This causes:

1. **Code duplication** - Same file exists in multiple locations
2. **Sync issues** - Changes to source aren't reflected in package
3. **Outdated packages** - Published packages have old code
4. **Maintenance burden** - Need to manually sync files

## The Solution: Hard Links

**Hard links** create multiple directory entries pointing to the same inode (file on disk).

### Benefits:
- ✅ **Single source of truth** - One file on disk
- ✅ **Automatic sync** - Changes reflected everywhere
- ✅ **No duplication** - Saves disk space
- ✅ **Git-friendly** - Tracked in one location

### How to Create Hard Links

```bash
# WRONG: Copying (creates duplicate)
cp server/start_server.py packages/cloudbrain-server/cloudbrain_server/start_server.py

# RIGHT: Hard linking (same file, multiple entries)
ln server/start_server.py packages/cloudbrain-server/cloudbrain_server/start_server.py
```

### Verify Hard Links

```bash
# Check link count (should be 2 or more)
ls -li packages/cloudbrain-server/cloudbrain_server/start_server.py

# Output:
# 259354070 -rw-r--r--@ 2 jk  staff  102103  6 Feb 22:52 start_server.py
#           ^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#           inode     link count (2 = hard linked)
```

### Find Duplicate Copies

```bash
# Find files with same inode but link count 1 (actual duplicates)
find . -type f -exec ls -li {} \; | awk '$3==1 {print "DUPLICATE:", $NF}'
```

## CloudBrain Package Structure

### Required Files for cloudbrain-server

The `cloudbrain-server` package needs ALL files that `start_server.py` imports:

**Core files:**
- `start_server.py` - Main server entry point
- `rest_api.py` - REST API endpoints
- `token_manager.py` - Token management
- `db_config.py` - Database configuration

**Dependencies:**
- `logging_config.py` - Logging setup
- `env_config.py` - Environment configuration
- `jwt_manager.py` - JWT token management
- `websocket_api.py` - WebSocket API

### How to Determine Which Files to Package

1. **Check imports** in main entry point:
   ```bash
   grep -E "^from |^import" start_server.py
   ```

2. **Recursively check dependencies**:
   ```bash
   # Check what each imported file needs
   grep -E "^from |^import" rest_api.py
   grep -E "^from |^import" token_manager.py
   # ... and so on
   ```

3. **Include all dependencies** in package

## Automated Setup

Use the provided `setup_packages.py` script:

```bash
python3 scripts/setup_packages.py
```

This script:
- ✅ Automatically creates hard links
- ✅ Verifies existing links
- ✅ Reports success/failure
- ✅ Prevents accidental copies

## Preventing AI Duplication

### For AI Assistants

When AI assistants create or modify package structures:

1. **Always use hard links** for code files
2. **Check link count** after operations
3. **Verify imports** are satisfied
4. **Run setup script** to ensure consistency

### Code Review Checklist

When reviewing package changes:

- [ ] All `.py` files are hard linked (link count >= 2)
- [ ] No duplicate copies exist (same inode, link count = 1)
- [ ] All imports are satisfied
- [ ] Package builds successfully
- [ ] Package imports work correctly

## Common Mistakes

### ❌ Mistake 1: Using `cp` instead of `ln`
```bash
cp server/start_server.py packages/cloudbrain-server/cloudbrain_server/start_server.py
```

### ✅ Fix: Use `ln`
```bash
ln server/start_server.py packages/cloudbrain-server/cloudbrain_server/start_server.py
```

### ❌ Mistake 2: Only including main files
Only including `start_server.py` but not its dependencies.

### ✅ Fix: Include all dependencies
Check imports and include all required files.

### ❌ Mistake 3: Not verifying hard links
Assuming files are hard linked without checking.

### ✅ Fix: Verify link count
```bash
ls -li packages/cloudbrain-server/cloudbrain_server/*.py
```

## Quick Reference

| Command | Purpose |
|----------|-----------|
| `ln source target` | Create hard link |
| `ls -li file` | Check inode and link count |
| `find . -type f -exec ls -li {} \;` | List all files with inodes |
| `python3 scripts/setup_packages.py` | Automated package setup |

## Summary

✅ **Use hard links** - Not copies
✅ **Verify link counts** - Should be >= 2
✅ **Include all dependencies** - Check imports
✅ **Use setup script** - Automate the process
✅ **Review packages** - Prevent duplication before publishing

By following these guidelines, you'll prevent code duplication and ensure packages stay in sync with source code.