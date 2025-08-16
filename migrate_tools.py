#!/usr/bin/env python3
"""
Migration helper to move shortcuts JSON files to the tools folder
"""

import shutil
from pathlib import Path

def migrate_tools():
    """Move all shortcuts_*.json files to tools directory"""
    
    # Define directories
    current_dir = Path('.')
    tools_dir = Path('tools')
    
    # Create tools directory if it doesn't exist
    tools_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all shortcuts JSON files in current directory
    json_files = list(current_dir.glob('shortcuts_*.json'))
    
    if not json_files:
        print("✅ No JSON files to migrate. All clean!")
        return
    
    print("🔍 Found the following JSON files to migrate:")
    for file in json_files:
        print(f"  • {file.name}")
    
    print(f"\n📦 These will be moved to the '{tools_dir}' folder.")
    choice = input("Continue? (y/n): ")
    
    if choice.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Migrate files
    print("\n🚀 Migrating files...")
    success_count = 0
    error_count = 0
    
    for file in json_files:
        try:
            dest = tools_dir / file.name
            
            # Check if destination already exists
            if dest.exists():
                print(f"  ⚠️  {file.name} already exists in tools folder. Skipping.")
                continue
            
            # Move the file
            shutil.move(str(file), str(dest))
            print(f"  ✅ Moved {file.name}")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to move {file.name}: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Migration Summary:")
    print(f"  ✅ Successfully moved: {success_count} files")
    if error_count > 0:
        print(f"  ❌ Failed: {error_count} files")
    
    print(f"\n✨ Your tool configurations are now organized in the '{tools_dir}' folder!")
    print("The HotKey Trainer will automatically find them there.")

if __name__ == "__main__":
    migrate_tools()