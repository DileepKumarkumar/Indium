import streamlit as st
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
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

def query_individual_function(query_text, extracted_data, k=5):
    """
    Query the FAISS index for the given query text and retrieve relevant functions.
    """
    query_embedding = model.encode([query_text])
    D, I = index.search(np.array(query_embedding, dtype=np.float32), k)

    results = []
    seen_function_signatures = set()

    for i in range(k):
        idx = I[0][i]
        if idx == -1:  # No result found for this query
            continue

        # Extract relevant details
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
                "output": output
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
        )
    return "\n".join(structured_output)

# Streamlit app
def main():
    st.title("Enhanced Scenario Query Functionality Search")
    st.write(
        "This app processes test scenarios, retrieves relevant functions, and allows you to dynamically select the functions most appropriate for your steps."
    )

    # Load extracted data
    extracted_data = load_descriptions()
    st.success("Preloaded function database loaded successfully.")

    # Initialize session state for all relevant functions
    if "all_relevant_functions" not in st.session_state:
        st.session_state.all_relevant_functions = []

    # Text area for scenario query input
    scenario_query = st.text_area(
        "Enter the scenario query:",
        placeholder="Enter your scenario query here, with steps like 'Step 1: Do X', 'Step 2: Do Y', etc."
    )

    # Initialize session state for step processing
    if "steps_processed" not in st.session_state:
        st.session_state.steps_processed = set()

    if scenario_query:
        # Split scenario into steps
        steps = scenario_query.strip().split("\n")

        # Process each step
        for i, step in enumerate(steps):
            step_id = f"step_{i}"
            cleaned_step = clean_step(step)

            st.write(f"{cleaned_step}")
            # Display cleaned query
            st.write(f"**Query for Step {i + 1}:** {cleaned_step}")

            # Skip steps already processed
            if step_id in st.session_state.steps_processed:
                continue

            # Query FAISS for relevant functions
            relevant_functions = query_individual_function(cleaned_step, extracted_data)

            # Check for exact match
            exact_match = next(
                (func for func in relevant_functions if func['function_name'].lower() in cleaned_step.lower()), None
            )

            if exact_match:
                st.success(f"Exact match found for Step {i + 1}: {exact_match['function_name']}")
                st.session_state.all_relevant_functions.append(exact_match)
                st.session_state.steps_processed.add(step_id)
            else:
                st.warning(f"No exact match found for Step {i + 1}. Please select the most relevant function.")
                st.write(format_functions(relevant_functions))

                # Add function selection option
                selected_function = st.selectbox(
                    f"Select the most relevant function for Step {i + 1}:",
                    options=[None] + relevant_functions,
                    format_func=lambda func: func["function_name"] if func else "Select a function"
                )

                if selected_function:
                    st.session_state.all_relevant_functions.append(selected_function)
                    st.session_state.steps_processed.add(step_id)

        # Display all relevant functions
        if st.session_state.all_relevant_functions:
            st.write("### Aggregated Relevant Functions:")
            st.text_area(
                "All Relevant Functions",
                value=format_functions(st.session_state.all_relevant_functions),
                height=300
            )

        # Button to build model prompt
        if st.button("Generate Model Prompt"):
            prompt = "\n".join([
                f"{i + 1}. Class: {func['class_name']}, Function: {func['function_name']}, Input: {func['input']}, Output: {func['output']}"
                for i, func in enumerate(st.session_state.all_relevant_functions)
            ])
            st.text_area("Model Prompt", value=prompt, height=300)

    st.write("---")
    st.info(
        "Ensure that the FAISS index file (`faiss_index.index`) is available locally and "
        "that the embedding model `sentence-transformers/all-MiniLM-L6-v2` is properly installed."
    )


if __name__ == "__main__":
    main()
