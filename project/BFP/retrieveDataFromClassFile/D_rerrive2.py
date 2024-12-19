import streamlit as st
import re
import javalang
import json
import os
import pandas as pd

# Function to remove comments from Java code
def remove_comments(java_code):
    """
    Removes all comments from the given Java code.
    Handles single-line, multi-line, and documentation comments.
    """
    # Remove single-line comments
    java_code = re.sub(r'//.*', '', java_code)
    # Remove multi-line and documentation comments (/* ... */ and /** ... */)
    java_code = re.sub(r'/\*.*?\*/', '', java_code, flags=re.DOTALL)
    return java_code

# Function to extract methods from the cleaned Java code
def extract_functions(java_code):
    """
    Extracts functions from Java code, removes comments, and returns method details.
    """
    cleaned_code = remove_comments(java_code)
    tree = javalang.parse.parse(cleaned_code)

    methods_data = []

    for path, class_decl in tree.filter(javalang.tree.ClassDeclaration):
        class_name = class_decl.name

        for i, method in enumerate(class_decl.methods):
            function_name = method.name
            return_type = method.return_type.name if method.return_type else "void"
            parameters = [f"{param.type.name} {param.name}" for param in method.parameters]

            # Start line of the method
            start_line = method.position.line - 1

            # End line calculation
            if i < len(class_decl.methods) - 1:
                end_line = class_decl.methods[i + 1].position.line - 1
            else:
                end_line = len(cleaned_code.splitlines())

            method_code = "\n".join(cleaned_code.splitlines()[start_line:end_line]).strip()

            methods_data.append({
                "Class Name": class_name,
                "Method Name": function_name,
                "Code": method_code,
                "Input": parameters,
                "Output": return_type
            })

    return methods_data

# Check if the method is already present in JSON based on class and method name
def check_existing_data(data, output_file='parsed_data.json'):
    try:
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, 'r') as file:
                existing_data = json.load(file)
        else:
            existing_data = []
    except json.JSONDecodeError:
        existing_data = []

    # Check if method already exists
    for existing_method in existing_data:
        if existing_method['Class Name'] == data['Class Name'] and existing_method['Method Name'] == data['Method Name']:
            return True

    return False

# Save method data incrementally to JSON, ensuring no duplicates
def save_to_json_incremental(data, output_file='parsed_data.json'):
    if not check_existing_data(data, output_file):
        try:
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                with open(output_file, 'r') as file:
                    existing_data = json.load(file)
            else:
                existing_data = []
        except json.JSONDecodeError:
            existing_data = []

        existing_data.append(data)

        with open(output_file, 'w') as file:
            json.dump(existing_data, file, indent=4)
        st.write(f"Data saved to {output_file}")
    else:
        st.write(f"Data for {data['Method Name']} already exists in {output_file}")

# Check if the method is already present in Excel based on class and method name
def check_existing_excel(data, output_file='parsed_data.xlsx'):
    if os.path.exists(output_file):
        df = pd.read_excel(output_file)
        existing_methods = df[(df['Class Name'] == data['Class Name']) & (df['Method Name'] == data['Method Name'])]
        if not existing_methods.empty:
            return True
    return False

# Save method data incrementally to Excel, ensuring no duplicates
def save_to_excel_incremental(data, output_file='parsed_data.xlsx'):
    if not check_existing_excel(data, output_file):
        df_new = pd.DataFrame([data])
        try:
            df_existing = pd.read_excel(output_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_new
        df_combined.to_excel(output_file, index=False)
        st.write(f"Data saved to {output_file}")
    else:
        st.write(f"Data for {data['Method Name']} already exists in {output_file}")

# Process uploaded or provided Java file (either uploaded or from file path)
def process_java_file(file_input):
    java_code = ""

    # If the input is a file path, read the file
    if isinstance(file_input, str) and os.path.exists(file_input):
        with open(file_input, "r", encoding="utf-8") as file:
            java_code = file.read()
    # If the input is a file-like object, read the file content
    elif isinstance(file_input, bytes):
        java_code = file_input.decode("utf-8")
    
    if java_code:
        extracted_methods = extract_functions(java_code)

        # Save to JSON
        for method in extracted_methods:
            save_to_json_incremental(method, "parsed_data.json")

        # Save to Excel
        for method in extracted_methods:
            save_to_excel_incremental(method, "parsed_data.xlsx")

        # Print the extracted methods
        for method in extracted_methods:
            st.json(method)

# Streamlit UI
st.title("Java Method Extractor and Saver")

st.write("""
This app allows you to:
1. Upload a Java file or provide a file path to extract methods.
2. The app processes the file, removes comments, and saves method details to both a JSON and Excel file.
3. Duplicate methods (based on class and method name) are not added to the output files.
""")

# Input multiple file paths
input_method = st.radio("Choose Input Method", ('Upload Java File', 'Enter Java File Paths'))

if input_method == 'Upload Java File':
    uploaded_file = st.file_uploader("Upload your Java file", type=["java"])

    if uploaded_file is not None:
        st.write("Processing the uploaded Java file...")
        process_java_file(uploaded_file.getvalue())
        st.success("Java file processed successfully and methods saved to JSON and Excel files.")
else:
    file_paths_input = st.text_area("Enter the paths to your Java files (separate paths with commas or newlines):")
    if file_paths_input:
        file_paths = [path.strip() for path in file_paths_input.split(",")]

        for file_path in file_paths:
            if os.path.exists(file_path):
                st.write(f"Processing the Java file: {file_path}...")
                process_java_file(file_path)
                st.success(f"Java file processed successfully and methods saved to JSON and Excel files: {file_path}")
            else:
                st.error(f"The file at path {file_path} does not exist.")
