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
    REQUIRED_FILES = ['viewer.py', 'quiz_system.py', 'trainer_core.py', 'typing_test.py']
    TOOLS_DIR = Path('tools')
    
    def __init__(self):
        super().__init__()
        self.interceptor = InterceptorManager()
        self.running = True
        self.tools = []
        self.current_menu = 'main'  # Track current menu
        self._ensure_tools_directory()
        self._load_tools()
    
    def _ensure_tools_directory(self):
        """Create tools directory if it doesn't exist"""
        if not self.TOOLS_DIR.exists():
            self.TOOLS_DIR.mkdir(parents=True, exist_ok=True)
            self.print_color(f"📁 Created '{self.TOOLS_DIR}' directory for tool configurations", 'GREEN')
    
    def _load_tools(self):
        """Load available tools from JSON files in tools directory"""
        self.tools = []
        
        # First check tools directory
        json_files = list(self.TOOLS_DIR.glob('shortcuts_*.json'))
        
        # If no files in tools dir, check for files in current directory (for migration)
        legacy_files = []
        if not json_files:
            legacy_files = list(Path('.').glob('shortcuts_*.json'))
            if legacy_files:
                self._offer_migration(legacy_files)
                # Reload from tools directory after migration
                json_files = list(self.TOOLS_DIR.glob('shortcuts_*.json'))
        
        # Parse found files
        for json_file in sorted(json_files):
            tool = self._parse_tool_file(json_file)
            if tool:
                self.tools.append(tool)
    
    def _offer_migration(self, legacy_files: List[Path]):
        """Offer to migrate JSON files to tools directory"""
        self.print_color("\n📦 Found tool files in the main directory!", 'YELLOW')
        print(f"Would you like to move them to the '{self.TOOLS_DIR}' folder for better organization?")
        print("\nFiles found:")
        for file in legacy_files:
            print(f"  • {file.name}")
        
        choice = input("\nMove files to tools folder? (y/n): ")
        if choice.lower() == 'y':
            self._migrate_files(legacy_files)
    
    def _migrate_files(self, files: List[Path]):
        """Move JSON files to tools directory"""
        import shutil
        
        self.print_color("\n🚀 Migrating files...", 'CYAN')
        for file in files:
            try:
                dest = self.TOOLS_DIR / file.name
                shutil.move(str(file), str(dest))
                print(f"  ✅ Moved {file.name}")
            except Exception as e:
                print(f"  ❌ Failed to move {file.name}: {e}")
        
        self.print_color("\n✨ Migration complete!", 'GREEN')
        time.sleep(1)
    
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
        
        if issues:
            self._display_issues(issues)
            return False
        
        return True
    
    def _display_issues(self, issues: List[str]):
        """Display prerequisite issues"""
        self.print_color("❌ Prerequisites check failed:", 'RED')
        for issue in issues:
            print(f"  • {issue}")
    
    def display_main_menu(self) -> Optional[str]:
        """Display streamlined main menu"""
        self._show_status()
        
        print("Choose an option:")
        print()
        print("  1) 🎯 Select Tool to Practice")
        print("  2) ⌨️  Typing Test")
        print("  3) ⚙️  Settings")
        print("  4) ❌ Exit")
        print()
        
        choice = input("Enter choice [1-4]: ")
        return choice if choice in ['1', '2', '3', '4'] else None
    
    def display_tools_menu(self) -> Optional[str]:
        """Display tool selection menu"""
        self.show_header("🎯 SELECT TOOL TO PRACTICE")
        
        if not self.tools:
            self.print_color("📂 No tools found!", 'YELLOW')
            print(f"Add shortcuts_*.json files to '{self.TOOLS_DIR}' directory")
            print()
            print("  0) ← Back to Main Menu")
            print()
            choice = input("Enter choice: ")
            return choice
        
        print("Available tools:")
        print()
        
        for i, tool in enumerate(self.tools, 1):
            print(f"  {i}) {tool.icon} {tool.name}")
            if tool.description:
                print(f"     {tool.description} ({tool.shortcut_count} shortcuts)")
            else:
                print(f"     {tool.shortcut_count} shortcuts")
            print()
        
        print(f"  0) ← Back to Main Menu")
        print()
        
        max_option = len(self.tools)
        choice = input(f"Enter choice [0-{max_option}]: ")
        
        # Validate choice
        try:
            choice_num = int(choice)
            if 0 <= choice_num <= max_option:
                return choice
        except ValueError:
            pass
        
        return None
    
    def display_settings_menu(self) -> Optional[str]:
        """Display settings menu"""
        self.show_header("⚙️ SETTINGS")
        
        print("Tools & Utilities:")
        print()
        print("  1) 👁️ Real-time Key Viewer")
        print("     See what keys you're pressing")
        print()
        print("  2) 🎯 Freestyle Practice")
        print("     Manual control mode")
        print()
        print("  3) 🔧 Interceptor Status")
        print("     Check/restart interceptor")
        print()
        print("  4) ➕ Add New Tool")
        print("     Create shortcuts for a new tool")
        print()
        print("  5) 📂 Open Tools Folder")
        print("     Open the tools folder in Finder")
        print()
        print("  0) ← Back to Main Menu")
        print()
        
        choice = input("Enter choice [0-5]: ")
        return choice if choice in ['0', '1', '2', '3', '4', '5'] else None
    
    def _show_status(self):
        """Show current trainer status"""
        if self.is_trainer_active():
            self.print_color("Status: 🔴 Trainer ON (keys blocked)", 'RED')
        else:
            self.print_color("Status: 🟢 Trainer OFF (keys normal)", 'GREEN')
        print()
    
    def handle_main_menu_choice(self, choice: str):
        """Handle main menu selection"""
        if choice == '1':
            # Go to tools menu
            self.current_menu = 'tools'
        elif choice == '2':
            # Run typing test
            self.run_typing_test()
        elif choice == '3':
            # Go to settings menu
            self.current_menu = 'settings'
        elif choice == '4':
            # Exit
            self.exit_launcher()
    
    def handle_tools_menu_choice(self, choice: str):
        """Handle tools menu selection"""
        if choice == '0':
            self.current_menu = 'main'
            return
        
        try:
            tool_index = int(choice) - 1
            if 0 <= tool_index < len(self.tools):
                self.run_quiz(self.tools[tool_index].file)
        except (ValueError, IndexError):
            pass
    
    def handle_settings_menu_choice(self, choice: str):
        """Handle settings menu selection"""
        if choice == '0':
            self.current_menu = 'main'
        elif choice == '1':
            self.run_viewer()
        elif choice == '2':
            self.run_freestyle()
        elif choice == '3':
            self.check_interceptor_status()
        elif choice == '4':
            self.create_new_tool()
            self._load_tools()  # Reload tools after creation
        elif choice == '5':
            self.open_tools_folder()
    
    def run_typing_test(self):
        """Launch the typing test"""
        self.print_color("\n⌨️ Starting Typing Test...", 'GREEN')
        print("The trainer will activate automatically")
        time.sleep(1)
        subprocess.run([sys.executable, "typing_test.py"])
    
    def open_tools_folder(self):
        """Open the tools folder in Finder"""
        self.print_color(f"\n📂 Opening '{self.TOOLS_DIR}' folder...", 'CYAN')
        subprocess.run(['open', str(self.TOOLS_DIR.absolute())])
        print(f"You can add or edit JSON files here.")
        print(f"Files should be named: shortcuts_[toolname].json")
    
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
        
        # Show available resources
        if self.tools:
            print(f"📚 {len(self.tools)} tool(s) available for practice")
        else:
            self.print_color(f"📂 No tools found in '{self.TOOLS_DIR}' folder", 'YELLOW')
        print()
    
    def _main_loop(self):
        """Main menu loop"""
        while self.running:
            # Display appropriate menu based on current state
            if self.current_menu == 'main':
                choice = self.display_main_menu()
                if choice:
                    self.handle_main_menu_choice(choice)
                else:
                    self._handle_invalid_choice()
                    
            elif self.current_menu == 'tools':
                choice = self.display_tools_menu()
                if choice:
                    self.handle_tools_menu_choice(choice)
                else:
                    self._handle_invalid_choice()
                
                # Stay in tools menu unless going back
                if choice != '0':
                    input("\nPress Enter to continue...")
                    
            elif self.current_menu == 'settings':
                choice = self.display_settings_menu()
                if choice:
                    self.handle_settings_menu_choice(choice)
                else:
                    self._handle_invalid_choice()
                
                # Stay in settings menu unless going back
                if choice != '0':
                    input("\nPress Enter to continue...")
            
            # Clear screen for next iteration
            if self.running and self.current_menu == 'main':
                self.show_header(f"🎮 HotKey Trainer v{self.VERSION}")
    
    def _handle_invalid_choice(self):
        """Handle invalid menu choice"""
        self.print_color("❌ Invalid choice. Please try again.", 'RED')
        time.sleep(1)


