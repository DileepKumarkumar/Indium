import json
import tiktoken  # Ensure the tiktoken library is installed

def calculate_tokens(text, model="gpt-4"):
    """
    Accurately count tokens using tiktoken
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Error in token calculation: {e}")
        # Fallback to a rough estimation
        return len(text.split()) * 4  # Rough approximation

# Path to your JSON file
file_path = "BFL_parsed_data.json"

# Load the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Function to recursively calculate tokens for all text fields in the JSON
def calculate_tokens_in_json(data, model="gpt-4"):
    total_tokens = 0

    if isinstance(data, dict):
        for key, value in data.items():
            total_tokens += calculate_tokens_in_json(value, model)
    elif isinstance(data, list):
        for item in data:
            total_tokens += calculate_tokens_in_json(item, model)
    elif isinstance(data, str):
        total_tokens += calculate_tokens(data, model)
    
    return total_tokens

# Calculate tokens
total_tokens = calculate_tokens_in_json(json_data, model="gpt-4")
print(f"Total tokens used for the JSON file: {total_tokens}")
