import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage

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

def query_individual_function(function_name, qb_function_name, extracted_data, k=2):
    # Structure the query with `function_name: {qb_function_name}`
    combined_query = f"{function_name}: {qb_function_name}"
    
    # Generate embedding for the combined query
    query_embedding = model.encode([combined_query])

    # Search the FAISS index for the nearest neighbors
    D, I = index.search(np.array(query_embedding, dtype=np.float32), k)

    results = []
    seen_function_signatures = set()

    for i in range(k):
        idx = I[0][i]
        
        # Extract class name, function name, code, input, and output fields
        class_name = extracted_data[idx].get("class_name")
        func_name = extracted_data[idx].get("function_name")
        input_params = extracted_data[idx].get("input", [])
        output = extracted_data[idx].get("output")
        
        # Create a unique signature to avoid duplicate entries
        function_signature = (class_name, func_name)
        
        if function_signature not in seen_function_signatures:
            seen_function_signatures.add(function_signature)
            # Append the extracted information to results
            results.append({
                "class_name": class_name,
                "function_name": func_name,
                "input": input_params,
                "output": output
            })
    
    return results


def get_relevant_functions(DB_scenario_query, extracted_data, k=1):
    # Split DB_scenario_query by commas to get each function name
    function_queries = [fn.strip() for fn in DB_scenario_query.split(",")]
    
    # Query FAISS for each function name and collect results
    all_relevant_functions = []
    seen_function_signatures = set()
    
    for query in function_queries:
        # Separate function name and embedded function name
        parts = query.split(":")
        function_name = parts[0].strip()
        embedded_function_name = parts[1].strip() if len(parts) > 1 else ""

        # Query individual function with both names        
        relevant_functions = query_individual_function(function_name, embedded_function_name, extracted_data, k)
        
        # Append only unique functions based on class name and function name
        for func in relevant_functions:
            # Create a unique signature for each function to avoid duplicates
            function_signature = (func['class_name'], func['function_name'])
            
            if function_signature not in seen_function_signatures:
                seen_function_signatures.add(function_signature)
                all_relevant_functions.append(func)
    
    return format_functions(all_relevant_functions)

def format_functions(functions):
    # Format the functions in a structured output
    structured_output = []
    for i, func in enumerate(functions, start=1):
        structured_output.append(
            f"{i}. \n"
            f"Class Name: {func['class_name']}\n"
            f"Function Name: {func['function_name']}\n"
            f"Input: {func['input']}\n"
            f"Output: {func['output']}\n"
        )
    # Join all structured function details into a single string
    return "\n".join(structured_output)


def generate_test_code_with_ollama(scenario_query, all_relevant_functions):
    # Initialize the local Ollama client for DeepSeek
    local_llm = ChatOllama(
        model="deepseek-coder:6.7b",
        base_url="http://localhost:11434",  # Replace with your local Ollama endpoint if different
        temperature=0.5  # Adjust for creativity vs. precision
    )
### Relevant Functions:
# {relevant_codes}
    # Construct the full prompt with the scenario, relevant function codes, and example
    prompt = f"""
    ### Instructions to Model:
    **Instructions**: Generate Java code that precisely implements each step from the 
    **Current Scenario** using only the **Relevant Functions** provided. Follow the 
    **Java Code Template** below, with accurate imports, object initialization, 
    and test data retrieval. Ensure that each function call strictly matches its 
    required parameters from the relevant functions, avoiding any extra comments, 
    explanations, or placeholders.

    ### Current Scenario:

    {scenario_query}

    ### Relevant Functions:
    - **Function Details**: Each function includes its class name, function name, 
    required input parameters, and expected output.
    - **Class and Function Information**:
    {all_relevant_functions}

    ### Java Code Template:

    ```java
    // **Imports**
    // Import necessary classes based on the functions used in the scenario
    import baseClass.BaseClass;
    import iSAFE.ApplicationKeywords;
    // Dynamically include imports based on the function class names provided

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

                // Retrieve test data for each parameter from the data source
                {{Dynamic Test Data Retrieval}}

                // Execute steps as outlined in the Current Scenario:
                {{Dynamic Scenario Implementation}}

            }} catch (Exception e) {{
                e.printStackTrace();
            }}
            finally{{
                print("pages")
            }}
        }}
    }}

    ###important note for code generation
    - The code generation should implement all the steps mentoned in the current scenario
    """

    # Generate response using the DeepSeek model
    response = local_llm.invoke([HumanMessage(content=prompt)])  # Use invoke instead of __call__
    test_code = response.content.strip()  # Extract generated test code directly
    
    return test_code, prompt

