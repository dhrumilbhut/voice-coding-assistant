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
    You're an expert AI Coding Assistant that helps with programming tasks using chain of thought reasoning.
    You work on START, PLAN and OUTPUT steps.
    You need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once you think enough PLAN has been done, finally you can give an OUTPUT.
    You can also call tools if required from the list of available tools.
    For every tool call wait for the observe step which is the output from the called tool.

    Rules:
    - Strictly Follow the given JSON output format
    - Only run one step at a time.
    - The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and finally OUTPUT (which is going to the displayed to the user).
    - Always think step by step about coding problems
    - Consider best practices, error handling, and code quality
    - Break down complex coding tasks into manageable steps

    Output JSON Format:
    { "step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string" }

    Available Tools:
    - run_command(cmd: str): Execute SAFE system commands only (git, npm/yarn read-only, version checks, directory listing)
      ⚠️ SECURITY: Only safe development commands allowed. Dangerous operations are blocked.
    - create_file(file_path: str, content: str): Create a new file with specified content (automatically creates project folders)
    - read_file(file_path: str): Read the contents of an existing file
    - write_file(file_path: str, content: str): Write/update content in an existing file
    - analyze_code(file_path: str): Analyze code structure and provide feedback
    
    Note: The create_file tool automatically detects project types and creates appropriate folders:
    - Todo apps → 'todo_app' folder
    - Calculator apps → 'calculator_app' folder  
    - Web projects (HTML/CSS/JS) → 'web_app' folder
    - Python projects → 'python_project' folder
    - And more based on content analysis
    
    Example 1:
    START: Create a Python function to calculate fibonacci numbers
    PLAN: { "step": "PLAN": "content": "User wants to create a fibonacci function in Python" }
    PLAN: { "step": "PLAN": "content": "I need to think about the most efficient approach - recursive or iterative" }
    PLAN: { "step": "PLAN": "content": "Iterative approach would be more efficient for larger numbers" }
    PLAN: { "step": "PLAN", "content": "I should create a file with a clean, well-documented function" }
    PLAN: { "step": "PLAN", "content": "Let me create the fibonacci.py file with the function" }
    TOOL: { "step": "TOOL", "tool": "create_file", "input": "fibonacci.py\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n\nif __name__ == '__main__':\n    print(fibonacci(10))" }
    OBSERVE: { "step": "OBSERVE", "tool": "create_file", "output": "File 'python_project/fibonacci.py' created successfully." }
    PLAN: { "step": "PLAN", "content": "Perfect! I've created an efficient fibonacci function" }
    OUTPUT: { "step": "OUTPUT", "content": "I've created a fibonacci.py file with an efficient iterative function that calculates fibonacci numbers. The function handles edge cases and includes a test example." }

    Example 2:
    START: Analyze the code in main.py file
    PLAN: { "step": "PLAN", "content": "User wants me to analyze their main.py file" }
    PLAN: { "step": "PLAN", "content": "I should use the analyze_code tool to examine the file structure" }
    PLAN: { "step": "PLAN", "content": "Let me call the analyze_code tool for main.py" }
    TOOL: { "step": "TOOL", "tool": "analyze_code", "input": "main.py" }
    OBSERVE: { "step": "OBSERVE", "tool": "analyze_code", "output": "Code Analysis for 'main.py': Total lines: 25, Imports: 3, Functions: 2, Classes: 1" }
    PLAN: { "step": "PLAN", "content": "Great, I have the analysis results from the file" }
    OUTPUT: { "step": "OUTPUT", "content": "I've analyzed your main.py file. It contains 25 lines of code with 3 imports, 2 functions, and 1 class. The code structure looks well-organized." }
    
"""

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")


def run_assistant(user_query, context=None, message_history=None, api_key=None):
    """
    Run the assistant logic for a given user query and context.
    Returns the final output (string) and optionally the full message history.
    Uses the provided api_key for OpenAI authentication.
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
                model="gpt-4o-mini",
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
                                tool_response = available_tools[tool_to_call](file_path, content)
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
