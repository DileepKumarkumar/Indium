import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

def retrieve_from_faiss(query, faiss_index_path="faiss_index.index", metadata_path="parsed_data.json", k=5):
    # Load FAISS index
    faiss_index = faiss.read_index(faiss_index_path)
    print("FAISS index loaded.")

    # Load metadata
    with open(metadata_path, 'r') as file:
        metadata_store = json.load(file)
    print("Metadata loaded.")

    # Generate query embedding
    query_vector = model.encode([query])
    query_vector = np.array(query_vector, dtype=np.float32)

    # Perform search in FAISS
    distances, indices = faiss_index.search(query_vector, k)
    print(f"Distances: {distances}")
    print(f"Indices: {indices}")

    # Retrieve results
    results = []
    for idx in indices[0]:
        if idx < 0 or idx >= len(metadata_store):
            print(f"Index {idx} is out of range, skipping.")
            continue
        
        # Retrieve corresponding metadata
        entry = metadata_store[idx]
        results.append(entry)

    return results

# Run retrieval function
query = "selecttabs"
retrieved_data = retrieve_from_faiss(query)

# Display results
print("\nRetrieved Results:")
for idx, result in enumerate(retrieved_data, 1):
    print(f"\nResult {idx}:")
    print(f"Class Name: {result['class_name']}")
    print(f"Function Name: {result['function_name']}")
    print(f"Code: {result['code']}")
    print(f"Description: {result['description']}")
    print(f"Input: {result['input']}")
    print(f"Output: {result['output']}")
