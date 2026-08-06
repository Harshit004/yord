import re

def convert_to_inline_math(filepath):
    with open(filepath, 'r') as f:
        text = f.read()

    # Find all $$ ... $$ blocks, regardless of indentation
    # We will replace them with inline math $ ... $
    # And we'll strip internal newlines to ensure it renders as a single inline block
    def replace_func(match):
        indent = match.group(1)
        math_content = match.group(2).strip()
        # Remove newlines inside the math content
        math_content = re.sub(r'\s*\n\s*', ' ', math_content)
        # Wrap with $
        return f"{indent}${math_content}$"

    # Match an optional indent, $$, anything in between, and $$
    new_text = re.sub(r'^([ \t]*)\$\$\n(.*?)\n[ \t]*\$\$', replace_func, text, flags=re.MULTILINE | re.DOTALL)

    with open(filepath, 'w') as f:
        f.write(new_text)

if __name__ == "__main__":
    convert_to_inline_math('/Users/harshit/Desktop/yord/README.md')
