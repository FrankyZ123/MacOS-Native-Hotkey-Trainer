# 🎮 HotKey Trainer

<div align="center">

[![macOS](https://img.shields.io/badge/macOS-10.15+-black?style=flat-square&logo=apple)](https://www.apple.com/macos/)
[![Swift](https://img.shields.io/badge/Swift-5.0+-orange?style=flat-square&logo=swift)](https://swift.org/)
[![Python](https://img.shields.io/badge/Python-3.7+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**Master keyboard shortcuts for any application through interactive practice**

[Features](#✨-features) • [Installation](#📦-installation) • [Usage](#🚀-usage) • [Contributing](#🤝-contributing) • [License](#📄-license)

</div>

---

## 🌟 Overview

HotKey Trainer is a macOS application that helps you master keyboard shortcuts for any application through interactive practice sessions. It temporarily intercepts your keyboard input, allowing you to practice shortcuts without triggering actual commands, making it safe to learn even destructive shortcuts.

### 🎯 Key Benefits

- **Safe Practice**: Keys are intercepted so you can practice any shortcut without consequences
- **Multi-Tool Support**: Learn shortcuts for VSCode, Chrome, Slack, macOS, or any app you use
- **Interactive Feedback**: Real-time validation shows if you typed the shortcut correctly
- **Progress Tracking**: See your accuracy and speed improvements over time
- **Customizable**: Add your own tools and shortcuts via simple JSON files

## ✨ Features

### 🎮 Practice Modes

- **Quiz Mode**: Practice shortcuts with instant feedback
- **Typing Test**: Improve your general typing speed and accuracy
- **Real-time Viewer**: See exactly what keys you're pressing
- **Freestyle Mode**: Manual control for custom practice sessions

### 🛠️ Smart Features

- **Automatic Trainer Control**: The app manages keyboard interception automatically
- **Chord Support**: Practice complex multi-step shortcuts (e.g., `Cmd+K` then `Cmd+S`)
- **Difficulty Levels**: Shortcuts organized by difficulty and category
- **Native Performance**: Swift-based key interceptor for zero-latency capture

## 📦 Installation

### Prerequisites

- macOS 10.15 (Catalina) or later
- Python 3.7 or later
- Xcode Command Line Tools

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hotkey-trainer.git
   cd hotkey-trainer
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   The setup script will:
   - Build the native Swift interceptor
   - Check Python dependencies
   - Configure accessibility permissions
   - Create the start script

3. **Grant Accessibility Permissions**
   
   When prompted, grant accessibility permissions to Terminal (or your terminal app):
   - Open System Preferences → Security & Privacy → Privacy → Accessibility
   - Add and check ✅ your terminal application

4. **Start the application**
   ```bash
   ./start.sh
   ```

## 🚀 Usage

### Main Menu

When you run `./start.sh`, you'll see the main menu:

```
🎮 HotKey Trainer v2.0
━━━━━━━━━━━━━━━━━━━━━
Status: 🟢 Trainer OFF (keys normal)

Choose an option:
  1) 🎯 Select Tool to Practice
  2) ⌨️  Typing Test
  3) ⚙️  Settings
  4) ❌ Exit
```

### Practice Flow

1. **Select a Tool**: Choose from available tools (VSCode, Chrome, Slack, etc.)
2. **Choose Practice Mode**: All shortcuts, by category, or random selection
3. **Practice**: Type each shortcut as shown
4. **Get Feedback**: Instant validation with helpful hints
5. **Review Results**: See your performance statistics

### Keyboard Controls

- **Toggle Trainer**: `Cmd+Shift+-` (manually toggle on/off)
- **Skip Shortcut**: `` ` `` (backtick) during practice
- **Exit Practice**: `` `` `` (double backtick) or `Ctrl+C`

## 📂 Project Structure

```
hotkey-trainer/
├── build/                  # Compiled Swift binary (generated)
├── tools/                  # JSON shortcut configurations
│   ├── shortcuts_vscode.json
│   ├── shortcuts_chrome.json
│   └── shortcuts_*.json
├── KeyInterceptor.swift    # Native key interceptor
├── launcher.py            # Main application launcher
├── quiz_system.py         # Quiz engine
├── viewer.py              # Real-time key viewer
├── typing_test.py         # Typing speed test
├── trainer_core.py        # Shared functionality
├── setup.sh              # Installation script
├── start.sh              # Application starter
└── README.md             # This file
```

## 🎨 Customization

### Adding New Tools

1. **Create a JSON file** in the `tools/` directory:
   ```json
   {
     "name": "My App",
     "icon": "🚀",
     "description": "Shortcuts for My App",
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
         "description": "New file",
         "category": "basic",
         "difficulty": 1,
         "tips": ["Creates a new file", "Most common shortcut"]
       }
     ],
     "practice_sets": {
       "all": {
         "name": "All Shortcuts",
         "description": "Practice all shortcuts"
       }
     }
   }
   ```

2. **Use the built-in tool creator**:
   - Select "Settings" from main menu
   - Choose "Add New Tool"
   - Follow the prompts

### Shortcut Format

- **Simple**: `"cmd+s"` - Single key combination
- **Chord**: `"cmd+k cmd+s"` - Multi-step shortcut
- **Modifiers**: `cmd`, `shift`, `alt`, `ctrl`, `fn`
- **Special Keys**: `space`, `return`, `escape`, `tab`, `delete`

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Accessibility Permission Required" | Grant permission in System Preferences → Security & Privacy → Accessibility |
| "Interceptor not found" | Run `./setup.sh` to build the interceptor |
| Keys not being captured | Ensure trainer shows 🔴 status, toggle with `Cmd+Shift+-` |
| Python module not found | Ensure Python 3.7+ is installed: `python3 --version` |

### Debug Mode

For verbose output, run components directly:
```bash
# Test interceptor
./build/key-interceptor

# Test specific module
python3 viewer.py
```

## 🤝 Contributing

We love contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Ideas for Contributions

- 📱 Add more tool configurations (Photoshop, Final Cut, etc.)
- 🌍 Internationalization support
- 📊 Advanced statistics and progress tracking
- 🎨 GUI version using SwiftUI or PyQt
- 🧪 Unit tests for Python components
- 📚 Video tutorials and documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the macOS community
- Inspired by typing trainers and the need for better shortcut mastery
- Thanks to all contributors and users

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/hotkey-trainer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/hotkey-trainer/discussions)

---

<div align="center">

**Happy Training! 🎮**

Made with ☕ and 🎵 by developers who forget shortcuts

</div>