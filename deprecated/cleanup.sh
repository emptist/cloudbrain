#!/bin/bash
# Complete Cleanup Script
# Removes conda and cleans up Python packages

echo "=========================================="
echo "🧹 Complete Cleanup Script"
echo "=========================================="
echo ""

# Part 1: Remove Conda
echo "📦 Part 1: Removing Conda"
echo "------------------------------------------"
echo ""

if command -v conda &>/dev/null; then
    echo "⚠️  Conda found"
    
    # Try conda's own uninstall
    if [ -f "$HOME/anaconda3/uninstall.sh" ]; then
        echo "Running anaconda3 uninstall..."
        bash "$HOME/anaconda3/uninstall.sh"
    elif [ -f "$HOME/anaconda2/uninstall.sh" ]; then
        echo "Running anaconda2 uninstall..."
        bash "$HOME/anaconda2/uninstall.sh"
    elif [ -f "$HOME/miniconda3/uninstall.sh" ]; then
        echo "Running miniconda3 uninstall..."
        bash "$HOME/miniconda3/uninstall.sh"
    elif [ -f "$HOME/miniconda2/uninstall.sh" ]; then
        echo "Running miniconda2 uninstall..."
        bash "$HOME/miniconda2/uninstall.sh"
    else
        echo "Manual removal..."
        
        # Remove directories
        for dir in "$HOME/anaconda3" "$HOME/anaconda2" "$HOME/miniconda3" "$HOME/miniconda2" "$HOME/conda"; do
            if [ -d "$dir" ]; then
                rm -rf "$dir"
                echo "Removed: $dir"
            fi
        done
        
        # Remove from shell configs
        for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.zprofile"; do
            if [ -f "$rc" ]; then
                sed -i '/conda/d' "$rc"
                echo "Cleaned: $rc"
            fi
        done
        
        # Remove conda command
        for path in /usr/local/bin /usr/bin /opt/homebrew/bin; do
            for cmd in conda mamba; do
                if [ -f "$path/$cmd" ]; then
                    sudo rm -f "$path/$cmd" 2>/dev/null || rm -f "$path/$cmd"
                    echo "Removed: $path/$cmd"
                fi
            done
        done
    fi
    
    # Remove conda configs
    for file in "$HOME/.conda" "$HOME/.condarc"; do
        if [ -f "$file" ]; then
            rm -f "$file"
            echo "Removed: $file"
        fi
    done
    
    echo "✅ Conda removed!"
else
    echo "✅ No conda found"
fi

echo ""
echo ""

# Part 2: Clean up Python packages (before venv)
echo "📦 Part 2: Cleaning Python Packages"
echo "------------------------------------------"
echo ""

# Check if we're in the cloudbrain directory
if [ -f "requirements.txt" ]; then
    echo "📍 Found requirements.txt in current directory"
    echo ""
    
    # Show current Python
    CURRENT_PYTHON=$(which python3)
    echo "Current Python: $CURRENT_PYTHON"
    echo ""
    
    # Show pip location
    PIP_LOCATION=$(python3 -m pip show pip | grep "Location:" | awk '{print $2}')
    echo "Pip location: $PIP_LOCATION"
    echo ""
    
    # List installed packages
    echo "📦 Installed packages:"
    python3 -m pip list --format=columns | head -20
    echo ""
    
    echo "⚠️  These packages were installed BEFORE the .venv"
    echo "⚠️  They are in system Python, not in .venv"
    echo ""
    
    echo "💡 To clean them up:"
    echo "   1. Use: python3 -m pip uninstall <package>"
    echo "   2. Or: python3 -m pip cache purge"
    echo ""
    
    read -p "Do you want to clean up these packages? (y/n): " clean_packages
    
    if [ "$clean_packages" = "y" ] || [ "$clean_packages" = "Y" ]; then
        echo ""
        echo "🧹 Cleaning up packages..."
        echo ""
        
        # Uninstall packages that were installed
        PACKAGES_TO_REMOVE=("websockets" "httpx" "psycopg2-binary" "anyio" "h11" "httpcore" "certifi" "idna")
        
        for package in "${PACKAGES_TO_REMOVE[@]}"; do
            if python3 -m pip show "$package" &>/dev/null; then
                echo "Uninstalling: $package"
                python3 -m pip uninstall -y "$package"
            fi
        done
        
        # Clean pip cache
        echo ""
        echo "🧹 Cleaning pip cache..."
        python3 -m pip cache purge
        
        echo ""
        echo "✅ Packages cleaned up!"
    else
        echo "⏭ Skipping package cleanup"
    fi
else
    echo "⚠️  requirements.txt not found"
    echo "Are you in the cloudbrain directory?"
fi

echo ""
echo ""

# Part 3: Verify cleanup
echo "📦 Part 3: Verification"
echo "------------------------------------------"
echo ""

echo "🔍 Checking for conda..."
if command -v conda &>/dev/null; then
    echo "⚠️  Conda still found!"
    echo "   Location: $(which conda)"
    echo "   You may need to restart your terminal"
else
    echo "✅ No conda found"
fi

echo ""
echo "🔍 Checking Python..."
echo "   Python: $(which python3)"
echo "   Pip: $(python3 -m pip --version)"

echo ""
echo "🔍 Checking .venv..."
if [ -d ".venv" ]; then
    echo "✅ .venv exists"
    echo "   Location: $(pwd)/.venv"
    echo "   Python: $(.venv/bin/python3 --version 2>&1 | head -1)"
else
    echo "⚠️  .venv not found"
    echo "   Run: python3 -m venv .venv"
fi

echo ""
echo "=========================================="
echo "📝 Summary"
echo "=========================================="
echo ""

echo "✅ Cleanup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Restart your terminal"
echo "   2. Verify: which python3"
echo "   3. Activate venv: source .venv/bin/activate"
echo "   4. Start server: ./start_server.sh"
echo ""
echo "=========================================="