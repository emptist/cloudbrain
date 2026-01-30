#!/usr/bin/env python3
"""
Fix translations for Esperanto documents
This script properly translates the content from Chinese/English to Esperanto
"""

import os
import re

# Comprehensive translation dictionary
TRANSLATION_DICT = {
    # English to Esperanto
    "Overview": "Superrigardo",
    "Summary": "Resumo", 
    "Analysis": "Analizo",
    "Database": "Datumbazo",
    "System": "Sistemo",
    "Implementation": "Implemento",
    "Guide": "Gvidilo",
    "Reference": "Referenco",
    "Setup": "Agordo",
    "Current State": "Nuna Stato",
    "Architecture": "Arkitekturo",
    "Plugin": "Kromaĵo",
    "Entry": "Enirejo",
    "Feedback": "Retrokuplo",
    "Ready for Copy": "Pretas por Kopio",
    "Client Security": "Klienta Sekureco",
    "Override": "Superregi",
    "AiDB Analysis Summary": "AiDB Analiza Resumo",
    "CloudBrain (CB) / 云宫迅音之超级悟空 (Super Cloud Monkey King) Database": "CloudBrain (CB) Datumbazo",
    "AI外脑通知系统 - 用户指南": "AI-Ekstera Cerba Sciiga Sistemo - Uzanta Gvidilo",
    
    # Chinese to Esperanto
    "概述": "Superrigardo",
    "分析总结": "Analiza Resumo",
    "数据库": "Datumbazo", 
    "当前状态": "Nuna Stato",
    "编辑器插件架构": "Redaktila Kromaĵa Arkitekturo",
    "插件入口": "Kromaĵa Enirejo",
    "反馈": "Retrokuplo",
    "准备复制": "Pretas por Kopio",
    "参考资料": "Referencaj Materialoj",
    "规则3:客户端安全覆盖": "Regulo 3: Klienta Sekureca Superregado",
    "设置指南": "Agorda Gvidilo",
    
    # Common phrases
    "is a comprehensive": "estas kompreneca",
    "designed for": "desegnita por",
    "serving as": "servanta kiel",
    "external memory": "ekstera memoro",
    "storing, retrieving, and organizing": "memorado, retrovo kaj organizado",
    "code snippets": "kodaj fragmentoj",
    "bug solutions": "cimaj solvoj",
    "design decisions": "desegnaj decidoj",
    "documentation": "dokumentado",
    "contains project-agnostic": "enhavas projekto-neŭtralajn",
    "suitable for cross-project sharing": "taŭga por trans-projekta dividado",
    "designed to be portable": "desegnita por esti portebla",
    "preserving valuable": "konservante valorajn",
    "collaboration patterns": "kunlaboraj modeloj",
    "insights and best practices": "komprenoj kaj bonaj praktikoj",
    "without including": "sen inkluzivi",
    "project-specific sensitive information": "projekto-specifajn sentivajn informojn",
}

def translate_text(text):
    """Translate text using the dictionary"""
    translated = text
    for original, translation in TRANSLATION_DICT.items():
        translated = translated.replace(original, translation)
    return translated

def fix_file(file_path):
    """Fix a single file's translation"""
    print(f"Fixing {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove duplicate headers and fix structure
        lines = content.split('\n')
        cleaned_lines = []
        
        # Find the main title
        main_title = None
        for i, line in enumerate(lines):
            if line.startswith('# ') and '---' not in line and 'Esperanto' not in line:
                main_title = line[2:].strip()
                break
        
        # Rebuild content with proper structure
        new_content = f"# {os.path.basename(file_path).replace('_eo.md', '')} (Esperanto Traduko)\n\n---\n\n"
        
        if main_title:
            new_content += f"# {translate_text(main_title)}\n\n"
        
        # Process the rest of the content
        in_code_block = False
        for line in lines:
            # Skip placeholder lines and duplicates
            if 'This is a placeholder translation' in line:
                continue
            if line.startswith('# ') and 'Esperanto' in line:
                continue
            if line == '---' and '---' in new_content:
                continue
            
            # Handle code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                new_content += line + '\n'
                continue
            
            if not in_code_block:
                # Translate headers
                if line.startswith('#'):
                    header_level = len(re.match(r'^(#+)', line).group(1))
                    header_text = line.lstrip('#').strip()
                    translated_header = translate_text(header_text)
                    new_content += f"{'#' * header_level} {translated_header}\n"
                else:
                    # Translate regular text
                    new_content += translate_text(line) + '\n'
            else:
                # Keep code blocks as-is
                new_content += line + '\n'
        
        # Write back the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Fixed {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix all translations"""
    files_to_fix = [
        "ANALYSIS_SUMMARY_eo.md",
        "CLOUD_BRAIN_DB_eo.md", 
        "CURRENT_STATE_eo.md",
        "EDITOR_PLUGIN_ARCHITECTURE_eo.md",
        "PLUGIN_ENTRY_eo.md",
        "README_FEEDBACK_eo.md",
        "READY_FOR_COPY_eo.md",
        "REFERENCES_eo.md",
        "RULE_3_CLIENT_SECURITY_OVERRIDE_eo.md",
        "SETUP_GUIDE_eo.md"
    ]
    
    print("Fixing translations for 10 documents...")
    
    success_count = 0
    for filename in files_to_fix:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            if fix_file(file_path):
                success_count += 1
        else:
            print(f"✗ File not found: {filename}")
    
    print(f"\nFixed {success_count}/{len(files_to_fix)} files")

if __name__ == "__main__":
    main()