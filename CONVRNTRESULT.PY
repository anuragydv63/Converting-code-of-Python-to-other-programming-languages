import re
import json

class CodeConverter:
    def __init__(self):
        # Basic syntax mapping for different languages
        self.syntax_map = {
            'javascript': {
                'function': 'function',
                'print': 'console.log',
                'if': 'if',
                'else': 'else',
                'for': 'for',
                'while': 'while',
                'class': 'class',
                'return': 'return',
                'end_line': ';'
            },
            'java': {
                'function': 'public static void',
                'print': 'System.out.println',
                'if': 'if',
                'else': 'else',
                'for': 'for',
                'while': 'while',
                'class': 'public class',
                'return': 'return',
                'end_line': ';'
            },
            'cpp': {
                'function': 'void',
                'print': 'cout <<',
                'input': 'cin >>',
                'if': 'if',
                'else': 'else',
                'for': 'for',
                'while': 'while',
                'class': 'class',
                'return': 'return',
                'end_line': ';',
                'endl': ' << endl'
            }
        }

    def detect_code_structure(self, python_code):
        """Analyze Python code structure"""
        structure = {
            'functions': [],
            'classes': [],
            'variables': [],
            'imports': []
        }
        
        lines = python_code.split('\n')
        for line in lines:
            if line.startswith('def '):
                structure['functions'].append(line)
            elif line.startswith('class '):
                structure['classes'].append(line)
            elif '=' in line and not line.strip().startswith('#'):
                structure['variables'].append(line)
            elif line.startswith('import ') or line.startswith('from '):
                structure['imports'].append(line)
                
        return structure

    def convert_to_language(self, python_code, target_language):
        """Convert Python code to target language"""
        if target_language not in self.syntax_map:
            return f"Sorry, {target_language} conversion not supported yet."
            
        syntax = self.syntax_map[target_language]
        structure = self.detect_code_structure(python_code)
        converted_code = []
        
        # Add language-specific headers
        if target_language == 'cpp':
            converted_code.append('#include <iostream>\nusing namespace std;\n\nint main() {\n')
            indent_level = 1
        elif target_language == 'java':
            converted_code.append('import java.util.Scanner;\n\npublic class MainProgram {\n')
            converted_code.append('    public static void main(String[] args) {\n')
            converted_code.append('        Scanner scanner = new Scanner(System.in);\n')  # Create Scanner once
            indent_level = 2
        elif target_language == 'javascript':
            converted_code.append('// JavaScript code\n')
            indent_level = 0
            
        # Convert each line based on structure
        lines = python_code.split('\n')
        
        for line in lines:
            converted_line = line.strip()
            
            # Handle comments
            if line.strip().startswith('#'):
                if target_language in ['cpp', 'java', 'javascript']:
                    converted_line = f"// {line.strip()[1:]}"
            
            # Handle input statements
            elif 'input(' in line:
                content = re.search(r'input\((.*?)\)', line).group(1)
                if target_language == 'cpp':
                    # C++ input handling (existing code)
                    if '=' in line:
                        var_name = line.split('=')[0].strip()
                        var_type = 'double' if 'float' in line else 'int'
                        converted_line = f"{var_type} {var_name}{syntax['end_line']}\n"
                        converted_line += '    ' * indent_level + f"{syntax['print']} {content}{syntax['endl']}{syntax['end_line']}\n"
                        converted_line += '    ' * indent_level + f"{syntax['input']} {var_name}{syntax['end_line']}"
                elif target_language == 'java':
                    # Java input handling
                    if '=' in line:
                        var_name = line.split('=')[0].strip()
                        var_type = 'double' if 'float' in line else 'int'
                        converted_line = f"{var_type} {var_name}{syntax['end_line']}\n"
                        converted_line += '    ' * indent_level + f"System.out.println({content}){syntax['end_line']}\n"
                        converted_line += '    ' * indent_level + f"{var_name} = scanner.next{var_type.capitalize()}(){syntax['end_line']}"
                else:  # JavaScript
                    # JavaScript input handling
                    if '=' in line:
                        var_name = line.split('=')[0].strip()
                        converted_line = f"const {var_name} = parseFloat(prompt({content})){syntax['end_line']}"
            
            # Handle variable assignments
            elif '=' in line and not line.strip().startswith('#'):
                var_name = line.split('=')[0].strip()
                value = line.split('=')[1].strip()
                if target_language == 'cpp':
                    # C++ variable handling (existing code)
                    if value.replace('.', '').isdigit():
                        if '.' in value:
                            converted_line = f"double {var_name} = {value}{syntax['end_line']}"
                        else:
                            converted_line = f"int {var_name} = {value}{syntax['end_line']}"
                    elif value.startswith('"') or value.startswith("'"):
                        converted_line = f"string {var_name} = {value}{syntax['end_line']}"
                    elif '+' in value or '-' in value or '*' in value or '/' in value:
                        converted_line = f"auto {var_name} = {value}{syntax['end_line']}"
                elif target_language == 'java':
                    # Java variable handling
                    if value.replace('.', '').isdigit():
                        if '.' in value:
                            converted_line = f"double {var_name} = {value}{syntax['end_line']}"
                        else:
                            converted_line = f"int {var_name} = {value}{syntax['end_line']}"
                    elif value.startswith('"') or value.startswith("'"):
                        converted_line = f"String {var_name} = {value}{syntax['end_line']}"
                    elif '+' in value or '-' in value or '*' in value or '/' in value:
                        converted_line = f"double {var_name} = {value}{syntax['end_line']}"
                else:  # JavaScript
                    # JavaScript variable handling
                    if value.replace('.', '').isdigit():
                        converted_line = f"const {var_name} = {value}{syntax['end_line']}"
                    elif value.startswith('"') or value.startswith("'"):
                        converted_line = f"const {var_name} = {value}{syntax['end_line']}"
                    elif '+' in value or '-' in value or '*' in value or '/' in value:
                        converted_line = f"const {var_name} = {value}{syntax['end_line']}"
            
            # Handle functions
            elif line.startswith('def '):
                func_name = re.search(r'def (\w+)\((.*?)\):', line).group(1)
                params = re.search(r'def (\w+)\((.*?)\):', line).group(2)
                converted_line = f"{syntax['function']} {func_name}({params}) {{"
                
            # Handle print statements
            elif 'print(' in line:
                content = re.search(r'print\((.*?)\)', line).group(1)
                if target_language == 'cpp':
                    # C++ print handling (existing code)
                    if ',' in content:
                        parts = content.split(',')
                        converted_line = f"{syntax['print']} {parts[0].strip()}"
                        for part in parts[1:]:
                            converted_line += f" << {part.strip()}"
                        converted_line += f"{syntax['endl']}{syntax['end_line']}"
                    else:
                        converted_line = f"{syntax['print']} {content}{syntax['endl']}{syntax['end_line']}"
                elif target_language == 'java':
                    # Java print handling
                    if ',' in content:
                        parts = content.split(',')
                        converted_line = f"System.out.println({parts[0].strip()} + {parts[1].strip()}){syntax['end_line']}"
                    else:
                        converted_line = f"System.out.println({content}){syntax['end_line']}"
                else:  # JavaScript
                    # JavaScript print handling
                    if ',' in content:
                        parts = content.split(',')
                        converted_line = f"console.log({parts[0].strip()} + {parts[1].strip()}){syntax['end_line']}"
                    else:
                        converted_line = f"console.log({content}){syntax['end_line']}"
                
            # Handle return statements
            elif line.strip().startswith('return '):
                content = line.strip()[7:]
                converted_line = f"return {content}{syntax['end_line']}"
                
            if converted_line:
                converted_code.append('    ' * indent_level + converted_line)
                
            if line.strip() == '':
                converted_code.append('')
                
        # Close brackets for language-specific syntax
        if target_language == 'cpp':
            converted_code.append('    return 0;\n}')
        elif target_language == 'java':
            converted_code.append('    }\n}')  # Close main method and class
        elif target_language == 'javascript':
            # No need to add closing brackets for JavaScript
            pass
            
        return '\n'.join(converted_code)

