import streamlit as st
from langchain.llms import OpenAIChat
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import os
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage

# Load the embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

# File paths
FAISS_INDEX_PATH = "faiss_index_new.index"
JSON_DATA_PATH = "parsed_data.json"

# Helper functions
def load_descriptions():
    """Load extracted data from a predefined JSON file."""
    if not os.path.exists(JSON_DATA_PATH):
        st.error(f"JSON file '{JSON_DATA_PATH}' not found.")
        return []
    with open(JSON_DATA_PATH, 'r') as file:
        extracted_data = json.load(file)
    return extracted_data

def clean_step(step_description):
    """Cleans the step description by removing special characters, step prefixes, etc."""
    cleaned_step = re.sub(r"step\s*\d+:?", "", step_description, flags=re.IGNORECASE).strip()
    # Remove unnecessary spaces and capitalize words for a concise format
    cleaned_step = re.sub(r"\s+", "", cleaned_step).strip()
    # Ensure no leading or trailing colons remain
    cleaned_step = cleaned_step.lstrip(":").strip()
    return cleaned_step

def build_sparse_index(extracted_data):
    """Build a sparse index (TF-IDF) from the function descriptions."""
    corpus = [item.get("description", "") for item in extracted_data]
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
    """Perform hybrid search by combining dense and sparse retrieval."""
    if not os.path.exists(FAISS_INDEX_PATH):
        st.error(f"FAISS index file '{FAISS_INDEX_PATH}' not found.")
        return []

    # Load FAISS index
    index = faiss.read_index(FAISS_INDEX_PATH)
    
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

# Extract steps from the user input
def extract_steps(description):
    steps = []
    lines = description.split("\n")
    for i, line in enumerate(lines):
        if line.strip():
            steps.append({
                "step": f"Step {i+1}",
                "description": line.strip()
            })
    return steps


def process_steps_and_search(description, extracted_data, k=1, alpha=0.5):
    """Process each step from the description and perform a hybrid search for the most relevant function."""
    steps = extract_steps(description)

    step_results = []
    for step in steps:
        step_description = step["description"]
        cleaned_description = clean_step(step_description)

        # Perform hybrid search
        relevant_functions = hybrid_search(cleaned_description, extracted_data, k=k, alpha=alpha)

        # Store the top result for the step
        if relevant_functions:
            top_function = relevant_functions[0]  # Top-1 relevant function
            step_results.append({
                "step": step["step"],
                "description": step_description,
                "cleaned_description": cleaned_description,  # Include cleaned description
                "top_function": top_function
            })
        else:
            step_results.append({
                "step": step["step"],
                "description": step_description,
                "cleaned_description": cleaned_description,  # Include cleaned description
                "top_function": None
            })

    return step_results


def format_step_results(step_results):
    """Format the step results for display."""
    formatted_output = []
    for step in step_results:
        step_info = (
            f"{step['step']}:\n"
            f"Original Description: {step['description']}\n"
            f"Cleaned Description: {step['cleaned_description']}\n"  # Add cleaned description
        )
        if step["top_function"]:
            function = step["top_function"]
            step_info += (
                f"Top Function:\n"
                f"  Class Name: {function['class_name']}\n"
                f"  Function Name: {function['function_name']}\n"
                f"  Input: {function['input']}\n"
                f"  Output: {function['output']}\n"
                f"  Score: {function['score']:.4f}\n"
            )
        else:
            step_info += "Top Function: None\n"
        formatted_output.append(step_info)
    return "\n".join(formatted_output)



# Function to dynamically initialize the selected model
def initialize_model(model_choice):
    if model_choice == "DeepSeek":
        return ChatOllama(
            model="deepseek-coder:6.7b",
            base_url="http://localhost:11434",
            temperature=0.5
        )
    elif model_choice == "Codex":
        return OpenAIChat(api_key="your_openai_api_key", model="code-davinci-002")
    elif model_choice == "LLaMA 3":
        return ChatOllama(
            model="llama-3:13b",
            base_url="http://localhost:11434",
            temperature=0.5
        )
    elif model_choice == "LLaMA 3.1":
        return ChatOllama(
            model="llama-3.1:13b",
            base_url="http://localhost:11434",
            temperature=0.5
        )
    elif model_choice == "OpenAI":
        return OpenAIChat(api_key="your_openai_api_key", model="gpt-4")
    else:
        st.error("Invalid model selection.")
        return None
# Function to generate test code using the selected model
def generate_test_code_with_selected_model(local_llm, user_query, step_results, custom_prompt=None):
    formatted_functions = format_step_results(step_results)
    default_prompt =f"""
     ### Instructions to Model:
    **Instructions**: Generate Java code that precisely implements each step from the 
    **Current Scenario** using only the **Relevant Functions** provided. Follow the 
    **Java Code Template** below, with accurate imports, object initialization, 
    and test data retrieval. Ensure that each function call strictly matches its 
    required parameters from the relevant functions, avoiding any extra comments, 
    explanations, or placeholders.

    ### Current Scenario:

    {user_query}

    ### Relevant Functions:
    - **Function Details**: Each function includes its class name, function name, 
    required input parameters, and expected output.
    - **Class and Function Information**:
    {formatted_functions}

    ### Java Code Template:

    ```java
    // **Imports**
    // Import necessary classes based on the functions used in the scenario
    import baseClass.BaseClass;
    import iSAFE.ApplicationKeywords;
    {{Dynamically include imports based on the function class names provided}}

    public class TC_{{TestClassName}} extends ApplicationKeywords {{
        BaseClass obj;
        // Page object declarations based on relevant functions used
        {{Dynamic Page Objects Initialization}}


        public TC_{{TestClassName}}(BaseClass obj) {{
            super(obj);
            this.obj = obj;
        }}

        public void runScenario() {{
            try {{
                // Initialize page objects for each class used in the relevant functions
                {{Dynamic Page Objects Assignment}}
                {{Dynamic class initialization}}

                // Retrieve test data for each parameter from the data source {{using retrive function}}
                {{Dynamic Test Data Retrieval}}

                // Execute steps as outlined in the Current Scenario:
                {{Dynamic Scenario Implementation using}}

            }} catch (Exception e) {{
                e.printStackTrace();
            }}
            finally {{
                print("pages")
            }}
        }}
    }}
    ```

    ### Important note for code generation:
    - The code generation should implement all the steps mentioned in the current scenario.
    """
    # Use the custom prompt if provided, else fallback to the default prompt
    prompt_to_use = custom_prompt if custom_prompt else default_prompt
    response = local_llm.invoke([HumanMessage(content=prompt_to_use)])
    test_code = response.content.strip() if hasattr(response, "content") else response.strip()
    return test_code, prompt_to_use







