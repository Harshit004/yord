import re

with open('/Users/harshit/Desktop/yord/README.md', 'r') as f:
    lines = f.readlines()

in_list = False
for i, line in enumerate(lines):
    if re.match(r'^[-*]\s', line) or re.match(r'^\d+\.\s', line):
        if not in_list and i > 0 and lines[i-1].strip() != '' and not lines[i-1].startswith('#'):
            print(f"Line {i+1}: List without preceding empty line -> {line.strip()}")
        in_list = True
    elif line.strip() == '':
        in_list = False
