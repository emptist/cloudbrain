#!/usr/bin/env python3
"""Fix indentation in start_server.py"""

import re

with open('/Users/jk/gits/hub/cloudbrain/server/start_server.py', 'r') as f:
    lines = f.readlines()

# Find the outer try block and fix indentation
output = []
in_outer_try = False
outer_try_indent = 0

for i, line in enumerate(lines, 1):
    stripped = line.lstrip()
    
    # Check if this is the outer try statement
    if stripped.startswith('try:') and 'async def handle_client' in ''.join(lines[max(0, i-10):i]):
        in_outer_try = True
        outer_try_indent = len(line) - len(stripped)
        output.append(line)
        continue
    
    # If we're in the outer try block
    if in_outer_try:
        current_indent = len(line) - len(stripped)
        
        # Check if this is an except/finally for the outer try
        if stripped.startswith('except ') or stripped.startswith('finally:'):
            # This should be at the same level as the outer try
            if current_indent == outer_try_indent:
                output.append(line)
            else:
                # Fix indentation
                output.append(' ' * outer_try_indent + stripped + '\n')
            continue
        
        # Check if we're starting a new method (end of outer try)
        if stripped.startswith('async def ') or stripped.startswith('def '):
            in_outer_try = False
            output.append(line)
            continue
    
    output.append(line)

with open('/Users/jk/gits/hub/cloudbrain/server/start_server.py', 'w') as f:
    f.writelines(output)

print("Fixed indentation")