import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage

# Load FAISS index and metadata
index_path = "D:/own/Indium/project/BF/faiss_index.index"  # Update with your index path
metadata_path = "D:/own/Indium/project/BF/metadata.json"  # Update with your metadata path

# Load the index and metadata
index = faiss.read_index(index_path)
with open(metadata_path, "r") as f:
    metadata = json.load(f)

# Initialize model for encoding queries
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Query to search for
query = """
Test Scenario 1: Check if the horizontal menu bar is displayed under the header section
Given the application is launched
When the user navigates to the top section of the application
Then the horizontal menu bar should be visible under the header area
"""
  # Example description; change as needed
query_embedding = model.encode([query])

# Perform search in FAISS index
k = 5  # Number of top results to return
_, top_k_indices = index.search(np.array(query_embedding), k)

# Retrieve the top-k results from the metadata
top_k_results = [metadata[i] for i in top_k_indices[0]]

# Extracting context from the retrieved results
context = "\n".join([f"Implementation: {result['code_implementation']}" for result in top_k_results])

# Define test scenario
test_scenario = "Test if the API can handle encrypted responses properly using AES-256 encryption."

# Combine the scenario and framework knowledge
prompt = f"""Given the following test scenario:\n{test_scenario}\n\nAnd the following related framework information:\n{context}\n\nGenerate a Java test case with the following structure:
- Include @Test annotation with iteration management.
- Use the methods correctly as per the scenario.
- Include iteration count handling (e.g., for loops, `checkIteration`, `updateDataSetReport`).
- Ensure proper test initialization and teardown using `TestStart()` and `TestEnd()`.
- Use methods like `navigateTo()` and `verifyElementIsDisplayed()` for navigation and validation.

Output the Java test code in the format required by our framework."""

# Initialize the LLaMA model using ChatOllama
local_llm = ChatOllama(
    model="llama3",
    base_url="http://localhost:11434",  # Replace with your local Ollama endpoint if different
    temperature=0.7  # Adjust temperature as needed for creativity vs. precision
)

# Send the prompt to the LLaMA model
response = local_llm([HumanMessage(content=prompt)])

# Print or store the generated test code
print("Generated Test Code:\n", response.content)



import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
embedding_model = OllamaEmbeddings(model="nomic-embed-text")
import os
from langchain.docstore.document import Document as lnDoc
from typing import List
 
def create_or_update_vector_db(stories):
    """Creates or updates the vector database based on the provided data."""
    pro = st.session_state.get("project")
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    index_name = f"{pro}_Database"
    document_objs = []
 
    if os.path.exists(index_name):
        print("DB found")
        # Load the existing vector store
        vector_db = FAISS.load_local(index_name, embeddings=embedding_model, allow_dangerous_deserialization=True)
       
        # # Add the new documents to the existing index
        # vector_db.add_documents(document_objs)
        existing_titles = get_existing_storys(vector_db)
    else:
        # Create a new vector store
        print("DB not found")
        # vector_db = FAISS.from_documents(document_objs, embedding=embedding_model)
        vector_db = None
        existing_titles = set()
   
   
    for doc in stories:
        if doc['title'] in existing_titles:
            continue
       
        document =  lnDoc(page_content = f"{doc['title']} - {doc['story']}", metadata={"title": doc['title']})
        document_objs.append(document)
 
    if document_objs:
        if vector_db is None:
            vector_db = FAISS.from_documents(document_objs, embedding=embedding_model)
        else:
            vector_db.add_documents(document_objs)
 
        vector_db.save_local(index_name)
 

 "Generated Test Code:
Based on your instructions, here is a Java code snippet that implements the given scenario. Please replace `{Dynamic Page Objects Initialization}`, `{Dynamic Test Data Retrieval}` and `{Dynamic Scenario Implementation}` with actual code based on your requirements. Also, ensure to import the necessary classes for each function in your test case.