class ToolCreator:
    """Helper class for creating new tool configurations"""
    
    def __init__(self, launcher: TrainerLauncher):
        self.launcher = launcher
    
    def create(self):
        """Interactive tool creation process"""
        self.launcher.print_color("\n➕ Create New Tool", 'CYAN')
        print("-" * 30)
        
        print("\nThis will help you create a shortcuts JSON file for a new tool.")
        print(f"The file will be saved in the '{self.launcher.TOOLS_DIR}' folder.\n")
        
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
        """Save template to file in tools directory"""
        # Ensure tools directory exists
        self.launcher.TOOLS_DIR.mkdir(parents=True, exist_ok=True)
        
        filename = f"shortcuts_{tool_name.lower().replace(' ', '_')}.json"
        filepath = self.launcher.TOOLS_DIR / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(template, f, indent=2)
            return str(filepath)
        except Exception as e:
            self.launcher.print_color(f"❌ Error creating file: {e}", 'RED')
            return None
    
    def _display_success(self, filepath: str):
        """Display success message and next steps"""
        self.launcher.print_color(f"\n✅ Created {filepath}", 'GREEN')
        print("\nNext steps:")
        print(f"1. Edit the file to add your shortcuts")
        print("2. The tool will appear in the menu automatically")
        print("\nExample shortcut format:")
        print('''  {
    "keys": "cmd+shift+p",
    "description": "Command palette",
    "category": "basic",
    "difficulty": 1,
    "tips": ["Opens command palette", "Search for any command"]
  }''')
        print(f"\nYou can also open the tools folder from the Settings menu.")


def main():
    """Main entry point"""
    launcher = TrainerLauncher()
    launcher.run()


if __name__ == "__main__":
    main()