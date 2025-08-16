#!/usr/bin/env python3
"""
Simple wrapper to run quiz for specific tools
This replaces quiz.py, quiz_vscode.py, etc.
"""

import sys
from pathlib import Path

# Import the main quiz system
from quiz_system import ShortcutQuiz, select_shortcuts_file

def run_tool_quiz(tool_name: str = None):
    """Run quiz for a specific tool or let user choose"""
    
    # Map common tool names to their JSON files
    tool_map = {
        'vscode': 'shortcuts_vscode.json',
        'macos': 'shortcuts_macos.json',
        'asana': 'shortcuts_asana.json',
        'chrome': 'shortcuts_chrome.json',
        'slack': 'shortcuts_slack.json',
    }
    
    # Determine which file to use
    shortcuts_file = None
    
    if tool_name and tool_name.lower() in tool_map:
        shortcuts_file = tool_map[tool_name.lower()]
        if not Path(shortcuts_file).exists():
            print(f"❌ {shortcuts_file} not found!")
            shortcuts_file = None
    elif len(sys.argv) > 1:
        # Check if a file was passed as argument
        if Path(sys.argv[1]).exists():
            shortcuts_file = sys.argv[1]
        elif sys.argv[1].lower() in tool_map:
            shortcuts_file = tool_map[sys.argv[1].lower()]
    
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
    #   python run_quiz.py shortcuts_custom.json
    #   python run_quiz.py  (interactive selection)
    
    run_tool_quiz()