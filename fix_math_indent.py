import re

def fix_markdown(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    out = []
    in_math_block = False
    prefix = ""
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for opening $$
        match_open = re.match(r'^([ \t>]*)\$\$\s*$', line)
        
        if not in_math_block and match_open:
            in_math_block = True
            prefix = match_open.group(1)
            out.append(line)
            i += 1
            continue
            
        if in_math_block:
            # Check for closing $$
            if line.strip() == '$$':
                in_math_block = False
                out.append(f"{prefix}$$\n")
            else:
                # Content inside math block
                # Fix double escapes \\\\ -> \\
                line = line.replace('\\\\\\\\', '\\\\')
                
                stripped = line.lstrip()
                if stripped != '':
                    out.append(f"{prefix}{stripped}")
                else:
                    out.append('\n')
            i += 1
            continue
        
        # NOT in math block
        
        # 1. Fix line 315 inline matrices
        if line.strip().startswith('**Problem**: Given a query $\\mathbf{q} = [1.0, 2.0]^T$, keys'):
            out.append("**Problem**: Given a query $\\mathbf{q} = [1.0, 2.0]^T$, keys\n")
            out.append("$$\n")
            out.append("K = \\begin{bmatrix} 2.0 & 0.0 \\\\ 1.0 & 3.0 \\end{bmatrix}\n")
            out.append("$$\n")
            out.append("and values\n")
            out.append("$$\n")
            out.append("V = \\begin{bmatrix} 4.0 & 1.0 \\\\ 0.0 & 2.0 \\end{bmatrix}\n")
            out.append("$$\n")
            out.append("with $d_k = 2$:\n")
            i += 1
            continue

        # 2. Fix line 564 inline matrix
        if 'Given $A = \\begin{bmatrix} 0 & 1 \\\\\\\\ 1 & 0 \\end{bmatrix}$,' in line:
            out.append("2. **Question**: Given \n")
            out.append("   $$\n")
            out.append("   A = \\begin{bmatrix} 0 & 1 \\\\ 1 & 0 \\end{bmatrix}\n")
            out.append("   $$\n")
            out.append("   calculate $A^2$. What does it mean?\n")
            i += 1
            continue
            
        # 3. Fix line 565 inline matrix
        if '- *Answer Key*: $A^2 = \\begin{bmatrix} 1 & 0 \\\\\\\\ 0 & 1 \\end{bmatrix}$. Nodes reach themselves' in line:
            out.append("   - *Answer Key*: \n")
            out.append("     $$\n")
            out.append("     A^2 = \\begin{bmatrix} 1 & 0 \\\\ 0 & 1 \\end{bmatrix}\n")
            out.append("     $$\n")
            out.append("     Nodes reach themselves in 2 hops due to a bidirectional cycle.\n")
            i += 1
            continue

        out.append(line)
        i += 1

    # Write back
    with open(file_path, 'w') as f:
        f.writelines(out)
    print("Done formatting.")

fix_markdown('/Users/harshit/Desktop/yord/README.md')