def main():
    json_file_path = "parsed_data.json"  # Path to your extracted JSON file
    extracted_data = load_descriptions(json_file_path)

    DB_scenario_query = """loginToSalesForce, selectTabs,  , 
    clickOnTabs, selectOrDeselectCheckBox, clickOnSaveButton"""

    # Example scenario query
    scenario_query = """
        Goal : Verify that on dealer level Pennat Flag should be true

        Step 1 : login to the sales force login page  
        step 2 : selecttabs accounts label 
        step 3 : enter dealers values in table search and click
        step 4 : click on tabs to details label 
        step 5 : click edit icon 
        step 6 : select check box pannat flag
        step 7 : click on save button
        """

    # Retrieve relevant functions from the FAISS index for each function name in the query
    all_relevant_functions = get_relevant_functions(DB_scenario_query, extracted_data)

    #print(all_relevant_functions)
    # Format relevant functions into a single string
    #all_relevant_functions = "\n\n".join(relevant_functions)

   
    # Print relevant functions
    # print("Relevant Function:")
    print(all_relevant_functions)
    print("\n-------------------------------------\n")

    # Generate the test code using DeepSeek
    test_code, prompt = generate_test_code_with_ollama(scenario_query, all_relevant_functions)
    
    # Print the generated test code
    if test_code:
        print("Final Prompt for Model Input:\n")
        print(prompt)
        print("Generated Test Code:")
        print(test_code)

