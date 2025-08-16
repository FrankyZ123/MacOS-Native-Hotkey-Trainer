#!/usr/bin/env python3
"""
Unified Quiz System - loads shortcuts from JSON files
Extensible system for practicing any tool's keyboard shortcuts
"""

import json
import time
import sys
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from trainer_core import TrainerCore

class ShortcutQuiz(TrainerCore):
    """Generic quiz system that loads shortcuts from JSON files"""
    
    def __init__(self, shortcuts_file: str):
        super().__init__()
        self.shortcuts_file = shortcuts_file
        self.data = self.load_shortcuts()
        
        # Extract data from JSON
        self.tool_name = self.data['name']
        self.tool_icon = self.data.get('icon', '🎮')
        self.tool_description = self.data.get('description', '')
        self.categories = self.data.get('categories', {})
        self.shortcuts = self.data['shortcuts']
        self.practice_sets = self.data.get('practice_sets', {})
        
        # Quiz state
        self.exit_keys = ['escape', 'esc', 'ctrl+c', 'cmd+q', 'cmd+.']
        self.stats = {
            'completed': 0,
            'skipped': 0,
            'attempts': [],
            'by_category': {},
            'by_difficulty': {1: 0, 2: 0, 3: 0}
        }
        
        # Initialize category stats
        for cat_id in self.categories:
            self.stats['by_category'][cat_id] = 0
    
    def load_shortcuts(self) -> Dict:
        """Load shortcuts from JSON file"""
        json_path = Path(self.shortcuts_file)
        if not json_path.exists():
            raise FileNotFoundError(f"Shortcuts file not found: {self.shortcuts_file}")
        
        with open(json_path, 'r') as f:
            return json.load(f)
    
    def format_shortcut_for_display(self, shortcut: str, is_chord: bool = False) -> str:
        """Format shortcut for display with nice symbols"""
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
            'forwarddelete': 'Forward Delete',
            'escape': 'Esc',
            'left': '←',
            'right': '→',
            'up': '↑',
            'down': '↓',
            'home': 'Home',
            'end': 'End',
            'pageup': 'Page Up',
            'pagedown': 'Page Down'
        }
        
        # Handle chord shortcuts (e.g., "cmd+k cmd+s")
        if is_chord or ' ' in shortcut:
            chord_parts = shortcut.lower().split(' ')
            formatted_chords = []
            for chord in chord_parts:
                parts = chord.split('+')
                display_parts = []
                for part in parts:
                    if part in key_display:
                        display_parts.append(key_display[part])
                    elif part.startswith('f') and len(part) > 1 and part[1:].isdigit():
                        display_parts.append(part.upper())
                    elif len(part) == 1:
                        display_parts.append(part.upper())
                    else:
                        display_parts.append(part.capitalize())
                formatted_chords.append(' '.join(display_parts))
            return '  then  '.join(formatted_chords)
        
        # Regular shortcut
        parts = shortcut.lower().split('+')
        display_parts = []
        
        for part in parts:
            if part in key_display:
                display_parts.append(key_display[part])
            elif part.startswith('f') and len(part) > 1 and part[1:].isdigit():
                display_parts.append(part.upper())
            elif len(part) == 1:
                display_parts.append(part.upper())
            else:
                display_parts.append(part.capitalize())
        
        return ' '.join(display_parts)
    
    def select_practice_mode(self) -> Tuple[str, List[Dict]]:
        """Let user choose practice mode and return selected shortcuts"""
        self.clear_screen()
        self.show_header(f"{self.tool_icon} {self.tool_name.upper()} PRACTICE MODE")
        
        self.print_color("Choose your practice mode:", 'CYAN')
        print()
        
        # Show predefined practice sets
        option_num = 1
        options = {}
        
        for set_id, set_info in self.practice_sets.items():
            options[str(option_num)] = (set_id, set_info)
            
            # Count shortcuts in this set
            if set_info.get('shortcut_indices'):
                count = len(set_info['shortcut_indices'])
            else:
                count = len(self.shortcuts)
            
            print(f"  {option_num}) {set_info['name']} ({count} shortcuts)")
            print(f"     ", end="")
            self.print_color(set_info['description'], 'BLUE')
            option_num += 1
        
        # Add category-based options
        print()
        self.print_color("Or practice by category:", 'MAGENTA')
        for cat_id, cat_info in self.categories.items():
            # Count shortcuts in this category
            count = sum(1 for s in self.shortcuts if s.get('category') == cat_id)
            if count > 0:
                options[str(option_num)] = ('category', cat_id)
                icon = cat_info.get('icon', '📝')
                print(f"  {option_num}) {icon} {cat_info['name']} ({count} shortcuts)")
                option_num += 1
        
        # Add random option
        print()
        options[str(option_num)] = ('random', None)
        print(f"  {option_num}) 🎲 Random Selection (10 shortcuts)")
        
        print()
        while True:
            choice = input(f"Enter choice [1-{option_num}]: ")
            if choice in options:
                selection_type, selection_data = options[choice]
                
                if selection_type in self.practice_sets:
                    # Predefined set
                    set_info = self.practice_sets[selection_type]
                    if set_info.get('shortcut_indices'):
                        shortcuts = [self.shortcuts[i] for i in set_info['shortcut_indices']]
                    else:
                        shortcuts = self.shortcuts
                    return selection_type, shortcuts
                    
                elif selection_type == 'category':
                    # Category-based
                    shortcuts = [s for s in self.shortcuts if s.get('category') == selection_data]
                    return f"category_{selection_data}", shortcuts
                    
                elif selection_type == 'random':
                    # Random selection
                    num_random = min(10, len(self.shortcuts))
                    shortcuts = random.sample(self.shortcuts, num_random)
                    return "random", shortcuts
                    
            self.print_color(f"Invalid choice. Please enter 1-{option_num}.", 'RED')
    
    def practice_shortcut(self, shortcut_data: Dict, number: int, total: int) -> str:
        """
        Practice a single shortcut
        Returns: 'completed', 'skipped', or 'exit'
        """
        self.clear_screen()
        self.clear_capture_file()
        
        shortcut = shortcut_data['keys']
        description = shortcut_data['description']
        category = shortcut_data.get('category', '')
        difficulty = shortcut_data.get('difficulty', 1)
        tips = shortcut_data.get('tips', [])
        is_chord = shortcut_data.get('is_chord', False)
        
        # Header
        print("=" * 50)
        print(f"{self.tool_name.upper()} PRACTICE {number}/{total}")
        
        # Show category and difficulty
        if category and category in self.categories:
            cat_info = self.categories[category]
            cat_color = cat_info.get('color', 'BLUE').upper()
            cat_icon = cat_info.get('icon', '📝')
            self.print_color(f"{cat_icon} {cat_info['name']}", cat_color)
        
        # Difficulty stars
        difficulty_stars = "⭐" * difficulty + "☆" * (3 - difficulty)
        print(f"Difficulty: {difficulty_stars}")
        print("=" * 50)
        print()
        
        self.print_color(f"Type this {self.tool_name} shortcut:", 'CYAN')
        print()
        
        # Display the shortcut
        display_keys = self.format_shortcut_for_display(shortcut, is_chord)
        self.print_color(f"    🎯  {display_keys}", 'MAGENTA')
        print(f"    📝 {description}")
        print()
        print("-" * 50)
        
        # Show tips
        if tips:
            print("💡 Tips:")
            for tip in tips[:2]:  # Show max 2 tips
                print(f"  • {tip}")
        
        # Special instructions for chords
        if is_chord:
            self.print_color("  ⚠️  This is a chord: Press first combo, release, then second", 'YELLOW')
        
        print()
        print("Press ESC to skip, ESC twice to exit")
        print()
        
        # Practice loop
        normalized_expected = self.normalize_keys(shortcut)
        attempts = 0
        consecutive_escapes = 0
        
        while True:
            keys = self.read_new_keys()
            
            for key in keys:
                # Check for exit
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
                    
                    # Update category and difficulty stats
                    if category in self.stats['by_category']:
                        self.stats['by_category'][category] += 1
                    self.stats['by_difficulty'][difficulty] += 1
                    
                    # Feedback based on attempts
                    if attempts == 1:
                        self.print_color("🎯 Perfect! First try!", 'GREEN')
                    elif attempts == 2:
                        self.print_color("👍 Great! Got it on the second try!", 'YELLOW')
                    else:
                        print(f"Got it in {attempts} attempts!")
                    
                    time.sleep(0.8)
                    return 'completed'
                else:
                    # Check if it's a meaningful attempt
                    if '+' in key or key.lower() in ['space', 'return', 'delete', 'tab', '`'] or key.lower().startswith('f'):
                        self.print_color(" ❌ Try again", 'RED')
                        
                        # Provide hints for common mistakes
                        if difficulty <= 2 and attempts > 2:
                            self.provide_hint(normalized_expected, normalized_key)
                    else:
                        print()  # Just show single keys without judgment
            
            time.sleep(0.05)
    
    def provide_hint(self, expected: str, actual: str):
        """Provide contextual hints based on the mistake"""
        expected_parts = set(expected.split('+'))
        actual_parts = set(actual.split('+'))
        
        missing = expected_parts - actual_parts
        extra = actual_parts - expected_parts
        
        if missing:
            if 'cmd' in missing:
                print("    💡 Hint: Don't forget the Command key (⌘)")
            elif 'alt' in missing:
                print("    💡 Hint: Include the Option/Alt key (⌥)")
            elif 'shift' in missing:
                print("    💡 Hint: Add the Shift key (⇧)")
            elif 'ctrl' in missing:
                print("    💡 Hint: Use the Control key (⌃)")
            elif 'fn' in missing:
                print("    💡 Hint: Hold the fn key")
        elif extra:
            if 'ctrl' in extra and 'cmd' in expected_parts:
                print("    💡 Hint: Use Cmd (⌘) not Ctrl on Mac")
    
    def run_quiz(self):
        """Run the complete quiz session"""
        self.show_header(f"{self.tool_icon} {self.tool_name.upper()} PRACTICE")
        
        if self.tool_description:
            print(f"{self.tool_description}\n")
        
        # Select practice mode
        mode, selected_shortcuts = self.select_practice_mode()
        
        # Show what we're practicing
        self.clear_screen()
        self.show_header(f"{self.tool_icon} {self.tool_name.upper()} PRACTICE")
        
        mode_display = mode.replace('_', ' ').title()
        self.print_color(f"Mode: {mode_display}", 'MAGENTA')
        print(f"Shortcuts to practice: {len(selected_shortcuts)}\n")
        
        self.print_color("📋 Instructions:", 'CYAN')
        print("  • The trainer will activate automatically")
        print("  • Type each shortcut exactly as shown")
        print("  • Press ESC to skip a shortcut")
        print("  • Press ESC twice to exit\n")
        
        # Ensure trainer is off initially
        self.ensure_trainer_off()
        
        input("Press Enter to start...")
        
        # Activate trainer
        print()
        if not self.ensure_trainer_on():
            self.print_color("⚠️  Could not activate trainer automatically.", 'YELLOW')
            print("Please press Cmd+Shift+- manually to activate.")
            input("Press Enter when you see '🔴 Trainer ON'...")
        else:
            time.sleep(0.5)
        
        # Practice each shortcut
        for i, shortcut_data in enumerate(selected_shortcuts, 1):
            result = self.practice_shortcut(shortcut_data, i, len(selected_shortcuts))
            
            if result == 'completed':
                self.stats['completed'] += 1
            elif result == 'skipped':
                self.stats['skipped'] += 1
            elif result == 'exit':
                print("\n⚠️  Exiting practice...")
                break
        
        # Deactivate trainer
        self.ensure_trainer_off()
        
        # Show results
        self.show_results(selected_shortcuts)
    
    def show_results(self, practiced_shortcuts: List[Dict]):
        """Show comprehensive practice results"""
        self.show_header(f"📊 {self.tool_name.upper()} RESULTS")
        
        total_attempted = self.stats['completed'] + self.stats['skipped']
        
        # Overall score
        if self.stats['completed'] == len(practiced_shortcuts):
            self.print_color(f"🎉 PERFECT SCORE! 🎉", 'GREEN')
            print(f"\nYou mastered all {len(practiced_shortcuts)} {self.tool_name} shortcuts!")
            if self.tool_name == "VSCode":
                print("You're ready to code at lightning speed! ⚡")
            elif self.tool_name == "macOS":
                print("You're a macOS power user! 🚀")
        else:
            print(f"Completed: {self.stats['completed']}/{len(practiced_shortcuts)}")
            if self.stats['skipped'] > 0:
                print(f"Skipped: {self.stats['skipped']}")
        
        # Performance metrics
        if self.stats['attempts']:
            avg_attempts = sum(self.stats['attempts']) / len(self.stats['attempts'])
            print(f"\nAverage attempts per shortcut: {avg_attempts:.1f}")
            
            if avg_attempts < 1.5:
                self.print_color("🏆 Excellent muscle memory!", 'GREEN')
            elif avg_attempts < 2.5:
                self.print_color("👍 Good job! Keep practicing!", 'YELLOW')
            else:
                self.print_color("💪 You're learning! Practice makes perfect!", 'CYAN')
        
        # Category breakdown
        categories_practiced = {cat: count for cat, count in self.stats['by_category'].items() if count > 0}
        if categories_practiced:
            print("\nBy category:")
            for cat_id, count in categories_practiced.items():
                if cat_id in self.categories:
                    cat_info = self.categories[cat_id]
                    icon = cat_info.get('icon', '📝')
                    print(f"  {icon} {cat_info['name']}: {count} completed")
        
        # Difficulty breakdown
        if any(self.stats['by_difficulty'].values()):
            print("\nBy difficulty:")
            diff_names = {1: "⭐ Easy", 2: "⭐⭐ Medium", 3: "⭐⭐⭐ Hard"}
            for diff, count in self.stats['by_difficulty'].items():
                if count > 0:
                    print(f"  {diff_names[diff]}: {count} completed")
        
        # Detailed shortcut list
        if total_attempted > 0:
            print(f"\nShortcuts practiced:")
            print("-" * 50)
            
            for i, shortcut_data in enumerate(practiced_shortcuts[:total_attempted], 1):
                if i <= self.stats['completed']:
                    status = "✅"
                    color = 'GREEN'
                else:
                    status = "⭕"
                    color = 'YELLOW'
                
                keys = shortcut_data['keys']
                desc = shortcut_data['description']
                display_keys = self.format_shortcut_for_display(keys, shortcut_data.get('is_chord', False))
                
                print(f"  {status} ", end="")
                self.print_color(f"{display_keys:25} - {desc}", color)
        
        # Tips for improvement
        print("\n" + "=" * 50)
        self.print_color(f"💡 {self.tool_name} Pro Tips:", 'CYAN')
        
        if self.tool_name == "VSCode" and self.stats['completed'] > 0:
            print("• Practice these shortcuts in your actual code")
            print("• Combine shortcuts for powerful workflows")
            print("• Customize keybindings: Cmd+K Cmd+S")
        elif self.tool_name == "macOS" and self.stats['completed'] > 0:
            print("• Use these shortcuts in your daily workflow")
            print("• Most shortcuts work across all Mac apps")
            print("• Explore app-specific shortcuts in Help menu")
        
        print("\nThe trainer has been turned OFF automatically.")
        self.print_color(f"Your keyboard is back to normal! {self.tool_icon}", 'GREEN')


