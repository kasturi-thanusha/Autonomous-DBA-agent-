#!/bin/bash
# Autonomous DBA Agent - Setup Script

echo "🚀 Starting setup for Autonomous DBA Agent..."

# 1. System Dependencies (WSL Ubuntu)
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-venv libpq-dev gcc python3-dev

# 2. Virtual Environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Python Dependencies
echo "pip: Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Directories
echo "📁 Creating data and log directories..."
mkdir -p data logs

echo "✅ Setup complete!"
echo ""
echo "Next Steps:"
echo "1. Configure your .env file (use .env.example as template)"
echo "2. Run the Dashboard: streamlit run app.py"
echo "3. Run the MCP Server: python -m mcp_server.server"
echo "4. Run Autonmous Monitor: python -m scheduler.monitor"
