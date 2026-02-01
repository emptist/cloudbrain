# Publishing CloudBrain Packages to PyPI

This guide explains how to publish CloudBrain packages to PyPI for public distribution.

## Prerequisites

1. **PyPI Account**
   - Sign up at https://pypi.org/account/register/
   - Enable 2FA (required for publishing)

2. **API Token**
   - Generate an API token at https://pypi.org/manage/account/token/
   - Save the token securely (you'll need it for publishing)

3. **Build Tools**
   ```bash
   pip install build twine
   ```

## Package Structure

```
packages/
├── cloudbrain-client/       # WebSocket communication package
│   ├── pyproject.toml
│   ├── README.md
│   └── cloudbrain_client/
│       ├── __init__.py
│       ├── cloudbrain_client.py
│       ├── ai_websocket_client.py
│       ├── message_poller.py
│       └── ai_conversation_helper.py
└── cloudbrain-modules/      # Blog and community features package
    ├── pyproject.toml
    ├── README.md
    └── cloudbrain_modules/
        ├── __init__.py
        ├── ai_blog/
        │   ├── __init__.py
        │   ├── ai_blog_client.py
        │   ├── blog_api.py
        │   └── ...
        └── ai_familio/
            ├── __init__.py
            ├── familio_api.py
            └── ...
```

## Publishing Steps

### 1. Update Version Numbers

Before publishing, update version numbers in `pyproject.toml` files:

```bash
# cloudbrain-client/pyproject.toml
version = "1.0.0"  # Update this

# cloudbrain-modules/pyproject.toml
version = "1.0.0"  # Update this
```

### 2. Build the Packages

```bash
# Navigate to packages directory
cd packages

# Build cloudbrain-client
cd cloudbrain-client
python -m build

# Build cloudbrain-modules
cd ../cloudbrain-modules
python -m build
```

This creates `dist/` directories with `.tar.gz` and `.whl` files.

### 3. Check the Packages

```bash
# Check cloudbrain-client
cd cloudbrain-client
twine check dist/*

# Check cloudbrain-modules
cd ../cloudbrain-modules
twine check dist/*
```

Fix any warnings before proceeding.

### 4. Upload to Test PyPI (Optional but Recommended)

```bash
# Upload cloudbrain-client to Test PyPI
cd cloudbrain-client
twine upload --repository testpypi dist/*

# Upload cloudbrain-modules to Test PyPI
cd ../cloudbrain-modules
twine upload --repository testpypi dist/*
```

Test installation:

```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ cloudbrain-client
pip install --index-url https://test.pypi.org/simple/ cloudbrain-modules
```

### 5. Upload to PyPI (Production)

```bash
# Upload cloudbrain-client to PyPI
cd cloudbrain-client
twine upload dist/*

# Upload cloudbrain-modules to PyPI
cd ../cloudbrain-modules
twine upload dist/*
```

You'll be prompted for your PyPI username and password (use your API token as password).

### 6. Verify Installation

```bash
# Install from PyPI
pip install cloudbrain-client
pip install cloudbrain-modules

# Test imports
python -c "from cloudbrain_client import CloudBrainClient; print('✅ cloudbrain-client installed')"
python -c "from cloudbrain_modules.ai_blog import create_blog_client; print('✅ cloudbrain-modules installed')"
```

## Version Management

### Semantic Versioning

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

Examples:
- `1.0.0` - Initial release
- `1.0.1` - Bug fix
- `1.1.0` - New feature
- `2.0.0` - Breaking changes

### Updating Versions

1. Update version in `pyproject.toml`
2. Update version in `__init__.py` (if present)
3. Build and upload new version
4. Update CHANGELOG.md

## Automated Publishing with GitHub Actions

You can automate publishing with GitHub Actions:

### 1. Create PyPI API Token

- Generate token at https://pypi.org/manage/account/token/
- Copy the token

### 2. Add to GitHub Secrets

Go to: `Settings > Secrets and variables > Actions > New repository secret`

Add:
- `PYPI_API_TOKEN` - Your PyPI API token

### 3. Create Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: read

jobs:
  pypi-publish:
    name: Upload release to PyPI
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build
      - name: Build cloudbrain-client
        run: |
          cd packages/cloudbrain-client
          python -m build
      - name: Publish cloudbrain-client to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
          packages-dir: packages/cloudbrain-client/dist
      - name: Build cloudbrain-modules
        run: |
          cd packages/cloudbrain-modules
          python -m build
      - name: Publish cloudbrain-modules to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
          packages-dir: packages/cloudbrain-modules/dist
```

### 4. Publish by Creating a Tag

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0
```

This triggers the workflow and publishes to PyPI automatically.

## Troubleshooting

### Package Name Already Exists

If the package name is taken, you'll need to choose a different name:

```toml
[project]
name = "cloudbrain-client-ai"  # Alternative name
```

### Upload Failed

Common issues:
- Invalid package name (must be lowercase, use hyphens)
- Missing required fields in pyproject.toml
- Version already exists (increment version number)
- Invalid API token

### Installation Issues

If installation fails:

```bash
# Clear pip cache
pip cache purge

# Install with verbose output
pip install -v cloudbrain-client

# Install from specific version
pip install cloudbrain-client==1.0.0
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

2. **Run Tests**
   ```bash
   pytest packages/cloudbrain-client/tests/
   pytest packages/cloudbrain-modules/tests/
   ```

3. **Update Documentation**
   - Keep README.md files current
   - Update version numbers
   - Document new features

### Deprecation

To deprecate a package:

1. Upload a new version with deprecation warning
2. Update README to recommend alternative
3. Mark as deprecated on PyPI (contact PyPI support)

## Best Practices

1. **Test Before Publishing**
   - Always test on Test PyPI first
   - Run all tests
   - Check documentation

2. **Use Semantic Versioning**
   - Follow semantic versioning strictly
   - Document breaking changes

3. **Keep Changelog**
   - Maintain CHANGELOG.md
   - Document all changes

4. **Secure API Tokens**
   - Never commit tokens to git
   - Use environment variables or secrets
   - Rotate tokens regularly

5. **Monitor Downloads**
   - Check PyPI statistics
   - Monitor for issues

## Resources

- [PyPI Documentation](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)