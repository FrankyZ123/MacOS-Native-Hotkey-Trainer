#!/usr/bin/env python3
"""
Typing Test - Practice typing speed and accuracy
"""

import time
import random
from typing import List, Tuple
from trainer_core import TrainerCore


class TypingTest(TrainerCore):
    """Simple typing test to practice speed and accuracy"""
    
    # Sample words for typing practice
    WORD_LISTS = {
        'easy': [
            'cat', 'dog', 'run', 'jump', 'fast', 'slow', 'big', 'small',
            'red', 'blue', 'green', 'yellow', 'happy', 'sad', 'good', 'bad',
            'hot', 'cold', 'up', 'down', 'left', 'right', 'yes', 'no',
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
            'sun', 'moon', 'star', 'sky', 'tree', 'fish', 'bird', 'flower'
        ],
        'medium': [
            'computer', 'keyboard', 'monitor', 'practice', 'typing', 'speed',
            'accuracy', 'message', 'document', 'program', 'window', 'folder',
            'network', 'internet', 'website', 'password', 'username', 'email',
            'calendar', 'schedule', 'meeting', 'project', 'deadline', 'report',
            'analysis', 'creative', 'solution', 'problem', 'customer', 'service'
        ],
        'hard': [
            'extraordinary', 'sophisticated', 'implementation', 'architecture',
            'development', 'programming', 'engineering', 'technology', 'innovation',
            'collaboration', 'communication', 'optimization', 'performance',
            'efficiency', 'productivity', 'professional', 'management', 'strategy',
            'comprehensive', 'documentation', 'infrastructure', 'deployment',
            'configuration', 'administration', 'maintenance', 'troubleshooting'
        ],
        'sentences': [
            'The quick brown fox jumps over the lazy dog.',
            'Pack my box with five dozen liquor jugs.',
            'How vexingly quick daft zebras jump!',
            'The five boxing wizards jump quickly.',
            'Sphinx of black quartz, judge my vow.',
            'Two driven jocks help fax my big quiz.',
            'Practice makes perfect when learning to type.',
            'Keyboard shortcuts save time and increase productivity.',
            'Learning to touch type is a valuable skill.',
            'Consistent practice improves typing speed and accuracy.'
        ]
    }
    
    def __init__(self):
        super().__init__()
        self.test_duration = 60  # seconds
        self.difficulty = 'medium'
        self.test_type = 'words'  # 'words' or 'sentences'
        self.words_typed = []
        self.start_time = None
        self.end_time = None
    
    def select_test_type(self):
        """Let user select test type and difficulty"""
        self.show_header("⌨️ TYPING TEST")
        
        print("Select test type:")
        print()
        print("  1) Words - Easy")
        print("  2) Words - Medium")
        print("  3) Words - Hard")
        print("  4) Sentences")
        print("  5) Custom duration")
        print()
        
        choice = input("Enter choice [1-5]: ")
        
        if choice == '1':
            self.difficulty = 'easy'
            self.test_type = 'words'
        elif choice == '2':
            self.difficulty = 'medium'
            self.test_type = 'words'
        elif choice == '3':
            self.difficulty = 'hard'
            self.test_type = 'words'
        elif choice == '4':
            self.test_type = 'sentences'
            self.difficulty = 'sentences'
        elif choice == '5':
            self.set_custom_duration()
            return self.select_test_type()  # Re-select after setting duration
        else:
            self.print_color("Invalid choice, using medium difficulty", 'YELLOW')
    
    def set_custom_duration(self):
        """Set custom test duration"""
        print("\nCurrent duration: {} seconds".format(self.test_duration))
        duration = input("Enter duration in seconds (30-300): ")
        
        try:
            duration = int(duration)
            if 30 <= duration <= 300:
                self.test_duration = duration
                self.print_color(f"✅ Duration set to {duration} seconds", 'GREEN')
            else:
                self.print_color("Duration must be between 30 and 300 seconds", 'YELLOW')
        except ValueError:
            self.print_color("Invalid input, keeping current duration", 'YELLOW')
        
        time.sleep(1)
    
    def get_test_text(self) -> str:
        """Get the next text to type"""
        if self.test_type == 'sentences':
            return random.choice(self.WORD_LISTS['sentences'])
        else:
            # Get 5-8 random words for a line
            num_words = random.randint(5, 8)
            words = random.sample(self.WORD_LISTS[self.difficulty], 
                                min(num_words, len(self.WORD_LISTS[self.difficulty])))
            return ' '.join(words)
    
    def display_instructions(self):
        """Display test instructions"""
        self.clear_screen()
        self.show_header("⌨️ TYPING TEST")
        
        self.print_color(f"Test Type: {self.test_type.title()} - {self.difficulty.title()}", 'CYAN')
        print(f"Duration: {self.test_duration} seconds")
        print()
        
        self.print_color("📋 Instructions:", 'CYAN')
        print("  • Type the text exactly as shown")
        print("  • Press SPACE between words")
        print("  • Press ENTER to submit each line")
        print("  • Accuracy matters more than speed")
        print("  • The test will run for {} seconds".format(self.test_duration))
        print()
        
        # Ensure trainer is OFF initially
        if self.is_trainer_active():
            self.ensure_trainer_off()
        
        input("Press Enter to start the test...")
    
    def run_test(self):
        """Run the main typing test"""
        self.clear_screen()
        
        # Activate trainer
        if not self.ensure_trainer_on():
            self.print_color("⚠️ Could not activate trainer automatically.", 'YELLOW')
            print("Please press Cmd+Shift+- manually to activate.")
            input("Press Enter when you see '🔴 Trainer ON'...")
        
        self.clear_capture_file()
        
        # Test header
        self.print_color("🔴 TYPING TEST IN PROGRESS", 'RED')
        print("=" * 50)
        print()
        
        self.start_time = time.time()
        self.end_time = self.start_time + self.test_duration
        
        correct_chars = 0
        total_chars = 0
        words_completed = 0
        current_text = self.get_test_text()
        current_typed = ""
        
        # Display first text
        print("Type this:")
        self.print_color(f"  {current_text}", 'MAGENTA')
        print()
        print("Your typing: ", end='', flush=True)
        
        while time.time() < self.end_time:
            remaining = int(self.end_time - time.time())
            
            # Read new keys
            keys = self.read_new_keys()
            
            for key in keys:
                # Handle special keys
                if key.lower() == 'return':
                    # Check if they typed the text correctly
                    if current_typed.strip() == current_text:
                        correct_chars += len(current_text)
                        words_completed += len(current_text.split())
                        self.print_color(" ✅", 'GREEN')
                    else:
                        self.print_color(" ❌", 'RED')
                    
                    total_chars += len(current_text)
                    
                    # Get new text
                    current_text = self.get_test_text()
                    current_typed = ""
                    
                    print(f"\n[{remaining}s remaining]")
                    print("\nType this:")
                    self.print_color(f"  {current_text}", 'MAGENTA')
                    print()
                    print("Your typing: ", end='', flush=True)
                    
                elif key.lower() == 'delete':
                    if current_typed:
                        current_typed = current_typed[:-1]
                        print('\b \b', end='', flush=True)
                        
                elif key.lower() == 'space':
                    current_typed += ' '
                    print(' ', end='', flush=True)
                    
                elif key.lower() in ['escape', 'esc']:
                    print("\n\n[Test cancelled]")
                    return None
                    
                elif len(key) == 1 or key in ['!', '@', '#', '$', '%', '^', '&', '*', 
                                              '(', ')', '-', '_', '=', '+', '[', ']',
                                              '{', '}', '\\', '|', ';', ':', "'", '"',
                                              ',', '.', '<', '>', '/', '?']:
                    # Regular character
                    current_typed += key
                    print(key, end='', flush=True)
            
            time.sleep(0.01)
        
        # Test complete
        print("\n\n" + "=" * 50)
        self.print_color("⏱️ TIME'S UP!", 'YELLOW')
        
        # Calculate results
        duration = self.test_duration
        accuracy = (correct_chars / total_chars * 100) if total_chars > 0 else 0
        wpm = (words_completed / duration) * 60
        
        return {
            'duration': duration,
            'words': words_completed,
            'accuracy': accuracy,
            'wpm': wpm,
            'correct_chars': correct_chars,
            'total_chars': total_chars
        }
    
    def show_results(self, results):
        """Display test results"""
        if results is None:
            return
        
        self.show_header("📊 TYPING TEST RESULTS")
        
        # Main metrics
        print(f"Duration: {results['duration']} seconds")
        print(f"Words typed: {results['words']}")
        print()
        
        # WPM with color coding
        wpm = results['wpm']
        print(f"Speed: ", end='')
        if wpm >= 60:
            self.print_color(f"{wpm:.1f} WPM - Excellent! 🚀", 'GREEN')
        elif wpm >= 40:
            self.print_color(f"{wpm:.1f} WPM - Good! 👍", 'YELLOW')
        elif wpm >= 25:
            self.print_color(f"{wpm:.1f} WPM - Keep practicing! 💪", 'CYAN')
        else:
            self.print_color(f"{wpm:.1f} WPM - Focus on accuracy first 🎯", 'MAGENTA')
        
        # Accuracy with color coding
        accuracy = results['accuracy']
        print(f"Accuracy: ", end='')
        if accuracy >= 95:
            self.print_color(f"{accuracy:.1f}% - Perfect! ⭐", 'GREEN')
        elif accuracy >= 85:
            self.print_color(f"{accuracy:.1f}% - Very good! ✨", 'YELLOW')
        elif accuracy >= 70:
            self.print_color(f"{accuracy:.1f}% - Good effort! 👌", 'CYAN')
        else:
            self.print_color(f"{accuracy:.1f}% - Slow down for accuracy 🎯", 'MAGENTA')
        
        print()
        print("-" * 50)
        
        # Tips based on performance
        self.print_color("💡 Tips:", 'CYAN')
        
        if wpm < 30:
            print("  • Focus on accuracy over speed")
            print("  • Practice touch typing fundamentals")
            print("  • Use all fingers, not just index fingers")
        elif wpm < 50:
            print("  • Good progress! Keep practicing daily")
            print("  • Try not to look at the keyboard")
            print("  • Focus on problem keys")
        else:
            print("  • Excellent typing speed!")
            print("  • Challenge yourself with harder texts")
            print("  • Try typing code or technical content")
        
        if accuracy < 90:
            print("  • Slow down to improve accuracy")
            print("  • Accuracy is more important than speed")
            print("  • Speed will come naturally with practice")
    
    def run(self):
        """Main entry point"""
        try:
            self.select_test_type()
            self.display_instructions()
            results = self.run_test()
            
            # Ensure trainer is off
            self.ensure_trainer_off()
            
            if results:
                self.show_results(results)
                
                print("\n" + "=" * 50)
                choice = input("\nTry again? (y/n): ")
                if choice.lower() == 'y':
                    self.run()
            else:
                print("\nTest cancelled.")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Test interrupted!")
            self.ensure_trainer_off()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.ensure_trainer_off()
        
        print("\nYour keyboard is back to normal! ⌨️")


def main():
    """Main entry point"""
    test = TypingTest()
    test.run()


if __name__ == "__main__":
    main()