def main():
    """Main entry point for running a quiz"""
    import sys
    
    # Determine which quiz to run based on command line args or let user choose
    if len(sys.argv) > 1:
        shortcuts_file = sys.argv[1]
    else:
        # List available shortcut files
        shortcut_files = list(Path('.').glob('shortcuts_*.json'))
        
        if not shortcut_files:
            print("❌ No shortcut files found!")
            print("Create shortcuts_*.json files to use this system.")
            sys.exit(1)
        
        print("Available tools to practice:")
        for i, file in enumerate(shortcut_files, 1):
            # Load just the name from the file
            with open(file, 'r') as f:
                data = json.load(f)
                name = data.get('name', file.stem)
                icon = data.get('icon', '🎮')
                desc = data.get('description', '')
                print(f"  {i}) {icon} {name}")
                if desc:
                    print(f"     {desc}")
        
        print()
        while True:
            choice = input(f"Select tool [1-{len(shortcut_files)}]: ")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(shortcut_files):
                    shortcuts_file = str(shortcut_files[idx])
                    break
            except ValueError:
                pass
            print("Invalid choice. Please try again.")
    
    # Run the quiz
    try:
        quiz = ShortcutQuiz(shortcuts_file)
        quiz.run_quiz()
    except KeyboardInterrupt:
        print("\n\n⚠️  Practice interrupted!")
        print("Your keyboard is back to normal.")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()