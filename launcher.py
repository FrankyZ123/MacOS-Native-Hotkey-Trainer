#!/usr/bin/env python3
"""
Unified launcher for HotKey Trainer v2.0
Now with JSON-based extensible shortcut system
"""

import subprocess
import time
import sys
import os
import json
import signal
from pathlib import Path
from trainer_core import TrainerCore, InterceptorManager

class TrainerLauncher(TrainerCore):
    def __init__(self):
        super().__init__()
        self.interceptor = InterceptorManager()
        self.running = True
        self.available_tools = self.discover_tools()
    
    def discover_tools(self) -> list:
        """Discover available tools from shortcuts_*.json files"""
        tools = []
        for json_file in Path('.').glob('shortcuts_*.json'):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    tools.append({
                        'file': str(json_file),
                        'name': data.get('name', json_file.stem),
                        'icon': data.get('icon', '🎮'),
                        'description': data.get('description', ''),
                        'shortcut_count': len(data.get('shortcuts', []))
                    })
            except (json.JSONDecodeError, KeyError):
                continue
        return sorted(tools, key=lambda x: x['name'])
    
    def check_prerequisites(self) -> bool:
        """Check if everything is ready"""
        issues = []
        
        if not self.interceptor.check_built():
            issues.append("Interceptor not built (run ./setup.sh first)")
        
        required_files = ['viewer.py', 'quiz_system.py', 'trainer_core.py']
        for file in required_files:
            if not Path(file).exists():
                issues.append(f"Missing {file}")
        
        if not self.available_tools:
            issues.append("No shortcut files found (shortcuts_*.json)")
        
        if issues:
            self.print_color("❌ Prerequisites check failed:", 'RED')
            for issue in issues:
                print(f"  • {issue}")
            return False
        
        return True
    
    def show_menu(self) -> str:
        """Show main menu and get choice"""
        # Show current status
        if self.is_trainer_active():
            self.print_color("Status: 🔴 Trainer ON (keys blocked)", 'RED')
        else:
            self.print_color("Status: 🟢 Trainer OFF (keys normal)", 'GREEN')
        print()
        
        self.print_color("Choose an option:", 'MAGENTA')
        print()
        
        option_num = 1
        options = {}
        
        # Real-time viewer
        print(f"  {option_num}) 👁️ Real-time Key Viewer")
        print("     ", end="")
        self.print_color("See what keys you're pressing", 'BLUE')
        options[str(option_num)] = 'viewer'
        option_num += 1
        print()
        
        # Practice quizzes for each tool
        if self.available_tools:
            self.print_color("Practice Shortcuts:", 'CYAN')
            for tool in self.available_tools:
                print(f"  {option_num}) {tool['icon']} {tool['name']} Practice")
                print("     ", end="")
                desc = tool['description'] or f"Practice {tool['shortcut_count']} shortcuts"
                self.print_color(desc, 'BLUE')
                options[str(option_num)] = ('quiz', tool['file'])
                option_num += 1
            print()
        
        # Freestyle practice
        print(f"  {option_num}) 🎯 Freestyle Practice")
        print("     ", end="")
        self.print_color("Manual control mode", 'BLUE')
        options[str(option_num)] = 'freestyle'
        option_num += 1
        print()
        
        # Interceptor status
        print(f"  {option_num}) 🔧 Interceptor Status")
        print("     ", end="")
        self.print_color("Check/restart interceptor", 'BLUE')
        options[str(option_num)] = 'status'
        option_num += 1
        print()
        
        # Add new tool
        print(f"  {option_num}) ➕ Add New Tool")
        print("     ", end="")
        self.print_color("Create shortcuts for a new tool", 'GREEN')
        options[str(option_num)] = 'add_tool'
        option_num += 1
        print()
        
        # Exit
        print(f"  {option_num}) ❌ Exit")
        options[str(option_num)] = 'exit'
        print()
        
        choice = input(f"Enter choice [1-{option_num}]: ")
        if choice in options:
            return options[choice]
        return None
    
    def run_viewer(self):
        """Run the real-time viewer"""
        self.print_color("\n👁️ Starting Real-time Key Viewer...", 'GREEN')
        print("The trainer will activate automatically")
        time.sleep(1)
        subprocess.run([sys.executable, "viewer.py"])
    
    def run_quiz(self, shortcuts_file: str):
        """Run a practice quiz for specific tool"""
        self.print_color(f"\n🎮 Starting Practice Quiz...", 'GREEN')
        print("The trainer will activate automatically")
        time.sleep(1)
        subprocess.run([sys.executable, "quiz_system.py", shortcuts_file])
    
    def run_freestyle(self):
        """Run freestyle mode with manual control"""
        self.print_color("\n🎯 Starting Freestyle Practice...", 'GREEN')
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
        
        input("Press Enter to continue...")
        
        # Stop background interceptor and run in foreground
        self.interceptor.stop(silent=True)
        
        try:
            self.interceptor.run_foreground()
        except KeyboardInterrupt:
            print("\nReturning to menu...")
        
        # Restart in background
        self.interceptor.start(silent=True)
    
    def check_interceptor_status(self):
        """Check and manage interceptor status"""
        self.print_color("\n🔧 Interceptor Status", 'CYAN')
        print("-" * 30)
        
        if self.interceptor.is_running():
            pid = self.interceptor.get_pid()
            self.print_color(f"✅ Running (PID: {pid})", 'GREEN')
            
            choice = input("\nRestart interceptor? (y/n): ")
            if choice.lower() == 'y':
                self.interceptor.stop()
                time.sleep(0.5)
                success, pid = self.interceptor.start()
                if success:
                    self.print_color(f"✅ Restarted (PID: {pid})", 'GREEN')
                else:
                    self.print_color("❌ Failed to restart", 'RED')
        else:
            self.print_color("❌ Not running", 'RED')
            
            choice = input("\nStart interceptor? (y/n): ")
            if choice.lower() == 'y':
                success, pid = self.interceptor.start()
                if success:
                    self.print_color(f"✅ Started (PID: {pid})", 'GREEN')
                else:
                    self.print_color("❌ Failed to start", 'RED')
    
    def create_new_tool(self):
        """Helper to create a new tool JSON file"""
        self.print_color("\n➕ Create New Tool", 'CYAN')
        print("-" * 30)
        
        print("\nThis will help you create a shortcuts JSON file for a new tool.")
        print("You can also manually create a shortcuts_[toolname].json file.\n")
        
        # Get basic info
        tool_name = input("Tool name (e.g., 'Chrome', 'Slack'): ").strip()
        if not tool_name:
            print("Cancelled.")
            return
        
        tool_icon = input("Icon emoji (press Enter for default 🎮): ").strip() or "🎮"
        tool_desc = input("Description (optional): ").strip()
        
        # Create template
        template = {
            "name": tool_name,
            "description": tool_desc,
            "icon": tool_icon,
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
        
        # Save file
        filename = f"shortcuts_{tool_name.lower().replace(' ', '_')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(template, f, indent=2)
            
            self.print_color(f"\n✅ Created {filename}", 'GREEN')
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
            
            # Reload tools
            self.available_tools = self.discover_tools()
            
        except Exception as e:
            self.print_color(f"❌ Error creating file: {e}", 'RED')
    
    def cleanup(self):
        """Clean up on exit"""
        print()
        self.print_color("🧹 Cleaning up...", 'YELLOW')
        self.interceptor.stop()
        self.print_color("👋 Goodbye!", 'GREEN')
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Main run loop"""
        # Check prerequisites
        if not self.check_prerequisites():
            print("\nPlease fix the issues above and try again.")
            sys.exit(1)
        
        # Set up signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start interceptor in background
            self.show_header("🎮 HotKey Trainer v2.0")
            
            success, pid = self.interceptor.start()
            if not success:
                self.print_color("Failed to start interceptor.", 'RED')
                print("Try running with sudo or check permissions.")
                sys.exit(1)
            
            self.print_color(f"✅ Interceptor running (PID: {pid})", 'GREEN')
            
            # Show available tools
            if self.available_tools:
                print(f"\n📚 {len(self.available_tools)} tool(s) available for practice:")
                for tool in self.available_tools:
                    print(f"   {tool['icon']} {tool['name']} ({tool['shortcut_count']} shortcuts)")
            print()
            
            # Main menu loop
            while self.running:
                action = self.show_menu()
                
                if action is None:
                    self.print_color("❌ Invalid choice. Please try again.", 'RED')
                    time.sleep(1)
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif action == 'viewer':
                    self.run_viewer()
                    input("\nPress Enter to continue...")
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif isinstance(action, tuple) and action[0] == 'quiz':
                    self.run_quiz(action[1])
                    input("\nPress Enter to continue...")
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif action == 'freestyle':
                    self.run_freestyle()
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif action == 'status':
                    self.check_interceptor_status()
                    input("\nPress Enter to continue...")
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif action == 'add_tool':
                    self.create_new_tool()
                    input("\nPress Enter to continue...")
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif action == 'exit':
                    self.running = False
            
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    launcher = TrainerLauncher()
    launcher.run()

if __name__ == "__main__":
    main()