#!/bin/bash

echo "🤖 Autonomous AI Agent Setup"
echo "=============================="
echo ""

# Step 1: Check virtual environment
echo "📦 Step 1: Checking virtual environment..."
if [ -d "./.venv" ]; then
    echo "✅ Found virtual environment at ./.venv"
    source ./.venv/bin/activate
elif [ -d "../.venv" ]; then
    echo "✅ Found virtual environment at ../.venv"
    source ../.venv/bin/activate
else
    echo "⚠️  No virtual environment found at ./.venv or ../.venv"
    echo "Creating virtual environment at ./.venv..."
    python -m venv .venv
    source ./.venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi
echo ""

# Step 2: Check for running server
echo "🌐 Step 2: Checking for CloudBrain server..."
if lsof -Pi :8766 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ CloudBrain server is already running on port 8766"
    echo "You can connect to the existing server!"
else
    echo "⚠️  No CloudBrain server detected on port 8766"
    echo "Please start the CloudBrain server first"
    echo "Or check if it's running on a different port"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 1
    fi
fi
echo ""

# Step 3: Install package
echo "📥 Step 3: Installing cloudbrain-client..."
pip install cloudbrain-client==1.1.1
if [ $? -eq 0 ]; then
    echo "✅ Package installed successfully"
else
    echo "❌ Failed to install package"
    exit 1
fi
echo ""

# Step 4: Check if code exists
echo "📄 Step 4: Checking for autonomous agent code..."
if [ -f "autonomous_ai_agent_esperanto.py" ]; then
    echo "✅ Found autonomous_ai_agent_esperanto.py"
else
    echo "⚠️  autonomous_ai_agent_esperanto.py not found"
    echo "Please search CloudBrain for 'autonomous agent code' and save it"
    echo ""
    read -p "Press Enter after you've saved the code..."
fi
echo ""

# Step 5: Run the agent
echo "🚀 Step 5: Running the autonomous agent..."
python autonomous_ai_agent_esperanto.py
