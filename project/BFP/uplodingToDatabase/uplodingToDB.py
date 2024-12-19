import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

def preprocess_data(json_file_path):
    """
    Load and preprocess data from JSON for FAISS indexing.
    Includes input and output fields in the combined text for embeddings.
    """
    with open(json_file_path, 'r') as file:
        extracted_data = json.load(file)

    documents = []
    metadata = []

    for entry in extracted_data:
        # Extract fields from the JSON file
        class_name = entry.get("class_name", "UnknownClass")
        function_name = entry.get("function_name", "UnknownFunction")
        description = entry.get("description", "No description available.")
        code = entry.get("code", "No code provided.")
        input_field = entry.get("input", "No input specified.")
        output_field = entry.get("output", "No output specified.")

        # Combine fields into a single string for embeddings
        combined_text = (
            f"Class Name: {class_name} "
            f"Function Name: {function_name} "
            f"Description: {description} "
            f"Code: {code} "
            f"Input: {input_field} "
            f"Output: {output_field}"
        )

        # Add combined text to documents and store metadata
        documents.append(combined_text)
        metadata.append({
            "class_name": class_name,
            "function_name": function_name,
            "description": description,
            "code": code,
            "input": input_field,
            "output": output_field
        })

    return documents, metadata

def generate_embeddings(documents):
    """
    Generate normalized embeddings using a sentence transformer model.
    """
    embeddings = model.encode(documents)
    faiss.normalize_L2(embeddings)  # Normalize embeddings for cosine similarity
    return np.array(embeddings, dtype=np.float32)

def create_hnsw_index(embeddings, metadata, index_path="faiss_hnsw_index.index", metadata_path="metadata.json"):
    """
    Create and save a FAISS HNSW index with the given embeddings and metadata.
    """
    # Initialize FAISS HNSW index
    dimension = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dimension, 32)  # Use HNSW with M=32
    index.hnsw.efConstruction = 200  # Construction parameter for HNSW
    index.add(embeddings)  # Add embeddings to the index

    # Save the index to disk
    faiss.write_index(index, index_path)
    print(f"FAISS HNSW index saved to '{index_path}'.")

    # Save metadata for retrieval purposes
    with open(metadata_path, "w") as meta_file:
        json.dump(metadata, meta_file)
    print(f"Metadata saved to '{metadata_path}'.")

def upload_data_to_faiss(json_file_path, index_path="faiss_hnsw_index.index", metadata_path="metadata.json"):
    """
    Full process to preprocess, embed, and upload data to FAISS HNSW.
    """
    print("Preprocessing data...")
    documents, metadata = preprocess_data(json_file_path)

    print("Generating embeddings...")
    embeddings = generate_embeddings(documents)

    print("Creating FAISS HNSW index...")
    create_hnsw_index(embeddings, metadata, index_path, metadata_path)

    print("Data successfully uploaded to FAISS HNSW.")

# Run the upload process
if __name__ == "__main__":
    json_file_path = "parsed_data.json"  # Path to the JSON file with extracted data
    upload_data_to_faiss(json_file_path)
