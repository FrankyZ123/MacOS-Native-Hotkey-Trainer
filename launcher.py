#!/usr/bin/env python3
"""
Unified launcher for HotKey Trainer
Manages the interceptor process and provides access to all tools
"""

import subprocess
import time
import sys
import os
import signal
from pathlib import Path
from trainer_core import TrainerCore, InterceptorManager

class TrainerLauncher(TrainerCore):
    def __init__(self):
        super().__init__()
        self.interceptor = InterceptorManager()
        self.running = True
    
    def check_prerequisites(self) -> bool:
        """Check if everything is ready"""
        issues = []
        
        if not self.interceptor.check_built():
            issues.append("Interceptor not built (run ./setup.sh first)")
        
        required_files = ['viewer.py', 'quiz.py', 'trainer_core.py']
        for file in required_files:
            if not Path(file).exists():
                issues.append(f"Missing {file}")
        
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
        print("  1) 🔍 Real-time Key Viewer")
        print("     ", end="")
        self.print_color("See what keys you're pressing", 'BLUE')
        print()
        print("  2) 📝 Practice Quiz")
        print("     ", end="")
        self.print_color("Test yourself on 10 shortcuts", 'BLUE')
        print()
        print("  3) 🎯 Freestyle Practice")
        print("     ", end="")
        self.print_color("Manual control mode", 'BLUE')
        print()
        print("  4) 🔧 Interceptor Status")
        print("     ", end="")
        self.print_color("Check/restart interceptor", 'BLUE')
        print()
        print("  5) ❌ Exit")
        print()
        
        return input("Enter choice [1-5]: ")
    
    def run_viewer(self):
        """Run the real-time viewer"""
        self.print_color("\n🔍 Starting Real-time Key Viewer...", 'GREEN')
        print("The trainer will activate automatically")
        time.sleep(1)
        subprocess.run([sys.executable, "viewer.py"])
    
    def run_quiz(self):
        """Run the practice quiz"""
        self.print_color("\n📝 Starting Practice Quiz...", 'GREEN')
        print("The trainer will activate automatically")
        time.sleep(1)
        subprocess.run([sys.executable, "quiz.py"])
    
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
            print()
            
            # Main menu loop
            while self.running:
                choice = self.show_menu()
                
                if choice == '1':
                    self.run_viewer()
                    input("\nPress Enter to continue...")
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif choice == '2':
                    self.run_quiz()
                    input("\nPress Enter to continue...")
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif choice == '3':
                    self.run_freestyle()
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif choice == '4':
                    self.check_interceptor_status()
                    input("\nPress Enter to continue...")
                    self.show_header("🎮 HotKey Trainer v2.0")
                    
                elif choice == '5':
                    self.running = False
                    
                else:
                    self.print_color("❌ Invalid choice. Please try again.", 'RED')
                    time.sleep(1)
                    self.show_header("🎮 HotKey Trainer v2.0")
            
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    launcher = TrainerLauncher()
    launcher.run()

if __name__ == "__main__":
    main()