import re

def fix_math_blocks_root(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    out = []
    in_math_block = False
    
    for line in lines:
        if not in_math_block:
            # Check for opening ```math (with or without indentation)
            match = re.match(r'^([ \t>]*)```math\s*$', line)
            if match:
                in_math_block = True
                # Always output $$ at the root level (no indentation)
                out.append("$$\n")
            else:
                out.append(line)
        else:
            # Check for closing ```
            match = re.match(r'^([ \t>]*)```\s*$', line)
            if match:
                in_math_block = False
                out.append("$$\n")
            else:
                # Remove the indentation from the math content itself as well?
                # Sometimes it's better to keep the math content unindented.
                # Let's strip the leading whitespace that matches the block's indentation.
                # But to be safe and simple, let's just strip leading spaces from math lines.
                out.append(line.lstrip(' \t'))
                
    with open(filepath, 'w') as f:
        f.writelines(out)

if __name__ == "__main__":
    fix_math_blocks_root('/Users/harshit/Desktop/yord/README.md')
