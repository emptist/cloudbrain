#!/usr/bin/env python3
import os
import re

def remove_chinese(text):
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')
    return chinese_pattern.sub('', text)

files = [
    "ANALYSIS_SUMMARY_eo.md",
    "CLOUD_BRAIN_DB_eo.md",
    "CURRENT_STATE_eo.md",
    "EDITOR_PLUGIN_ARCHITECTURE_eo.md",
    "PLUGIN_ENTRY_eo.md",
    "SETUP_GUIDE_eo.md",
    "README_FEEDBACK_eo.md",
    "READY_FOR_COPY_eo.md",
    "RULE_3_CLIENT_SECURITY_OVERRIDE_eo.md",
    "REFERENCES_eo.md",
    "AI_CONVERSATION_SYSTEM_eo.md",
    "AI_NOTIFICATION_SYSTEM_eo.md",
    "AI_RULE_SYSTEM_eo.md"
]

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as fp:
            content = fp.read()
        new_content = remove_chinese(content)
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(new_content)
        print(f"Removed Chinese from {f}")
    else:
        print(f"File not found: {f}")