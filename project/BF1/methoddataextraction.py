import javalang
import json
import pandas as pd
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage
import os

# Initialize the LLM model
llm = local_llm = ChatOllama(
        model="llama3",
        base_url="http://localhost:11434",
        temperature=0.5
)

def parse_java_file(file_path):
    with open(file_path, 'r') as file:
        java_code = file.read()
    
    # Parse the Java code
    tree = javalang.parse.parse(java_code)
    
    # Iterate through the classes in the file
    for path, class_declaration in tree.filter(javalang.tree.ClassDeclaration):
        class_name = class_declaration.name
        
        # Extract methods from the class
        for i, method in enumerate(class_declaration.methods):
            function_name = method.name
            return_type = method.return_type.name if method.return_type else "void"
            parameters = [f"{param.type.name} {param.name}" for param in method.parameters]
            
            # Determine start line and end line for method
            start_line = method.position.line - 1
            
            # Identify end line based on the next method start or end of file
            if i < len(class_declaration.methods) - 1:
                end_line = class_declaration.methods[i + 1].position.line - 1
            else:
                end_line = len(java_code.splitlines())
            
            # Extract code for the specific method
            method_code = "\n".join(java_code.splitlines()[start_line:end_line]).strip()

            # Generate method description using LLM
            description_prompt = f"Provide a brief description for the Java method:\n{method_code}"
            description = llm([HumanMessage(content=description_prompt)]).content
            
            # Store the method details
            method_data = {
                "class_name": class_name,
                "function_name": function_name,
                "code": method_code,
                "description": description,
                "input": parameters,
                "output": return_type
            }
            
            # Save to Excel incrementally
            save_to_excel_incremental(method_data, "parsed_data.xlsx")
            
            # Save to JSON incrementally
            save_to_json_incremental(method_data, "parsed_data.json")
            
            print(json.dumps(method_data, indent=4))

def save_to_excel_incremental(data, output_file='parsed_data.xlsx'):
    # Append data to an existing or new Excel file
    try:
        df_existing = pd.read_excel(output_file)
        df_new = pd.DataFrame([data])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    except FileNotFoundError:
        df_combined = pd.DataFrame([data])
    df_combined.to_excel(output_file, index=False)
    print(f"Data for {data['function_name']} saved to {output_file}")

def save_to_json_incremental(data, output_file='parsed_data.json'):
    # Append data to an existing or new JSON file
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
    print(f"Data for {data['function_name']} saved to {output_file}")

# Example usage with multiple file paths
file_paths = [
  'C:/Users/I1817/Downloads/SFDC_TwoWheeler_Tasks/SFDC_TwoWheeler_Tasks/src/baseClass/BaseClass.java'
]

for file_path in file_paths:
    parsed_data = parse_java_file(file_path)