if __name__ == "__main__":
    main()


 # example_scenario_code = """ 
    #         Example (contain the scenario, Relevent functions and code implementation that directly applies):

    #         Scenario: 
    #         Gole : Verify that on dealer level Pennat Flag should be true

    #         Step 1 : login to the Salesforce login page, 
    #         step 2 : select accounts label, 
    #         step 3 : enter dealer values in table search and click, 
    #         step 4 : click on details label, 
    #         step 5 : click edit icon, 
    #         step 6 : select checkbox Pennant flag,
    #         step 7 : click on save button

            
    #         Relevent code functions:

    #                     public boolean loginToSalesForce(String appURL_SalesForce, String SalesforceuserName, String Salesforcepassword) {
    #                     waitForPageToLoad();
    #                     boolean flag = false;
    #                     try {
    #                         testStepInfo("Sales Force Login Page");
    #                         for(int i=0;i<=3;i++)
    #                         {
    #                             navigateTo(appURL_SalesForce);
    #                             String URL = driver.getCurrentUrl();
    #                             if (URL.contains("uat.sandbox")||URL.contains("twfpreprod.sandbox")) {
    #                                 break;
    #                             }
    #                         }			
    #                         waitForElement(txt_userNameAdmin,  5);
    #                         if (isElementDisplayed(txt_userNameAdmin, 5)) {
    #                             typeIn(txt_userNameAdmin, SalesforceuserName);
    #                             if (isElementDisplayed(txt_passWordAdmin, 5)) {
    #                                 typeInMaskedData(txt_passWordAdmin, Salesforcepassword);
    #                                 if (isElementDisplayed(btn_loginAdmin, 5)) {
    #                                     clickOn(btn_loginAdmin);
    #                                     waitForPageToLoad();
    #                                 } else {
    #                                     testStepFailed("Login button is not present");
    #                                 }
    #                             } else {
    #                                 testStepFailed("Password field is not present");
    #                             }
    #                         }
    #                         else if(isElementDisplayed(txt_homePage, 10))
    #                         {
    #                             testStepInfo("# Successfully Logged Into Master #");
    #                         }
    #                         else {
    #                             testStepFailed("User Name field is not present");
    #                         }									
    #                         if (isElementDisplayed(error, 5)) {
    #                             testStepFailed("Failed in login. Warning : " + getText(error));
    #                             flag = true;
    #                         } else {
    #                             testStepInfo("# Successfully Logged Into Master #");
    #                         }
    #                     } catch (Exception e) {
    #                         testStepFailed("loginToSalesForce failed.Error " + e.getClass().getName());
    #                     }
    #                     return flag;
    #                 }public boolean loginToSalesForce(String appURL_SalesForce, String SalesforceuserName, String Salesforcepassword) {
    #                     waitForPageToLoad();
    #                     boolean flag = false;
    #                     try {
    #                         testStepInfo("Sales Force Login Page");
    #                         for(int i=0;i<=3;i++)
    #                         {
    #                             navigateTo(appURL_SalesForce);
    #                             String URL = driver.getCurrentUrl();
    #                             if (URL.contains("uat.sandbox")||URL.contains("twfpreprod.sandbox")) {
    #                                 break;
    #                             }
    #                         }			
    #                         waitForElement(txt_userNameAdmin,  5);
    #                         if (isElementDisplayed(txt_userNameAdmin, 5)) {
    #                             typeIn(txt_userNameAdmin, SalesforceuserName);
    #                             if (isElementDisplayed(txt_passWordAdmin, 5)) {
    #                                 typeInMaskedData(txt_passWordAdmin, Salesforcepassword);
    #                                 if (isElementDisplayed(btn_loginAdmin, 5)) {
    #                                     clickOn(btn_loginAdmin);
    #                                     waitForPageToLoad();
    #                                 } else {
    #                                     testStepFailed("Login button is not present");
    #                                 }
    #                             } else {
    #                                 testStepFailed("Password field is not present");
    #                             }
    #                         }
    #                         else if(isElementDisplayed(txt_homePage, 10))
    #                         {
    #                             testStepInfo("# Successfully Logged Into Master #");
    #                         }
    #                         else {
    #                             testStepFailed("User Name field is not present");
    #                         }									
    #                         if (isElementDisplayed(error, 5)) {
    #                             testStepFailed("Failed in login. Warning : " + getText(error));
    #                             flag = true;
    #                         } else {
    #                             testStepInfo("# Successfully Logged Into Master #");
    #                         }
    #                     } catch (Exception e) {
    #                         testStepFailed("loginToSalesForce failed.Error " + e.getClass().getName());
    #                     }
    #                     return flag;
    #                 }
    #             --------------------------------------------------------

    #                     public void switchToApplicationClassicOrLightning(String mode) {
    #                     try {
    #                         if (mode.equalsIgnoreCase("Lightning")) {
    #                             if (!isElementDisplayed("Waffle icon#xpath=//div[@class='slds-icon-waffle']", 2)) {
    #                                 if (isElementDisplayed(GOR.img_user, 2)) {
    #                                     testStepPassed("Already present in lightining mode");
    #                                 } else {
    #                                     clickOn(GOR.lnk_switchToLightning);
    #                                     if (isElementDisplayed(GOR.txt_salesForceSearchbox, 2)) {
    #                                         testStepPassed("# Successfully navigated to application lightning mode #");
    #                                     } else {
    #                                         testStepFailed("Failed to navigate application lightning mode");
    #                                     }
    #                                 }
    #                             } else {
    #                                 testStepPassed("# Already present in lightining mode #");
    #                             }
    #                         } else if (mode.equals("Classic")) {
    #                             if (isElementDisplayed(GOR.lnk_switchToLightning, 2)) {
    #                                 testStepPassed("Already present in classic mode");
    #                             } else {
    #                                 clickOnSpecialElement(GOR.img_user);
    #                                 clickOn(GOR.lnk_switchToClassic);
    #                                 if (isElementDisplayed(GOR.lnk_switchToLightning, 2)) {
    #                                     testStepPassed("# Successfully navigated application to Classic mode #");
    #                                 } else {
    #                                     testStepFailed("Failed to navigate to application Classic mode");
    #                                 }
    #                             }
    #                         }
    #                     } catch (Exception e) {
    #                         testStepFailed("An exception occurred switchToApplicationClassicOrLightning() " + e.getClass().getName());
    #                     }
    #                 }

    #                 -------------------------------------------------------------

    #                 public void selectTabs(String optionToClick) {
    #                     try {
    #                         waitForPageToLoad();
    #                         String navigationOption = "'" + optionToClick + "' navigation option #xpath=//span[text()='" + optionToClick
    #                                 + "']//parent::a | //a[text()='" + optionToClick+"']//parent::a";		
    #                         waitForElement(navigationOption, 10);
    #                         if (isElementDisplayed(navigationOption, 10)) {
    #                             scrollbycordinates(navigationOption);
    #                             clickOnSpecialElement(navigationOption);
    #                             waitTime(3);
    #                             waitForPageToLoad();
    #                             testStepPassed("'" + optionToClick + "' navigation option is clicked successfully");
    #                         } else {
    #                             testStepFailed("'" + optionToClick + "' navigation option is not present");
    #                         }
    #                     } catch (Exception e) {
    #                         testStepFailed("Failed in selectTabs. Exception: " + e.getClass().getName());
    #                     }
    #                 }

    #                 -------------------------------------------------------------------------------

    #                     public void enterValueInTableSearchAndClick(String value) {
    #                     try {
    #                         String search = "Search #xpath=//div/input[@type='search']";
    #                         String searchValue = value + "#xpath=//a[@title='" + value + "']";
    #                         waitForElement(search, 10);
    #                         if (isElementDisplayed(search, 10)) {
    #                             WebElement searchBtn = findWebElement(search);
    #                             searchBtn.sendKeys(value);
    #                             searchBtn.sendKeys(Keys.ENTER);
    #                             waitForPageToLoad();
    #                             if (isElementDisplayed(searchValue, elementLoadWaitTime)) {
    #                                 highLighterMethodManualScreenShot(searchValue, value);
    #                                 clickOn(searchValue);
    #                                 waitForPageToLoad();
    #                             } else {
    #                                 testStepFailed(value + " is not present");
    #                             }
    #                         } else {
    #                             testStepFailed("Search field is not present");
    #                         }
    #                     } catch (Exception e) {
    #                         testStepFailed("Failed in enterValueInTableSearch. Exception : " + e.getClass().getName());
    #                     }
    #                 }


    #                 ------------------------------------------------------------------------------------------

    #                     public void clickOnTabs(String linkName) {
    #                     try {
    #                         refreshPage();
    #                         waitForPageToLoad();
    #                         String link = linkName + "#xpath=//div[contains(@class,'active')]//a[text()='" + linkName + "']";
    #                         waitForElement(link, 10);
    #                         if (isElementDisplayed(link, 10)) {
    #                             scrollToElement(link);
    #                             scrollToWebElement(link);
    #                             clickOnSpecialElement(link);
    #                             waitForPageToLoad();
    #                         } else {
    #                             testStepFailed(linkName + " tab is not present");
    #                         }
    #                     } catch (Exception e) {
    #                         testStepFailed("Failed in clickOnTabs " + e.getClass().getName());
    #                     }
    #                 }

    #                 ---------------------------------------------------------------------------

    #                     public void clickEditIcon(String labelName) {
    #                     try {
    #                         String button = labelName + " Edit or Change#xpath=//span[text()='" + labelName
    #                                 + "']/parent::div//..//button";
    #                         waitForElement(button, 10);
    #                         if (isElementPresent(button)) {
    #                             scrollToElement(button);
    #                             scrollToWebElement(button);
    #                             clickOn(button);
    #                             waitForPageToLoad();
    #                             waitTime(3);
    #                         } else {
    #                             testStepFailed(labelName + " edit button is not available");
    #                         }
    #                     } catch (Exception e) {
    #                         testStepFailed("Failed in clickEditIcon. Exception" + e.getMessage());
    #                     }
    #                 }

    #                 ----------------------------------------------------------------------

    #                     public void selectOrDeselectCheckBox(String labelName, String status) {
    #                     try {
    #                         String checkBox = labelName + "#xpath=//label[text()='"+labelName+"']//ancestor::tr//td//input";
    #                         waitForElement(checkBox, 10);
    #                         if (isElementPresent(checkBox)) {
    #                             scrollToWebElement(checkBox);
    #                             scrollToElementTillPresent(checkBox);
    #                             if (status.equalsIgnoreCase("check")) {
    #                                 if (!isCheckBoxSelected(checkBox)) {
    #                                     scrollToElement(checkBox);
    #                                     scrollToWebElement(checkBox);
    #                                     clickOnSpecialElement(checkBox);
    #                                     manualScreenshot(labelName + " Check box is successfully checked");
    #                                 } else {
    #                                     manualScreenshot(labelName + " check box is already checked");
    #                                 }
    #                             } else if (status.equalsIgnoreCase("uncheck")) {
    #                                 if (isCheckBoxSelected(checkBox)) {
    #                                     scrollToElement(checkBox);
    #                                     scrollToWebElement(checkBox);
    #                                     clickOnSpecialElement(checkBox);
    #                                     manualScreenshot(labelName + " Check box is successfully Unchecked");
    #                                 } else {
    #                                     manualScreenshot(labelName + " Check box is already Unchecked");
    #                                 }
    #                             }
    #                         } else {
    #                             testStepFailed(labelName + " checkbox is not present");
    #                         }
    #                     } catch (Exception e) {
    #                         writeToLogFile("INFO", "Exception :" + e);
    #                         testStepFailed("selectCheckBox failed. Exception: " + e.getClass().getName());
    #                     }
    #                 }

    #                 -----------------------------------------------------------------------------------------

    #                     public void clickOnSaveButton(String buttonLabel) {
    #                     try { 
    #                         String button = buttonLabel + "#xpath=//button[text()='" + buttonLabel + "'] | //button[@title='" + buttonLabel + "']";
    #                         waitForElement(button, implicitlyWaitTime);
    #                         WebElement element = findWebElement(button);
    #                         if (isElementDisplayed(button, 5)) {
    #                             scrollToWebElement(button);
    #                             Actions action = new Actions(driver);
    #                             action.moveToElement(element).click().perform();
    #                             waitTime(5);
    #                             manualScreenshot("Clicked on "+buttonLabel);
    #                         } else {
    #                             testStepFailed(buttonLabel + "  is not present.");
    #                         }
    #                     } catch (Exception e) {
    #                         testStepFailed(
    #                                 "Failed in clickOnSaveButton. Exception : " + e.getClass().getName());
    #                     }
    #                 }


    #     Code Implementation Example:

                            
    #                         // **Imports**
    #                         import baseClass.BaseClass;
    #                         import iSAFE.ApplicationKeywords;
    #                         import pages.Login_Logout.loginLogoutPage;
    #                         import pages.SalesForce.homePage_Admin;
    #                         import pages.SalesForce.customerPage_Admin;

    #                         // **Class Structure**
    #                         public class TC_01_US_5294448 extends ApplicationKeywords {{

    #                             // Declaring objects for base class and page objects used in this test case
    #                             BaseClass obj;
    #                             loginLogoutPage loginLogoutPage;
    #                             homePage_Admin homePageAdmin;
    #                             customerPage_Admin customerPageAdmin;

    #                             // Flag variable to track the test case status
    #                             private boolean flag = false;

    #                             // Constructor to initialize the test case with the base class instance
    #                             public TC_01_US_5294448(BaseClass obj) {{
    #                                 super(obj);
    #                                 this.obj = obj;
    #                             }}

    #                             // **Methods**
    #                             // Main test method that executes the steps of the test case
    #                             public void US_5294448_TC_01() {{
    #                                 try {{
    #                                     // Initializing page objects with the base class object
    #                                     loginLogoutPage = new loginLogoutPage(obj);
    #                                     homePageAdmin = new homePage_Admin(obj);
    #                                     customerPageAdmin = new customerPage_Admin(obj);

    #                                     // Retrieving test data from the data source
    #                                     String environment = retrieve("Environment");
    #                                     GOR.environmentValue = environment;
    #                                     String dealerFinnoneValue = retrieve("Dealer Finnone Value");
    #                                     String dealerNameValue = retrieve("Dealer Name Value");
    #                                     String detailsLabel = retrieve("Details Label");

    #                                     // Step 1: Log in to Salesforce with admin credentials
    #                                     flag = loginLogoutPage.loginToSalesForce(adminURL, adminUserName, adminPassword);
    #                                     if (flag) {{
    #                                         return;
    #                                     }}

    #                                     // Step 2: Switch to the appropriate application view (Classic or Lightning)
    #                                     homePageAdmin.switchToApplicationClassicOrLightning(GOR.mode);

    #                                     // Step 3: Pre-condition verification step
    #                                     testStepInfo("***** Pre-conditions *****");
    #                                     testStepInfo("Verify that in account level, Pennant Flag field should be true");

    #                                     // Step 4: Navigate to the Accounts tab and search for the dealer
    #                                     selectTabs(accountsLabel);
    #                                     homePageAdmin.enterValueInTableSearchAndClick(dealerFinnoneValue, dealerNameValue);

    #                                     // Step 5: Open the details tab and edit the Pennant Flag field
    #                                     customerPageAdmin.clickOnTabs(detailsLabel);
    #                                     customerPageAdmin.clickEditIcon("PENNAT FLAG");
    #                                     customerPageAdmin.selectOrDeselectCheckBox("PENNAT FLAG", "check");

    #                                     // Step 6: Save changes
    #                                     homePageAdmin.clickOnSaveButton(saveLabel);
    #                                 }}
    #                                 catch (Exception e) {{
    #                                     // Exception handling in case of an error during test execution
    #                                     e.printStackTrace();
    #                                 }}
    #                             }}
    #                         }}



    #         """


