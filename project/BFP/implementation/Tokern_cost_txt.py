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

# Path to your text file
file_path = "output.txt"

# Read the text file
with open(file_path, 'r', encoding='utf-8') as file:
    text_content = file.read()

# Calculate tokens for the entire text
total_tokens = calculate_tokens(text_content, model="gpt-4")
print(f"Total tokens used for the text file: {total_tokens}")
