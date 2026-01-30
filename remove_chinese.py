#!/usr/bin/env python3
"""
Remove Chinese characters from Esperanto translation files.
Also translate English terms to Esperanto using a dictionary.
"""

import os
import re

# Dictionary for English to Esperanto translation (partial)
TRANSLATION_DICT = {
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
    "AI": "AI",
    "cloud brain": "nuba cerbo",
    "rule": "regulo",
    "database": "datumbazo",
    "system": "sistemo",
}

def remove_chinese(text):
    """Remove CJK Unified Ideographs and other Chinese punctuation."""
    # Regex matching Chinese characters (CJK Unified Ideographs)
    # Also includes common Chinese punctuation
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')
    return chinese_pattern.sub('', text)

def translate_english(text):
    """Replace English terms with Esperanto equivalents."""
    translated = text
    for en, eo in TRANSLATION_DICT.items():
        translated = translated.replace(en, eo)
    return translated

def process_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    output_lines = []
    in_code_block = False
    
    for line in lines:
        # Detect code block start/end
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            output_lines.append(line)
            continue
        
        if not in_code_block:
            # Remove Chinese characters
            line = remove_chinese(line)
            # Translate English terms
            line = translate_english(line)
        
        output_lines.append(line)
    
    new_content = '\n'.join(output_lines)
    # Remove extra blank lines caused by removal
    new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  Done.")

if __name__ == '__main__':
    priority1 = [
        "EDITOR_PLUGIN_ARCHITECTURE_eo.md",
        "PLUGIN_ENTRY_eo.md",
        "SETUP_GUIDE_eo.md"
    ]
    for f in priority1:
        if os.path.exists(f):
            process_file(f)
        else:
            print(f"File not found: {f}")
    print("Completed removal of Chinese characters and basic translation.")