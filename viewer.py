#!/usr/bin/env python3
"""
Real-time key viewer with automatic trainer control
Press Enter to start capturing, ESC or Ctrl+C to stop
"""

import time
import sys
from trainer_core import TrainerCore

class KeyViewer(TrainerCore):
    def __init__(self):
        super().__init__()
        self.exit_keys = ['escape', 'esc', 'ctrl+c']
    
    def setup(self):
        """Setup and show instructions"""
        self.show_header("🔍 REAL-TIME KEY VIEWER")
        
        print("This tool shows you exactly what keys you're pressing.\n")
        self.print_color("📝 Instructions:", 'CYAN')
        print("  • Press Enter to start capturing")
        print("  • The trainer will activate automatically")
        print("  • All keys will be blocked and displayed")
        print("  • Press ESC or Ctrl+C to stop\n")
        
        # Make sure trainer is OFF initially
        if self.is_trainer_active():
            print("Trainer is currently ON, turning it OFF...")
            self.ensure_trainer_off()
        
        input("Press Enter to start capturing keys...")
        print()
        
        # Turn ON the trainer
        if not self.ensure_trainer_on():
            self.print_color("⚠️  Could not activate trainer automatically.", 'YELLOW')
            print("Please press Cmd+Shift+- manually to activate.")
            input("Press Enter when you see '🔴 Trainer ON'...")
        
        self.clear_capture_file()
        
        print()
        self.print_color("🔴 CAPTURING - Your keys are being intercepted", 'RED')
        print("-" * 50)
        print("Type anything... (ESC to stop)\n")
    
    def watch(self):
        """Main watch loop with exit detection"""
        exit_pressed = False
        
        while not exit_pressed:
            try:
                keys = self.read_new_keys()
                
                for key in keys:
                    if self.check_for_exit(key, self.exit_keys):
                        print(f"{key} [Exiting...]")
                        exit_pressed = True
                        break
                    else:
                        print(key)
                
                sys.stdout.flush()
                time.sleep(0.01)  # 10ms polling
                
            except KeyboardInterrupt:
                print("\n[Ctrl+C pressed]")
                break
    
    def cleanup(self):
        """Clean exit and turn off trainer"""
        print("\n" + "-" * 50)
        
        # Turn OFF the trainer
        if self.is_trainer_active():
            self.ensure_trainer_off()
        
        print()
        self.print_color("✅ Done! Your keyboard is back to normal.\n", 'GREEN')

def main():
    """Main entry point"""
    viewer = KeyViewer()
    
    try:
        viewer.setup()
        viewer.watch()
    except KeyboardInterrupt:
        viewer.print_color("\n⚠️  Interrupted!", 'YELLOW')
    except Exception as e:
        viewer.print_color(f"\n❌ Error: {e}", 'RED')
    finally:
        viewer.cleanup()

if __name__ == "__main__":
    main()