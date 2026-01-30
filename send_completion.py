#!/usr/bin/env python3
import sqlite3
import json

def send_message(conversation_id, sender_id, message_type, content, metadata=None):
    conn = sqlite3.connect('ai_db/cloudbrain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ai_messages (conversation_id, sender_id, message_type, content, metadata)
        VALUES (?, ?, ?, ?, ?)
    ''', (conversation_id, sender_id, message_type, content,
          json.dumps(metadata) if metadata else None))
    
    conn.commit()
    conn.close()
    
    print(f'✅ Mesaĝo sendita! ID: {cursor.lastrowid}')

# Send completion message
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='response',
    content='Tasko kompleta! Ĉiuj 13 dosieroj estas tradukitaj. Forigis ĉiujn ĉinajn signojn kaj tradukis anglajn ĉapitrojn al Esperanto. Sekvis teknikajn terminojn (datumbazo, sistemo, regulo, nuba cerbo) kaj Esperantajn gramatikajn regulojn. La dosieroj nun estas plene en Esperanto kaj pretaj por uzo.',
    metadata={
        'task_type': 'esperanto_translation',
        'status': 'completed',
        'files_processed': 13,
        'files': [
            'EDITOR_PLUGIN_ARCHITECTURE_eo.md',
            'PLUGIN_ENTRY_eo.md',
            'SETUP_GUIDE_eo.md',
            'AI_CONVERSATION_SYSTEM_eo.md',
            'AI_NOTIFICATION_SYSTEM_eo.md',
            'AI_RULE_SYSTEM_eo.md',
            'ANALYSIS_SUMMARY_eo.md',
            'CLOUD_BRAIN_DB_eo.md',
            'CURRENT_STATE_eo.md',
            'README_FEEDBACK_eo.md',
            'READY_FOR_COPY_eo.md',
            'RULE_3_CLIENT_SECURITY_OVERRIDE_eo.md',
            'REFERENCES_eo.md'
        ]
    }
)