"""
Unified server that runs both the simple REST API and true MCP server.
This provides the hybrid approach with both interfaces available.
"""

import asyncio
import uvicorn
from multiprocessing import Process
import time

def run_simple_api():
    """Run the simple REST API server on port 8000."""
    from server import app
    uvicorn.run(app, host="0.0.0.0", port=8000)

def run_mcp_server():
    """Run the MCP-compliant server on port 8001."""
    from mcp_server import app
    uvicorn.run(app, host="0.0.0.0", port=8001)

def main():
    """Start both servers concurrently."""
    print("🚀 Starting Voice Coding Assistant - Hybrid Mode")
    print("=" * 60)
    print("📡 Simple REST API: http://localhost:8000")
    print("   - Endpoint: POST /api/ask")
    print("   - Documentation: http://localhost:8000")
    print("")
    print("🔌 MCP Server: http://localhost:8001")
    print("   - Endpoint: POST /mcp/rpc (JSON-RPC 2.0)")
    print("   - Info: http://localhost:8001/mcp/info")
    print("=" * 60)
    
    # Start both servers as separate processes
    simple_api_process = Process(target=run_simple_api)
    mcp_server_process = Process(target=run_mcp_server)
    
    try:
        simple_api_process.start()
        time.sleep(1)  # Give first server time to start
        mcp_server_process.start()
        
        print("✅ Both servers are running!")
        print("Press Ctrl+C to stop both servers")
        
        # Wait for both processes
        simple_api_process.join()
        mcp_server_process.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        simple_api_process.terminate()
        mcp_server_process.terminate()
        simple_api_process.join()
        mcp_server_process.join()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()