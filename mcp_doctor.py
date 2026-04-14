import subprocess
import json
import os
import sys
import time

def test_mcp():
    print("🩺 Running MCP Diagnostic Check...")
    print(f"Current Working Directory: {os.getcwd()}")
    print("-" * 40)

    # 1. Environment Verification
    venv_python = os.path.join(os.getcwd(), "venv", "bin", "python3")
    if not os.path.exists(venv_python):
        print(f"⚠️ Warning: Virtual environment not found at {venv_python}")
        print("Falling back to system 'python3'...")
        python_exec = "python3"
    else:
        python_exec = venv_python

    # 2. Start MCP Server Process (Standard I/O mode)
    try:
        # We use python -m mcp_server.server to ensure module resolution works
        process = subprocess.Popen(
            [python_exec, "-m", "mcp_server.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()}
        )
        
        # 3. Simulate a tool discovery request (Standard MCP Protocol)
        print("🔍 Sending discovery request to MCP Core...")
        discovery_payload = json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "MCP-Doctor-Client", "version": "1.0.0"}
            }
        }) + "\n"
        
        process.stdin.write(discovery_payload)
        process.stdin.flush()
        
        # Give a second for response
        time.sleep(1)
        
        # Read response
        output = process.stdout.readline()
        
        if output:
            print("✅ SUCCESS: MCP Server responded with valid JSON-RPC.")
            print("📜 Handshake Payload:")
            print(output[:200] + "...") # Print first snippet
            
            # 4. Check for our custom tools
            list_tools_payload = json.dumps({
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 2,
                "params": {}
            }) + "\n"
            process.stdin.write(list_tools_payload)
            process.stdin.flush()
            
            # Sleep a bit more for tool listing
            time.sleep(1)
            tools_output = process.stdout.readline()
            
            if "list_slow_queries" in tools_output:
                print("✅ VERIFIED: 'list_slow_queries' tool is registered.")
            if "read_agent_logs" in tools_output:
                print("✅ VERIFIED: 'read_agent_logs' (observability) is active.")
                
            print("-" * 40)
            print("🏥 DIAGNOSTIC RESULT: All MCP Core subsystems are healthy.")
        else:
            print("❌ FAILURE: Server started but did not respond to I/O.")
            err = process.stderr.read()
            if err:
                print(f"⚠️ Error Trace: {err}")
                
    except Exception as e:
        print(f"💥 CRITICAL ERROR: Could not talk to the MCP Core: {e}")
    finally:
        try:
            process.terminate()
        except:
            pass

if __name__ == "__main__":
    test_mcp()