# import json
# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from langchain.chat_models import ChatOllama
# from langchain.schema import HumanMessage

# # Load the embedding model
# model_name = "sentence-transformers/all-MiniLM-L6-v2"
# model = SentenceTransformer(model_name)

# # Load the FAISS index
# index = faiss.read_index("faiss_index.index")

# def load_descriptions(json_file_path):
#     # Load extracted data from the JSON file
#     with open(json_file_path, 'r') as file:
#         extracted_data = json.load(file)
#     return extracted_data

# def query_faiss_index(DB_scenario_query, extracted_data, k=9):
#     # Generate embedding for the query
#     query_embedding = model.encode([DB_scenario_query])

#     # Search the FAISS index for the nearest neighbors
#     D, I = index.search(np.array(query_embedding, dtype=np.float32), k)

#     # Prepare results while removing duplicates based on function names
#     results = []
#     seen_function_names = set()
    
#     for i in range(k):
#         idx = I[0][i]
#         code_snippet = extracted_data[idx]["code"]
#         function_name = extracted_data[idx]["function_name"]  # Assuming each entry has a "function_name" key
        
#         if function_name not in seen_function_names:
#             seen_function_names.add(function_name)
#             results.append(code_snippet)
    
#     return results


# def generate_test_code_with_ollama(example_scenario_code, scenario_query, relevant_codes):
#     # Initialize the local Ollama client for DeepSeek
#     local_llm = ChatOllama(
#         model="deepseek-coder:6.7b",
#         base_url="http://localhost:11434",  # Replace with your local Ollama endpoint if different
#         temperature=0.5  # Adjust for creativity vs. precision
#     )

