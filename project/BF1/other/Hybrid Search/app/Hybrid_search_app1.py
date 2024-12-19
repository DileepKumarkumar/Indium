import streamlit as st
import prompt_templates
from functions import (
    format_step_results, initialize_model, load_descriptions, validate_input, 
    process_steps_and_search, generate_test_code_with_selected_model)

def main():
    st.title("Test Code Generation System")

    # Model selection
    model_choice = st.selectbox(
        "Choose a Model for Code Generation:",
        options=["DeepSeek", "Codex", "LLaMA 3", "LLaMA 3.1", "OpenAI", "codestral:latest", "codellama:latest"]
    )

    # Scenario input
    user_query = st.text_area("Enter your scenario description:")

    if st.button("Validate Input Format"):
        validation_feedback = validate_input(user_query)
        if validation_feedback == "Input format is correct!":
            st.success("Input format is valid. You can proceed to fetch relevant functions.")
        else:
            st.error(f"Invalid Input Format: {validation_feedback}")
            return  # Exit the flow if input format is incorrect

    # Validate scenario input
    if not user_query.strip():
        st.warning("Please enter a valid scenario description.")
        return

    # Select prompt template
    selected_template_name = st.selectbox(
        "Select a Prompt Template:",
        options=["Prompt Template 1", "Prompt Template 2", "Prompt Template 3"]
    )

    # Ensure step results are available in session state
    if "step_results" not in st.session_state:
        st.session_state.step_results = []

    # Fetch relevant functions when the button is clicked
    if st.button("Get Relevant Functions"):
        # Load descriptions (make sure this function returns the data you expect)
        extracted_data = load_descriptions()
        
        # Process the user query and fetch relevant functions
        step_results = process_steps_and_search(user_query, extracted_data)
        
        # Save the results in session state for later use
        st.session_state.step_results = step_results

    if st.session_state.step_results:
        # Display relevant functions
        st.subheader("Relevant Functions:")
        formatted_functions = format_step_results(st.session_state.step_results)
        st.text(formatted_functions)

        # Generate final prompt based on selected template
        if selected_template_name == "Prompt Template 1":
            final_prompt = prompt_templates.get_prompt_template_1(
                user_query=user_query,
                formatted_functions=formatted_functions
            )
        elif selected_template_name == "Prompt Template 2":
            final_prompt = prompt_templates.get_prompt_template_2(
                user_query=user_query,
                formatted_functions=formatted_functions
            )
        elif selected_template_name == "Prompt Template 3":
            final_prompt = prompt_templates.get_prompt_template_3(
                user_query=user_query,
                formatted_functions=formatted_functions
            )

        st.text_area("Generated Prompt (Editable):", value=final_prompt, height=300)

        # Generate code if the button is clicked
        if st.button("Generate Code"):
            if not final_prompt.strip():
                st.error("Generated prompt is empty. Ensure the relevant functions are correctly processed.")
                return

            # Initialize model based on user selection
            local_llm = initialize_model(model_choice)
            
            # Generate test code using the model
            test_code, _ = generate_test_code_with_selected_model(
                local_llm, user_query, st.session_state.step_results, final_prompt
            )
            
            # Display generated test code
            st.subheader("Generated Test Code:")
            st.code(test_code, language="java")
    else:
        st.warning("No relevant functions found. Please click 'Get Relevant Functions' first.")

if __name__ == "__main__":
    main()
