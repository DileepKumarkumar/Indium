import streamlit as st
import javalang
import json
import pandas as pd
import os
import re

# Function to remove comments from Java code
def remove_comments(java_code):
    java_code = re.sub(r'//.*', '', java_code)  # Remove single-line comments
    java_code = re.sub(r'/\*.*?\*/', '', java_code, flags=re.DOTALL)  # Remove multi-line comments
    return java_code

def preprocess_code(java_code):
    """
    Preprocess Java code to handle unterminated strings or multiline issues.
    """
    lines = java_code.splitlines()
    cleaned_lines = []
    open_quote = None

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            cleaned_lines.append(line)
            continue

        # Detect starting quotes
        if open_quote is None:
            if '"' in stripped_line or "'" in stripped_line:
                if stripped_line.count('"') % 2 == 1:
                    open_quote = '"'
                elif stripped_line.count("'") % 2 == 1:
                    open_quote = "'"
        else:
            # Check if this line ends the quote
            if open_quote in stripped_line and stripped_line.count(open_quote) % 2 == 1:
                open_quote = None

        # Combine lines into a single string if inside a quote
        if open_quote:
            line = line.replace('\n', '')  # Avoid breaking multiline strings
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

# Function to parse a single Java file
def parse_java_file(file_content):
    try:
        # Preprocess the code
        preprocessed_code = preprocess_code(file_content.decode('utf-8'))

        # Remove comments
        cleaned_code = remove_comments(preprocessed_code)

        # Parse the cleaned Java code
        tree = javalang.parse.parse(cleaned_code)
        data = []

        for _, class_declaration in tree.filter(javalang.tree.ClassDeclaration):
            class_name = class_declaration.name

            for i, method in enumerate(class_declaration.methods):
                function_name = method.name
                return_type = method.return_type.name if method.return_type else "void"
                parameters = [f"{param.type.name} {param.name}" for param in method.parameters]
                start_line = method.position.line - 1

                if i < len(class_declaration.methods) - 1:
                    end_line = class_declaration.methods[i + 1].position.line - 1
                else:
                    end_line = len(cleaned_code.splitlines())

                method_code = "\n".join(cleaned_code.splitlines()[start_line:end_line]).strip()

                # Mocking description for simplicity
                description = f"Description for {function_name} in {class_name}"

                method_data = {
                    "Class Name": class_name,
                    "Method Name": function_name,
                    "Code": method_code,
                    "Description": description,
                    "Input": parameters,
                    "Output": return_type
                }
                data.append(method_data)

        return data

    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        return []


# Function to save parsed data to Excel and JSON
def save_to_files(data, excel_file, json_file):
    try:
        df = pd.DataFrame(data)
        df.to_excel(excel_file, index=False)
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving files: {str(e)}")

# Streamlit UI
st.title("Java File Parser")
st.write("Upload Java files or provide paths to extract method details.")

# File path input
file_paths = st.text_area(
    "Enter Java file paths (one per line):",
    placeholder="e.g., /path/to/file1.java\n/path/to/file2.java"
)
uploaded_files = st.file_uploader("Or upload Java files:", type=["java"], accept_multiple_files=True)

excel_file_name = st.text_input("Enter name for Excel file:", value="parsed_data.xlsx")
json_file_name = st.text_input("Enter name for JSON file:", value="parsed_data.json")

if st.button("Start Parsing"):
    all_data = []

    # Process file paths
    if file_paths.strip():
        for file_path in file_paths.strip().splitlines():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read().encode('utf-8')
                all_data.extend(parse_java_file(file_content))
                st.success(f"Parsed file: {file_path}")
            except Exception as e:
                st.error(f"Failed to process file {file_path}: {e}")

    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                file_content = uploaded_file.read()
                all_data.extend(parse_java_file(file_content))
                st.success(f"Parsed uploaded file: {uploaded_file.name}")
            except Exception as e:
                st.error(f"Failed to process uploaded file {uploaded_file.name}: {e}")

    # Save results
    if all_data:
        save_to_files(all_data, excel_file_name, json_file_name)
        st.success(f"Output saved to `{excel_file_name}` and `{json_file_name}`.")
    else:
        st.warning("No valid data extracted.")
