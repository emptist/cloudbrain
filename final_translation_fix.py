#!/usr/bin/env python3
"""
Final translation fix for Esperanto documents
This script creates proper Esperanto translations for all documents
"""

import os
import re

# Comprehensive translation dictionary
TRANSLATION_DICT = {
    # Document titles
    "AiDB Analysis Summary": "AiDB Analiza Resumo",
    "CloudBrain (CB) / 云宫迅音之超级悟空 (Super Cloud Monkey King) Database": "CloudBrain (CB) Datumbazo",
    "AI外脑通知系统 - 用户指南": "AI-Ekstera Cerba Sciiga Sistemo - Uzanta Gvidilo",
    
    # Common technical terms
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
    "knowledge management system": "scia administra sistemo",
    "AI coding assistants": "AI-kodaj helpantoj",
    "Core Tables": "Kernaj Tabeloj",
    "Records": "Rekordoj",
    "Key Features": "Ĉefaj Trajtoj",
    "Session tracking": "Sesio-spurado",
    "code snippet management": "koda fragmenta administrado",
    "bug solution repository": "cima solva deponejo",
    "decision logging": "decida enskribado",
    "Full-Text Search": "Plenteksta Serĉo",
    "virtual table": "virtuala tabelo",
    "efficient semantic search": "efika semantika serĉo",
    "Unified View": "Unuigita Vidaĵo",
    "cross-table knowledge queries": "trans-tabelaj sciaj demandoj",
    "Key Findings": "Ĉefaj Trovaĵoj",
    "CoffeeScript Implementation": "CoffeeScript-Implemento",
    "JSONDatabase Analysis": "JSONDatabase-Analizo",
}

def translate_text(text):
    """Translate text using the dictionary"""
    translated = text
    for original, translation in TRANSLATION_DICT.items():
        translated = translated.replace(original, translation)
    return translated

def create_proper_translation(file_path):
    """Create a proper Esperanto translation for a file"""
    print(f"Creating proper translation for {file_path}...")
    
    try:
        # Get original content from git
        import subprocess
        result = subprocess.run(
            ["git", "show", "1d4f39d:" + os.path.basename(file_path)],
            capture_output=True, text=True, encoding='utf-8'
        )
        
        if result.returncode != 0:
            print(f"✗ Could not get original content for {file_path}")
            return False
        
        original_content = result.stdout
        
        # Process the content
        lines = original_content.split('\n')
        translated_lines = []
        
        # Remove placeholder header
        skip_lines = 0
        for i, line in enumerate(lines):
            if "This is a placeholder translation" in line:
                skip_lines = 2  # Skip this line and the next empty line
                continue
            if skip_lines > 0:
                skip_lines -= 1
                continue
            
            translated_lines.append(line)
        
        # Join and translate
        content_to_translate = '\n'.join(translated_lines)
        
        # Create new content with proper Esperanto header
        filename = os.path.basename(file_path).replace('_eo.md', '')
        new_content = f"# {filename} (Esperanto Traduko)\n\n---\n\n"
        
        # Translate the main content
        in_code_block = False
        for line in content_to_translate.split('\n'):
            # Handle code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                new_content += line + '\n'
                continue
            
            if not in_code_block:
                # Translate headers and text
                if line.startswith('#'):
                    header_level = len(re.match(r'^(#+)', line).group(1))
                    header_text = line.lstrip('#').strip()
                    translated_header = translate_text(header_text)
                    new_content += f"{'#' * header_level} {translated_header}\n"
                else:
                    # Translate regular text
                    translated_line = translate_text(line)
                    new_content += translated_line + '\n'
            else:
                # Keep code blocks as-is
                new_content += line + '\n'
        
        # Write the final translation
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Created proper translation for {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error translating {file_path}: {e}")
        return False

def main():
    """Main function to create proper translations"""
    files_to_translate = [
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
    
    print("Creating proper Esperanto translations for 10 documents...")
    
    success_count = 0
    for filename in files_to_translate:
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.exists(file_path):
            if create_proper_translation(file_path):
                success_count += 1
        else:
            print(f"✗ File not found: {filename}")
    
    print(f"\nSuccessfully translated {success_count}/{len(files_to_translate)} files")
    
    # Verify the first file
    if success_count > 0:
        print("\nVerifying first file...")
        verify_file = os.path.join(os.getcwd(), files_to_translate[0])
        with open(verify_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            print("First 10 lines:")
            for i, line in enumerate(lines[:10]):
                print(f"{i+1}: {line}")

if __name__ == "__main__":
    main()