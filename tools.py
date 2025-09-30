"""
Tool functions for the coding assistant agent.
Contains all the available tools that the agent can use to help with coding tasks.
"""

import os
import re
from pathlib import Path


def run_command(cmd: str):
    """Execute system commands for build tools, git, package managers, etc."""
    result = os.system(cmd)
    return f"Command executed with exit code: {result}"


def detect_project_name(file_path: str, content: str):
    """Detect project name from file path or content."""
    # Check if file_path already contains a folder
    if '/' in file_path or '\\' in file_path:
        return None  # Don't modify if already in a folder
    
    # Common project indicators in filenames
    project_patterns = {
        'todo': ['todo', 'task', 'checklist'],
        'calculator': ['calc', 'calculator', 'math'],
        'weather': ['weather', 'forecast', 'climate'],
        'blog': ['blog', 'post', 'article'],
        'portfolio': ['portfolio', 'resume', 'cv'],
        'ecommerce': ['shop', 'store', 'cart', 'ecommerce'],
        'dashboard': ['dashboard', 'admin', 'panel'],
        'chat': ['chat', 'message', 'messenger'],
        'game': ['game', 'puzzle', 'play'],
        'landing': ['landing', 'home', 'index']
    }
    
    # Check filename
    filename_lower = file_path.lower()
    for project, keywords in project_patterns.items():
        if any(keyword in filename_lower for keyword in keywords):
            return f"{project}_app"
    
    # Check content for project indicators
    content_lower = content.lower()
    for project, keywords in project_patterns.items():
        if any(keyword in content_lower for keyword in keywords):
            return f"{project}_app"
    
    # Check for common HTML patterns
    if file_path.endswith('.html'):
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean title for folder name
            clean_title = re.sub(r'[^\w\s-]', '', title).strip()
            clean_title = re.sub(r'[-\s]+', '_', clean_title).lower()
            if clean_title and len(clean_title) > 2:
                return clean_title
    
    # Default project name based on file types
    if file_path.endswith(('.html', '.css', '.js')):
        return 'web_app'
    elif file_path.endswith('.py'):
        return 'python_project'
    
    return None


def create_file(file_path: str, content: str):
    """Create a new file with the specified content in appropriate project folder."""
    try:
        # Detect if this should be in a project folder
        project_name = detect_project_name(file_path, content)
        
        if project_name:
            # Create project folder if it doesn't exist
            project_path = Path(project_name)
            project_path.mkdir(exist_ok=True)
            
            # Update file path to be inside project folder
            file_path = project_path / file_path
            
            print(f"📁 Creating project folder: {project_name}")
        
        # Create the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"File '{file_path}' created successfully."
    except Exception as e:
        return f"Error creating file: {str(e)}"


def read_file(file_path: str):
    """Read the contents of a file."""
    try:
        # Check if file exists in current directory first
        if not os.path.exists(file_path):
            # Look for the file in project folders
            for item in os.listdir('.'):
                if os.path.isdir(item):
                    potential_path = Path(item) / file_path
                    if potential_path.exists():
                        file_path = potential_path
                        break
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File contents:\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str):
    """Write content to an existing file (overwrites existing content)."""
    try:
        # Check if file exists in current directory or project folders
        if not os.path.exists(file_path):
            # Look for the file in project folders
            for item in os.listdir('.'):
                if os.path.isdir(item):
                    potential_path = Path(item) / file_path
                    if potential_path.exists():
                        file_path = potential_path
                        break
        
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