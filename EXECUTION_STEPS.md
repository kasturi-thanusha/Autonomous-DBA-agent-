# Execution Steps

The architecture is multi-faceted. You can run individual components based on your current need. Ensure your virtual environment is active `source venv/bin/activate` before running.

## 1. Run the Dashboard (Streamlit)
To visualize identified optimizations, AI metrics, and trigger tasks manually:
```bash
streamlit run app.py
```
This boots up a premium Web UI dynamically hosted at `http://localhost:8501`.

## 2. Start the Real-Time Background Monitor
To enable the agent to act purely autonomously in the background (capturing spikes and generating Groq insights without human interaction):
```bash
python scheduler/monitor.py
```
*Note: This runs infinitely in the terminal daemon until you press `Ctrl+C`.*

## 3. Expose the Agent Tools to Claude (MCP Server)
If you want to plug the optimization tools directly into Claude Desktop using the Model Context Protocol:
Add the following to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "Postgres-Optimizer": {
      "command": "python",
      "args": ["/absolute/path/to/slow query ai agent/mcp_server/server.py"]
    }
  }
}
```
Restart Claude Desktop, and you can now ask Claude questions like *"What queries are currently running slow in my database?"* and it will invoke the local Python server internally.
