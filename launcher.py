#!/usr/bin/env python3
"""
HotKey Trainer v2.0 - Main Launcher
Clean, modular launcher for the keyboard shortcut training system
"""

import subprocess
import time
import sys
import os
import json
import signal
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from trainer_core import TrainerCore, InterceptorManager


@dataclass
class Tool:
    """Represents a tool with keyboard shortcuts"""
    file: str
    name: str
    icon: str
    description: str
    shortcut_count: int


class MenuOption:
    """Menu option configuration"""
    def __init__(self, key: str, label: str, description: str, action):
        self.key = key
        self.label = label
        self.description = description
        self.action = action


class TrainerLauncher(TrainerCore):
    """Main launcher for HotKey Trainer"""
    
    VERSION = "2.0"
    REQUIRED_FILES = ['viewer.py', 'quiz_system.py', 'trainer_core.py']
    
    def __init__(self):
        super().__init__()
        self.interceptor = InterceptorManager()
        self.running = True
        self.tools = []
        self._load_tools()
    
    def _load_tools(self):
        """Load available tools from JSON files"""
        self.tools = []
        for json_file in sorted(Path('.').glob('shortcuts_*.json')):
            tool = self._parse_tool_file(json_file)
            if tool:
                self.tools.append(tool)
    
    def _parse_tool_file(self, json_file: Path) -> Optional[Tool]:
        """Parse a tool configuration file"""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                return Tool(
                    file=str(json_file),
                    name=data.get('name', json_file.stem),
                    icon=data.get('icon', '🎮'),
                    description=data.get('description', ''),
                    shortcut_count=len(data.get('shortcuts', []))
                )
        except (json.JSONDecodeError, KeyError, IOError):
            return None
    
    def check_prerequisites(self) -> bool:
        """Verify all required components are present"""
        issues = []
        
        # Check interceptor
        if not self.interceptor.check_built():
            issues.append("Interceptor not built (run ./setup.sh first)")
        
        # Check required Python files
        for file in self.REQUIRED_FILES:
            if not Path(file).exists():
                issues.append(f"Missing {file}")
        
        # Check for shortcut files
        if not self.tools:
            issues.append("No shortcut files found (shortcuts_*.json)")
        
        if issues:
            self._display_issues(issues)
            return False
        
        return True
    
    def _display_issues(self, issues: List[str]):
        """Display prerequisite issues"""
        self.print_color("❌ Prerequisites check failed:", 'RED')
        for issue in issues:
            print(f"  • {issue}")
    
    def display_menu(self) -> Optional[str]:
        """Display main menu and get user choice"""
        self._show_status()
        options = self._build_menu_options()
        self._display_menu_options(options)
        return self._get_menu_choice(options)
    
    def _show_status(self):
        """Show current trainer status"""
        if self.is_trainer_active():
            self.print_color("Status: 🔴 Trainer ON (keys blocked)", 'RED')
        else:
            self.print_color("Status: 🟢 Trainer OFF (keys normal)", 'GREEN')
        print()
    
    def _build_menu_options(self) -> Dict[str, MenuOption]:
        """Build available menu options"""
        options = {}
        option_num = 1
        
        # Core features
        options[str(option_num)] = MenuOption(
            'viewer',
            "👁️ Real-time Key Viewer",
            "See what keys you're pressing",
            self.run_viewer
        )
        option_num += 1
        
        # Tool-specific practice
        if self.tools:
            for tool in self.tools:
                options[str(option_num)] = MenuOption(
                    ('quiz', tool.file),
                    f"{tool.icon} {tool.name} Practice",
                    tool.description or f"Practice {tool.shortcut_count} shortcuts",
                    lambda t=tool: self.run_quiz(t.file)
                )
                option_num += 1
        
        # Utility options
        utility_options = [
            MenuOption('freestyle', "🎯 Freestyle Practice", 
                      "Manual control mode", self.run_freestyle),
            MenuOption('status', "🔧 Interceptor Status", 
                      "Check/restart interceptor", self.check_interceptor_status),
            MenuOption('add_tool', "➕ Add New Tool", 
                      "Create shortcuts for a new tool", self.create_new_tool),
            MenuOption('exit', "❌ Exit", "", self.exit_launcher)
        ]
        
        for opt in utility_options:
            options[str(option_num)] = opt
            option_num += 1
        
        return options
    
    def _display_menu_options(self, options: Dict[str, MenuOption]):
        """Display menu options organized by category"""
        self.print_color("Choose an option:", 'MAGENTA')
        print()
        
        # Group options by type
        practice_options = []
        utility_options = []
        
        for key, opt in options.items():
            if isinstance(opt.key, tuple) and opt.key[0] == 'quiz':
                practice_options.append((key, opt))
            elif opt.key in ['viewer', 'freestyle']:
                practice_options.insert(0, (key, opt))
            else:
                utility_options.append((key, opt))
        
        # Display practice options
        if practice_options:
            for key, opt in practice_options[:2]:  # Viewer and freestyle
                self._display_single_option(key, opt)
            
            if len(practice_options) > 2:
                print()
                self.print_color("Practice Shortcuts:", 'CYAN')
                for key, opt in practice_options[2:]:
                    self._display_single_option(key, opt)
        
        # Display utility options
        if utility_options:
            print()
            for key, opt in utility_options:
                self._display_single_option(key, opt)
    
    def _display_single_option(self, key: str, option: MenuOption):
        """Display a single menu option"""
        print(f"  {key}) {option.label}")
        if option.description:
            print(f"     ", end="")
            self.print_color(option.description, 'BLUE')
    
    def _get_menu_choice(self, options: Dict[str, MenuOption]) -> Optional[str]:
        """Get and validate user menu choice"""
        max_option = len(options)
        print()
        choice = input(f"Enter choice [1-{max_option}]: ")
        return choice if choice in options else None
    
    def run_viewer(self):
        """Launch the real-time key viewer"""
        self.print_color("\n👁️ Starting Real-time Key Viewer...", 'GREEN')
        print("The trainer will activate automatically")
        time.sleep(1)
        subprocess.run([sys.executable, "viewer.py"])
    
    def run_quiz(self, shortcuts_file: str):
        """Launch practice quiz for specific tool"""
        self.print_color(f"\n🎮 Starting Practice Quiz...", 'GREEN')
        print("The trainer will activate automatically")
        time.sleep(1)
        subprocess.run([sys.executable, "quiz_system.py", shortcuts_file])
    
    def run_freestyle(self):
        """Launch freestyle practice mode"""
        self.print_color("\n🎯 Starting Freestyle Practice...", 'GREEN')
        self._display_freestyle_instructions()
        input("Press Enter to continue...")
        
        # Switch to foreground mode
        self.interceptor.stop(silent=True)
        try:
            self.interceptor.run_foreground()
        except KeyboardInterrupt:
            print("\nReturning to menu...")
        
        # Restart in background
        self.interceptor.start(silent=True)
    
    def _display_freestyle_instructions(self):
        """Display freestyle mode instructions"""
        print("\nManual Control Mode:")
        print("  • Press ", end="")
        self.print_color("Cmd+Shift+-", 'MAGENTA')
        print(" to toggle trainer")
        print("  • ", end="")
        self.print_color("🔴", 'RED')
        print(" = Keys blocked (practice mode)")
        print("  • ", end="")
        self.print_color("🟢", 'GREEN')
        print(" = Keys normal")
        print("  • Press ", end="")
        self.print_color("Ctrl+C", 'MAGENTA')
        print(" to return to menu\n")
    
    def check_interceptor_status(self):
        """Check and manage interceptor status"""
        self.print_color("\n🔧 Interceptor Status", 'CYAN')
        print("-" * 30)
        
        if self.interceptor.is_running():
            self._handle_running_interceptor()
        else:
            self._handle_stopped_interceptor()
    
    def _handle_running_interceptor(self):
        """Handle running interceptor status"""
        pid = self.interceptor.get_pid()
        self.print_color(f"✅ Running (PID: {pid})", 'GREEN')
        
        choice = input("\nRestart interceptor? (y/n): ")
        if choice.lower() == 'y':
            self._restart_interceptor()
    
    def _handle_stopped_interceptor(self):
        """Handle stopped interceptor status"""
        self.print_color("❌ Not running", 'RED')
        
        choice = input("\nStart interceptor? (y/n): ")
        if choice.lower() == 'y':
            self._start_interceptor()
    
    def _restart_interceptor(self):
        """Restart the interceptor"""
        self.interceptor.stop()
        time.sleep(0.5)
        success, pid = self.interceptor.start()
        if success:
            self.print_color(f"✅ Restarted (PID: {pid})", 'GREEN')
        else:
            self.print_color("❌ Failed to restart", 'RED')
    
    def _start_interceptor(self):
        """Start the interceptor"""
        success, pid = self.interceptor.start()
        if success:
            self.print_color(f"✅ Started (PID: {pid})", 'GREEN')
        else:
            self.print_color("❌ Failed to start", 'RED')
    
    def create_new_tool(self):
        """Create a new tool configuration"""
        creator = ToolCreator(self)
        creator.create()
        self._load_tools()  # Reload tools after creation
    
    def exit_launcher(self):
        """Exit the launcher"""
        self.running = False
    
    def cleanup(self):
        """Clean up resources on exit"""
        print()
        self.print_color("🧹 Cleaning up...", 'YELLOW')
        self.interceptor.stop()
        self.print_color("👋 Goodbye!", 'GREEN')
    
    def signal_handler(self, sig, frame):
        """Handle interrupt signals gracefully"""
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Main application loop"""
        # Check prerequisites
        if not self.check_prerequisites():
            print("\nPlease fix the issues above and try again.")
            sys.exit(1)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            self._initialize()
            self._main_loop()
        finally:
            self.cleanup()
    
    def _initialize(self):
        """Initialize the application"""
        self.show_header(f"🎮 HotKey Trainer v{self.VERSION}")
        
        # Start interceptor
        success, pid = self.interceptor.start()
        if not success:
            self.print_color("Failed to start interceptor.", 'RED')
            print("Try running with sudo or check permissions.")
            sys.exit(1)
        
        self.print_color(f"✅ Interceptor running (PID: {pid})", 'GREEN')
        self._display_available_tools()
    
    def _display_available_tools(self):
        """Display available tools summary"""
        if self.tools:
            print(f"\n📚 {len(self.tools)} tool(s) available for practice:")
            for tool in self.tools:
                print(f"   {tool.icon} {tool.name} ({tool.shortcut_count} shortcuts)")
        print()
    
    def _main_loop(self):
        """Main menu loop"""
        while self.running:
            choice = self.display_menu()
            
            if choice is None:
                self._handle_invalid_choice()
            else:
                self._execute_menu_choice(choice)
    
    def _handle_invalid_choice(self):
        """Handle invalid menu choice"""
        self.print_color("❌ Invalid choice. Please try again.", 'RED')
        time.sleep(1)
        self.show_header(f"🎮 HotKey Trainer v{self.VERSION}")
    
    def _execute_menu_choice(self, choice: str):
        """Execute the selected menu option"""
        options = self._build_menu_options()
        if choice in options:
            options[choice].action()
            
            # Post-action handling
            if options[choice].key != 'exit':
                input("\nPress Enter to continue...")
                self.show_header(f"🎮 HotKey Trainer v{self.VERSION}")


class ToolCreator:
    """Helper class for creating new tool configurations"""
    
    def __init__(self, launcher: TrainerLauncher):
        self.launcher = launcher
    
    def create(self):
        """Interactive tool creation process"""
        self.launcher.print_color("\n➕ Create New Tool", 'CYAN')
        print("-" * 30)
        
        print("\nThis will help you create a shortcuts JSON file for a new tool.")
        print("You can also manually create a shortcuts_[toolname].json file.\n")
        
        # Gather information
        tool_info = self._gather_tool_info()
        if not tool_info:
            print("Cancelled.")
            return
        
        # Create and save template
        template = self._create_template(tool_info)
        filename = self._save_template(template, tool_info['name'])
        
        if filename:
            self._display_success(filename)
    
    def _gather_tool_info(self) -> Optional[Dict[str, str]]:
        """Gather tool information from user"""
        tool_name = input("Tool name (e.g., 'Chrome', 'Slack'): ").strip()
        if not tool_name:
            return None
        
        tool_icon = input("Icon emoji (press Enter for default 🎮): ").strip() or "🎮"
        tool_desc = input("Description (optional): ").strip()
        
        return {
            'name': tool_name,
            'icon': tool_icon,
            'description': tool_desc
        }
    
    def _create_template(self, tool_info: Dict[str, str]) -> Dict:
        """Create JSON template for new tool"""
        return {
            "name": tool_info['name'],
            "description": tool_info['description'],
            "icon": tool_info['icon'],
            "version": "1.0.0",
            "categories": {
                "basic": {
                    "name": "Basic",
                    "color": "green",
                    "icon": "🟢"
                }
            },
            "shortcuts": [
                {
                    "keys": "cmd+n",
                    "description": "Example shortcut - replace this",
                    "category": "basic",
                    "difficulty": 1,
                    "tips": ["Replace this with actual shortcuts"]
                }
            ],
            "practice_sets": {
                "all": {
                    "name": "All Shortcuts",
                    "description": "Practice all shortcuts",
                    "shortcut_indices": None
                }
            }
        }
    
    def _save_template(self, template: Dict, tool_name: str) -> Optional[str]:
        """Save template to file"""
        filename = f"shortcuts_{tool_name.lower().replace(' ', '_')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(template, f, indent=2)
            return filename
        except Exception as e:
            self.launcher.print_color(f"❌ Error creating file: {e}", 'RED')
            return None
    
    def _display_success(self, filename: str):
        """Display success message and next steps"""
        self.launcher.print_color(f"\n✅ Created {filename}", 'GREEN')
        print("\nNext steps:")
        print(f"1. Edit {filename} to add your shortcuts")
        print("2. Restart the launcher to see your new tool")
        print("\nExample shortcut format:")
        print('''  {
    "keys": "cmd+shift+p",
    "description": "Command palette",
    "category": "basic",
    "difficulty": 1,
    "tips": ["Opens command palette", "Search for any command"]
  }''')


def main():
    """Main entry point"""
    launcher = TrainerLauncher()
    launcher.run()


if __name__ == "__main__":
    main()