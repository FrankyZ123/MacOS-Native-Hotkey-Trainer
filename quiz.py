#!/usr/bin/env python3
"""
Interactive Hotkey Practice Quiz with automatic trainer control
"""

import time
import sys
from trainer_core import TrainerCore
from typing import Dict, List, Tuple

class HotkeyQuiz(TrainerCore):
    def __init__(self):
        super().__init__()
        
        # Shortcuts to practice - progressing from simple to complex
        self.shortcuts = [
            ("cmd+n", "New window/file"),
            ("shift+cmd+n", "New folder"),
            ("space", "Quick Look/Play"),
            ("cmd+delete", "Delete line"),
            ("shift+cmd+.", "Show hidden files"),
            ("cmd+w", "Close tab/window"),
            ("alt+cmd+escape", "Force quit"),
            ("shift+cmd+3", "Screenshot"),
            ("ctrl+cmd+space", "Emoji picker"),
            ("shift+cmd+/", "Help menu"),
        ]
        
        self.exit_keys = ['escape', 'esc', 'ctrl+c', 'cmd+q', 'cmd+.']
        self.stats = {
            'completed': 0,
            'skipped': 0,
            'attempts': []
        }
    
    def format_shortcut_for_display(self, shortcut: str) -> str:
        """Format shortcut for learn mode display"""
        # Map technical notation to display symbols
        key_display = {
            'cmd': '⌘',
            'alt': '⌥', 
            'shift': '⇧',
            'ctrl': '⌃',
            'fn': 'fn',
            'tab': 'Tab',
            'space': 'Space',
            'return': 'Return',
            'delete': 'Delete',
            'escape': 'Esc',
            'left': '←',
            'right': '→',
            'up': '↑',
            'down': '↓',
        }
        
        parts = shortcut.lower().split('+')
        display_parts = []
        
        for part in parts:
            if part in key_display:
                display_parts.append(key_display[part])
            elif len(part) == 1:
                # Single character or symbol
                display_parts.append(part.upper())
            else:
                # Keep as is but capitalize
                display_parts.append(part.capitalize())
        
        # Join with spaces, no plus signs
        return ' '.join(display_parts)
    
    def practice_shortcut(self, shortcut: str, description: str, number: int, total: int) -> str:
        """
        Practice a single shortcut
        Returns: 'completed', 'skipped', or 'exit'
        """
        self.clear_screen()
        self.clear_capture_file()
        
        print("=" * 50)
        print(f"PRACTICE {number}/{total}")
        print("=" * 50)
        print()
        self.print_color(f"Type this shortcut:", 'CYAN')
        print()
        
        # Convert shortcut to display format
        display_keys = self.format_shortcut_for_display(shortcut)
        self.print_color(f"    🎯  {display_keys}", 'MAGENTA')
        print(f"    ({description})")
        print()
        print("-" * 50)
        print("💡 Tip: Press ESC to skip or exit\n")
        
        normalized_expected = self.normalize_keys(shortcut)
        attempts = 0
        consecutive_escapes = 0
        
        while True:
            keys = self.read_new_keys()
            
            for key in keys:
                # Check for exit key first
                if self.check_for_exit(key, self.exit_keys):
                    consecutive_escapes += 1
                    if consecutive_escapes >= 2:
                        print(f"You typed: {key} - Exiting...")
                        return 'exit'
                    print(f"You typed: {key} - Skipping...")
                    return 'skipped'
                
                consecutive_escapes = 0
                attempts += 1
                print(f"You typed: {key}", end="")
                normalized_key = self.normalize_keys(key)
                
                # Check if correct
                if normalized_key == normalized_expected:
                    self.print_color(" ✅ Correct!", 'GREEN')
                    self.stats['attempts'].append(attempts)
                    
                    if attempts > 1:
                        print(f"Got it in {attempts} attempts!")
                    time.sleep(0.8)
                    return 'completed'
                else:
                    # Only judge complete key combos
                    if '+' in key or key.lower() in ['space', 'return', 'delete', 'tab']:
                        self.print_color(" ❌ Try again", 'RED')
                    else:
                        print()  # Just show single modifier keys
            
            time.sleep(0.05)
    
    def run_quiz(self):
        """Run the practice session"""
        self.show_header("🎮 HOTKEY PRACTICE QUIZ")
        
        print("This will test you on 10 common macOS shortcuts.\n")
        self.print_color("📋 Instructions:", 'CYAN')
        print("  • The trainer will activate automatically")
        print("  • Type each shortcut as shown")
        print("  • Press ESC to skip a shortcut")
        print("  • Press ESC twice to exit\n")
        
        # Make sure trainer is OFF initially
        self.ensure_trainer_off()
        
        input("Press Enter to start...")
        
        # Turn ON the trainer
        print()
        if not self.ensure_trainer_on():
            self.print_color("⚠️  Could not activate trainer automatically.", 'YELLOW')
            print("Please press Cmd+Shift+- manually to activate.")
            input("Press Enter when you see '🔴 Trainer ON'...")
        else:
            time.sleep(0.5)
        
        # Practice each shortcut
        for i, (shortcut, description) in enumerate(self.shortcuts, 1):
            result = self.practice_shortcut(shortcut, description, i, len(self.shortcuts))
            
            if result == 'completed':
                self.stats['completed'] += 1
            elif result == 'skipped':
                self.stats['skipped'] += 1
            elif result == 'exit':
                print("\n⚠️  Exiting practice...")
                break
        
        # Turn OFF trainer
        self.ensure_trainer_off()
        
        # Show results
        self.show_results()
    
    def show_results(self):
        """Show practice results"""
        self.show_header("📊 PRACTICE RESULTS")
        
        total_attempted = self.stats['completed'] + self.stats['skipped']
        
        if self.stats['completed'] == len(self.shortcuts):
            self.print_color("🎉 PERFECT SCORE! 🎉", 'GREEN')
            print(f"\nYou completed all {len(self.shortcuts)} shortcuts!")
        else:
            print(f"Completed: {self.stats['completed']}/{len(self.shortcuts)}")
            if self.stats['skipped'] > 0:
                print(f"Skipped: {self.stats['skipped']}")
        
        if self.stats['attempts']:
            avg_attempts = sum(self.stats['attempts']) / len(self.stats['attempts'])
            print(f"Average attempts: {avg_attempts:.1f}")
        
        print("\nShortcuts practiced:")
        print()
        
        for i, (shortcut, description) in enumerate(self.shortcuts[:total_attempted], 1):
            if i <= self.stats['completed']:
                status = "✅"
                color = 'GREEN'
            else:
                status = "⭕"
                color = 'YELLOW'
            
            # Format shortcut for display
            display_keys = self.format_shortcut_for_display(shortcut)
            print(f"  {status} ", end="")
            self.print_color(f"{display_keys:20} - {description}", color)
        
        print("\nThe trainer has been turned OFF automatically.")
        self.print_color("Your keyboard is back to normal! 🎮", 'GREEN')

def main():
    """Main entry point"""
    quiz = HotkeyQuiz()
    
    try:
        quiz.run_quiz()
    except KeyboardInterrupt:
        quiz.print_color("\n\n⚠️  Practice interrupted!", 'YELLOW')
        if quiz.is_trainer_active():
            print("Turning off trainer...")
            quiz.ensure_trainer_off()
        print("Your keyboard is back to normal.")
        sys.exit(0)
    except Exception as e:
        quiz.print_color(f"\n❌ Error: {e}", 'RED')
        if quiz.is_trainer_active():
            quiz.ensure_trainer_off()
        sys.exit(1)

if __name__ == "__main__":
    main()