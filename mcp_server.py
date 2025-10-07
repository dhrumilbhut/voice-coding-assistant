"""
True MCP (Model Context Protocol) compliant server implementation.
This runs alongside the existing REST API to provide proper MCP support.
"""

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
import json
import uuid
from assistant_core import run_assistant
from tools import AVAILABLE_TOOLS
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# MCP Protocol Models
class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int, None] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class McpError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

# MCP-specific models
class ServerInfo(BaseModel):
    name: str = "voice-coding-assistant"
    version: str = "1.0.0"

class Implementation(BaseModel):
    name: str = "voice-coding-assistant-mcp"
    version: str = "1.0.0"

class ServerCapabilities(BaseModel):
    logging: Dict[str, Any] = {}
    tools: Dict[str, Any] = {}
    resources: Dict[str, Any] = {}

class InitializeParams(BaseModel):
    protocolVersion: str
    capabilities: Dict[str, Any]
    clientInfo: Dict[str, Any]

class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class Resource(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None

class ToolCallParams(BaseModel):
    name: str
    arguments: Dict[str, Any]

app = FastAPI()

# Set up rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# MCP server state
server_initialized = False
client_capabilities = {}

def create_error_response(request_id: Union[str, int, None], code: int, message: str, data: Any = None) -> JsonRpcResponse:
    """Create a JSON-RPC error response."""
    return JsonRpcResponse(
        id=request_id,
        error={
            "code": code,
            "message": message,
            "data": data
        }
    )

def create_success_response(request_id: Union[str, int, None], result: Any) -> JsonRpcResponse:
    """Create a JSON-RPC success response."""
    return JsonRpcResponse(
        id=request_id,
        result=result
    )

def get_mcp_tools() -> List[Tool]:
    """Convert internal tools to MCP tool format."""
    tools = []
    
    # Define schemas for each tool
    tool_schemas = {
        "create_file": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path where the file should be created"},
                "content": {"type": "string", "description": "Content to write to the file"}
            },
            "required": ["file_path", "content"]
        },
        "read_file": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path of the file to read"}
            },
            "required": ["file_path"]
        },
        "write_file": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path of the file to write to"},
                "content": {"type": "string", "description": "Content to write to the file"}
            },
            "required": ["file_path", "content"]
        },
        "analyze_code": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path of the code file to analyze"}
            },
            "required": ["file_path"]
        },
        "run_command": {
            "type": "object",
            "properties": {
                "cmd": {"type": "string", "description": "Safe system command to execute"}
            },
            "required": ["cmd"]
        }
    }
    
    # Define descriptions for each tool
    tool_descriptions = {
        "create_file": "Create a new file with specified content. Automatically detects project type and creates appropriate folder structure.",
        "read_file": "Read the contents of an existing file. Searches in current directory and project folders.",
        "write_file": "Write/update content in an existing file. Overwrites existing content.",
        "analyze_code": "Analyze code structure and provide feedback including line count, imports, functions, and classes.",
        "run_command": "Execute safe system commands only. Dangerous operations are blocked for security."
    }
    
    for tool_name in AVAILABLE_TOOLS.keys():
        tools.append(Tool(
            name=tool_name,
            description=tool_descriptions.get(tool_name, f"Tool: {tool_name}"),
            inputSchema=tool_schemas.get(tool_name, {"type": "object"})
        ))
    
    return tools

