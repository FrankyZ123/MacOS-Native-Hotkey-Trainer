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
