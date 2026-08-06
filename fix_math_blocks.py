import re
import sys

def fix_math_blocks(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    out = []
    in_math_block = False
    
    for line in lines:
        if not in_math_block:
            # Check for opening ```math
            match = re.match(r'^([ \t>]*)```math\s*$', line)
            if match:
                in_math_block = True
                out.append(f"{match.group(1)}$$\n")
            else:
                out.append(line)
        else:
            # Check for closing ```
            match = re.match(r'^([ \t>]*)```\s*$', line)
            if match:
                in_math_block = False
                out.append(f"{match.group(1)}$$\n")
            else:
                out.append(line)
                
    with open(filepath, 'w') as f:
        f.writelines(out)

if __name__ == "__main__":
    fix_math_blocks('/Users/harshit/Desktop/yord/README.md')
