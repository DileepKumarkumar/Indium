import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

def retrieve_from_faiss(query, index_file="faiss_index.index", metadata_file="metadata.json", top_k=5):
    """
    Retrieve the most relevant entries from the FAISS index based on the query.

    Args:
        query (str): The search query.
        index_file (str): Path to the FAISS index file.
        metadata_file (str): Path to the metadata file.
        top_k (int): Number of top results to retrieve.

    Returns:
        List[dict]: A list of metadata dictionaries for the top-k results.
    """
    # Load FAISS index
    if not os.path.exists(index_file):
        raise FileNotFoundError(f"FAISS index file '{index_file}' not found.")
    index = faiss.read_index(index_file)

    # Load metadata
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Metadata file '{metadata_file}' not found.")
    with open(metadata_file, 'r') as file:
        metadata_store = json.load(file)

    # Generate embedding for the query
    query_embedding = model.encode([query])

    # Perform search on the FAISS index
    distances, indices = index.search(np.array(query_embedding, dtype=np.float32), top_k)

    # Retrieve metadata for the top-k results
    results = []
    for i, idx in enumerate(indices[0]):
        if idx == -1:  # FAISS may return -1 for empty results
            continue
        # Retrieve the unique key and corresponding metadata
        unique_id = list(metadata_store.keys())[idx]
        result_metadata = metadata_store[unique_id]
        results.append({
            "rank": i + 1,
            "distance": distances[0][i],
            "metadata": result_metadata
        })

    return results

# Example usage
query = "login user function"
top_k_results = retrieve_from_faiss(query)

# Display the results
if top_k_results:
    print("Top-k results:")
    for result in top_k_results:
        print(f"Rank {result['rank']} (Distance: {result['distance']}):")
        print(result["metadata"])
else:
    print("No relevant results found.")