```java
import baseClass.BaseClass;
import iSAFE.ApplicationKeywords;

public class TC_{TestClassName} extends ApplicationKeywords  {
    BaseClass obj;

    // Page object declarations based on relevant functions used
    loginLogoutPage_obj = null;
    customerPage_FOS_Revamp_obj = null;
    homePage_Admin_obj = null;
    customerPage_Admin_obj = null;

    public TC_{TestClassName}(BaseClass obj)  {
        super(obj);
        this.obj = obj;<｜begin▁of▁sentence｜>: loginLogoutPage_obj = new loginLogoutPage(obj);
        customerPage_FOS_Revamp_obj = new customerPage_FOS_Revamp(obj);
        homePage_Admin_obj = new homePage_Admin(obj);
        customerPage_Admin_obj = new customerPage_Admin(obj);
    }

    public void runScenario()  {
        try  {
            // Retrieve test data for each parameter from the data source
             String appURL_Fos = ""Your App URL"";
             String userName = ""Your Username"";
             String password = ""Your Password"";
             String dealerValue1 = ""Dealer Value 1"";
             String dealerValue2 = ""Dealer Value 2"";

            // Execute steps as outlined in the Current Scenario:
             loginLogoutPage_obj.loginToFOSApplication(appURL_Fos, userName, password);
             customerPage_FOS_Revamp_obj.selectCustomerTabs(""Accounts"");
             homePage_Admin_obj.enterValueInTableSearchAndClick(dealerValue1, dealerValue2);
             customerPage_Admin_obj.clickOnLink(""Details"");
             homePage_Admin_obj.selectOrDeselectCheckBoxInSetup(""Pennat Flag"", ""Select"");
implemented in separate classes and each class has a constructor to initialize its page objects. The test data is hard-coded for simplicity, but it can be retrieved from an external source or database as per your requirements. Please replace `{TestClassName}` with actual name of your test class."

"Generated Test Code:
Based on your instructions and requirements, here's a possible Java implementation of your test case. This is just an example and you might need to adjust it according to your actual class names, function signatures and data sources.

```java
import baseClass.BaseClass;
import iSAFE.ApplicationKeywords;

public class TC_DealerPennatFlag extends ApplicationKeywords {
    BaseClass obj;
    loginLogoutPage loginObj;
    customerPage_FOS_Revamp accountTabObj;
    homePage_Admin tableSearchObj;
    customerPage_Admin detailsObj;
    homePage_Admin editIconObj;
    homePage_Admin pennatFlagObj;
    homePage_Admin saveButtonObj;

    public TC_DealerPennatFlag(BaseClass obj) {
        super(obj);
        this.obj = obj;
        loginObj = new loginLogoutPage();
        accountTabObj = new customerPage_FOS_Revamp();
        tableSearchObj = new homePage_Admin();
        detailsObj = new customerPage_Admin();
        editIconObj = new homePage_Admin();
        pennatFlagObj = new homePage_Admin();
        saveButtonObj = new homePage_Admin();
    }

    public void runScenario() {
        try {
            // Retrieve test data for each parameter from the data source
            String appURL_Fos = ""yourAppUrl"";
            String userName = ""yourUsername"";
            String password = ""yourPassword"";
            String dealerValue1 = ""dealerValue1"";
            String dealerValue2 = ""dealerValue2"";

            // Execute steps as outlined in the Current Scenario:
            loginObj.loginToFOSApplication(appURL_Fos, userName, password);
            accountTabObj.selectCustomerTabs(""Accounts"");
            tableSearchObj.enterValueInTableSearchAndClick(dealerValue1, dealerValue2);
            detailsObj.clickOnLink(""Details"");
            editIconObj.selectOrDeselectCheckBoxInSetup(""Edit Icon"", ""Select"");
            pennatFlagObj.selectOrDeselectCheckBoxInSetup(""Pennat Flag"", ""Select"");
            saveButtonObj.clickOnSaveButton(""Save"");

        } catch (Exception e) {
            e<｜begin▁of▁sentence｜>hould be an actual exception, but I'm guessing that you want to print the stack trace for now.<｜end▁of▁sentence｜>
            < e.printStackTrace();
        }
    }
}
```
Please replace `""yourAppUrl""`, `""yourUsername""` and `""yourPassword""` with your actual data.

Also note that this is a very simplified example. In real-world scenarios, you might need to handle exceptions more gracefully (e.g., by retrying failed operations, logging the error instead of just printing it out, etc.), use explicit waits for elements to be present before interacting with them, and so on.

(myllama) D:\unsloth\Indium\project\BF1>"