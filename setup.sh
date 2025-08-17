#!/bin/bash

# HotKey Trainer Setup Script
# Builds and configures the Swift-based key interceptor

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     🎮 HotKey Trainer Setup            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    echo ""
}

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This tool requires macOS"
        exit 1
    fi
    
    os_version=$(sw_vers -productVersion)
    print_success "macOS $os_version detected"
    
    # Check for Swift
    if ! command -v swift &> /dev/null; then
        print_error "Swift not found!"
        echo ""
        echo "Install Xcode Command Line Tools with:"
        echo "  xcode-select --install"
        exit 1
    fi
    
    swift_version=$(swift --version 2>&1 | head -n 1)
    print_success "$swift_version"
    
    # Check for Python 3
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1)
        print_success "$python_version"
    else
        print_error "Python 3 not found!"
        echo "Please install Python 3 to use all features"
        exit 1
    fi
}

# Build the Swift interceptor
build_interceptor() {
    print_status "Building native interceptor..."
    
    if [ ! -f "KeyInterceptor.swift" ]; then
        print_error "KeyInterceptor.swift not found!"
        exit 1
    fi
    
    # Create build directory
    mkdir -p build
    
    # Compile with optimizations
    print_status "Compiling Swift code..."
    
    if swiftc -O \
        -o build/key-interceptor \
        -framework Cocoa \
        -framework ApplicationServices \
        KeyInterceptor.swift 2>build/build.log; then
        
        print_success "Build successful!"
        chmod +x build/key-interceptor
        
        # Show binary info
        local size=$(du -h build/key-interceptor | cut -f1)
        print_status "Binary size: $size"
        
    else
        print_error "Build failed! Check build/build.log for details"
        cat build/build.log
        exit 1
    fi
}

# Check Python files
check_python_files() {
    print_status "Checking Python components..."
    
    # Updated for refactored structure (removed typing_test.py)
    required_files=("trainer_core.py" "viewer.py" "quiz_system.py" "launcher.py")
    optional_files=("run_quiz.py" "migrate_tools.py")
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "$file found"
        else
            missing_files+=("$file")
        fi
    done
    
    # Check optional files
    for file in "${optional_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "$file found (optional)"
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "Missing Python files:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
}

# Check and request accessibility permissions
setup_accessibility() {
    print_status "Checking accessibility permissions..."
    
    # Create permission check script
    cat > build/check_permissions.swift << 'EOF'
import Cocoa
let trusted = AXIsProcessTrustedWithOptions(
    [kAXTrustedCheckOptionPrompt.takeUnretainedValue(): false] as CFDictionary
)
exit(trusted ? 0 : 1)
EOF
    
    if swift build/check_permissions.swift 2>/dev/null; then
        print_success "Accessibility permissions already granted"
    else
        print_warning "Accessibility permissions needed!"
        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}IMPORTANT: Grant Accessibility Permissions${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "The app needs accessibility permissions to capture keys."
        echo ""
        echo "When you first run the app, macOS will prompt you."
        echo "You'll need to:"
        echo ""
        echo "  1. Open System Preferences"
        echo "  2. Go to Security & Privacy → Privacy → Accessibility"
        echo "  3. Click the lock 🔒 to make changes"
        echo "  4. Add and check ✅ Terminal (or your terminal app)"
        echo "  5. You may need to restart the terminal"
        echo ""
        read -p "Press Enter to continue..."
    fi
    
    rm -f build/check_permissions.swift
}

# Create start script
create_start_script() {
    print_status "Creating start script..."
    
    cat > start.sh << 'EOF'
#!/bin/bash

# HotKey Trainer Starter
# Single entry point for the application

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if interceptor is built
if [ ! -f "./build/key-interceptor" ]; then
    echo -e "${YELLOW}Interceptor not found. Running setup...${NC}"
    echo ""
    
    if [ -f "./setup.sh" ]; then
        ./setup.sh
        
        # Check if setup was successful
        if [ ! -f "./build/key-interceptor" ]; then
            echo -e "${RED}Setup failed. Please check the errors above.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Error: setup.sh not found!${NC}"
        echo "Please ensure you have all required files:"
        echo "  • KeyInterceptor.swift"
        echo "  • setup.sh"
        echo "  • trainer_core.py"
        echo "  • viewer.py"
        echo "  • quiz_system.py"
        echo "  • launcher.py"
        exit 1
    fi
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check for required Python files (updated - removed typing_test.py)
required_files=("trainer_core.py" "viewer.py" "quiz_system.py" "launcher.py")
missing=false

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}Error: $file not found!${NC}"
        missing=true
    fi
done

if [ "$missing" = true ]; then
    echo "Please ensure all required Python files are present"
    exit 1
fi

# Run the launcher
echo -e "${GREEN}🎮 Starting HotKey Trainer...${NC}"
echo ""
python3 launcher.py
EOF
    
    chmod +x start.sh
    print_success "Created start.sh"
}

# Main installation
main() {
    clear
    print_header
    
    # Run all setup steps
    check_requirements
    echo ""
    
    build_interceptor
    echo ""
    
    check_python_files
    echo ""
    
    setup_accessibility
    echo ""
    
    create_start_script
    echo ""
    
    # Success message
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       ✅ Setup Complete! ✅            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Installation successful!"
    echo ""
    echo -e "${CYAN}To start HotKey Trainer:${NC}"
    echo "  ./start.sh"
    echo ""
    echo -e "${CYAN}Features:${NC}"
    echo "  • Real-time key viewer"
    echo "  • Practice quiz with shortcuts for multiple tools"
    echo "  • Freestyle practice mode"
    echo "  • Automatic trainer management"
    echo ""
    echo -e "${CYAN}Controls:${NC}"
    echo "  • Toggle: Cmd+Shift+-"
    echo "  • Exit: Ctrl+C"
    echo ""
    
    read -p "Would you like to start the app now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        ./start.sh
    fi
}

# Run main
main "$@"