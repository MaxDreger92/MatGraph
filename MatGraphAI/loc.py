import os

def count_lines_of_code(directory):
    total_lines = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    total_lines += sum(1 for line in f)
    return total_lines

# Replace 'your/project/directory' with the path to your project directory
directory_path = './'
total_lines = count_lines_of_code(directory_path)
print(f"Total lines of Python code: {total_lines}")
