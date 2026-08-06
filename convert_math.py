import re

def replace_dollars_with_math_blocks(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    out = []
    in_math_block = False
    prefix = ""
    
    for line in lines:
        match_open = re.match(r'^([ \t>]*)\$\$\s*$', line)
        if not in_math_block and match_open:
            in_math_block = True
            prefix = match_open.group(1)
            # Replace opening $$ with ```math
            out.append(f"{prefix}```math\n")
            continue
            
        if in_math_block:
            match_close = re.match(r'^([ \t>]*)\$\$\s*$', line)
            if match_close:
                in_math_block = False
                # Replace closing $$ with ```
                out.append(f"{prefix}```\n")
            else:
                out.append(line)
            continue
            
        out.append(line)

    with open(file_path, 'w') as f:
        f.writelines(out)

replace_dollars_with_math_blocks('/Users/harshit/Desktop/yord/README.md')
