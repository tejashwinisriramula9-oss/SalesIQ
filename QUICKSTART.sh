#!/bin/bash
# SalesIQ - Quick Start Guide
# Run this script to get SalesIQ up and running

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           SalesIQ - Quick Start Setup Script               ║"
echo "║      Enterprise Business Intelligence Platform v1.0.0      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo -e "${YELLOW}[1/5]${NC} Checking Python installation..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python not found. Please install Python 3.9+"
    exit 1
fi
echo "✓ Python found"
echo ""

# Step 2: Create Virtual Environment
echo -e "${YELLOW}[2/5]${NC} Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Step 3: Activate Virtual Environment
echo -e "${YELLOW}[3/5]${NC} Activating virtual environment..."
source venv/bin/activate 2>/dev/null || venv\Scripts\activate
echo "✓ Virtual environment activated"
echo ""

# Step 4: Install Dependencies
echo -e "${YELLOW}[4/5]${NC} Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Step 5: Verify Setup
echo -e "${YELLOW}[5/5]${NC} Verifying setup..."
python verify_setup.py
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✓ SalesIQ is ready to run!                       ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║   Run the following command to start the application:      ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║   ${NC}streamlit run app.py${GREEN}                                    ║${NC}"
echo -e "${GREEN}║                                                            ║${NC}"
echo -e "${GREEN}║   The app will open at: http://localhost:8501              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
