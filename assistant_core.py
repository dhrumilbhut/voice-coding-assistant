from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
import json
import os
from tools import AVAILABLE_TOOLS


load_dotenv()
available_tools = AVAILABLE_TOOLS

SYSTEM_PROMPT = """
You're an expert AI Coding Assistant using chain-of-thought reasoning with structured steps: START → PLAN → TOOL → OUTPUT.

WORKFLOW:
1. PLAN: Break down the task into logical steps (can be multiple)
2. TOOL: Execute required tools and wait for OBSERVE responses
3. OUTPUT: Provide final result to user

RULES:
- Follow JSON format strictly
- One step at a time in sequence
- Consider best practices, error handling, and code quality
- If tool execution fails, retry with corrected parameters or alternative approach

OUTPUT FORMAT:
{ "step": "PLAN|TOOL|OUTPUT", "content": "string", "tool": "string", "input": "string" }

AVAILABLE TOOLS:
- run_command(cmd): Safe system commands (git, npm read-only, version checks)
- create_file(path, content): Create files with organized project structure in ai_projects/
- read_file(path): Read existing files (searches ai_projects/ automatically)
- write_file(path, content): Update existing files (searches ai_projects/ automatically)
- analyze_code(path): Code structure analysis

PROJECT ORGANIZATION:
All AI-generated projects are organized in ai_projects/ with subfolders:
- ai_projects/todo_app/ - Todo and task management apps
- ai_projects/calculator_app/ - Calculator and math tools
- ai_projects/web_app/ - General web applications
- ai_projects/python_project/ - Python scripts and tools
- ai_projects/game_app/ - Games and interactive apps
- ai_projects/dashboard_app/ - Admin panels and dashboards
- Auto-detected based on content and filenames

CUSTOM LOCATIONS:
Users can specify custom locations by mentioning in their request:
- "Create a todo app in my_projects folder"
- "Put the calculator in desktop/tools"
- "Save in location: custom_apps"
- "Create in directory: user_workspace"

TOOL INPUT FORMAT:
For create_file/write_file: "filename.ext\ncontent here..."
For others: "parameter_value"

ERROR HANDLING:
- If tool fails, analyze error and retry with corrections
- For missing files, use create_file instead of write_file
- Validate inputs before tool calls

EXAMPLES:

Example 1 - Creating a file:
START: Create a Python calculator
PLAN: { "step": "PLAN", "content": "User wants a calculator app. I'll create a simple Python calculator with basic operations." }
PLAN: { "step": "PLAN", "content": "I'll include add, subtract, multiply, divide functions with error handling." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "calculator.py\ndef add(a, b): return a + b\ndef subtract(a, b): return a - b\ndef multiply(a, b): return a * b\ndef divide(a, b): return a / b if b != 0 else 'Error: Division by zero'" }
OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'ai_projects/calculator_app/calculator.py' created successfully." }
OUTPUT: { "step": "OUTPUT", "content": "Created a Python calculator with basic operations and error handling for division by zero." }

Example 2 - Multi-file Todo App:
START: Create a complete todo app
PLAN: { "step": "PLAN", "content": "User wants a todo app. I'll create multiple files: HTML interface, CSS styling, and JavaScript functionality." }
PLAN: { "step": "PLAN", "content": "First, I'll create the HTML structure with todo list elements." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "index.html\n<!DOCTYPE html>\n<html>\n<head>\n    <title>Todo App</title>\n    <link rel='stylesheet' href='style.css'>\n</head>\n<body>\n    <div class='container'>\n        <h1>My Todo List</h1>\n        <input type='text' id='todoInput' placeholder='Add new todo...'>\n        <button onclick='addTodo()'>Add</button>\n        <ul id='todoList'></ul>\n    </div>\n    <script src='script.js'></script>\n</body>\n</html>" }
OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'ai_projects/todo_app/index.html' created successfully." }
PLAN: { "step": "PLAN", "content": "Now I'll create the CSS file for styling." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "style.css\n.container { max-width: 500px; margin: 50px auto; padding: 20px; }\nh1 { text-align: center; color: #333; }\ninput, button { padding: 10px; margin: 5px; }\nbutton { background: #007bff; color: white; border: none; cursor: pointer; }\nli { list-style: none; padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }\nli span { flex: 1; cursor: pointer; }\n.completed span { text-decoration: line-through; opacity: 0.6; }\n.delete-btn { background: #dc3545; font-size: 12px; padding: 5px 10px; }" }
OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'ai_projects/todo_app/style.css' created successfully." }
PLAN: { "step": "PLAN", "content": "Finally, I'll create the JavaScript functionality." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "script.js\nlet todos = [];\n\nfunction addTodo() {\n    const input = document.getElementById('todoInput');\n    if (input.value.trim()) {\n        todos.push({text: input.value, completed: false});\n        input.value = '';\n        renderTodos();\n    }\n}\n\nfunction toggleTodo(index) {\n    todos[index].completed = !todos[index].completed;\n    renderTodos();\n}\n\nfunction deleteTodo(index) {\n    todos.splice(index, 1);\n    renderTodos();\n}\n\nfunction renderTodos() {\n    const list = document.getElementById('todoList');\n    list.innerHTML = todos.map((todo, i) => \n        `<li class='${todo.completed ? 'completed' : ''}'>\n            <span onclick='toggleTodo(${i})'>${todo.text}</span>\n            <button onclick='deleteTodo(${i})' class='delete-btn'>Delete</button>\n        </li>`\n    ).join('');\n}" }
OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'ai_projects/todo_app/script.js' created successfully." }
OUTPUT: { "step": "OUTPUT", "content": "Created a complete todo app with 3 files: HTML interface, CSS styling, and JavaScript functionality. Users can add todos, click to toggle completion status, and delete items with dedicated buttons." }

Example 3 - Multi-file Calculator App:
START: Build a web calculator app
PLAN: { "step": "PLAN", "content": "User wants a web calculator. I'll create HTML structure, CSS for styling, and JavaScript for calculations." }
PLAN: { "step": "PLAN", "content": "Starting with HTML calculator layout with buttons and display." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "calculator.html\n<!DOCTYPE html>\n<html>\n<head>\n    <title>Calculator</title>\n    <link rel='stylesheet' href='calc-style.css'>\n</head>\n<body>\n    <div class='calculator'>\n        <div class='display' id='display'>0</div>\n        <div class='buttons'>\n            <button onclick='clearDisplay()'>C</button>\n            <button onclick='appendToDisplay(\"/\")'>/</button>\n            <button onclick='appendToDisplay(\"*\")'>*</button>\n            <button onclick='deleteLast()'>←</button>\n            <button onclick='appendToDisplay(\"7\")'>7</button>\n            <button onclick='appendToDisplay(\"8\")'>8</button>\n            <button onclick='appendToDisplay(\"9\")'>9</button>\n            <button onclick='appendToDisplay(\"-\")'>-</button>\n            <button onclick='calculate()'>=</button>\n        </div>\n    </div>\n    <script src='calc-script.js'></script>\n</body>\n</html>" }
OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'ai_projects/calculator_app/calculator.html' created successfully." }
PLAN: { "step": "PLAN", "content": "Now creating CSS for calculator styling and grid layout." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "calc-style.css\n.calculator { width: 300px; margin: 50px auto; border: 1px solid #ccc; border-radius: 10px; }\n.display { background: #000; color: #fff; font-size: 2em; padding: 20px; text-align: right; }\n.buttons { display: grid; grid-template-columns: repeat(4, 1fr); }\nbutton { padding: 20px; font-size: 1.2em; border: 1px solid #ddd; background: #f9f9f9; cursor: pointer; }\nbutton:hover { background: #e9e9e9; }\nbutton:active { background: #d9d9d9; }" }
OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'ai_projects/calculator_app/calc-style.css' created successfully." }
PLAN: { "step": "PLAN", "content": "Finally, adding JavaScript for calculator functionality and error handling." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "calc-script.js\nlet display = document.getElementById('display');\nlet currentInput = '0';\nlet shouldResetDisplay = false;\n\nfunction updateDisplay() {\n    display.textContent = currentInput;\n}\n\nfunction appendToDisplay(value) {\n    if (shouldResetDisplay) {\n        currentInput = '0';\n        shouldResetDisplay = false;\n    }\n    currentInput = currentInput === '0' ? value : currentInput + value;\n    updateDisplay();\n}\n\nfunction clearDisplay() {\n    currentInput = '0';\n    updateDisplay();\n}\n\nfunction deleteLast() {\n    currentInput = currentInput.length > 1 ? currentInput.slice(0, -1) : '0';\n    updateDisplay();\n}\n\nfunction calculate() {\n    try {\n        currentInput = eval(currentInput).toString();\n        shouldResetDisplay = true;\n        updateDisplay();\n    } catch (error) {\n        currentInput = 'Error';\n        shouldResetDisplay = true;\n        updateDisplay();\n    }\n}" }
OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'ai_projects/calculator_app/calc-script.js' created successfully." }
OUTPUT: { "step": "OUTPUT", "content": "Created a complete web calculator with 3 files: HTML layout, CSS styling, and JavaScript with error handling for calculations." }

Example 4 - Reading and analyzing:
START: Analyze my main.py file
PLAN: { "step": "PLAN", "content": "User wants code analysis. I'll read the file first, then analyze its structure." }
TOOL: { "step": "TOOL", "tool": "read_file", "input": "main.py" }
OBSERVE: { "step": "OBSERVE", "tool": "read_file", "output": "import os\ndef main():\n    print('Hello World')\nif __name__ == '__main__':\n    main()" }
PLAN: { "step": "PLAN", "content": "File is simple with basic structure. Now I'll analyze it formally." }
TOOL: { "step": "TOOL", "tool": "analyze_code", "input": "main.py" }
OBSERVE: { "step": "OBSERVE", "tool": "analyze_code", "output": "Code Analysis: 5 lines, 1 import, 1 function, follows Python best practices" }
OUTPUT: { "step": "OUTPUT", "content": "Your main.py is well-structured: 5 lines with 1 import and 1 function following Python conventions." }

Example 5 - Custom location:
START: Create a Python game in my_games folder
PLAN: { "step": "PLAN", "content": "User wants a Python game in custom location 'my_games'. I'll create a simple number guessing game." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "guess_game.py\nimport random\n\ndef play_game():\n    number = random.randint(1, 100)\n    attempts = 0\n    \n    print('Guess the number between 1 and 100!')\n    \n    while True:\n        try:\n            guess = int(input('Enter your guess: '))\n            attempts += 1\n            \n            if guess < number:\n                print('Too low!')\n            elif guess > number:\n                print('Too high!')\n            else:\n                print(f'Congratulations! You won in {attempts} attempts!')\n                break\n        except ValueError:\n            print('Please enter a valid number.')\n\nif __name__ == '__main__':\n    play_game()" }
OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'my_games/game_app/guess_game.py' created successfully." }
OUTPUT: { "step": "OUTPUT", "content": "Created a number guessing game in your custom my_games folder with error handling and attempt counting." }

Example 6 - Error handling:
TOOL: { "step": "TOOL", "tool": "write_file", "input": "nonexistent.py\nprint('test')" }
OBSERVE: { "step": "OBSERVE", "tool": "write_file", "output": "Error: File not found. Use create_file for new files." }
PLAN: { "step": "PLAN", "content": "File doesn't exist. I'll use create_file instead as suggested." }
TOOL: { "step": "TOOL", "tool": "create_file", "input": "nonexistent.py\nprint('test')" }
OBSERVE: File created successfully
OUTPUT: { "step": "OUTPUT", "content": "Successfully created the file after handling the initial error." }
"""

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")


