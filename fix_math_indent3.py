import re

def fix_math_indent(file_path):
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
            out.append(line)
            continue
            
        if in_math_block:
            if line.strip() == '$$':
                in_math_block = False
                out.append(f"{prefix}$$\n")
            else:
                stripped = line.lstrip()
                if stripped != '':
                    out.append(f"{prefix}{stripped}")
                else:
                    out.append('\n')
            continue
            
        out.append(line)

    with open(file_path, 'w') as f:
        f.writelines(out)

fix_math_indent('/Users/harshit/Desktop/yord/README.md')
