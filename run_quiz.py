#!/usr/bin/env python3
"""
Simple wrapper to run quiz for specific tools
Works with new naming convention (tool.json instead of shortcuts_tool.json)
"""

import sys
from pathlib import Path

# Import the main quiz system
from quiz_system import ShortcutQuiz, select_shortcuts_file

def run_tool_quiz(tool_name: str = None):
    """Run quiz for a specific tool or let user choose"""
    
    # Define tools directory
    TOOLS_DIR = Path('tools')
    
    # Map common tool names to their JSON files (new naming)
    tool_map = {
        'vscode': 'vscode.json',
        'macos': 'macos.json',
        'asana': 'asana.json',
        'chrome': 'chrome.json',
        'slack': 'slack.json',
    }
    
    # Also support legacy naming for backwards compatibility
    legacy_map = {
        'vscode': 'shortcuts_vscode.json',
        'macos': 'shortcuts_macos.json',
        'asana': 'shortcuts_asana.json',
        'chrome': 'shortcuts_chrome.json',
        'slack': 'shortcuts_slack.json',
    }
    
    # Determine which file to use
    shortcuts_file = None
    
    if tool_name and tool_name.lower() in tool_map:
        # Try new naming first
        tools_file = TOOLS_DIR / tool_map[tool_name.lower()]
        if tools_file.exists():
            shortcuts_file = str(tools_file)
        # Try legacy naming in tools dir
        elif (TOOLS_DIR / legacy_map[tool_name.lower()]).exists():
            shortcuts_file = str(TOOLS_DIR / legacy_map[tool_name.lower()])
        # Fallback to current directory for backwards compatibility
        elif Path(tool_map[tool_name.lower()]).exists():
            shortcuts_file = tool_map[tool_name.lower()]
        elif Path(legacy_map[tool_name.lower()]).exists():
            shortcuts_file = legacy_map[tool_name.lower()]
        else:
            print(f"❌ {tool_map[tool_name.lower()]} not found!")
            print(f"Please ensure the file exists in the 'tools' directory")
            shortcuts_file = None
            
    elif len(sys.argv) > 1:
        # Check if a file was passed as argument
        arg_path = Path(sys.argv[1])
        
        # Check if it's a full path
        if arg_path.exists():
            shortcuts_file = str(arg_path)
        # Check in tools directory
        elif (TOOLS_DIR / arg_path).exists():
            shortcuts_file = str(TOOLS_DIR / arg_path)
        # Check if it's a tool name
        elif sys.argv[1].lower() in tool_map:
            # Try new naming
            tools_file = TOOLS_DIR / tool_map[sys.argv[1].lower()]
            if tools_file.exists():
                shortcuts_file = str(tools_file)
            # Try legacy naming
            elif (TOOLS_DIR / legacy_map[sys.argv[1].lower()]).exists():
                shortcuts_file = str(TOOLS_DIR / legacy_map[sys.argv[1].lower()])
            elif Path(tool_map[sys.argv[1].lower()]).exists():
                shortcuts_file = tool_map[sys.argv[1].lower()]
            elif Path(legacy_map[sys.argv[1].lower()]).exists():
                shortcuts_file = legacy_map[sys.argv[1].lower()]
    
    # If no file determined, let user choose
    if not shortcuts_file:
        shortcuts_file = select_shortcuts_file()
    
    if not shortcuts_file:
        print("No tool selected. Exiting.")
        sys.exit(1)
    
    # Run the quiz
    try:
        quiz = ShortcutQuiz(shortcuts_file)
        quiz.run_quiz()
    except KeyboardInterrupt:
        print("\n\n⚠️  Practice interrupted!")
        print("Your keyboard is back to normal.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Quick shortcuts for common tools
    # Usage: python run_quiz.py [tool_name or json_file]
    # Examples:
    #   python run_quiz.py vscode
    #   python run_quiz.py asana.json
    #   python run_quiz.py  (interactive selection)
    
    run_tool_quiz()