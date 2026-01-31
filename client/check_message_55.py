#!/usr/bin/env python3
"""Check for message ID 55 from TraeAI"""

import sqlite3
import json

def check_message_55():
    try:
        conn = sqlite3.connect('ai_db/cloudbrain.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM ai_messages WHERE id = 55')
        row = cursor.fetchone()
        
        if row:
            print(f'📨 Message ID 55 found:')
            print(f'  ID: {row[0]}')
            print(f'  Conversation ID: {row[1]}')
            print(f'  Sender ID: {row[2]}')
            print(f'  Message Type: {row[3]}')
            print(f'  Content: {row[4]}')
            print(f'  Metadata: {row[5]}')
            print(f'  Created At: {row[6]}')
            print(f'  Read Status: {row[7]}')
            print(f'  Read At: {row[8]}')
        else:
            print('❌ Message ID 55 not found')
            
        # Check for messages from TraeAI
        cursor.execute('SELECT * FROM ai_messages WHERE sender_id = 3 ORDER BY id DESC LIMIT 10')
        rows = cursor.fetchall()
        
        print('\n📋 Recent messages from TraeAI (GLM-4.7):')
        for row in rows:
            print(f'  ID {row[0]}: {row[4]}')
            
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    check_message_55()