#     # Construct the full prompt with the scenario, relevant function codes, and example

#     prompt = f"""
#         Using the example provided strictly as a framework structure template, generate test code based on the current scenario and relevant functions only. 

#         **Example Framework Structure (for reference only):**
#         {example_scenario_code}  # <- This is the example scenario code for reference

#         **Current Scenario (for code generation):**
#         {scenario_query}  # <- Current scenario that should be used for generating code

#         **Relevant Function Codes:**
#         {relevant_codes}  # <- Functions retrieved from the vector database for this scenario

#         **Instructions:**
#         1. **Structure Reference Only**: The example above is for reference to match framework structure, imports, class definitions, error-handling format, and method setup. Do NOT reuse the example scenario or code.
#         2. **Use Current Scenario Only**: Code must follow the structure but should address the current scenario requirements using only the relevant functions provided.
#         3. **Framework Alignment**: Match the naming conventions, control flow, and error-handling format exactly as shown in the example structure.
#         4. **No Placeholder Text or Extraneous Content**: The output should only contain relevant, executable test steps based on the current scenario.
#         5. **Step by step implementation of steps in the scenario**: in output it should display the step and the restestive code lines implementation of it.
#         Generate the test code accordingly.
#     """



#     # Generate response using the DeepSeek model
#     response = local_llm.invoke([HumanMessage(content=prompt)])  # Use invoke instead of __call__
#     test_code = response.content.strip()  # Extract generated test code directly

