import re

def escape_math(filepath):
    with open(filepath, 'r') as f:
        text = f.read()

    # We need to find all inline math blocks $...$ and double their backslashes.
    # But wait, what if there are block math $$...$$? Let's handle both.
    
    # First, handle $$...$$
    def repl_block(m):
        math_content = m.group(1)
        # Double all backslashes
        math_content = math_content.replace('\\', '\\\\')
        return f"$${math_content}$$"

    text = re.sub(r'\$\$(.*?)\$\$', repl_block, text, flags=re.DOTALL)
    
    # Next, handle $...$
    def repl_inline(m):
        math_content = m.group(1)
        math_content = math_content.replace('\\', '\\\\')
        # Also replace | with \| ? No, if it was already \| we doubled the backslash so it's \\|
        # If it was just |, some parsers treat it as table. But let's stick to backslashes for now.
        return f"${math_content}$"

    text = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', repl_inline, text, flags=re.DOTALL)

    with open(filepath, 'w') as f:
        f.write(text)

if __name__ == "__main__":
    escape_math('/Users/harshit/Desktop/yord/README.md')
