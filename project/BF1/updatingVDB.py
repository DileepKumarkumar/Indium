import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

def upload_to_faiss_with_update(json_file_path, index_file="faiss_index.index", metadata_file="metadata.json"):
    # Load extracted data from the JSON file
    with open(json_file_path, 'r') as file:
        extracted_data = json.load(file)

    # Initialize metadata storage
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as file:
            metadata_store = json.load(file)
    else:
        metadata_store = {}

    # Load or create FAISS index
    if os.path.exists(index_file):
        index = faiss.read_index(index_file)
    else:
        dimension = model.get_sentence_embedding_dimension()  # Get the number of dimensions
        index = faiss.IndexFlatL2(dimension)

    # Prepare data for FAISS and update process
    documents = []
    new_embeddings = []
    updated_metadata = []

    for entry in extracted_data:
        # Unique identifier for deduplication (e.g., class + function name)
        unique_id = f"{entry['class_name']}::{entry['function_name']}"
        
        # Check if the entry already exists
        if unique_id in metadata_store:
            # Update existing metadata
            metadata_store[unique_id].update({
                "code": entry.get("code", metadata_store[unique_id].get("code")),
                "description": entry.get("description", metadata_store[unique_id].get("description")),
                "input": entry.get("input", metadata_store[unique_id].get("input")),
                "output": entry.get("output", metadata_store[unique_id].get("output")),
            })
        else:
            # Add new entry
            documents.append(f"{entry['class_name']} {entry['function_name']} {entry['description']}")
            metadata_store[unique_id] = {
                "class_name": entry["class_name"],
                "function_name": entry["function_name"],
                "code": entry.get("code"),
                "description": entry.get("description"),
                "input": entry.get("input"),
                "output": entry.get("output"),
            }
            updated_metadata.append(unique_id)

    # Generate embeddings for new documents
    if documents:
        new_embeddings = model.encode(documents)

        # Add embeddings to the FAISS index
        index.add(np.array(new_embeddings, dtype=np.float32))

    # Save updated FAISS index and metadata
    faiss.write_index(index, index_file)
    with open(metadata_file, 'w') as file:
        json.dump(metadata_store, file, indent=4)

    print(f"FAISS index updated. Total entries: {index.ntotal}")
    print(f"Metadata updated with {len(updated_metadata)} new entries.")
    print(f"Updated metadata saved to '{metadata_file}'.")

# Run upload function
json_file_path = "parsed_data.json"  # Path to your extracted JSON file
upload_to_faiss_with_update(json_file_path)