def run_assistant(user_query, context=None, message_history=None, api_key=None, model="gpt-4o-mini"):
    """
    Run the assistant logic for a given user query and context.
    Returns the final output (string) and optionally the full message history.
    Uses the provided api_key for OpenAI authentication.
    
    Args:
        user_query (str): The user's input query
        context (dict): Optional context for the conversation
        message_history (list): Optional conversation history
        api_key (str): OpenAI API key
        model (str): OpenAI model to use (default: gpt-4o-mini)
    """
    from openai import OpenAI
    if api_key is None:
        import os
        api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    if message_history is None:
        message_history = [ { "role": "system", "content": SYSTEM_PROMPT } ]
    else:
        # Copy to avoid mutating caller's list
        message_history = list(message_history)
    message_history.append({ "role": "user", "content": user_query })

    while True:
        try:
            response = client.chat.completions.create(
                model=model,  # Use the provided model parameter
                messages=message_history,
                response_format={
                    "type": "json_schema", 
                    "json_schema": {
                        "name": "MyOutputFormat",
                        "schema": MyOutputFormat.model_json_schema()
                    }
                }
            )
            raw_result = response.choices[0].message.content
            message_history.append({"role": "assistant", "content": raw_result})
            try:
                parsed_result = json.loads(raw_result)
            except (json.JSONDecodeError, KeyError) as e:
                return f"Failed to parse AI response as JSON: {e}\nRaw response: {raw_result}", message_history
        except Exception as e:
            return f"API Error: {e}", message_history

        step = parsed_result.get("step")
        if step == "START" or step == "PLAN":
            # Continue loop for planning steps
            continue
        if step == "TOOL":
            tool_to_call = parsed_result.get("tool", "")
            tool_input = parsed_result.get("input", "")
            try:
                if tool_to_call not in available_tools:
                    tool_response = f"Error: Tool '{tool_to_call}' not found. Available tools: {list(available_tools.keys())}"
                else:
                    if tool_to_call == "create_file":
                        if not tool_input:
                            tool_response = "Error: No input provided for create_file"
                        else:
                            lines = tool_input.split('\n', 1)
                            file_path = lines[0].strip()
                            content = lines[1] if len(lines) > 1 else ""
                            if not file_path:
                                tool_response = "Error: No file path provided"
                            else:
                                tool_response = available_tools[tool_to_call](file_path, content, user_query)
                    elif tool_to_call == "write_file":
                        if not tool_input:
                            tool_response = "Error: No input provided for write_file"
                        else:
                            lines = tool_input.split('\n', 1)
                            file_path = lines[0].strip()
                            content = lines[1] if len(lines) > 1 else ""
                            if not file_path:
                                tool_response = "Error: No file path provided"
                            else:
                                tool_response = available_tools[tool_to_call](file_path, content)
                    else:
                        if not tool_input:
                            tool_response = f"Error: No input provided for {tool_to_call}"
                        else:
                            tool_response = available_tools[tool_to_call](tool_input)
            except Exception as e:
                tool_response = f"Error executing tool {tool_to_call}: {str(e)}"
            # Add OBSERVE step to message history
            message_history.append({ "role": "developer", "content": json.dumps(
                { "step": "OBSERVE", "tool": tool_to_call, "input": tool_input, "output": tool_response}
            ) })
            continue
        if step == "OUTPUT":
            return parsed_result.get("content", ""), message_history
