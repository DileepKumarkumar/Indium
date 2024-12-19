import streamlit as st
# Define prompt templates
def get_prompt_template_1(user_query, formatted_functions):

    prompt_template_1 = f"""
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
                    {{Dynamic Scenario Implementation}}

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
    return prompt_template_1

def get_prompt_template_2(user_query, formatted_functions):

    prompt_template_2 =  f"""
        ### Instructions to Model:
        **Instructions**: Generate Java code that fully implements each step from the 
        **Current Scenario** using only the **Relevant Functions** provided. Follow the 
        **Java Code Template** below, ensuring the following:
        1. **Complete Imports**: Include all necessary imports for every class referenced in the scenario and relevant functions.
        2. **Dynamic Object Initialization**: Initialize objects for all classes used in the relevant functions, ensuring they are correctly instantiated and assigned.
        3. **Comprehensive Test Data Retrieval**: Retrieve every required input parameter for all functions used in the scenario. Ensure all inputs are fetched dynamically from the data source without leaving placeholders.
        4. **Implementation of Steps**: Implement each step from the scenario in detail, ensuring correct function calls with their respective input parameters.
        5. **Consistent Structure**: Maintain a structured format as per the Java Code Template provided.

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
        // Import all necessary classes and packages based on the functions used in the scenario
        import baseClass.BaseClass;
        import iSAFE.ApplicationKeywords;
        // Dynamically include imports for all class names from relevant functions
        {{Dynamically include imports based on the function class names provided for each steps in the provided Relevent functions}}

        public class TC_{{TestClassName}} extends ApplicationKeywords {{
            BaseClass obj;
            // Dynamically declare page object instances based on relevant functions
            {{Dynamic Page Object Declarations}}

            public TC_{{TestClassName}}(BaseClass obj) {{
                super(obj);
                this.obj = obj;
            }}

            public void runScenario() {{
                try {{
                    // Dynamically initialize page objects for each relevant class
                    {{Dynamic Page Object Initialization}}

                    // Dynamically retrieve all test data required for input parameters
                    //for Test data retrieval the data should be taken from the input field of the relevent functions provided all that paramaters should be retrived.
                    {{Dynamic Test Data Retrieval }}

                    // Execute steps as outlined in the Current Scenario and pass the input parameters that are mentioned for the respective step function data.
                    {{Dynamic Scenario Implementation}}
                }} catch (Exception e) {{
                    e.printStackTrace();
                }}
                finally {{
                    System.out.println("Scenario execution completed.");
                }}
            }}
        }}
        
        ### Important note for code generation:
        - The code generation should implement all the steps mentioned in the current scenario.
        - All the input parameters should be retrieved from the data sheet using the retrieve function
        """

    return prompt_template_2
# prompt_template_3 = f"""
#             Important Note:
#                 Generate Java code strictly according to the instructions below, ensuring every step in the current scenario is fully implemented.
#                 All imports, data retrieval, object initialization, and scenario execution should strictly follow the format and structure defined below.
#                 No steps, inputs, or outputs should be skipped or left unimplemented.
#             ---------------------------------------------------------------------------
#             Instructions to Model:
#             Objective: Generate Java test code that implements the Current Scenario in full detail using the Relevant Functions provided. Adhere strictly to the format, flow, and structure outlined in the Java Code Template below.
#             Dynamic Imports:

#             Dynamically include imports for all class names referenced in the relevant functions. Ensure only the required classes are imported.
#             Dynamic Object Initialization:

#             Initialize objects for all classes mentioned in the relevant functions. Ensure correct instantiation and association with the BaseClass object.
#             Complete Data Retrieval:

#             Dynamically retrieve all required input parameters for every function in the scenario using the retrieve method.
#             Validation: Validate retrieved data to ensure no null or empty values. If any data is missing, log an error message.
#             Output Handling:

#             Appropriately handle outputs from each function. Use outputs as inputs for subsequent steps, log them, or store them as needed.
#             Ensure no outputs are ignored unless explicitly stated in the scenario.
#             Detailed Comments:

#             Add clear and concise comments before every block of code to explain its purpose.
#             Include logging to track the execution flow and outputs at each step.
#             Enhanced Exception Handling:

#             Use specific exception handling where possible. Provide meaningful error messages and logs for debugging.
#             Maintain Structural Consistency:

#             Follow the Java Code Template strictly. Ensure imports, object declarations, data retrieval, and scenario steps align with the template structure.

#             ### Current Scenario:

#             {user_query}

#             ### Relevant Functions:

#             {format_step_results(step_results)}


#             ### Java Code Template:


#             ```java
#             // **Imports**: Dynamically include imports for all required classes based on relevant functions.
#             import baseClass.BaseClass;
#             import iSAFE.ApplicationKeywords;
#             {{Dynamic Import Statements for Classes in Relevant Functions}}

