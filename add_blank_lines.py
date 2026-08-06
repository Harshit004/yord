import os

def add_blank_lines_around_math(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    new_lines = []
    in_math = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '$$':
            if not in_math:
                # Entering math block
                # Ensure blank line before
                if new_lines and new_lines[-1].strip() != '':
                    new_lines.append('\n')
                new_lines.append(line)
                in_math = True
            else:
                # Exiting math block
                new_lines.append(line)
                in_math = False
                # Ensure blank line after
                if i + 1 < len(lines) and lines[i+1].strip() != '':
                    new_lines.append('\n')
        else:
            new_lines.append(line)

    with open(filepath, 'w') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    add_blank_lines_around_math('/Users/harshit/Desktop/yord/README.md')
