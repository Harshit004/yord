import re

def fix_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    out = []
    in_math_block = False
    prefix = ""
    
    for i, line in enumerate(lines):
        # 1. Inline matrix replacements
        # Line 315
        if '**Problem**: Given a query $\\mathbf{q} = [1.0, 2.0]^T$, keys $K = \\begin{bmatrix}' in line:
            out.append("**Problem**: Given a query $\\mathbf{q} = [1.0, 2.0]^T$, keys\n")
            out.append("$$\n")
            out.append("K = \\begin{bmatrix} 2.0 & 0.0 \\\\ 1.0 & 3.0 \\end{bmatrix}\n")
            out.append("$$\n")
            out.append("and values\n")
            out.append("$$\n")
            out.append("V = \\begin{bmatrix} 4.0 & 1.0 \\\\ 0.0 & 2.0 \\end{bmatrix}\n")
            out.append("$$\n")
            out.append("with $d_k = 2$:\n")
            continue
            
        # Line 564
        if 'Given $A = \\begin{bmatrix} 0 & 1 \\\\\\\\ 1 & 0 \\end{bmatrix}$, calculate' in line:
            out.append("2. **Question**: Given \n")
            out.append("   $$\n")
            out.append("   A = \\begin{bmatrix} 0 & 1 \\\\ 1 & 0 \\end{bmatrix}\n")
            out.append("   $$\n")
            out.append("   calculate $A^2$. What does it mean?\n")
            continue
            
        # Line 565
        if '- *Answer Key*: $A^2 = \\begin{bmatrix} 1 & 0 \\\\\\\\ 0 & 1 \\end{bmatrix}$. Nodes reach' in line:
            out.append("   - *Answer Key*: \n")
            out.append("     $$\n")
            out.append("     A^2 = \\begin{bmatrix} 1 & 0 \\\\ 0 & 1 \\end{bmatrix}\n")
            out.append("     $$\n")
            out.append("     Nodes reach themselves in 2 hops due to a bidirectional cycle.\n")
            continue

        # 2. Block math indentation and \\\\ fixing
        match_open = re.match(r'^([ \t>]*)\$\$\s*$', line)
        if not in_math_block and match_open:
            in_math_block = True
            prefix = match_open.group(1)
            out.append(line)
            continue
            
        if in_math_block:
            match_close = re.match(r'^([ \t>]*)\$\$\s*$', line)
            if match_close:
                in_math_block = False
                out.append(f"{prefix}$$\n")
            else:
                line = line.replace('\\\\\\\\', '\\\\')
                stripped = re.sub(r'^[ \t>]*', '', line).rstrip('\n')
                if stripped != '':
                    out.append(f"{prefix}{stripped}\n")
                else:
                    out.append(prefix.rstrip(" \t") + "\n")
            continue
            
        out.append(line)

    with open(file_path, 'w') as f:
        f.writelines(out)

fix_file('/Users/harshit/Desktop/yord/README.md')
