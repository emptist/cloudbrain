#!/bin/bash
# Complete Conda Removal Script
# Safely removes all conda installations

echo "=========================================="
echo "🧹 Complete Conda Removal"
echo "=========================================="
echo ""

# Check if conda exists
if command -v conda &>/dev/null; then
    echo "⚠️  Conda found on system"
    echo ""
    
    # Show conda info
    echo "📍 Conda locations:"
    which conda
    echo ""
    
    conda info --envs 2>/dev/null || echo "No conda environments found"
    echo ""
    
    echo "🗑  Removing conda..."
    echo ""
    
    # Method 1: Use conda's own uninstall script (if available)
    if [ -f "$HOME/anaconda3/uninstall.sh" ]; then
        echo "Using anaconda3 uninstall script..."
        bash "$HOME/anaconda3/uninstall.sh"
    elif [ -f "$HOME/anaconda2/uninstall.sh" ]; then
        echo "Using anaconda2 uninstall script..."
        bash "$HOME/anaconda2/uninstall.sh"
    elif [ -f "$HOME/miniconda3/uninstall.sh" ]; then
        echo "Using miniconda3 uninstall script..."
        bash "$HOME/miniconda3/uninstall.sh"
    elif [ -f "$HOME/miniconda2/uninstall.sh" ]; then
        echo "Using miniconda2 uninstall script..."
        bash "$HOME/miniconda2/uninstall.sh"
    else
        # Method 2: Manual removal
        echo "Using manual removal method..."
        echo ""
        
        # Remove conda directories
        CONDA_DIRS=("$HOME/anaconda3" "$HOME/anaconda2" "$HOME/miniconda3" "$HOME/miniconda2" "$HOME/conda")
        
        for dir in "${CONDA_DIRS[@]}"; do
            if [ -d "$dir" ]; then
                echo "Removing: $dir"
                rm -rf "$dir"
            fi
        done
        
        # Remove conda from PATH
        echo "Removing conda from PATH..."
        
        # Remove from .bashrc
        if [ -f "$HOME/.bashrc" ]; then
            sed -i '/conda/d' "$HOME/.bashrc"
            echo "✅ Removed from .bashrc"
        fi
        
        # Remove from .zshrc
        if [ -f "$HOME/.zshrc" ]; then
            sed -i '/conda/d' "$HOME/.zshrc"
            echo "✅ Removed from .zshrc"
        fi
        
        # Remove from .bash_profile
        if [ -f "$HOME/.bash_profile" ]; then
            sed -i '/conda/d' "$HOME/.bash_profile"
            echo "✅ Removed from .bash_profile"
        fi
        
        # Remove from .zprofile
        if [ -f "$HOME/.zprofile" ]; then
            sed -i '/conda/d' "$HOME/.zprofile"
            echo "✅ Removed from .zprofile"
        fi
    fi
    
    # Remove conda initialization scripts
    echo ""
    echo "🗑  Removing conda initialization scripts..."
    
    CONDA_INIT=("$HOME/.conda" "$HOME/.condarc")
    
    for file in "${CONDA_INIT[@]}"; do
        if [ -f "$file" ]; then
            echo "Removing: $file"
            rm -f "$file"
        fi
    done
    
    # Remove conda from shell
    echo ""
    echo "🗑  Removing conda command..."
    
    # Remove conda command if it's a script
    CONDA_CMDS=("conda" "mamba")
    
    for cmd in "${CONDA_CMDS[@]}"; do
        for path in /usr/local/bin /usr/bin /opt/homebrew/bin; do
            if [ -f "$path/$cmd" ]; then
                echo "Removing: $path/$cmd"
                sudo rm -f "$path/$cmd" 2>/dev/null || rm -f "$path/$cmd"
            fi
        done
    done
    
    echo ""
    echo "✅ Conda removal complete!"
    echo ""
    
    # Verify removal
    echo "🔍 Verifying removal..."
    
    if command -v conda &>/dev/null; then
        echo "⚠️  Conda still found!"
        echo ""
        echo "You may need to:"
        echo "1. Restart your terminal"
        echo "2. Run: source ~/.zshrc (or ~/.bashrc)"
        echo "3. Check for conda in: echo $PATH"
    else
        echo "✅ Conda successfully removed!"
        echo ""
        echo "🎉 You're now using brew Python only!"
    fi
    
else
    echo "✅ No conda installation found"
    echo ""
    echo "You're already using brew Python!"
fi

echo ""
echo "=========================================="
echo "📝 Next Steps"
echo "=========================================="
echo ""
echo "1. Restart your terminal"
echo "2. Verify Python: which python3"
echo "3. Verify pip: python3 -m pip --version"
echo "4. Start using: ./start_server.sh"
echo ""
echo "=========================================="