# Main Streamlit application
def main():
    st.title("Test Code Generation System")

    # Model selection dropdown
    model_choice = st.selectbox(
        "Choose a Model for Code Generation:",
        options=["DeepSeek", "Codex", "LLaMA 3", "LLaMA 3.1", "OpenAI"]
    )

    # Text input for user query
    user_query = st.text_area("Enter your scenario description:")
   # Variables to manage visibility
    session_state = st.session_state
    if "step_results" not in session_state:
        session_state.step_results = None
    if "custom_prompt" not in session_state:
        session_state.custom_prompt = None

    # Step 3: Fetch relevant functions
    if st.button("Get Relevant Functions"):
        # Load descriptions or relevant data
        extracted_data = load_descriptions()
        if not extracted_data:
            st.error("Failed to load extracted data.")
            return

        # Retrieve relevant functions
        session_state.step_results = process_steps_and_search(user_query, extracted_data)
        if not session_state.step_results:
            st.error("No relevant functions found.")
            return

        st.subheader("Relevant Functions:")
        st.text(format_step_results(session_state.step_results))

        # Display the generated prompt for review
        st.subheader("Generated Prompt:")
        if "custom_prompt" not in st.session_state or not st.session_state.custom_prompt:
            # Initialize the custom prompt with the default prompt if not already set
            st.session_state.custom_prompt = f"""
            ### Instructions to Model:
            **Instructions**: Generate Java code that precisely implements each step from the 
            **Current Scenario** using only the **Relevant Functions** provided. Follow the 
            **Java Code Template** below, with accurate imports, object initialization, 
            and test data retrieval. Ensure that each function call strictly matches its 
            required parameters from the relevant functions, avoiding any extra comments, 
            explanations, or placeholders.

            ### Current Scenario:

            {user_query}

            ### Relevant Functions:
            - **Function Details**: Each function includes its class name, function name, 
            required input parameters, and expected output.
            - **Class and Function Information**:
            {format_step_results(session_state.step_results)}


            ### Java Code Template:

                ```java
                // **Imports**
                // Import necessary classes based on the functions used in the scenario
                import baseClass.BaseClass;
                import iSAFE.ApplicationKeywords;
                {{Dynamically include imports based on the function class names provided}}

                public class TC_{{TestClassName}} extends ApplicationKeywords {{
                    BaseClass obj;
                    // Page object declarations based on relevant functions used
                    {{Dynamic Page Objects Initialization}}


                    public TC_{{TestClassName}}(BaseClass obj) {{
                        super(obj);
                        this.obj = obj;
                    }}

                    public void runScenario() {{
                        try {{
                            // Initialize page objects for each class used in the relevant functions
                            {{Dynamic Page Objects Assignment}}
                            {{Dynamic class initialization}}

                            // Retrieve test data for each parameter from the data source {{using retrive function}}
                            {{Dynamic Test Data Retrieval}}

                            // Execute steps as outlined in the Current Scenario:
                            {{Dynamic Scenario Implementation using}}

                        }} catch (Exception e) {{
                            e.printStackTrace();
                        }}
                        finally {{
                            print("pages")
                        }}
                    }}
                }}
                ```

                ### Important note for code generation:
                - The code generation should implement all the steps mentioned in the current scenario.
            """
            # Add a checkbox to toggle full-screen mode
            full_screen = st.checkbox("View Prompt in Full-Screen Mode")

            if full_screen:
                # Display the prompt in a larger text area
                st.text_area("Generated Prompt (Full Screen):", st.session_state.custom_prompt, key="custom_prompt", height=600)
            else:
                # Display the prompt in a smaller text area with adjustable height
                st.text_area("Generated Prompt (editable):", st.session_state.custom_prompt, key="custom_prompt", height=200)
        # Step 4: Generate code only if functions are available
        if session_state.step_results:
            st.subheader("Ready to Generate Code")

            if st.button("Generate Code"):
                st.info("Processing...")
                local_llm = initialize_model(model_choice)
                if not local_llm:
                    return

                # Use the custom prompt or fallback to the default
                custom_prompt = session_state.get("custom_prompt", None)
                test_code, prompt_used = generate_test_code_with_selected_model(
                    local_llm, user_query, session_state.step_results, custom_prompt
                )

                # Display the generated code
                st.subheader("Generated Test Code:")
                st.code(test_code, language="java")

                # Display the prompt used for generation
                st.subheader("Prompt Used for Code Generation:")
                st.text(prompt_used)

# Run the application
if __name__ == "__main__":
    main()
