#!/usr/bin/env python3
import sqlite3
import json
import sys

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

# Send progress update
send_message(
    conversation_id=1,
    sender_id=2,
    message_type='update',
    content='Mi komencis laboron sur Prioritato 1 dosierojn. Forigis ĉinajn signojn el EDITOR_PLUGIN_ARCHITECTURE_eo.md, PLUGIN_ENTRY_eo.md, kaj SETUP_GUIDE_eo.md. Nun mi daŭrigos al Prioritato 2.',
    metadata={'task_type': 'esperanto_translation', 'status': 'in_progress', 'files_processed': 3}
)