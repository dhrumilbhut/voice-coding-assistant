# 🎤 Voice Coding Assistant

> Transform your voice into code with AI-powered development assistance

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com)


A sophisticated voice-controlled coding assistant that leverages OpenAI's GPT models to help developers create, analyze, and manage code through natural speech interaction. Simply speak your requirements, and watch as complete projects come to life!


## ✨ Features

- 🎙️ **Voice-to-Code**: Convert speech directly into functional code
- 🤖 **AI-Powered**: Integrates with OpenAI GPT-4o-mini for intelligent responses
- 📁 **Smart Project Organization**: Automatically creates organized project folders
- 🛠️ **Multi-Tool Support**: File creation, code analysis, command execution
- 🧠 **Chain-of-Thought Reasoning**: Multi-step planning for complex tasks
- 🌐 **Web Development Ready**: Instant HTML, CSS, JavaScript project scaffolding
- 🐍 **Python Support**: Create and analyze Python projects
- 📝 **Structured Outputs**: Reliable JSON-based AI responses
- 🛡️ **Rate Limiting**: Prevents abuse and controls API costs by limiting requests per user/IP
- 🔑 **User-Provided OpenAI API Key**: Each user must supply their own OpenAI API key for every request, ensuring privacy and cost control
- 🌐 **MCP Server Mode**: Run as a FastAPI server with a `/mcp/ask` endpoint for programmatic access
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

5. **Run as MCP Server (API mode)**
   ```bash
   uvicorn server:app --reload
   ```


## 🎯 Usage Examples
### Use the MCP API Endpoint

Send a POST request to `/mcp/ask` with your OpenAI API key:

```bash
curl -X POST "http://127.0.0.1:8000/mcp/ask" \
   -H "Content-Type: application/json" \
   -d '{
      "user_input": "Create a Python function to add two numbers",
      "api_key": "sk-...your-openai-key...",
      "context": {}
   }'
```

**Note:** Each request must include a valid OpenAI API key in the `api_key` field. Requests are rate-limited (default: 10/minute per IP).

### Create a Todo App
```
🎤 "Create a todo app with HTML, CSS, and JavaScript"
```
**Result**: Complete todo application in `todo_app/` folder with:
- `index.html` - Responsive HTML structure
- `style.css` - Modern CSS styling  
- `script.js` - Interactive JavaScript functionality

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
├── assistant_core.py    # Core assistant logic (shared by CLI and API)
├── server.py            # FastAPI MCP server (API mode)
├── tools.py             # Tool functions (file ops, analysis)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # This file
└── generated_projects/  # Auto-created project folders
   ├── todo_app/
   ├── calculator_app/
   └── web_app/
```

## 🛠️ Available Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `create_file` | Create new files with content | Building HTML, CSS, JS files |
| `read_file` | Read existing file contents | Code review and analysis |
| `write_file` | Update existing files | Modifying configurations |
| `analyze_code` | Analyze code structure | Getting code metrics |
| `run_command` | Execute system commands | Git operations, builds |

## 🎨 Smart Project Detection

The assistant automatically detects project types and creates organized folders:

| Project Type | Keywords | Folder Name |
|--------------|----------|-------------|
| 📝 Todo Apps | todo, task, checklist | `todo_app/` |
| 🧮 Calculator | calc, calculator, math | `calculator_app/` |
| 🌤️ Weather Apps | weather, forecast | `weather_app/` |
| 💼 Portfolio | portfolio, resume, cv | `portfolio_app/` |
| 🛒 E-commerce | shop, store, cart | `ecommerce_app/` |
| 🎮 Games | game, puzzle, play | `game_app/` |
| 🌐 Web Apps | General HTML/CSS/JS | `web_app/` |
| 🐍 Python | Python files | `python_project/` |

## 🔧 Configuration


### Environment Variables

For CLI mode, create a `.env` file with:

```env
# Required for CLI
OPENAI_API_KEY=your_openai_api_key_here
```

For API mode, each request must include an `api_key` field with a valid OpenAI API key. The `.env` file is not required for API usage.

### Supported Models

- `gpt-4o-mini` (default) - Fast and cost-effective
- `gpt-4o` - More capable for complex tasks
- `gpt-3.5-turbo` - Budget-friendly option

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

## 📋 Requirements

```
openai>=1.0.0
python-dotenv>=1.0.0
SpeechRecognition>=3.10.0
pydantic>=2.0.0
pyaudio>=0.2.11  # Optional, for microphone input
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- OpenAI for providing powerful language models
- SpeechRecognition library for voice input capabilities
- The Python community for excellent tooling and libraries



---

<div align="center">

**Made with ❤️ by Dhrumil Bhut**

[⭐ Star this repo](https://github.com/dhrumilbhut/voice-coding-assistant) if you find it helpful!

</div>
