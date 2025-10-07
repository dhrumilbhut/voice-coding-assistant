

from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict
from assistant_core import run_assistant
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()

# Set up rate limiter (e.g., 10 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



class MCPRequest(BaseModel):
    user_input: str
    api_key: str
    model: str = "gpt-4o-mini"  # Default model, user can override
    context: Dict[str, Any] = {}


class MCPResponse(BaseModel):
    response: str
    data: Dict[str, Any] = {}


@app.get("/")
def root():
    return {
        "message": "Voice Coding Assistant API Server",
        "endpoints": {
            "simple_api": "/api/ask",
            "mcp_compliant": "/mcp/rpc (run mcp_server.py on port 8001)"
        },
        "documentation": "See README.md for usage examples"
    }



@app.post("/api/ask", response_model=MCPResponse)
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
async def api_ask(request: Request, body: MCPRequest):
    api_key = body.api_key.strip() if body.api_key else ""
    if not api_key:
        return {"response": "Error: API key is required in the request.", "data": {}}
    if not (api_key.startswith("sk-") and len(api_key) >= 40):
        return {"response": "Error: Invalid API key format. Please provide a valid OpenAI API key.", "data": {}}
    response, _ = run_assistant(body.user_input, context=body.context, api_key=api_key, model=body.model)
    return MCPResponse(response=response, data={})
