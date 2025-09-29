"""
Tool functions for the coding assistant agent.
Contains all the available tools that the agent can use to help with coding tasks.
"""

import os


def run_command(cmd: str):
    """Execute system commands for build tools, git, package managers, etc."""
    result = os.system(cmd)
    return f"Command executed with exit code: {result}"


def create_file(file_path: str, content: str):
    """Create a new file with the specified content."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{file_path}' created successfully."
    except Exception as e:
        return f"Error creating file: {str(e)}"


def read_file(file_path: str):
    """Read the contents of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File contents:\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str):
    """Write content to an existing file (overwrites existing content)."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{file_path}' updated successfully."
    except Exception as e:
        return f"Error writing to file: {str(e)}"


def analyze_code(file_path: str):
    """Analyze code structure and provide basic feedback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        line_count = len(lines)
        
        # Basic analysis
        imports = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
        functions = [line for line in lines if line.strip().startswith('def ')]
        classes = [line for line in lines if line.strip().startswith('class ')]
        
        analysis = f"Code Analysis for '{file_path}':\n"
        analysis += f"- Total lines: {line_count}\n"
        analysis += f"- Imports: {len(imports)}\n"
        analysis += f"- Functions: {len(functions)}\n"
        analysis += f"- Classes: {len(classes)}\n\n"
        
        if imports:
            analysis += "Imports found:\n"
            for imp in imports[:5]:  # Show first 5 imports
                analysis += f"  {imp.strip()}\n"
        
        return analysis
    except Exception as e:
        return f"Error analyzing code: {str(e)}"


# Dictionary of all available tools
AVAILABLE_TOOLS = {
    "run_command": run_command,
    "create_file": create_file,
    "read_file": read_file,
    "write_file": write_file,
    "analyze_code": analyze_code
}