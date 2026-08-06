import re

with open('/Users/harshit/Desktop/yord/README.md', 'r') as f:
    lines = f.readlines()

out = []
in_math = False
prefix = ''

for i, line in enumerate(lines):
    match = re.match(r'^([ \t>]*)\$\$\s*$', line)
    
    if not in_math and match:
        in_math = True
        prefix = match.group(1)
        
        # Check if we need to insert a blank line before this opening $$
        if i > 0:
            prev_line = lines[i-1].rstrip('\n')
            # If previous line is not empty and not just '>'
            if prev_line.strip() != '' and prev_line.strip() != '>':
                # Insert blank line with the same prefix
                out.append(prefix.rstrip('\n') + '\n')
                
        out.append(line)
    elif in_math and match:
        # This is a closing $$
        in_math = False
        out.append(line)
    else:
        out.append(line)

with open('/Users/harshit/Desktop/yord/README.md', 'w') as f:
    f.writelines(out)
