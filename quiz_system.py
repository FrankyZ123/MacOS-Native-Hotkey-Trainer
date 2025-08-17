#!/usr/bin/env python3
"""
Unified Quiz System - Universal keyboard shortcut trainer
Loads shortcuts from JSON files for any application
"""

import json
import time
import sys
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from trainer_core import TrainerCore


class Difficulty(Enum):
    """Difficulty levels for shortcuts"""
    EASY = 1
    MEDIUM = 2
    HARD = 3


@dataclass
class Shortcut:
    """Data class for a keyboard shortcut"""
    keys: str
    description: str
    category: str = "basic"
    difficulty: int = 1
    tips: List[str] = field(default_factory=list)
    is_chord: bool = False
    
    def __post_init__(self):
        """Detect chord shortcuts automatically"""
        if ' ' in self.keys and not self.is_chord:
            self.is_chord = True


@dataclass
class Category:
    """Category information"""
    name: str
    color: str = "blue"
    icon: str = "📋"


@dataclass
class PracticeSet:
    """Practice set configuration"""
    name: str
    description: str
    shortcut_indices: Optional[List[int]] = None


class ShortcutQuiz(TrainerCore):
    """Universal quiz system for keyboard shortcuts"""
    
    # Class-level formatting constants
    KEY_DISPLAY_MAP = {
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
    
    # Changed: Use backtick for skip/exit instead of ESC
    SKIP_EXIT_KEYS = ['`', 'backtick', 'grave']  # Backtick key for skip/exit
    EMERGENCY_EXIT_KEYS = ['ctrl+c', 'cmd+q', 'cmd+.']  # Keep these for emergency exit
    TOOLS_DIR = Path('tools')  # Define tools directory
    
    def __init__(self, shortcuts_file: str = None):
        """Initialize quiz with optional shortcuts file"""
        super().__init__()
        
        if shortcuts_file:
            self.load_from_file(shortcuts_file)
        else:
            self._initialize_empty()
            
        self._reset_stats()
    
    def check_for_exit(self, key: str, exit_keys: Optional[List[str]] = None) -> bool:
        """
        Override parent's check_for_exit to NOT treat ESC as an exit key.
        Only check for the specific exit keys passed in.
        """
        if exit_keys is None:
            return False
        
        normalized = self.normalize_keys(key)
        return normalized in [self.normalize_keys(k) for k in exit_keys]
    
    def _initialize_empty(self):
        """Initialize with empty data"""
        self.tool_name = "Generic Tool"
        self.tool_icon = "🎮"
        self.tool_description = ""
        self.categories = {}
        self.shortcuts = []
        self.practice_sets = {}
    
    def _reset_stats(self):
        """Reset statistics for a new session"""
        self.stats = {
            'completed': 0,
            'skipped': 0,
            'attempts': [],
            'by_category': {cat_id: 0 for cat_id in self.categories},
            'by_difficulty': {d.value: 0 for d in Difficulty}
        }
    
    def load_from_file(self, shortcuts_file: str):
        """Load shortcuts configuration from JSON file"""
        json_path = Path(shortcuts_file)
        
        # If the path doesn't exist, check in tools directory
        if not json_path.exists() and not json_path.is_absolute():
            tools_path = self.TOOLS_DIR / json_path
            if tools_path.exists():
                json_path = tools_path
        
        if not json_path.exists():
            raise FileNotFoundError(f"Shortcuts file not found: {shortcuts_file}")
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        self._parse_json_data(data)
    
    def _parse_json_data(self, data: Dict):
        """Parse JSON data into internal structures"""
        self.tool_name = data.get('name', 'Unknown Tool')
        self.tool_icon = data.get('icon', '🎮')
        self.tool_description = data.get('description', '')
        
        # Parse categories
        self.categories = {
            cat_id: Category(**cat_data) 
            for cat_id, cat_data in data.get('categories', {}).items()
        }
        
        # Parse shortcuts
        self.shortcuts = [
            Shortcut(**shortcut_data) 
            for shortcut_data in data.get('shortcuts', [])
        ]
        
        # Parse practice sets
        self.practice_sets = {
            set_id: PracticeSet(**set_data)
            for set_id, set_data in data.get('practice_sets', {}).items()
        }
    
    def format_shortcut_for_display(self, shortcut: str, is_chord: bool = False) -> str:
        """Format shortcut for user-friendly display"""
        if is_chord or ' ' in shortcut:
            return self._format_chord(shortcut)
        return self._format_single_shortcut(shortcut)
    
    def _format_chord(self, shortcut: str) -> str:
        """Format chord shortcuts (e.g., 'cmd+k cmd+s')"""
        chord_parts = shortcut.lower().split(' ')
        formatted_chords = [
            self._format_single_shortcut(chord) 
            for chord in chord_parts
        ]
        return '  then  '.join(formatted_chords)
    
    def _format_single_shortcut(self, shortcut: str) -> str:
        """Format a single shortcut combination"""
        parts = shortcut.lower().split('+')
        display_parts = []
        
        for part in parts:
            if part in self.KEY_DISPLAY_MAP:
                display_parts.append(self.KEY_DISPLAY_MAP[part])
            elif part.startswith('f') and len(part) > 1 and part[1:].isdigit():
                display_parts.append(part.upper())
            elif len(part) == 1:
                display_parts.append(part.upper())
            else:
                display_parts.append(part.capitalize())
        
        return ' '.join(display_parts)
    
    def select_practice_mode(self) -> Tuple[str, List[Shortcut]]:
        """Interactive practice mode selection"""
        self.clear_screen()
        self.show_header(f"{self.tool_icon} {self.tool_name.upper()} PRACTICE MODE")
        
        options = self._build_practice_options()
        choice = self._get_user_choice(options)
        
        return self._process_mode_choice(choice, options)
    
    def _build_practice_options(self) -> Dict:
        """Build available practice options"""
        options = {}
        option_num = 1
        
        # Add predefined practice sets
        for set_id, practice_set in self.practice_sets.items():
            count = self._get_set_count(practice_set)
            options[str(option_num)] = ('set', set_id, practice_set)
            self._display_option(option_num, practice_set.name, 
                               practice_set.description, count)
            option_num += 1
        
        # Add category options
        if self.categories:
            print()
            self.print_color("Or practice by category:", 'MAGENTA')
            for cat_id, category in self.categories.items():
                count = self._get_category_count(cat_id)
                if count > 0:
                    options[str(option_num)] = ('category', cat_id, category)
                    print(f"  {option_num}) {category.icon} {category.name} ({count} shortcuts)")
                    option_num += 1
        
        # Add random option
        print()
        options[str(option_num)] = ('random', None, None)
        print(f"  {option_num}) 🎲 Random Selection (10 shortcuts)")
        
        return options
    
    def _get_set_count(self, practice_set: PracticeSet) -> int:
        """Get number of shortcuts in a practice set"""
        if practice_set.shortcut_indices:
            return len(practice_set.shortcut_indices)
        return len(self.shortcuts)
    
    def _get_category_count(self, cat_id: str) -> int:
        """Get number of shortcuts in a category"""
        return sum(1 for s in self.shortcuts if s.category == cat_id)
    
    def _display_option(self, num: int, name: str, description: str, count: int):
        """Display a practice option"""
        print(f"  {num}) {name} ({count} shortcuts)")
        print(f"     ", end="")
        self.print_color(description, 'BLUE')
    
    def _get_user_choice(self, options: Dict) -> str:
        """Get and validate user choice"""
        max_option = len(options)
        print()
        
        while True:
            choice = input(f"Enter choice [1-{max_option}]: ")
            if choice in options:
                return choice
            self.print_color(f"Invalid choice. Please enter 1-{max_option}.", 'RED')
    
    def _process_mode_choice(self, choice: str, options: Dict) -> Tuple[str, List[Shortcut]]:
        """Process the selected practice mode"""
        mode_type, mode_id, mode_data = options[choice]
        
        if mode_type == 'set':
            shortcuts = self._get_set_shortcuts(mode_data)
            return mode_id, shortcuts
        elif mode_type == 'category':
            shortcuts = [s for s in self.shortcuts if s.category == mode_id]
            return f"category_{mode_id}", shortcuts
        elif mode_type == 'random':
            num_random = min(10, len(self.shortcuts))
            shortcuts = random.sample(self.shortcuts, num_random)
            return "random", shortcuts
        
        return "all", self.shortcuts
    
    def _get_set_shortcuts(self, practice_set: PracticeSet) -> List[Shortcut]:
        """Get shortcuts for a practice set"""
        if practice_set.shortcut_indices:
            return [self.shortcuts[i] for i in practice_set.shortcut_indices]
        return self.shortcuts
    
    def practice_shortcut(self, shortcut: Shortcut, number: int, total: int) -> str:
        """Practice a single shortcut - returns: 'completed', 'skipped', or 'exit'"""
        self._display_shortcut_prompt(shortcut, number, total)
        return self._practice_loop(shortcut)
    
    def _display_shortcut_prompt(self, shortcut: Shortcut, number: int, total: int):
        """Display the shortcut practice prompt"""
        self.clear_screen()
        self.clear_capture_file()
        
        # Header
        print("=" * 50)
        print(f"{self.tool_name.upper()} PRACTICE {number}/{total}")
        
        # Category and difficulty
        if shortcut.category in self.categories:
            cat = self.categories[shortcut.category]
            self.print_color(f"{cat.icon} {cat.name}", cat.color.upper())
        
        difficulty_stars = "⭐" * shortcut.difficulty + "☆" * (3 - shortcut.difficulty)
        print(f"Difficulty: {difficulty_stars}")
        print("=" * 50)
        print()
        
        # Display shortcut
        self.print_color(f"Type this {self.tool_name} shortcut:", 'CYAN')
        print()
        display_keys = self.format_shortcut_for_display(shortcut.keys, shortcut.is_chord)
        self.print_color(f"    🎯  {display_keys}", 'MAGENTA')
        print(f"    📝 {shortcut.description}")
        print()
        print("-" * 50)
        
        # Tips
        if shortcut.tips:
            print("💡 Tips:")
            for tip in shortcut.tips[:2]:
                print(f"  • {tip}")
        
        if shortcut.is_chord:
            self.print_color("  ⚠️  This is a chord: Press first combo, release, then second", 'YELLOW')
        
        print()
        # Updated instructions for backtick
        self.print_color("Press ` (backtick) to skip, `` (twice) to exit", 'YELLOW')
        print()
    
    def _practice_loop(self, shortcut: Shortcut) -> str:
        """Main practice loop for a shortcut"""
        normalized_expected = self.normalize_keys(shortcut.keys)
        attempts = 0
        consecutive_backticks = 0
        last_backtick_time = 0
        
        while True:
            keys = self.read_new_keys()
            
            for key in keys:
                key_lower = key.lower()
                
                # Check for backtick (skip/exit key)
                if key_lower in self.SKIP_EXIT_KEYS or key == '`':
                    current_time = time.time()
                    # Reset counter if more than 1 second has passed
                    if current_time - last_backtick_time > 1.0:
                        consecutive_backticks = 0
                    
                    consecutive_backticks += 1
                    last_backtick_time = current_time
                    
                    if consecutive_backticks >= 2:
                        print(f"You typed: ` (backtick) twice - Exiting...")
                        return 'exit'
                    print(f"You typed: ` (backtick) - Skipping...")
                    return 'skipped'
                
                # Check for emergency exit keys (but NOT escape!)
                normalized_key = self.normalize_keys(key)
                if normalized_key in ['ctrl+c', 'cmd+q', 'cmd+.']:
                    print(f"You typed: {key} - Emergency exit...")
                    return 'exit'
                
                # Reset backtick counter for non-backtick keys
                consecutive_backticks = 0
                attempts += 1
                print(f"You typed: {key}", end="")
                
                if self.normalize_keys(key) == normalized_expected:
                    return self._handle_success(shortcut, attempts)
                else:
                    self._handle_mistake(key, normalized_expected, shortcut.difficulty, attempts)
            
            time.sleep(0.05)
    
    def _handle_success(self, shortcut: Shortcut, attempts: int) -> str:
        """Handle successful shortcut completion"""
        self.print_color(" ✅ Correct!", 'GREEN')
        self.stats['attempts'].append(attempts)
        
        # Update stats
        if shortcut.category in self.stats['by_category']:
            self.stats['by_category'][shortcut.category] += 1
        self.stats['by_difficulty'][shortcut.difficulty] += 1
        
        # Feedback
        if attempts == 1:
            self.print_color("🎯 Perfect! First try!", 'GREEN')
        elif attempts == 2:
            self.print_color("👍 Great! Got it on the second try!", 'YELLOW')
        else:
            print(f"Got it in {attempts} attempts!")
        
        time.sleep(0.8)
        return 'completed'
    
    def _handle_mistake(self, key: str, expected: str, difficulty: int, attempts: int):
        """Handle incorrect attempt"""
        if self._is_meaningful_attempt(key):
            self.print_color(" ❌ Try again", 'RED')
            if difficulty <= 2 and attempts > 2:
                self._provide_hint(expected, self.normalize_keys(key))
        else:
            print()
    
    def _is_meaningful_attempt(self, key: str) -> bool:
        """Check if this was a real attempt vs accidental keypress"""
        # Don't count backtick as meaningful since it's our skip key
        meaningful_keys = ['space', 'return', 'delete', 'tab']
        return ('+' in key or 
                key.lower() in meaningful_keys or 
                key.lower().startswith('f'))
    
    def _provide_hint(self, expected: str, actual: str):
        """Provide contextual hints based on the mistake"""
        expected_parts = set(expected.split('+'))
        actual_parts = set(actual.split('+'))
        
        missing = expected_parts - actual_parts
        extra = actual_parts - expected_parts
        
        hints = {
            'cmd': "Don't forget the Command key (⌘)",
            'alt': "Include the Option/Alt key (⌥)",
            'shift': "Add the Shift key (⇧)",
            'ctrl': "Use the Control key (⌃)",
            'fn': "Hold the fn key"
        }
        
        for mod, hint in hints.items():
            if mod in missing:
                print(f"    💡 Hint: {hint}")
                break
        
        if 'ctrl' in extra and 'cmd' in expected_parts:
            print("    💡 Hint: Use Cmd (⌘) not Ctrl on Mac")
    
    def run_quiz(self):
        """Main quiz execution"""
        self._display_welcome()
        mode, selected_shortcuts = self.select_practice_mode()
        self._prepare_practice(mode, selected_shortcuts)
        
        # Ensure trainer state
        self.ensure_trainer_off()
        input("Press Enter to start...")
        
        # Activate trainer
        self._activate_trainer()
        
        # Practice loop
        for i, shortcut in enumerate(selected_shortcuts, 1):
            result = self.practice_shortcut(shortcut, i, len(selected_shortcuts))
            self._update_stats(result)
            if result == 'exit':
                print("\n⚠️  Exiting practice...")
                break
        
        # Cleanup
        self.ensure_trainer_off()
        self.show_results(selected_shortcuts)
    
    def _display_welcome(self):
        """Display welcome screen"""
        self.show_header(f"{self.tool_icon} {self.tool_name.upper()} PRACTICE")
        if self.tool_description:
            print(f"{self.tool_description}\n")
    
    def _prepare_practice(self, mode: str, shortcuts: List[Shortcut]):
        """Prepare for practice session"""
        self.clear_screen()
        self.show_header(f"{self.tool_icon} {self.tool_name.upper()} PRACTICE")
        
        mode_display = mode.replace('_', ' ').title()
        self.print_color(f"Mode: {mode_display}", 'MAGENTA')
        print(f"Shortcuts to practice: {len(shortcuts)}\n")
        
        self.print_color("📋 Instructions:", 'CYAN')
        print("  • The trainer will activate automatically")
        print("  • Type each shortcut exactly as shown")
        # Updated instructions
        self.print_color("  • Press ` (backtick) to skip a shortcut", 'YELLOW')
        self.print_color("  • Press `` (backtick twice) to exit", 'YELLOW')
        print("  • Ctrl+C for emergency exit\n")
    
    def _activate_trainer(self):
        """Activate the trainer with error handling"""
        print()
        if not self.ensure_trainer_on():
            self.print_color("⚠️  Could not activate trainer automatically.", 'YELLOW')
            print("Please press Cmd+Shift+- manually to activate.")
            input("Press Enter when you see '🔴 Trainer ON'...")
        else:
            time.sleep(0.5)
    
    def _update_stats(self, result: str):
        """Update statistics based on result"""
        if result == 'completed':
            self.stats['completed'] += 1
        elif result == 'skipped':
            self.stats['skipped'] += 1
    
    def show_results(self, practiced_shortcuts: List[Shortcut]):
        """Display comprehensive practice results"""
        self.show_header(f"📊 {self.tool_name.upper()} RESULTS")
        
        self._display_score(practiced_shortcuts)
        self._display_performance()
        self._display_breakdown()
        self._display_practiced_shortcuts(practiced_shortcuts)
        self._display_tips()
        
        print("\nThe trainer has been turned OFF automatically.")
        self.print_color(f"Your keyboard is back to normal! {self.tool_icon}", 'GREEN')
    
    def _display_score(self, shortcuts: List[Shortcut]):
        """Display overall score"""
        if self.stats['completed'] == len(shortcuts):
            self.print_color(f"🎉 PERFECT SCORE! 🎉", 'GREEN')
            print(f"\nYou mastered all {len(shortcuts)} {self.tool_name} shortcuts!")
            self._display_achievement_message()
        else:
            print(f"Completed: {self.stats['completed']}/{len(shortcuts)}")
            if self.stats['skipped'] > 0:
                print(f"Skipped: {self.stats['skipped']}")
    
    def _display_achievement_message(self):
        """Display tool-specific achievement message"""
        messages = {
            "VSCode": "You're ready to code at lightning speed! ⚡",
            "macOS": "You're a macOS power user! 🚀",
            "Chrome": "Browse like a pro! 🌐",
            "Slack": "Communication master! 💬",
            "Asana": "Project management ninja! 📊"
        }
        message = messages.get(self.tool_name, "You're a keyboard ninja! 🥷")
        print(message)
    
    def _display_performance(self):
        """Display performance metrics"""
        if not self.stats['attempts']:
            return
        
        avg_attempts = sum(self.stats['attempts']) / len(self.stats['attempts'])
        print(f"\nAverage attempts per shortcut: {avg_attempts:.1f}")
        
        if avg_attempts < 1.5:
            self.print_color("🏆 Excellent muscle memory!", 'GREEN')
        elif avg_attempts < 2.5:
            self.print_color("👍 Good job! Keep practicing!", 'YELLOW')
        else:
            self.print_color("💪 You're learning! Practice makes perfect!", 'CYAN')
    
    def _display_breakdown(self):
        """Display category and difficulty breakdown"""
        # Category breakdown
        categories_practiced = {
            cat: count for cat, count in self.stats['by_category'].items() 
            if count > 0
        }
        
        if categories_practiced:
            print("\nBy category:")
            for cat_id, count in categories_practiced.items():
                if cat_id in self.categories:
                    cat = self.categories[cat_id]
                    print(f"  {cat.icon} {cat.name}: {count} completed")
        
        # Difficulty breakdown
        if any(self.stats['by_difficulty'].values()):
            print("\nBy difficulty:")
            diff_names = {1: "⭐ Easy", 2: "⭐⭐ Medium", 3: "⭐⭐⭐ Hard"}
            for diff, count in self.stats['by_difficulty'].items():
                if count > 0:
                    print(f"  {diff_names[diff]}: {count} completed")
    
    def _display_practiced_shortcuts(self, shortcuts: List[Shortcut]):
        """Display list of practiced shortcuts"""
        total_attempted = self.stats['completed'] + self.stats['skipped']
        
        if total_attempted == 0:
            return
        
        print(f"\nShortcuts practiced:")
        print("-" * 50)
        
        for i, shortcut in enumerate(shortcuts[:total_attempted], 1):
            status = "✅" if i <= self.stats['completed'] else "⭕"
            color = 'GREEN' if i <= self.stats['completed'] else 'YELLOW'
            
            display_keys = self.format_shortcut_for_display(
                shortcut.keys, 
                shortcut.is_chord
            )
            
            print(f"  {status} ", end="")
            self.print_color(f"{display_keys:25} - {shortcut.description}", color)
    
    def _display_tips(self):
        """Display tool-specific tips"""
        print("\n" + "=" * 50)
        self.print_color(f"💡 {self.tool_name} Pro Tips:", 'CYAN')
        
        tips = {
            "VSCode": [
                "• Practice these shortcuts in your actual code",
                "• Combine shortcuts for powerful workflows",
                "• Customize keybindings: Cmd+K Cmd+S"
            ],
            "macOS": [
                "• Use these shortcuts in your daily workflow",
                "• Most shortcuts work across all Mac apps",
                "• Explore app-specific shortcuts in Help menu"
            ],
            "Asana": [
                "• Use Tab+N to quickly create tasks",
                "• J and K navigate like Vim",
                "• Tab+numbers switch between views"
            ]
        }
        
        default_tips = [
            "• Practice daily for muscle memory",
            "• Start with easy shortcuts first",
            "• Use shortcuts in real work"
        ]
        
        for tip in tips.get(self.tool_name, default_tips):
            print(tip)


def main():
    """Main entry point for standalone execution"""
    import sys
    
    # Get shortcuts file from command line or let user choose
    if len(sys.argv) > 1:
        shortcuts_file = sys.argv[1]
    else:
        shortcuts_file = select_shortcuts_file()
    
    if not shortcuts_file:
        print("No shortcuts file selected. Exiting.")
        sys.exit(1)
    
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
        import traceback
        traceback.print_exc()
        sys.exit(1)


def select_shortcuts_file() -> Optional[str]:
    """Interactive file selection"""
    tools_dir = Path('tools')
    
    # Look for JSON files in tools directory (new naming convention)
    if tools_dir.exists():
        shortcut_files = list(tools_dir.glob('*.json'))
    else:
        # Fallback to current directory for backwards compatibility
        shortcut_files = list(Path('.').glob('*.json'))
        # Also check for old naming convention
        if not shortcut_files:
            shortcut_files = list(Path('.').glob('shortcuts_*.json'))
    
    if not shortcut_files:
        print("❌ No shortcut files found!")
        print(f"Create .json files in the '{tools_dir}' directory to use this system.")
        print("Example: asana.json, vscode.json, chrome.json")
        return None
    
    print("Available tools to practice:")
    for i, file in enumerate(shortcut_files, 1):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                name = data.get('name', file.stem)
                icon = data.get('icon', '🎮')
                desc = data.get('description', '')
                print(f"  {i}) {icon} {name}")
                if desc:
                    print(f"     {desc}")
        except:
            print(f"  {i}) {file.name}")
    
    print()
    while True:
        choice = input(f"Select tool [1-{len(shortcut_files)}]: ")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(shortcut_files):
                return str(shortcut_files[idx])
        except ValueError:
            pass
        print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()