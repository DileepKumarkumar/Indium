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
    # Remove "step" prefixes like "Step 1:", "step2:" (case-insensitive)
    cleaned_step = re.sub(r"step\s*\d+:?", "", step_description, flags=re.IGNORECASE).strip()
    # Remove all numbers and special characters except spaces
    cleaned_step = re.sub(r"[^A-Za-z\s]", "", cleaned_step)
    # Remove extra spaces
    cleaned_step = re.sub(r"\s+", "", cleaned_step).strip()
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

def validate_input(description):
    """Validate the user input to check if it follows the 'goal' and 'step' format."""
    lines = description.split("\n")
    goal_found = False
    steps_valid = True
    step_number = 1
    
    for line in lines:
        line = line.strip()
        
        if line.lower().startswith("goal:"):
            goal_found = True
        elif line.lower().startswith(f"step {step_number}:"):
            step_number += 1
        else:
            steps_valid = False
            break
    
    if not goal_found:
        return "Error: Goal is missing or incorrectly formatted."
    elif not steps_valid:
        return "Error: Steps are not in the correct order or are missing descriptions."
    else:
        return "Input format is correct!"

def extract_steps(description):
    """Extract goal and steps from the provided description."""
    steps = []
    goal = ""
    lines = description.split("\n")

    # First, extract the goal (line containing 'goal:')
    for i, line in enumerate(lines):
        if line.lower().startswith("goal"):
            goal = line.strip()  # Extract the goal description
        elif line.strip().startswith("step"):
            steps.append({
                "step": f"Step {i+0}",
                "description": line.strip()
            })

    # Returning the goal and steps
    return {"goal": goal, "steps": steps}

def process_steps_and_search(description, extracted_data, k=1, alpha=0.5):
    """Process each step from the description and perform a hybrid search for the most relevant function."""
    steps = extract_steps(description)["steps"]  # Extract steps from the description

    step_results = []
    for step in steps:
        step_description = step["description"]
        cleaned_description = clean_step(step_description)

        # Perform hybrid search (assuming this function is implemented elsewhere)
        relevant_functions = hybrid_search(cleaned_description, extracted_data, k=k, alpha=alpha)

        # Store the top result for the step
        if relevant_functions:
            top_function = relevant_functions[0]  # Top-1 relevant function
            step_results.append({
                "step": step["step"],
                # "description": step_description,
                # "cleaned_description": cleaned_description,  # Include cleaned description
                "top_function": top_function
            })
        else:
            step_results.append({
                "step": step["step"],
                # "description": step_description,
                # "cleaned_description": cleaned_description,  # Include cleaned description
                "top_function": None
            })

    return step_results

def format_step_results(step_results):
    """Format the step results for display."""
    formatted_output = []
    for step in step_results:
        step_info = (
            f"{step['step']}:\n"
            # f"Original Description: {step['description']}\n"
            # f"Cleaned Description: {step['cleaned_description']}\n"  # Add cleaned description
        )
        if step["top_function"]:
            function = step["top_function"]
            step_info += (
                # f"Top Function:\n"
                f"  Class Name: {function['class_name']}\n"
                f"  Function Name: {function['function_name']}\n"
                f"  Input: {function['input']}\n"
                f"  Output: {function['output']}\n"
                # f"  Score: {function['score']:.4f}\n"
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
            model="lllama3:latest",
            base_url="http://localhost:11434",
            temperature=0.5
        )
    elif model_choice == "LLaMA 3.1":
        return ChatOllama(
            model="llama3.1:latest",
            base_url="http://localhost:11434",
            temperature=0.5
        )
    elif model_choice == "OpenAI":
        return OpenAIChat(api_key="your_openai_api_key", model="gpt-4")
    elif model_choice == "codestral:latest":
        return ChatOllama(
            model="codestral:latest",
            base_url="http://localhost:11434",
            temperature=0.5
        )
    elif model_choice == "codellama:latest":
        return ChatOllama(
            model="codellama:latest",
            base_url="http://localhost:11434",
            temperature=0.5
        )
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
        options=["DeepSeek", "Codex", "LLaMA 3", "LLaMA 3.1", "OpenAI", "codestral:latest", "codellama:latest"]
    )

    # Text input for user query
    user_query = st.text_area("Enter your scenario description:")

    # Initialize session state variables
    if "step_results" not in st.session_state:
        st.session_state.step_results = None
    if "custom_prompt" not in st.session_state:
        st.session_state.custom_prompt = None

    # Validate input format
    # if st.button("Validate Input Format"):
    #     validation_feedback = validate_input(user_query)
    #     if validation_feedback == "Input format is correct!":
    #         st.success("Input format is valid. You can proceed to fetch relevant functions.")
    #     else:
    #         st.error(f"Invalid Input Format: {validation_feedback}")
    #         return  # Exit the flow if input format is incorrect

    # Step 1: Fetch relevant functions
    if st.button("Get Relevant Functions"):
        # Ensure the input format is valid before proceeding
        validation_feedback = validate_input(user_query)
        if validation_feedback == "Input format is correct!":
            st.success("Input format is valid. You can proceed to fetch relevant functions.")
        else:
            st.error(f"Invalid Input Format: {validation_feedback}")
            return  # Exit the flow if input format is incorrect

        extracted_data = load_descriptions()
        if not extracted_data:
            st.error("Failed to load extracted data.")
            return

        step_results = process_steps_and_search(user_query, extracted_data)
        if not step_results:
            st.error("No relevant functions found.")
            return

        st.session_state.step_results = step_results
        format_step_results(step_results)

        # Generate the default prompt
        default_prompt = f"""
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
            {format_step_results(step_results)}


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
        st.session_state.custom_prompt = default_prompt

    if st.session_state.step_results:
        st.subheader("Relevant Functions:")
        st.text(format_step_results(st.session_state.step_results))

    # Step 2: Display editable prompt after relevant functions are fetched
    if st.session_state.step_results:
        st.subheader("Generated Prompt (Editable):")

        # Add a checkbox for toggling full-screen mode
        full_screen = st.checkbox("View Prompt in Full-Screen Mode")
        text_area_height = 600 if full_screen else 200

        # Display the text area for editing the prompt
        st.session_state.custom_prompt = st.text_area(
            "Editable Prompt:",
            st.session_state.custom_prompt,
            height=text_area_height
        )

        # Step 3: Display "Generate Code" button only if relevant functions are available
        if st.button("Generate Code"):
            st.info("Generating code...")
            local_llm = initialize_model(model_choice)
            if not local_llm:
                st.error("Failed to initialize the model.")
                return

            test_code, prompt_used = generate_test_code_with_selected_model(
                local_llm, user_query, st.session_state.step_results, st.session_state.custom_prompt
            )

            # Display generated code
            st.subheader("Generated Test Code:")
            st.code(test_code, language="java")

            # Display the prompt used for generation
            st.subheader("Prompt Used for Code Generation:")
            st.text(prompt_used)


# Run the application
if __name__ == "__main__":
    main()
