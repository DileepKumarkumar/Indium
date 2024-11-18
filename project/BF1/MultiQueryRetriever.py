import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

# Load the FAISS index
index = faiss.read_index("faiss_index.index")
print("FAISS index loaded successfully.")

def load_descriptions(json_file_path):
    with open(json_file_path, 'r') as file:
        extracted_data = json.load(file)
    return extracted_data

def generate_multi_queries(query):
    # Generate simplified query variations
    return [model.encode(var) for var in [query, 
                                          f"function: {stepselecttabsusingtheoptimalcustomerdata}", 
                                          f"{query} implementation",
                                          {query} ]]

def multi_query_faiss_retrieval(query, extracted_data, k=20):
    query_embeddings = generate_multi_queries(query)
    all_results = {}
    
    for query_embedding in query_embeddings:
        D, I = index.search(np.array([query_embedding], dtype=np.float32), k)
        for i in range(len(I[0])):
            idx = I[0][i]
            function_name = extracted_data[idx]["function_name"]
            distance = D[0][i]

            # Key for uniqueness
            result_key = (function_name, extracted_data[idx]["class_name"])

            # Update if closer distance
            if result_key not in all_results or all_results[result_key]['distance'] > distance:
                all_results[result_key] = {
                    "function_number": idx,
                    "class_name": extracted_data[idx]["class_name"],
                    "function_name": function_name,
                    "distance": distance
                }
    
    # Sort results and return
    sorted_results = sorted(all_results.values(), key=lambda x: x['distance'])
    print("Results retrieved:", sorted_results)
    return sorted_results[:k]

def main():
    json_file_path = "parsed_data.json"
    extracted_data = load_descriptions(json_file_path)

    scenario_query = "stepselecttabsusingtheoptimalcustomerdata"
    results = multi_query_faiss_retrieval(scenario_query, extracted_data)

    print(f"Query: {scenario_query}")
    print("Relevant functions found:")
    for result in results:
        print(f"Class: {result['class_name']}, Function: {result['function_name']}, Distance: {result['distance']}")

if __name__ == "__main__":
    main()
