import streamlit as st
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

# Load the FAISS index
index = faiss.read_index("faiss_index_new.index")
st.write("FAISS index loaded successfully.")

# Load function descriptions from JSON
def load_descriptions(json_file_path):
    with open(json_file_path, 'r') as file:
        extracted_data = json.load(file)
    return extracted_data

# Generate multiple query embeddings
def generate_multi_queries(query):
    return [model.encode(var) for var in [query, 
                                          f"function: {query}", 
                                          f"{query} implementation"]]

# Retrieve relevant functions using FAISS
def multi_query_faiss_retrieval(query, extracted_data, k=20):
    query_embeddings = generate_multi_queries(query)
    all_results = {}
    
    for query_embedding in query_embeddings:
        D, I = index.search(np.array([query_embedding], dtype=np.float32), k)
        for i in range(len(I[0])):
            idx = I[0][i]
            function_name = extracted_data[idx]["function_name"]
            distance = D[0][i]

            result_key = (function_name, extracted_data[idx]["class_name"])

            if result_key not in all_results or all_results[result_key]['distance'] > distance:
                all_results[result_key] = {
                    "function_number": idx,
                    "class_name": extracted_data[idx]["class_name"],
                    "function_name": function_name,
                    "distance": distance
                }
    
    sorted_results = sorted(all_results.values(), key=lambda x: x['distance'])
    return sorted_results[:k]

# Streamlit UI
def main():
    st.title("FAISS Function Retrieval Interface")
    st.write("Enter a query to find relevant functions based on descriptions.")

    # Load extracted data from JSON
    json_file_path = "parsed_data.json"
    extracted_data = load_descriptions(json_file_path)

    # User input for the query
    scenario_query = st.text_input("Enter your query here", "")
    top_k = st.slider("Number of results to retrieve", min_value=1, max_value=20, value=20)

    if st.button("Retrieve Functions"):
        if scenario_query:
            # Retrieve results
            results = multi_query_faiss_retrieval(scenario_query, extracted_data, k=top_k)
            st.write(f"Query: {scenario_query}")
            st.write("Relevant functions found:")

            # Display each result in the UI
            for result in results:
                st.write(f"Class: {result['class_name']}")
                st.write(f"Function: {result['function_name']}")
                st.write(f"Distance: {result['distance']:.4f}")
                st.write("---")
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    main()
