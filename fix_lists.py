import re

with open('/Users/harshit/Desktop/yord/README.md', 'r') as f:
    lines = f.readlines()

new_lines = []

for i, line in enumerate(lines):
    is_list_item = bool(re.match(r'^\s*[-*]\s', line) or re.match(r'^\s*\d+\.\s', line))
    
    if is_list_item:
        if i > 0:
            prev_line = lines[i-1]
            is_prev_list_item = bool(re.match(r'^\s*[-*]\s', prev_line) or re.match(r'^\s*\d+\.\s', prev_line))
            # If the previous line is not empty and not another list item, we should insert a blank line.
            if prev_line.strip() != '' and not is_prev_list_item:
                if len(new_lines) > 0 and new_lines[-1].strip() != '':
                    new_lines.append('\n')

    new_lines.append(line)

with open('/Users/harshit/Desktop/yord/README.md', 'w') as f:
    f.writelines(new_lines)

print(f"Original length: {len(lines)}, New length: {len(new_lines)}")
