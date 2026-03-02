#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install it first: https://nodejs.org/"
    exit 1
fi

PORT=4310
URL="http://localhost:$PORT"

echo "🚀 Starting OpenClaw Workspace Viewer..."
echo "📂 Root: $(pwd)"
echo "🌍 URL: $URL"
echo "Press Ctrl+C to stop."

# Open browser after a short delay (in background)
(sleep 1 && open "$URL") &

# Start server
node server.js