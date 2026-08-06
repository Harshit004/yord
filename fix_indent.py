import re

with open('/Users/harshit/Desktop/yord/README.md', 'r') as f:
    lines = f.readlines()

out_lines = []
in_math_block = False
prefix = ''

for line in lines:
    if not in_math_block:
        # Check if this line opens a math block
        match = re.match(r'^((?:>\s*|\s*)*)\$\$\s*$', line)
        if match:
            in_math_block = True
            prefix = match.group(1)
            out_lines.append(line)
        else:
            out_lines.append(line)
    else:
        # We are inside a math block. Check if this line closes it.
        if line.strip() == '$$':
            in_math_block = False
            out_lines.append(f"{prefix}$$\n")
        else:
            # Add prefix if it doesn't already start with it
            if line.startswith(prefix):
                out_lines.append(line)
            else:
                # Strip leading whitespace and add prefix
                out_lines.append(f"{prefix}{line.lstrip()}")

with open('/Users/harshit/Desktop/yord/README.md', 'w') as f:
    f.writelines(out_lines)
