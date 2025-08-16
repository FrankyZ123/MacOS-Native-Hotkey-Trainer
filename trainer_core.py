#!/usr/bin/env python3
"""
Core functionality shared across all HotKey Trainer tools
"""

import time
import subprocess
import os
from pathlib import Path
from typing import Optional, List, Tuple

class TrainerCore:
    """Base class with shared functionality for all trainer tools"""
    
    def __init__(self):
        self.capture_file = Path.home() / "hotkey-trainer" / "captured_keys.txt"
        self.last_position = 0
        
        # Colors for terminal output
        self.colors = {
            'GREEN': '\033[0;32m',
            'RED': '\033[0;31m',
            'YELLOW': '\033[1;33m',
            'BLUE': '\033[0;34m',
            'CYAN': '\033[0;36m',
            'MAGENTA': '\033[0;35m',
            'NC': '\033[0m'  # No Color
        }
    
    def print_color(self, text: str, color: str = 'NC'):
        """Print colored text"""
        color_code = self.colors.get(color, self.colors['NC'])
        print(f"{color_code}{text}{self.colors['NC']}")
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def send_toggle_shortcut(self) -> None:
        """Send Cmd+Shift+- using AppleScript to toggle trainer"""
        try:
            subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to key code 27 using {command down, shift down}'
            ], capture_output=True, check=False)
            time.sleep(0.3)
        except Exception as e:
            self.print_color(f"Warning: Could not send toggle shortcut: {e}", 'YELLOW')
    
    def is_trainer_active(self) -> bool:
        """Check if trainer is currently active (capturing keys)"""
        return self.capture_file.exists()
    
    def ensure_trainer_on(self, max_attempts: int = 10) -> bool:
        """Turn trainer ON if it's not already"""
        if self.is_trainer_active():
            return True
        
        self.print_color("🔄 Activating trainer...", 'BLUE')
        self.send_toggle_shortcut()
        
        for _ in range(max_attempts):
            if self.is_trainer_active():
                self.print_color("✅ Trainer activated!", 'GREEN')
                return True
            time.sleep(0.1)
        
        return False
    
    def ensure_trainer_off(self, max_attempts: int = 10) -> bool:
        """Turn trainer OFF if it's on"""
        if not self.is_trainer_active():
            return True
        
        self.print_color("🔄 Deactivating trainer...", 'BLUE')
        self.send_toggle_shortcut()
        
        for _ in range(max_attempts):
            if not self.is_trainer_active():
                self.print_color("✅ Trainer deactivated!", 'GREEN')
                return True
            time.sleep(0.1)
        
        return False
    
    def clear_capture_file(self):
        """Clear the capture file by moving read position to end of file"""
        # Don't truncate the file since Swift has it open for writing
        # Instead, just move our read position to the current end of file
        if self.capture_file.exists():
            try:
                # Get the current file size to skip existing content
                self.last_position = self.capture_file.stat().st_size
            except (IOError, OSError):
                self.last_position = 0
        else:
            self.last_position = 0
    
    def read_new_keys(self) -> List[str]:
        """Read any new keys from capture file"""
        if not self.capture_file.exists():
            return []
        
        try:
            with open(self.capture_file, 'r') as f:
                f.seek(self.last_position)
                new_content = f.read()
                if new_content:
                    self.last_position = f.tell()
                    return [line.strip() for line in new_content.split('\n') if line.strip()]
        except (IOError, OSError):
            return []
        return []
    
    def normalize_keys(self, keys: str) -> str:
        """Normalize key combination for comparison"""
        if '+' not in keys:
            return keys.strip().lower()
        
        parts = keys.strip().lower().split('+')
        modifiers = []
        main_key = parts[-1]
        
        for part in parts[:-1]:
            if part in ['cmd', 'shift', 'alt', 'ctrl', 'fn']:
                modifiers.append(part)
        
        modifiers.sort()
        if modifiers:
            return '+'.join(modifiers) + '+' + main_key
        return main_key
    
    def check_for_exit(self, key: str, exit_keys: Optional[List[str]] = None) -> bool:
        """Check if user pressed an exit key"""
        if exit_keys is None:
            exit_keys = ['escape', 'esc', 'ctrl+c']
        
        normalized = self.normalize_keys(key)
        return normalized in exit_keys or 'escape' in normalized
    
    def show_header(self, title: str = "HotKey Trainer"):
        """Show a formatted header"""
        self.clear_screen()
        width = 42
        print("╔" + "═" * (width - 2) + "╗")
        print(f"║{title.center(width - 2)}║")
        print("╚" + "═" * (width - 2) + "╝")
        print()


class InterceptorManager:
    """Manages the key interceptor process"""
    
    def __init__(self):
        self.interceptor_path = Path("./build/key-interceptor")
        self.interceptor_process = None
        self.capture_file = Path.home() / "hotkey-trainer" / "captured_keys.txt"
    
    def check_built(self) -> bool:
        """Check if interceptor is built"""
        return self.interceptor_path.exists()
    
    def is_running(self) -> bool:
        """Check if interceptor is already running"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "key-interceptor"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def get_pid(self) -> Optional[int]:
        """Get PID of running interceptor"""
        try:
            result = subprocess.run(
                ["pgrep", "-f", "key-interceptor"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                return int(result.stdout.strip().split('\n')[0])
        except:
            pass
        return None
    
    def start(self, silent: bool = True) -> Tuple[bool, Optional[int]]:
        """
        Start the interceptor in background
        Returns: (success, pid)
        """
        if self.is_running():
            pid = self.get_pid()
            if not silent:
                print(f"⚠️  Interceptor already running (PID: {pid})")
            return True, pid
        
        if not silent:
            print("🚀 Starting interceptor...")
        
        try:
            if silent:
                self.interceptor_process = subprocess.Popen(
                    [str(self.interceptor_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            else:
                self.interceptor_process = subprocess.Popen(
                    [str(self.interceptor_path)],
                    start_new_session=True
                )
            
            time.sleep(1)
            
            if self.interceptor_process.poll() is None:
                pid = self.interceptor_process.pid
                if not silent:
                    print(f"✅ Interceptor started (PID: {pid})")
                return True, pid
            else:
                if not silent:
                    print("❌ Interceptor failed to start")
                return False, None
                
        except Exception as e:
            if not silent:
                print(f"❌ Error starting interceptor: {e}")
            return False, None
    
    def stop(self, silent: bool = False) -> bool:
        """Stop the interceptor"""
        if not silent:
            print("Stopping interceptor...")
        
        # Stop our process if we started it
        if self.interceptor_process:
            self.interceptor_process.terminate()
            try:
                self.interceptor_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.interceptor_process.kill()
            self.interceptor_process = None
        
        # Kill any other instances
        try:
            subprocess.run(
                ["pkill", "-f", "key-interceptor"],
                capture_output=True,
                check=False
            )
        except:
            pass
        
        # Clean up capture file
        if self.capture_file.exists():
            try:
                self.capture_file.unlink()
            except:
                pass
        
        if not silent:
            print("✅ Interceptor stopped")
        return True
    
    def run_foreground(self) -> None:
        """Run interceptor in foreground (for manual mode)"""
        try:
            subprocess.run([str(self.interceptor_path)])
        except KeyboardInterrupt:
            print("\nInterceptor stopped")