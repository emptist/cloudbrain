#!/bin/bash
# Quick Start Script for Real-time Communication Testing
# Choose between: Polling, WebSocket Server, or libsql Simulator

echo "=========================================="
echo "🤖 Cloud Brain Real-time Communication"
echo "=========================================="
echo ""
echo "Choose communication method:"
echo ""
echo "1. Polling (current, simple)"
echo "   - No server needed"
echo "   - 5 second delay"
echo "   - Command: python3 message_poller.py"
echo ""
echo "2. Local WebSocket Server"
echo "   - True real-time"
echo "   - Self-hosted"
echo "   - Command: python3 local_websocket_server.py"
echo ""
echo "3. libsql Simulator (recommended) ⭐"
echo "   - True real-time"
echo "   - Simulates libsql locally"
echo "   - Command: python3 libsql_local_simulator.py"
echo ""
echo "=========================================="

read -p "Enter choice (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "📨 Starting Polling..."
        echo ""
        python3 message_poller.py
        ;;
    2)
        echo ""
        echo "🚀 Starting Local WebSocket Server..."
        echo ""
        echo "In another terminal, run:"
        echo "  python3 ai_websocket_client.py"
        echo ""
        echo "Then choose option 1 (Local WebSocket Server)"
        echo ""
        python3 local_websocket_server.py
        ;;
    3)
        echo ""
        echo "🧪 Starting libsql Simulator..."
        echo ""
        echo "In another terminal, run:"
        echo "  python3 ai_websocket_client.py"
        echo ""
        echo "Then choose option 2 (libsql Simulator)"
        echo ""
        python3 libsql_local_simulator.py
        ;;
    *)
        echo ""
        echo "❌ Invalid choice"
        exit 1
        ;;
esac