#     return test_code

# def main():
#     json_file_path = "parsed_data.json"  # Path to your extracted JSON file
#     extracted_data = load_descriptions(json_file_path)

#     DB_scenario_query = """loginToFOSApplication, searchCustomer, selectModel, getDealId, 
#     selectTabs-customerDetailsTab, ckycPanValidation, addressEnrichment, customerDetails, 
#     financialInfo"""

#     # Example scenario query
#     scenario_query = """
#                 Gole: Verify that user should create customer till post approval stage
 
#                 step 1: login to the FOS application, use the function - loginToFOSApplication
#                 step 2: search for the customer, use the function - searchCustomer
#                 step 3: select the model, use ethe function - selectModel
#                 step 4: get the dealer ID, use the function - getDealId
#                 step 5: select customer details tab, use the cunction - selectTabs
#                 step 6: validate ckyc of pan, use the function - ckycPanValidation
#                 step 7: do the address enrichment, use the funation - addressEnrichment"""

#     relevant_functions = query_faiss_index(DB_scenario_query, extracted_data)

#     # Format relevant functions into a single string
#     relevant_codes = "\n\n".join(relevant_functions)

#     example_scenario_code = """ 
#             Example (showing both the scenario and code implementation that directly applies):

#             Scenario: login to the Salesforce login page, select accounts label, enter dealer values in table search and click, 
#             click on details label, click edit icon, select checkbox Pennant flag, and click on save button

