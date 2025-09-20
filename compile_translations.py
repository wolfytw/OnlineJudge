#!/usr/bin/env python3
"""
Compile .po files to .mo files manually since we don't have Django environment
"""
import os
import sys
import struct

def read_po_file(po_file_path):
    """
    Simple .po file parser to extract msgid and msgstr pairs
    """
    translations = {}
    current_msgid = ""
    current_msgstr = ""
    in_msgid = False
    in_msgstr = False
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('msgid '):
                if current_msgid and current_msgstr:
                    translations[current_msgid] = current_msgstr
                current_msgid = line[6:].strip('"')
                current_msgstr = ""
                in_msgid = True
                in_msgstr = False
            elif line.startswith('msgstr '):
                current_msgstr = line[7:].strip('"')
                in_msgid = False
                in_msgstr = True
            elif line.startswith('"') and line.endswith('"'):
                content = line[1:-1]
                if in_msgid:
                    current_msgid += content
                elif in_msgstr:
                    current_msgstr += content
    
    # Add the last translation
    if current_msgid and current_msgstr:
        translations[current_msgid] = current_msgstr
    
    return translations

def write_mo_file(mo_file_path, translations):
    """
    Write a simple .mo file
    """
    # Filter out empty translations
    translations = {k: v for k, v in translations.items() if k and v}
    
    if not translations:
        print("No translations found, creating empty .mo file")
        with open(mo_file_path, 'wb') as f:
            # Write minimal .mo file header
            f.write(struct.pack('<I', 0x950412de))  # Magic number
            f.write(struct.pack('<I', 0))  # Version
            f.write(struct.pack('<I', 0))  # Number of strings
            f.write(struct.pack('<I', 28))  # Offset of key table
            f.write(struct.pack('<I', 28))  # Offset of value table
            f.write(struct.pack('<I', 0))  # Hash table size
            f.write(struct.pack('<I', 28))  # Offset of hash table
        return
    
    # Prepare strings
    keys = list(translations.keys())
    values = list(translations.values())
    
    # Calculate offsets
    key_offsets = []
    value_offsets = []
    
    # Header size: 28 bytes + 8 bytes per string * 2 (for keys and values)
    strings_offset = 28 + len(keys) * 16
    
    current_offset = strings_offset
    
    # Calculate key offsets
    for key in keys:
        key_bytes = key.encode('utf-8')
        key_offsets.append((len(key_bytes), current_offset))
        current_offset += len(key_bytes) + 1  # +1 for null terminator
    
    # Calculate value offsets
    for value in values:
        value_bytes = value.encode('utf-8')
        value_offsets.append((len(value_bytes), current_offset))
        current_offset += len(value_bytes) + 1  # +1 for null terminator
    
    with open(mo_file_path, 'wb') as f:
        # Write header
        f.write(struct.pack('<I', 0x950412de))  # Magic number
        f.write(struct.pack('<I', 0))  # Version
        f.write(struct.pack('<I', len(keys)))  # Number of strings
        f.write(struct.pack('<I', 28))  # Offset of key table
        f.write(struct.pack('<I', 28 + len(keys) * 8))  # Offset of value table
        f.write(struct.pack('<I', 0))  # Hash table size
        f.write(struct.pack('<I', 0))  # Offset of hash table
        
        # Write key table
        for length, offset in key_offsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write value table
        for length, offset in value_offsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write strings
        for key in keys:
            f.write(key.encode('utf-8'))
            f.write(b'\x00')
        
        for value in values:
            f.write(value.encode('utf-8'))
            f.write(b'\x00')

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    po_file = os.path.join(script_dir, 'locale', 'zh_Hant', 'LC_MESSAGES', 'django.po')
    mo_file = os.path.join(script_dir, 'locale', 'zh_Hant', 'LC_MESSAGES', 'django.mo')
    
    if not os.path.exists(po_file):
        print(f"Error: {po_file} not found")
        sys.exit(1)
    
    print(f"Reading {po_file}...")
    translations = read_po_file(po_file)
    print(f"Found {len(translations)} translations")
    
    print(f"Writing {mo_file}...")
    write_mo_file(mo_file, translations)
    print("Done!")

if __name__ == '__main__':
    main()