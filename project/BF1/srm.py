import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

# Load the FAISS index
index = faiss.read_index("faiss_index.index")

def load_descriptions(json_file_path):
    # Load extracted data from the JSON file
    with open(json_file_path, 'r') as file:
        extracted_data = json.load(file)
    return extracted_data

def query_faiss_index(query, extracted_data, k=5):
    # Generate embedding for the query
    query_embedding = model.encode([query])

    # Search the FAISS index for the nearest neighbors
    D, I = index.search(np.array(query_embedding, dtype=np.float32), k)

    # Print raw FAISS output before accessing JSON details
    print("Raw FAISS output:")
    print("Indices:", I)
    print("Distances:", D)
    
    # Check if any of the results exactly match the query
    exact_match_result = None
    approximate_results = []

    for i in range(k):
        idx = I[0][i]
        function_name = extracted_data[idx]["function_name"]

        # Compile result entry
        result = {
            "function_number": [idx],
            "class_name": extracted_data[idx]["class_name"],
            "function_name": function_name,
            "description": extracted_data[idx]["description"],
            "distance": D[0][i]
        }

        # Check if function name exactly matches the query
        if query.lower().replace(" ", "") == function_name.lower().replace(" ", ""):
            exact_match_result = result
            break  # Stop if an exact match is found
        else:
            approximate_results.append(result)  # Collect approximate matches

    # Prioritize exact match if it exists, otherwise return approximate results
    if exact_match_result:
        return [exact_match_result]
    else:
        return approximate_results[:k]  # Fallback to approximate matches if no exact match


def main():
    json_file_path = "parsed_data.json"  # Path to your extracted JSON file
    extracted_data = load_descriptions(json_file_path)

    # Example scenario query
    scenario_query = "selecttabs"  # Adjust this based on your scenario
    results = query_faiss_index(scenario_query, extracted_data)

    # Print the results
    print(f"Query: {scenario_query}")
    print("Relevant functions found:")
    for result in results:
        print(f"Class: {result['class_name']}, Function: {result['function_name']}, Distance: {result['distance']}")

if __name__ == "__main__":
    main()