#             public class TC_{{TestClassName}} extends ApplicationKeywords {{
#                 BaseClass obj;

#                 // **Dynamic Declarations**: Declare objects for all classes referenced in relevant functions.
#                 {{Dynamic Object Declarations for Relevant Classes}}

#                 public TC_{{TestClassName}}(BaseClass obj) {{
#                     super(obj);
#                     this.obj = obj;
#                 }}

#                 public void runScenario() {{
#                     try {{
#                         // **Object Initialization**: Initialize objects for all relevant classes.
#                         {{Dynamic Object Initialization for Relevant Classes}}

#                         // **Data Retrieval**: Retrieve all input parameters dynamically and validate them.
#                         {{Dynamic Data Retrieval and Validation for All Inputs}}

#                         // **Scenario Execution**: Implement each step using retrieved inputs and relevant functions.
#                         {{Dynamic Scenario Implementation with Proper Handling of Outputs}}

#                     }} catch (NullPointerException e) {{
#                         System.out.println("Null value encountered: " + e.getMessage());
#                     }} catch (Exception e) {{
#                         e.printStackTrace();
#                     }} finally {{
#                         System.out.println("Scenario execution completed.");
#                     }}
#                 }}
#             }}

# """





# default_prompt = f"""

#             ###important note to be followed through out the code generation: generate the code according to the instructions and don't miss any step to impelement from imports to the all the scenario implementation###
#             ###****make sure that all the steps are implemented which are mentioned in the current scenario with out fail with the following steps in place****###
#             &&&every step should be implemented with all its requirements for each instructions mentioned in the java code templeate and below make sure every thing is implemented with out fail&&&
#             ### Instructions to Model:
#             **Instructions**: Generate Java code that fully implements each step from the 
#             **Current Scenario** using only the **Relevant Functions** provided. Follow the 
#             **Java Code Template** below, ensuring the following:
#             1. **Complete Imports**: Include all necessary imports for every class referenced in the scenario and relevant functions.
#             2. **Dynamic Object Initialization**: Initialize objects for all classes used in the relevant functions, ensuring they are correctly instantiated and assigned.
#             3. **Comprehensive Test Data Retrieval**: Retrieve every required input parameter for all functions used in the scenario. Ensure all inputs are fetched dynamically from the data source without leaving placeholders.
#             4. **Implementation of Steps**: Implement each step from the scenario in detail, ensuring correct function calls with their respective input parameters.
#             5. **Consistent Structure**: Maintain a structured format as per the Java Code Template provided.

#             ### Current Scenario:

#             {user_query}

#             ### Relevant Functions:
#             - **Function Details**: Each function includes its class name, function name, 
#             required input parameters, and expected output.
#             - **Class and Function Information**:
#             {format_step_results(step_results)}
#             ### Java Code Template:

#              ```java
#             // **Imports**
#             // Import all necessary classes and packages based on the functions used in the scenario
#             import baseClass.BaseClass;
#             import iSAFE.ApplicationKeywords;
#             // Dynamically include imports for all class names from relevant functions
#             {{Import all the class names that are mentioned in the each step of the relevant functions details provided}}

#             public class TC_{{TestClassName}} extends ApplicationKeywords {{
#                 BaseClass obj;
#                 // Dynamically declare page object instances based on relevant functions
#                 ***must follow: should retrive all the paremeters in the input field for each step in the relevent function details provided***
#                 {{Declarations Page Object for the all the class names mentioned in the each step of the relevant functions provided above}}

#                 public TC_{{TestClassName}}(BaseClass obj) {{
#                     super(obj);
#                     this.obj = obj;
#                 }}

#                 public void runScenario() {{
#                     try {{
#                         // Dynamically initialize page objects for each relevant class
#                         {{Initialization Page Object for the all the class names mentioned in the each step of the relevant functions provided above}}

#                         // Dynamically retrieve all test data required for input parameters
#                         //for Test data retrieval the data should be taken from the input field of the relevant functions provided all that parameters should be retrieved.
#                         {{Retrieve Test Data using {{retrieve()}} for the input parameters mentioned in the input filed as array for each step in the provided relevant functions, **must retrive all the input parameters**}}

#                         // Execute steps as outlined in the Current Scenario and pass the input parameters that are mentioned for the respective step function data.
#                         {{Dynamic Scenario Implementation for all the steps mentioned in the current scenario taking the relevant functions as reference}}
#                     }} catch (Exception e) {{
#                         e.printStackTrace();
#                     }}
#                     finally {{
#                         System.out.println("Scenario execution completed.");
#                     }}
#                 }}
#             }}
            
#             ### Important note for code generation:
#             - The code generation should implement all the steps mentioned in the current scenario.
#             - All the input parameters should be retrieved from the data sheet using the retrieve function
#             """
