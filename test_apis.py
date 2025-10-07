"""
Example usage of both the Simple REST API and True MCP Server.
Demonstrates how to interact with both interfaces.
"""

import requests
import json

# API endpoints
SIMPLE_API_URL = "http://localhost:8000/api/ask"
MCP_RPC_URL = "http://localhost:8001/mcp/rpc"
MCP_INFO_URL = "http://localhost:8001/mcp/info"

# Replace with your actual OpenAI API key
API_KEY = "sk-your-openai-api-key-here"

def test_simple_api():
    """Test the simple REST API"""
    print("\n📡 Testing Simple REST API")
    print("=" * 40)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ask",
            json={
                "user_input": "What is 2+2?",
                "api_key": API_KEY,
                "model": "gpt-4o-mini",  # Optional: specify model
                "context": {}
            },
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_mcp_initialization():
    """Test MCP server initialization."""
    print("\n🔌 Testing MCP Initialization")
    print("=" * 40)
    
    # MCP initialization request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        response = requests.post(MCP_RPC_URL, json=init_request)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        return result.get("result") is not None
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_mcp_tools():
    """Test MCP tools listing."""
    print("\n🛠️ Testing MCP Tools")
    print("=" * 40)
    
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = requests.post(MCP_RPC_URL, json=tools_request)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        if "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            print(f"Available tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print(f"Result: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_mcp_tool_call():
    """Test MCP tool execution."""
    print("\n⚙️ Testing MCP Tool Call")
    print("=" * 40)
    
    tool_call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "create_file",
            "arguments": {
                "file_path": "test_mcp.py",
                "content": "# Test file created via MCP\nprint('Hello from MCP!')",
                "api_key": API_KEY
            }
        }
    }
    
    try:
        response = requests.post(MCP_RPC_URL, json=tool_call_request)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_mcp_assistant():
    """Test MCP assistant functionality."""
    print("\n🤖 Testing MCP Assistant")
    print("=" * 40)
    
    assistant_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "assistant/ask",
        "params": {
            "user_input": "Create a simple calculator function in Python",
            "api_key": API_KEY,
            "model": "gpt-4o-mini",  # Optional: specify model
            "context": {}
        }
    }
    
    try:
        response = requests.post(MCP_RPC_URL, json=assistant_request)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        if "result" in result:
            print(f"Response: {result['result']['response']}")
        else:
            print(f"Result: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        print(f"Error: {e}")

def get_mcp_info():
    """Get MCP server information."""
    print("\n📋 MCP Server Info")
    print("=" * 40)
    
    try:
        response = requests.get(MCP_INFO_URL)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Info: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all tests."""
    print("🧪 Testing Voice Coding Assistant - Hybrid Mode")
    print("Make sure both servers are running (python hybrid_server.py)")
    print("Don't forget to set your API_KEY in this script!")
    
    if API_KEY == "sk-your-openai-api-key-here":
        print("\n❌ Please set your OpenAI API key in the script first!")
        return
    
    # Test simple API
    test_simple_api()
    
    # Test MCP server
    get_mcp_info()
    
    # Initialize MCP
    if test_mcp_initialization():
        test_mcp_tools()
        test_mcp_tool_call()
        test_mcp_assistant()
    else:
        print("❌ MCP initialization failed, skipping other tests")

if __name__ == "__main__":
    main()