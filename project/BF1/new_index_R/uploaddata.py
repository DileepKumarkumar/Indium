import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

def upload_to_faiss(json_file_path):
    # Load extracted data from the JSON file
    with open(json_file_path, 'r') as file:
        extracted_data = json.load(file)

    # Prepare data for FAISS
    documents = []
    method_details = []  # To store detailed info for each method

    for entry in extracted_data:
        # Collect the text you want to embed
        documents.append(f"{entry['class_name']} {entry['function_name']} {entry['description']} {entry['code']} {entry['input']} {entry['output']}")
        
        # Add method details including all fields
        method_details.append({
            "class_name": entry["class_name"],
            "function_name": entry["function_name"],
            "code": entry["code"],
            "description": entry["description"],
            "input": entry["input"],
            "output": entry["output"]
        })

    # Generate embeddings
    embeddings = model.encode(documents)

    # Create a FAISS index
    dimension = embeddings.shape[1]  # Get the number of dimensions from embeddings
    index = faiss.IndexFlatL2(dimension)  # Use L2 distance
    index.add(np.array(embeddings, dtype=np.float32))  # Add embeddings to the index

    # Optionally save the index to disk
    faiss.write_index(index, "faiss_index_new.index")
    print("FAISS index created and saved as 'faiss_index_new.index'.")

    # Print confirmation for each method uploaded
    for method in method_details:
        print(f"Function '{method['function_name']}' from class '{method['class_name']}' added to the FAISS vector database.")

# Run upload function
json_file_path = "parsed_data.json"  # Path to your extracted JSON file
upload_to_faiss(json_file_path)


