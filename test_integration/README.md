# CloudBrain Integration Test

This directory contains integration tests for the CloudBrain client package.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the CloudBrain client package from PyPI:
```bash
pip install cloudbrain-client
```

3. Ensure PostgreSQL is running and accessible:
```bash
# Check PostgreSQL status
psql -U cloudbrain_user -d cloudbrain -c "SELECT 1;"
```

## Running Tests

Run the integration test suite:
```bash
python test_integration.py
```

## What's Being Tested

1. **Brain State Management**: Save and load brain states for AIs
2. **Collaboration Features**: AI-to-AI messaging and collaborative memory
3. **Documentation Retrieval**: Search and browse documentation from database
4. **End-to-End Workflow**: Complete scenario with multiple AIs collaborating

## Expected Results

All tests should pass with the following outputs:
- ✅ Brain State Management: PASSED
- ✅ Collaboration Features: PASSED
- ✅ Documentation Retrieval: PASSED
- ✅ End-to-End Workflow: PASSED

## Troubleshooting

If tests fail, check:
- PostgreSQL is running and accessible
- Database credentials are correct
- cloudbrain-client package is installed (version 3.1.1 or later)
- ai_brain_state and ai_collaboration tables exist in database
