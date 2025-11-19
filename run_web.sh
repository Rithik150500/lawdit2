#!/bin/bash
# Launcher script for Lawdit Web Interface

set -e

echo "🚀 Starting Lawdit Web Interface..."
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   Consider activating your virtual environment first:"
    echo "   source venv/bin/activate"
    echo ""
fi

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Error: Streamlit is not installed."
    echo "   Install it with: pip install streamlit"
    exit 1
fi

# Check if .env exists
if [[ ! -f .env ]]; then
    echo "⚠️  Warning: .env file not found."
    echo "   Creating from template..."
    if [[ -f .env.example ]]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your API keys."
    else
        echo "❌ .env.example not found. Please configure manually."
    fi
    echo ""
fi

# Launch the web interface
echo "📍 Web interface will open at: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

streamlit run src/lawdit/web/app.py \
    --server.port=8501 \
    --server.address=localhost \
    --browser.gatherUsageStats=false
