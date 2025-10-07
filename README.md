# 🎤 Voice Coding Assistant

> Transform your voice into code with AI-powered development assistance

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com)


A sophisticated voice-controlled coding assistant that leverages OpenAI's GPT models to help developers create, analyze, and manage code through natural speech interaction. Simply speak your requirements, and watch as complete projects come to life!


## ✨ Features

- 🎙️ **Voice-to-Code**: Convert speech directly into functional code
- 🔊 **Text-to-Speech**: AI responses spoken aloud with OpenAI's streaming TTS
- 🤖 **AI-Powered**: Integrates with OpenAI GPT-4o-mini for intelligent responses
- 🎯 **Model Selection**: Users can choose from multiple OpenAI models (gpt-4o-mini, gpt-4o, gpt-3.5-turbo) based on their cost/performance needs
- 🏗️ **Hybrid Architecture**: Both Simple REST API and True MCP Protocol support
- 📁 **Smart Project Organization**: Automatically creates organized project folders in `ai_projects/`
- 🗂️ **Custom Locations**: Users can specify project locations - "Create in my_workspace folder"
- 🛠️ **Multi-Tool Support**: File creation, code analysis, command execution
- 🧠 **Chain-of-Thought Reasoning**: Multi-step planning for complex tasks
- 🌐 **Web Development Ready**: Instant HTML, CSS, JavaScript project scaffolding
- 🐍 **Python Support**: Create and analyze Python projects
- 📝 **Structured Outputs**: Reliable JSON-based AI responses
- 🛡️ **Rate Limiting**: Prevents abuse and controls API costs by limiting requests per user/IP
- 🔑 **User-Provided OpenAI API Key**: Each user must supply their own OpenAI API key for every request, ensuring privacy and cost control
- 🔌 **True MCP Server**: Full JSON-RPC 2.0 compliant Model Context Protocol implementation
- 📊 **Multi-Tenant Ready**: Supports multiple users with isolated API usage and billing
- 🧩 **Easy Integration**: Ready for use with external tools, scripts, or future VS Code extension

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Microphone (optional - works in text mode too)


### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/voice-coding-assistant.git
   cd voice-coding-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (CLI only)**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key (for CLI mode only)
   ```

4. **Run the assistant (CLI mode)**
   ```bash
   python main.py
   ```

5. **🔥 Run Hybrid Mode (Recommended)**
   ```bash
   python hybrid_server.py
   ```
   *Starts both Simple REST API (8000) and MCP Server (8001)*

6. **Or run individually:**
   ```bash
   # Simple REST API only
   uvicorn server:app --reload
   
   # MCP Server only  
   python mcp_server.py
   ```

7. **🧪 Test the APIs**
   ```bash
   python test_apis.py
   ```


## 🎯 Usage Examples

### CLI Mode
Run `python main.py` for interactive voice/text coding assistance.

### Simple REST API

Send a POST request to `/api/ask`:

<details>
<summary>📋 Click to view REST API curl example</summary>

```bash
curl -X POST "http://127.0.0.1:8000/api/ask" \
   -H "Content-Type: application/json" \
   -d '{
      "user_input": "Create a Python function to add two numbers",
      "api_key": "sk-...your-openai-key...",
      "model": "gpt-4o-mini",
      "context": {}
   }'
```

</details>



**🎯 Model Selection**: Users can specify which OpenAI model to use by including a `"model"` parameter. Defaults to `"gpt-4o-mini"` if not specified.

### True MCP (Model Context Protocol) Server

The project includes a **real MCP-compliant server** following the JSON-RPC 2.0 protocol:

<details>
<summary>🔌 1. Initialize the MCP connection</summary>

```bash
curl -X POST "http://127.0.0.1:8001/mcp/rpc" \
   -H "Content-Type: application/json" \
   -d '{
      "jsonrpc": "2.0",
      "id": 1,
      "method": "initialize",
      "params": {
         "protocolVersion": "2024-11-05",
         "capabilities": {"tools": {}},
         "clientInfo": {"name": "my-client", "version": "1.0.0"}
      }
   }'
```

</details>

<details>
<summary>🛠️ 2. List available tools</summary>

```bash
curl -X POST "http://127.0.0.1:8001/mcp/rpc" \
   -H "Content-Type: application/json" \
   -d '{
      "jsonrpc": "2.0",
      "id": 2,
      "method": "tools/list"
   }'
