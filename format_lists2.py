import re

with open('/Users/harshit/Desktop/yord/README.md', 'r') as f:
    lines = f.readlines()

new_lines = []
in_list = False
fixes = 0

for i, line in enumerate(lines):
    is_list_item = bool(re.match(r'^\s*[-*]\s', line) or re.match(r'^\s*\d+\.\s', line))
    is_empty = (line.strip() == '')
    
    if is_list_item:
        if not in_list:
            if len(new_lines) > 0:
                prev_line = new_lines[-1]
                if prev_line.strip() != '' and not prev_line.startswith('#') and not prev_line.startswith('>'):
                    new_lines.append('\n')
                    fixes += 1
        in_list = True
    else:
        if not is_empty and not (line.startswith(' ') or line.startswith('\t')):
            in_list = False

    new_lines.append(line)

with open('/Users/harshit/Desktop/yord/README.md', 'w') as f:
    f.writelines(new_lines)

print(f"Fixed {fixes} lists missing blank lines.")
