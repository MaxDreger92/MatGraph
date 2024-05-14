import re

def split_pascal_case(text):
    # Function to convert PascalCase to lower case with space
    return ' '.join(re.sub('([a-z])([A-Z])', r'\1 \2', word).lower() for word in text.split())

def replace_pascal_case_in_owl(file_path):
    # Read the original file content
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all PascalCase occurrences
    pascal_case_words = set(re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', content))
    
    # Replace each PascalCase word with its new format
    for word in pascal_case_words:
        if word != "AnnotationProperty":
            new_word = split_pascal_case(word)
            content = content.replace(word, new_word)
            print(word, new_word)
    
    # Write the modified content back to the file (or to a new file)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Example usage
replace_pascal_case_in_owl('quantities.owl')