# Example usage
def main():
    converter = CodeConverter()
    
    print("Welcome to Python Code Converter!")
    print("--------------------------------")
    
    # Get Python code input from user
    print("\nEnter your Python code:")
    print("Type 'END' on a new line when you're done")
    python_code = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        python_code.append(line)
    
    python_code = "\n".join(python_code)
    
    # Show available languages
    print("\nAvailable languages for conversion:")
    print("1. JavaScript")
    print("2. Java")
    print("3. C++")
    print("4. All languages")
    
    # Get target language choice
    while True:
        try:
            choice = int(input("\nEnter your choice (1-4): "))
            if 1 <= choice <= 4:
                break
            print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    # Convert and display results
    if choice == 1:
        languages = ['javascript']
    elif choice == 2:
        languages = ['java']
    elif choice == 3:
        languages = ['cpp']
    else:
        languages = ['javascript', 'java', 'cpp']
    
    for lang in languages:
        print(f"\nConverted to {lang.upper()}:")
        print("------------------------")
        try:
            converted = converter.convert_to_language(python_code, lang)
            print(converted)
        except Exception as e:
            print(f"Error converting to {lang}: {str(e)}")
        print("------------------------")
    
    print("\nConversion complete!")

if __name__ == "__main__":
    while True:
        main()
        if input("\nWant to convert another code? (y/n): ").lower() != 'y':
            break
    
    print("Thank you for using Python Code Converter!")
