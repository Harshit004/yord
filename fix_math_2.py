import re

def fix_markdown(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 1. Replace all double backslashes in display math blocks
    def fix_display_math(match):
        block_content = match.group(0)
        # Inside this block, replace all occurrences of 4 backslashes with 2 backslashes
        # In regex, \\\\ matches two backslashes. To replace 4 backslashes, we need \\\\\\\\ in regex.
        # But let's just do a string replace
        fixed = block_content.replace('\\\\\\\\', '\\\\')
        return fixed
    
    # regex for display math: $$ ... $$
    content = re.sub(r'\$\$.*?\$\$', fix_display_math, content, flags=re.DOTALL)
    
    # 2. Extract inline bmatrix to display math
    # We find things like: $K = \begin{bmatrix}... \end{bmatrix}$
    # And replace with $$ K = \begin{bmatrix}... \end{bmatrix} $$
    def extract_matrix(match):
        # match.group(0) is the entire inline math $...$
        inner = match.group(1)
        # return a display math block
        return f"\n$$\n{inner}\n$$\n"

    # Match $...$ containing begin{bmatrix}
    content = re.sub(r'\$([^$]*?\\begin\{bmatrix\}.*?\\end\{bmatrix\}[^$]*?)\$', extract_matrix, content, flags=re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
        
fix_markdown('/Users/harshit/Desktop/yord/README.md')
