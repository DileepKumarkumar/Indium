import json
import openpyxl
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage

# Configuration
file_path = "C:\\Users\\I1817\\Downloads\\book21.xlsx"  # Update this path
embedding_dimension = 384  # Dimensions of the sentence embeddings
model_name = "llama3"  # Use your local model name

# Load the Excel file for framework information
try:
    workbook = openpyxl.load_workbook(file_path)
except Exception as e:
    print(f"Error loading the Excel file: {e}")
    exit()

# Initialize the ChatOllama model
local_llm = ChatOllama(
    model=model_name,
    base_url="http://localhost:11434",
    temperature=0.5,  # Adjust temperature as needed
)

# Prepare a test scenario and related framework information
test_scenario = "Test if the API can handle encrypted responses properly using AES-256 encryption."
method_name = "BFL_AES256API"
method_description = "Encrypt data using AES-256"
method_implementation = "encryption_method_here()"

# Construct the prompt for the LLM
prompt = f"""
Given the following test scenario:
{test_scenario}

And the following related framework information:
Method: {method_name}, Description: {method_description}, Implementation: {method_implementation}

Please generate a comprehensive test case code that fits into the current framework.
"""

# Generate test code using the LLM
try:
    # Send the prompt to the model and get the response
    response = local_llm([HumanMessage(content=prompt)])

    # Extract generated code from the response
    generated_code = response.content  # Adjust according to the response structure

    # Output the generated code
    print("Generated Test Case Code:")
    print(generated_code)

except Exception as e:
    print(f"Error generating test code: {e}")
