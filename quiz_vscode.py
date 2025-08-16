#!/usr/bin/env python3
"""
Interactive VSCode Hotkey Practice Quiz with automatic trainer control
"""

import time
import sys
from trainer_core import TrainerCore
from typing import Dict, List, Tuple

class VSCodeQuiz(TrainerCore):
    def __init__(self):
        super().__init__()
        
        # Essential VSCode shortcuts for Mac - verified and tested
        self.shortcuts = [
            # Basic editing
            ("cmd+x", "Cut line (empty selection)"),
            ("cmd+c", "Copy line (empty selection)"),
            ("alt+up", "Move line up"),
            ("alt+down", "Move line down"),
            ("shift+alt+down", "Copy line down"),
            
            # Multi-cursor and selection
            ("cmd+d", "Add selection to next find match"),
            ("cmd+shift+l", "Select all occurrences"),
            ("alt+cmd+down", "Insert cursor below"),
            ("alt+cmd+up", "Insert cursor above"),
            
            # Navigation
            ("cmd+p", "Quick open file"),
            ("cmd+shift+p", "Command palette"),
            ("ctrl+g", "Go to line"),
            ("cmd+shift+o", "Go to symbol in file"),
            ("cmd+t", "Go to symbol in workspace"),
            
            # Code editing
            ("cmd+/", "Toggle line comment"),
            ("shift+alt+a", "Toggle block comment"),
            ("cmd+]", "Indent line"),
            ("cmd+[", "Outdent line"),
            ("shift+alt+f", "Format document"),
            
            # Advanced features (using fn+ for function keys on Mac)
            ("fn+f12", "Go to definition"),
            ("alt+fn+f12", "Peek definition"),
            ("shift+fn+f12", "Show references"),
            ("fn+f2", "Rename symbol"),
            ("cmd+.", "Quick fix/suggestions"),
            
            # Additional Mac-specific shortcuts
            ("cmd+k cmd+s", "Keyboard shortcuts"),  # This is a chord!
            ("ctrl+`", "Toggle terminal"),
            ("cmd+b", "Toggle sidebar"),
            ("cmd+shift+e", "Show Explorer"),
            ("cmd+shift+f", "Search in files"),
        ]
        
        self.exit_keys = ['escape', 'esc', 'ctrl+c', 'cmd+q', 'cmd+.']
        self.stats = {
            'completed': 0,
            'skipped': 0,
            'attempts': [],
            'difficulty_levels': {
                'basic': 0,
                'intermediate': 0,
                'advanced': 0
            }
        }
        
        # Categorize shortcuts by difficulty
        self.difficulty_map = {
            'basic': self.shortcuts[:5],
            'intermediate': self.shortcuts[5:15],
            'advanced': self.shortcuts[15:]
        }
    
    def select_practice_mode(self) -> str:
        """Let user choose practice mode"""
        self.clear_screen()
        self.show_header("🎮 VSCODE PRACTICE MODE")
        
        self.print_color("Choose your practice mode:", 'CYAN')
        print()
        print("  1) 📚 Full Practice (30 shortcuts)")
        print("  2) 🟢 Basic Editing (5 shortcuts)")
        print("  3) 🟡 Multi-cursor & Navigation (10 shortcuts)")
        print("  4) 🔴 Advanced Features (15 shortcuts)")
        print("  5) 🎲 Random Selection (10 shortcuts)")
        print()
        
        while True:
            choice = input("Enter choice [1-5]: ")
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            self.print_color("Invalid choice. Please enter 1-5.", 'RED')
    
    def get_shortcuts_for_mode(self, mode: str) -> List[Tuple[str, str]]:
        """Get shortcuts based on selected mode"""
        if mode == '1':
            return self.shortcuts
        elif mode == '2':
            return self.difficulty_map['basic']
        elif mode == '3':
            return self.difficulty_map['intermediate']
        elif mode == '4':
            return self.difficulty_map['advanced']
        elif mode == '5':
            import random
            return random.sample(self.shortcuts, min(10, len(self.shortcuts)))
        return self.shortcuts
    
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
            elif part.startswith('f') and part[1:].isdigit():
                # Function keys
                display_parts.append(part.upper())
            elif len(part) == 1:
                # Single character
                display_parts.append(part.upper())
            else:
                # Keep as is but capitalize
                display_parts.append(part.capitalize())
        
        # Special case for chord shortcuts (e.g., "cmd+k cmd+s")
        if ' ' in shortcut:
            chord_parts = shortcut.split(' ')
            formatted_chords = [self.format_shortcut_for_display(chord) for chord in chord_parts]
            return '  then  '.join(formatted_chords)
        
        # Join with spaces, no plus signs
        return ' '.join(display_parts)
    
    def practice_shortcut(self, shortcut: str, description: str, number: int, total: int, category: str = "") -> str:
        """
        Practice a single shortcut
        Returns: 'completed', 'skipped', or 'exit'
        """
        self.clear_screen()
        self.clear_capture_file()
        
        print("=" * 50)
        print(f"VSCODE PRACTICE {number}/{total}")
        if category:
            self.print_color(f"[{category}]", 'BLUE')
        print("=" * 50)
        print()
        self.print_color(f"Type this VSCode shortcut:", 'CYAN')
        print()
        
        # Convert shortcut to display format
        display_keys = self.format_shortcut_for_display(shortcut)
        self.print_color(f"    🎯  {display_keys}", 'MAGENTA')
        print(f"    📝 {description}")
        print()
        print("-" * 50)
        print("💡 Tips:")
        print("  • Press ESC to skip this shortcut")
        print("  • Press ESC twice to exit practice")
        
        # Add context-specific tips
        if "cmd+d" in shortcut.lower():
            print("  • This is super useful for renaming variables!")
        elif "cmd+p" in shortcut.lower():
            print("  • Type @ after to search symbols, : for line numbers")
        elif "fn+f" in shortcut.lower():
            print("  • Hold fn key + function key (check Mac settings)")
            print("  • Or use Cmd+click as alternative for Go to Definition!")
        elif "cmd+k" in shortcut.lower():
            print("  • This is a chord: press Cmd+K, release, then Cmd+S")
        elif "ctrl+`" in shortcut.lower():
            print("  • That's the backtick key (same key as ~)")
        print()
        
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
                    
                    # Track difficulty completion
                    if shortcut in [s for s, _ in self.difficulty_map['basic']]:
                        self.stats['difficulty_levels']['basic'] += 1
                    elif shortcut in [s for s, _ in self.difficulty_map['intermediate']]:
                        self.stats['difficulty_levels']['intermediate'] += 1
                    else:
                        self.stats['difficulty_levels']['advanced'] += 1
                    
                    if attempts == 1:
                        self.print_color("🎯 Perfect! First try!", 'GREEN')
                    elif attempts > 1:
                        print(f"Got it in {attempts} attempts!")
                    time.sleep(0.8)
                    return 'completed'
                else:
                    # Only judge complete key combos
                    if '+' in key or key.lower() in ['space', 'return', 'delete', 'tab', '`'] or key.lower().startswith('f'):
                        self.print_color(" ❌ Try again", 'RED')
                        
                        # Give hints for common mistakes
                        if 'cmd' in normalized_expected and 'ctrl' in normalized_key:
                            print("    💡 Hint: Use Cmd (⌘) not Ctrl on Mac")
                        elif 'alt' in normalized_expected and 'alt' not in normalized_key:
                            print("    💡 Hint: Don't forget the Alt/Option key")
                        elif 'fn' in normalized_expected and 'fn' not in normalized_key:
                            print("    💡 Hint: Hold the fn key for function keys")
                    else:
                        print()  # Just show single modifier keys
            
            time.sleep(0.05)
    
    def run_quiz(self):
        """Run the practice session"""
        self.show_header("💻 VSCODE HOTKEY PRACTICE")
        
        print("Master VSCode shortcuts to code faster!\n")
        
        # Select practice mode
        mode = self.select_practice_mode()
        selected_shortcuts = self.get_shortcuts_for_mode(mode)
        
        self.clear_screen()
        self.show_header("💻 VSCODE HOTKEY PRACTICE")
        
        mode_names = {
            '1': "Full Practice",
            '2': "Basic Editing",
            '3': "Multi-cursor & Navigation", 
            '4': "Advanced Features",
            '5': "Random Selection"
        }
        
        self.print_color(f"Mode: {mode_names[mode]}", 'MAGENTA')
        print(f"Shortcuts to practice: {len(selected_shortcuts)}\n")
        
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
        for i, (shortcut, description) in enumerate(selected_shortcuts, 1):
            # Determine category for display
            category = ""
            if (shortcut, description) in self.difficulty_map['basic']:
                category = "Basic"
            elif (shortcut, description) in self.difficulty_map['intermediate']:
                category = "Intermediate"
            else:
                category = "Advanced"
            
            result = self.practice_shortcut(shortcut, description, i, len(selected_shortcuts), category)
            
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
        self.show_results(selected_shortcuts)
    
    def show_results(self, practiced_shortcuts):
        """Show practice results with VSCode-specific feedback"""
        self.show_header("📊 VSCODE PRACTICE RESULTS")
        
        total_attempted = self.stats['completed'] + self.stats['skipped']
        
        if self.stats['completed'] == len(practiced_shortcuts):
            self.print_color("🎉 PERFECT SCORE! 🎉", 'GREEN')
            print(f"\nYou mastered all {len(practiced_shortcuts)} VSCode shortcuts!")
            print("You're ready to code at lightning speed! ⚡")
        else:
            print(f"Completed: {self.stats['completed']}/{len(practiced_shortcuts)}")
            if self.stats['skipped'] > 0:
                print(f"Skipped: {self.stats['skipped']}")
        
        if self.stats['attempts']:
            avg_attempts = sum(self.stats['attempts']) / len(self.stats['attempts'])
            print(f"Average attempts: {avg_attempts:.1f}")
            
            if avg_attempts < 1.5:
                self.print_color("🏆 Excellent muscle memory!", 'GREEN')
            elif avg_attempts < 2.5:
                self.print_color("👍 Good job! Keep practicing!", 'YELLOW')
            else:
                self.print_color("💪 You're learning! Practice makes perfect!", 'CYAN')
        
        # Show difficulty breakdown if applicable
        levels = self.stats['difficulty_levels']
        if any(levels.values()):
            print("\nDifficulty breakdown:")
            if levels['basic'] > 0:
                print(f"  🟢 Basic: {levels['basic']} completed")
            if levels['intermediate'] > 0:
                print(f"  🟡 Intermediate: {levels['intermediate']} completed")
            if levels['advanced'] > 0:
                print(f"  🔴 Advanced: {levels['advanced']} completed")
        
        print("\nShortcuts practiced:")
        print()
        
        for i, (shortcut, description) in enumerate(practiced_shortcuts[:total_attempted], 1):
            if i <= self.stats['completed']:
                status = "✅"
                color = 'GREEN'
            else:
                status = "⭕"
                color = 'YELLOW'
            
            print(f"  {status} ", end="")
            self.print_color(f"{shortcut.upper():20} - {description}", color)
        
        # VSCode-specific tips
        print("\n" + "=" * 50)
        self.print_color("💡 Pro Tips:", 'CYAN')
        
        if self.stats['completed'] > 0:
            print("• Practice these shortcuts in your actual code")
            print("• Try combining shortcuts for powerful workflows")
            print("• Customize keybindings in VSCode: Cmd+K Cmd+S")
        
        print("\nThe trainer has been turned OFF automatically.")
        self.print_color("Your keyboard is back to normal! 💻", 'GREEN')

def main():
    """Main entry point"""
    quiz = VSCodeQuiz()
    
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