@app.post("/mcp/rpc")
@limiter.limit("30/minute")  # Higher limit for MCP as it may need multiple calls
async def mcp_rpc_endpoint(request: Request):
    """Main MCP JSON-RPC endpoint."""
    global server_initialized, client_capabilities
    
    try:
        body = await request.json()
        rpc_request = JsonRpcRequest(**body)
    except Exception as e:
        return create_error_response(None, -32700, "Parse error", str(e)).dict()
    
    method = rpc_request.method
    params = rpc_request.params or {}
    request_id = rpc_request.id
    
    try:
        # Handle MCP initialization
        if method == "initialize":
            if server_initialized:
                return create_error_response(request_id, -32603, "Server already initialized").dict()
            
            try:
                init_params = InitializeParams(**params)
                client_capabilities = init_params.capabilities
                server_initialized = True
                
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "logging": {},
                        "tools": {
                            "listChanged": False
                        },
                        "resources": {
                            "subscribe": False,
                            "listChanged": False
                        }
                    },
                    "serverInfo": {
                        "name": "voice-coding-assistant",
                        "version": "1.0.0"
                    }
                }
                return create_success_response(request_id, result).dict()
            except Exception as e:
                return create_error_response(request_id, -32602, "Invalid params", str(e)).dict()
        
        # Check if server is initialized for other methods
        if not server_initialized and method != "initialize":
            return create_error_response(request_id, -32603, "Server not initialized").dict()
        
        # Handle notifications/ping
        if method == "notifications/initialized":
            # No response for notifications
            return None
        
        if method == "ping":
            return create_success_response(request_id, {}).dict()
        
        # Handle tools
        if method == "tools/list":
            tools = get_mcp_tools()
            tools_dict = [tool.dict() for tool in tools]
            return create_success_response(request_id, {"tools": tools_dict}).dict()
        
        if method == "tools/call":
            try:
                call_params = ToolCallParams(**params)
                tool_name = call_params.name
                tool_args = call_params.arguments
                
                # Validate API key for tool calls
                api_key = tool_args.get("api_key", "")
                if not api_key:
                    return create_error_response(request_id, -32602, "API key required in tool arguments").dict()
                
                if not (api_key.startswith("sk-") and len(api_key) >= 40):
                    return create_error_response(request_id, -32602, "Invalid API key format").dict()
                
                # Remove api_key from tool_args before processing
                tool_args_clean = {k: v for k, v in tool_args.items() if k != "api_key"}
                
                if tool_name not in AVAILABLE_TOOLS:
                    return create_error_response(request_id, -32601, f"Tool '{tool_name}' not found").dict()
                
                # Execute tool
                try:
                    if tool_name in ["create_file", "write_file"]:
                        result = AVAILABLE_TOOLS[tool_name](
                            tool_args_clean.get("file_path", ""),
                            tool_args_clean.get("content", "")
                        )
                    else:
                        # Single argument tools
                        arg_value = tool_args_clean.get("file_path") or tool_args_clean.get("cmd") or ""
                        result = AVAILABLE_TOOLS[tool_name](arg_value)
                    
                    return create_success_response(request_id, {
                        "content": [{
                            "type": "text",
                            "text": result
                        }],
                        "isError": False
                    }).dict()
                    
                except Exception as e:
                    return create_success_response(request_id, {
                        "content": [{
                            "type": "text", 
                            "text": f"Error executing tool: {str(e)}"
                        }],
                        "isError": True
                    }).dict()
                    
            except Exception as e:
                return create_error_response(request_id, -32602, "Invalid tool call params", str(e)).dict()
        
        # Handle resources (basic implementation)
        if method == "resources/list":
            # Return empty list for now - could be extended to list project files
            return create_success_response(request_id, {"resources": []}).dict()
        
        # Handle AI assistant calls
        if method == "assistant/ask":
            try:
                user_input = params.get("user_input", "")
                api_key = params.get("api_key", "")
                model = params.get("model", "gpt-4o-mini")  # Default model
                context = params.get("context", {})
                
                if not user_input:
                    return create_error_response(request_id, -32602, "user_input is required").dict()
                
                if not api_key:
                    return create_error_response(request_id, -32602, "api_key is required").dict()
                
                if not (api_key.startswith("sk-") and len(api_key) >= 40):
                    return create_error_response(request_id, -32602, "Invalid API key format").dict()
                
                response, _ = run_assistant(user_input, context=context, api_key=api_key, model=model)
                
                return create_success_response(request_id, {
                    "response": response,
                    "data": {}
                }).dict()
                
            except Exception as e:
                return create_error_response(request_id, -32603, "Internal error", str(e)).dict()
        
        # Unknown method
        return create_error_response(request_id, -32601, f"Method '{method}' not found").dict()
        
    except Exception as e:
        return create_error_response(request_id, -32603, "Internal error", str(e)).dict()

@app.get("/mcp/info")
async def mcp_info():
    """Get MCP server information."""
    return {
        "protocol": "Model Context Protocol (MCP)",
        "version": "2024-11-05",
        "server": {
            "name": "voice-coding-assistant",
            "version": "1.0.0"
        },
        "capabilities": {
            "tools": True,
            "resources": True,
            "logging": False
        },
        "endpoints": {
            "rpc": "/mcp/rpc",
            "info": "/mcp/info"
        },
        "documentation": "https://github.com/dhrumilbhut/voice-coding-assistant"
    }

# Add to existing server.py to keep both APIs
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)