```

</details>

<details>
<summary>⚡ 3. Call a tool</summary>

```bash
curl -X POST "http://127.0.0.1:8001/mcp/rpc" \
   -H "Content-Type: application/json" \
   -d '{
      "jsonrpc": "2.0",
      "id": 3,
      "method": "tools/call",
      "params": {
         "name": "create_file",
         "arguments": {
            "file_path": "hello.py",
            "content": "print(\"Hello MCP!\")",
            "api_key": "sk-...your-key..."
         }
      }
   }'
```

</details>

<details>
<summary>🤖 4. Use the AI assistant</summary>

```bash
curl -X POST "http://127.0.0.1:8001/mcp/rpc" \
   -H "Content-Type: application/json" \
   -d '{
      "jsonrpc": "2.0",
      "id": 4,
      "method": "assistant/ask",
      "params": {
         "user_input": "Create a todo app",
         "api_key": "sk-...your-key...",
         "model": "gpt-4o-mini",
         "context": {}
      }
   }'
```

</details>

**🎯 Model Selection**: Both APIs support user-selectable models via the `"model"` parameter. This allows API key owners to control cost and performance trade-offs.

**Note:** Each request must include a valid OpenAI API key. The simple API is rate-limited (10/minute), while MCP allows 30/minute for more complex workflows.

### Create a Todo App
```
🎤 "Create a todo app with HTML, CSS, and JavaScript"
```
**Result**: Complete todo application in `ai_projects/todo_app/` folder with:
- `index.html` - Responsive HTML structure
- `style.css` - Modern CSS styling  
- `script.js` - Interactive JavaScript functionality

### Create with Custom Location
```
🎤 "Create a calculator app in my_projects folder"
```
**Result**: Calculator application in `my_projects/calculator_app/` folder

### Analyze Code
```
🎤 "Analyze the main.py file"
```
**Result**: Detailed code analysis with metrics and insights

### Build a Calculator
```
🎤 "Create a calculator app"
```
**Result**: Functional calculator in `calculator_app/` folder


## 📂 Project Structure

```
voice-coding-assistant/
├── main.py              # Main application entry point (CLI)
├── assistant_core.py    # Core assistant logic (shared by CLI and APIs)
├── server.py            # Simple REST API server
├── mcp_server.py        # True MCP-compliant JSON-RPC server
├── hybrid_server.py     # Runs both APIs simultaneously  
├── tools.py             # Tool functions (file ops, analysis)
├── test_apis.py         # Example usage for both APIs
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
└── ai_projects/         # Organized AI-generated projects
   ├── todo_app/
   ├── calculator_app/
   ├── web_app/
   ├── game_app/
   └── python_project/
```

## 🛠️ Available Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `create_file` | Create new files with content | Building HTML, CSS, JS files |
| `read_file` | Read existing file contents | Code review and analysis |
| `write_file` | Update existing files | Modifying configurations |
| `analyze_code` | Analyze code structure | Getting code metrics |
| `run_command` | Execute system commands | Git operations, builds |

## 🎨 Smart Project Detection & Custom Locations

The assistant automatically detects project types and creates organized folders in `ai_projects/`:

| Project Type | Keywords | Default Folder | Custom Location Example |
|--------------|----------|----------------|------------------------|
| 📝 Todo Apps | todo, task, checklist | `ai_projects/todo_app/` | `my_workspace/todo_app/` |
| 🧮 Calculator | calc, calculator, math | `ai_projects/calculator_app/` | `desktop/tools/calculator_app/` |
| 🌤️ Weather Apps | weather, forecast | `ai_projects/weather_app/` | `projects/weather_app/` |
| 💼 Portfolio | portfolio, resume, cv | `ai_projects/portfolio_app/` | `websites/portfolio_app/` |
| 🛒 E-commerce | shop, store, cart | `ai_projects/ecommerce_app/` | `business/ecommerce_app/` |
| 🎮 Games | game, puzzle, play | `ai_projects/game_app/` | `my_games/game_app/` |
| 🌐 Web Apps | General HTML/CSS/JS | `ai_projects/web_app/` | `webdev/web_app/` |
| 🐍 Python | Python files | `ai_projects/python_project/` | `scripts/python_project/` |

### 🗂️ **Custom Location Examples**

Users can specify custom locations using natural language:

```bash
🎤 "Create a todo app in my_projects folder"
📁 Result: my_projects/todo_app/