#             Code Implementation Example:

#             **Imports**
#             // Importing necessary base classes and page object classes for the test case execution
#             import baseClass.BaseClass;
#             import iSAFE.ApplicationKeywords;
#             import pages.Login_Logout.loginLogoutPage;
#             import pages.SalesForce.homePage_Admin;
#             import pages.SalesForce.customerPage_Admin;

#             **Class Structure**
#             // Defining the test case class that extends ApplicationKeywords for keyword-driven test case execution
#             public class TC_01_US_5294448 extends ApplicationKeywords {{

#                 // Declaring objects for base class and page objects used in this test case
#                 BaseClass obj;
#                 loginLogoutPage loginLogoutPage;
#                 homePage_Admin homePageAdmin;
#                 customerPage_Admin customerPageAdmin;

#                 // Flag variable to track the test case status
#                 private boolean flag = false;

#                 // Constructor to initialize the test case with the base class instance
#                 public TC_01_US_5294448(BaseClass obj) {{
#                     super(obj);
#                     this.obj = obj;
#                 }}

#                 **Methods**
#                 // Main test method that executes the steps of the test case
#                 public void US_5294448_TC_01() {{
#                     try {{
#                         // Initializing page objects with the base class object
#                         loginLogoutPage = new loginLogoutPage(obj);
#                         homePageAdmin = new homePage_Admin(obj);
#                         customerPageAdmin = new customerPage_Admin(obj);

#                         // Retrieving test data from the data source
#                         String environment = retrieve("Environment");
#                         GOR.environmentValue = environment;
#                         String dealerFinnoneValue = retrieve("Dealer Finnone Value");
#                         String dealerNameValue = retrieve("Dealer Name Value");
#                         String detailsLabel = retrieve("Details Label");

#                         // Step 1: Log in to Salesforce with admin credentials
#                         flag = loginLogoutPage.loginToSalesForce(adminURL, adminUserName, adminPassword);
#                         if (flag) {{
#                             return;
#                         }}

#                         // Step 2: Switch to the appropriate application view (Classic or Lightning)
#                         homePageAdmin.switchToApplicationClassicOrLightning(GOR.mode);

#                         // Step 3: Pre-condition verification step
#                         testStepInfo("***** Pre-conditions *****");
#                         testStepInfo("Verify that in account level, Pennant Flag field should be true");

#                         // Step 4: Navigate to the Accounts tab and search for the dealer
#                         selectTabs(accountsLabel);
#                         homePageAdmin.enterValueInTableSearchAndClick(dealerFinnoneValue, dealerNameValue);

#                         // Step 5: Open the details tab and edit the Pennant Flag field
#                         customerPageAdmin.clickOnTabs(detailsLabel);
#                         customerPageAdmin.clickEditIcon("PENNAT FLAG");
#                         customerPageAdmin.selectOrDeselectCheckBox("PENNAT FLAG", "check");

#                         // Step 6: Save changes
#                         homePageAdmin.clickOnSaveButton(saveLabel);
#                     }}
#                     catch (Exception e) {{
#                         // Exception handling in case of an error during test execution
#                         e.printStackTrace();
#                     }}
#                 }}
#             }}


#             """
    
#     # Print relevant functions
#     print("Relevant Function Codes:")
#     print(relevant_codes)
#     print("\n-------------------------------------\n")

#     # Generate the test code using DeepSeek
#     test_code = generate_test_code_with_ollama(example_scenario_code, scenario_query, relevant_codes)

#     # Print the generated test code
#     if test_code:
#         print("Generated Test Code:")
#         print(test_code)

# if __name__ == "__main__":
#     main()
