import streamlit as st
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

# Load the FAISS index
index = faiss.read_index("faiss_index_new.index")

# Load function descriptions from JSON
def load_descriptions(json_file_path):
    with open(json_file_path, 'r') as file:
        extracted_data = json.load(file)
    return extracted_data

# Query the FAISS index
def query_faiss_index(query, extracted_data, k=5):
    # Generate embedding for the query
    query_embedding = model.encode([query])

    # Search the FAISS index for the nearest neighbors
    D, I = index.search(np.array(query_embedding, dtype=np.float32), k)

    # Check for an exact match and compile results
    exact_match_result = None
    approximate_results = []

    for i in range(k):
        idx = I[0][i]
        function_name = extracted_data[idx]["function_name"]

        # Compile result entry
        result = {
            "function_number": idx,
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


# Streamlit UI
def main():
    st.title("FAISS Function Retrieval Interface")
    st.write("Enter a query to find relevant functions based on descriptions.")

    # Load extracted data from JSON
    json_file_path = "parsed_data.json"
    extracted_data = load_descriptions(json_file_path)

    # User input for the query
    scenario_query = st.text_input("Enter your query here", "")
    top_k = st.slider("Number of results to retrieve", min_value=1, max_value=20, value=5)

    # Retrieve results when button is clicked
    if st.button("Retrieve Functions"):
        if scenario_query:
            # Retrieve results
            results = query_faiss_index(scenario_query, extracted_data, k=top_k)
            st.write(f"Query: {scenario_query}")
            st.write("Relevant functions found:")

            # Display each result in the UI
            for result in results:
                st.write(f"**Class:** {result['class_name']}")
                st.write(f"**Function:** {result['function_name']}")
                st.write(f"**Description:** {result['description']}")
                st.write(f"**Distance:** {result['distance']:.4f}")
                st.write("---")
        else:
            st.warning("Please enter a query.")

if __name__ == "__main__":
    main()