🎤 "Put the calculator in desktop/tools"
📁 Result: desktop/tools/calculator_app/

🎤 "Save in location: custom_workspace"
📁 Result: custom_workspace/[detected_project_type]/

🎤 "Create in directory: user_apps"  
📁 Result: user_apps/[detected_project_type]/
```

### 🎯 **Location Detection Patterns**
The system recognizes various ways users specify custom locations:
- "Create ... in [folder]"
- "Put ... in [folder]"
- "Save in location: [folder]"
- "Create in directory: [folder]"
- "Location: [folder]"
- "Folder: [folder]"

## 🏗️ **Hybrid Architecture Overview**

```
🎤 Voice Coding Assistant - Hybrid Architecture
├── 📡 Simple REST API (Port 8000)     ├── 🔌 MCP Server (Port 8001)
│   ├── POST /api/ask                  │   ├── JSON-RPC 2.0 Protocol
│   ├── Rate Limit: 10/min             │   ├── Rate Limit: 30/min
│   └── Perfect for MVPs               │   └── Standards Compliant
│                                      │
└── 🧠 Shared Core Logic (assistant_core.py)
    ├── OpenAI GPT Integration
    ├── Chain-of-Thought Reasoning
    ├── Tool Execution Engine
    └── Project Organization
```

### 🎯 **Why Hybrid Approach?**
- **🚀 Speed**: Simple REST for quick integrations and testing
- **📏 Standards**: MCP compliance for future-proof AI ecosystem integration
- **🔄 Flexibility**: Developers choose what fits their workflow
- **💡 Innovation**: Best of both worlds without compromise

## 🔧 Configuration

### API Comparison

| Feature | Simple REST API | True MCP Server |
|---------|----------------|-----------------|
| **Protocol** | HTTP REST | JSON-RPC 2.0 |
| **Port** | 8000 | 8001 |
| **Endpoint** | `/api/ask` | `/mcp/rpc` |
| **Rate Limit** | 10/minute | 30/minute |
| **Initialization** | None required | MCP handshake required |
| **Tool Discovery** | Not available | `/tools/list` method |
| **Compliance** | Simple & fast | MCP standard compliant |
| **Use Case** | Quick integration | Standard MCP clients |

### Environment Variables

For CLI mode, create a `.env` file with:

```env
# Required for CLI
OPENAI_API_KEY=your_openai_api_key_here
```

For API mode, each request must include an `api_key` field with a valid OpenAI API key. The `.env` file is not required for API usage.

### Supported Models

- `gpt-4o-mini` (default) - Fast and cost-effective, optimal for most coding tasks
- `gpt-4o` - More capable for complex architectural decisions and advanced coding
- `gpt-3.5-turbo` - Budget-friendly option for simple tasks
- `gpt-4` - Legacy model, more expensive but highly capable

**🎯 Model Selection**: Users can choose models based on their specific needs:
- **Cost-conscious**: Use `gpt-4o-mini` for routine coding tasks
- **Performance-critical**: Use `gpt-4o` for complex problem-solving
- **Budget-limited**: Use `gpt-3.5-turbo` for simple file generation

Since users provide their own API keys, they control the cost/performance trade-off!

## 🧠 How It Works

The assistant uses a structured reasoning approach:

1. **🔥 START**: Processes your voice/text input
2. **🧠 PLAN**: Creates multi-step execution plan
3. **🛠️ TOOL**: Executes necessary tools (file creation, analysis)
4. **👁️ OBSERVE**: Reviews tool outputs
5. **🤖 OUTPUT**: Provides final response

### Example Workflow

```
🎤 Input: "Create a landing page for a coffee shop"

🧠 Planning: "User wants a coffee shop landing page"
🧠 Planning: "I'll create HTML structure with header, menu, contact"
🧠 Planning: "Add CSS for warm, coffee-themed styling"
🧠 Planning: "Include JavaScript for interactive menu"

🛠️ Tool: create_file(index.html, [HTML content])
🛠️ Tool: create_file(style.css, [CSS content])  
🛠️ Tool: create_file(script.js, [JS content])

🤖 Output: "Created a complete coffee shop landing page!"
```

---

<div align="center">

**Made with ❤️ by Dhrumil Bhut**

[⭐ Star this repo](https://github.com/dhrumilbhut/voice-coding-assistant) if you find it helpful!

</div>