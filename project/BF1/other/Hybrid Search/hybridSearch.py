import streamlit as st
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

# Load the FAISS index
index = faiss.read_index("faiss_index_new.index")

# Preloaded JSON data (replace with your actual JSON data or file path)
JSON_DATA_PATH = "parsed_data.json"

def load_descriptions():
    """Load extracted data from a predefined JSON file."""
    with open(JSON_DATA_PATH, 'r') as file:
        extracted_data = json.load(file)
    return extracted_data

def clean_step(step_description):
    """Cleans the step description by removing special characters, step prefixes, etc."""
    cleaned_step = re.sub(r"step\s*\d+:?", "", step_description, flags=re.IGNORECASE).strip()
    cleaned_step = re.sub(r"\s+", "", cleaned_step).strip()
    cleaned_step = cleaned_step.lstrip(":")
    return cleaned_step

def build_sparse_index(extracted_data):
    """Build a sparse index (TF-IDF) from the function descriptions."""
    corpus = [item["description"] for item in extracted_data]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return vectorizer, tfidf_matrix

def sparse_search(query_text, vectorizer, tfidf_matrix, k=5):
    """Perform sparse retrieval using TF-IDF."""
    query_vector = vectorizer.transform([query_text])
    cosine_similarities = (tfidf_matrix @ query_vector.T).toarray().ravel()
    top_indices = np.argsort(cosine_similarities)[::-1][:k]
    return top_indices, cosine_similarities[top_indices]

def hybrid_search(query_text, extracted_data, k=5, alpha=0.5):
    """
    Perform hybrid search by combining dense and sparse retrieval.
    Alpha balances the contribution of dense (FAISS) and sparse (TF-IDF) scores.
    """
    # Dense search using FAISS
    query_embedding = model.encode([query_text])
    D_dense, I_dense = index.search(np.array(query_embedding, dtype=np.float32), k)
    
    # Sparse search using TF-IDF
    vectorizer, tfidf_matrix = build_sparse_index(extracted_data)
    I_sparse, D_sparse = sparse_search(query_text, vectorizer, tfidf_matrix, k)

    # Combine results
    scores = {}
    for i, idx in enumerate(I_dense[0]):
        if idx == -1:
            continue
        scores[idx] = scores.get(idx, 0) + (1 - alpha) * (1 / (D_dense[0][i] + 1e-6))

    for i, idx in enumerate(I_sparse):
        scores[idx] = scores.get(idx, 0) + alpha * (D_sparse[i])

    # Sort by combined scores
    combined_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

    # Deduplicate and retrieve details
    results = []
    seen_function_signatures = set()
    for idx, score in combined_results:
        class_name = extracted_data[idx].get("class_name")
        func_name = extracted_data[idx].get("function_name")
        input_params = extracted_data[idx].get("input", [])
        output = extracted_data[idx].get("output")

        # Create a unique signature to avoid duplicate entries
        function_signature = (class_name, func_name)
        if function_signature not in seen_function_signatures:
            seen_function_signatures.add(function_signature)
            results.append({
                "class_name": class_name,
                "function_name": func_name,
                "input": input_params,
                "output": output,
                "score": score
            })
    
    return results

def format_functions(functions):
    """Format the functions in a structured output for readability."""
    structured_output = []
    for i, func in enumerate(functions, start=1):
        structured_output.append(
            f"{i}. \n"
            f"Class Name: {func['class_name']}\n"
            f"Function Name: {func['function_name']}\n"
            f"Input: {func['input']}\n"
            f"Output: {func['output']}\n"
            f"Score: {func['score']:.4f}\n"
        )
    return "\n".join(structured_output)

# Streamlit UI
st.title("Hybrid Retrieval System")

user_query = st.text_area("Enter your query:")

if st.button("Retrieve Functions"):
    st.info("Loading data and performing retrieval...")
    extracted_data = load_descriptions()
    results = hybrid_search(user_query, extracted_data, k=5, alpha=0.5)
    st.text("Relevant Functions:\n" + format_functions(results))
