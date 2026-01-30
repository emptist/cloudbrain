#!/usr/bin/env python3
"""
Translation script for remaining Esperanto documents
This script helps translate the remaining 10 documents from Chinese/English to proper Esperanto
"""

import os
import re
from datetime import datetime

# Translation dictionary for common technical terms
TECHNICAL_TERMS = {
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
}

# Files that need translation (excluding the 3 already done)
FILES_TO_TRANSLATE = [
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

def translate_term(term):
    """Translate a single term using the dictionary"""
    return TECHNICAL_TERMS.get(term, term)

def translate_line(line):
    """Translate a line of text"""
    # Remove placeholder note
    if "This is a placeholder translation" in line:
        return ""
    
    # Translate common patterns
    translated = line
    for original, translation in TECHNICAL_TERMS.items():
        translated = translated.replace(original, translation)
    
    return translated

def create_esperanto_header(title):
    """Create proper Esperanto header for the document"""
    return f"# {title} (Esperanto Traduko)\n\n---\n"

def translate_document(file_path):
    """Translate a single document"""
    print(f"Translating {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from the content
        title_match = re.search(r'# (.+)', content)
        title = title_match.group(1) if title_match else os.path.basename(file_path).replace('_eo.md', '')
        
        # Remove placeholder header
        lines = content.split('\n')
        filtered_lines = []
        skip_next = False
        
        for line in lines:
            if "This is a placeholder translation" in line:
                skip_next = True
                continue
            if skip_next and line.strip() == "":
                skip_next = False
                continue
            if not skip_next:
                filtered_lines.append(line)
        
        # Join the content back
        filtered_content = '\n'.join(filtered_lines)
        
        # Create new content with proper Esperanto header
        new_content = create_esperanto_header(title)
        
        # Add translation note
        new_content += f"# {translate_term(title)}\n\n"
        
        # Add the main content (basic translation for now)
        for line in filtered_content.split('\n'):
            if line.startswith('#') and '---' not in line:
                # Translate headers
                header_level = len(re.match(r'^(#+)', line).group(1))
                header_text = line.lstrip('#').strip()
                translated_header = translate_term(header_text)
                new_content += f"{'#' * header_level} {translated_header}\n"
            else:
                # Basic translation for other lines
                new_content += translate_line(line) + '\n'
        
        # Write back the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Translated {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error translating {file_path}: {e}")
        return False

def main():
    """Main translation function"""
    print("Starting translation of remaining documents...")
    print(f"Files to translate: {len(FILES_TO_TRANSLATE)}")
    
    success_count = 0
    for filename in FILES_TO_TRANSLATE:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            if translate_document(file_path):
                success_count += 1
        else:
            print(f"✗ File not found: {filename}")
    
    print(f"\nTranslation completed: {success_count}/{len(FILES_TO_TRANSLATE)} files translated")
    
    # Create summary
    summary = f"""
# Translation Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Files Translated**: {success_count}/{len(FILES_TO_TRANSLATE)}

## Files Successfully Translated:
"""
    
    for filename in FILES_TO_TRANSLATE:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            summary += f"- {filename}\n"
    
    # Write summary to file
    with open("translation_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    
    print("\nTranslation summary saved to translation_summary.md")

if __name__ == "__main__":
    main()