#!/bin/bash
# Start libsql simulator in virtual environment

echo "=========================================="
echo "🧪 Starting libsql Simulator"
echo "=========================================="
echo ""

# Activate virtual environment
source .venv/bin/activate

echo "✅ Virtual environment activated"
echo "📍 Database: ai_db/cloudbrain.db"
echo "🌐 Address: ws://127.0.0.1:8766"
echo ""
echo "🚀 Starting server..."
echo ""

# Start server
python3 libsql_local_simulator.py