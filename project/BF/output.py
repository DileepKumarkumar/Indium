import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.schema import HumanMessage
from langchain_ollama import ChatOllama

# Load FAISS index and metadata
index_path = "D:/unsloth/Indium/project/BF/faiss_index.index"  # Update with your index path
metadata_path = "D:/unsloth/Indium/project/BF/meradata.json"  # Update with your metadata path


# Load the index and metadata
index = faiss.read_index(index_path)
with open(metadata_path, "r") as f:
    metadata = json.load(f)

# Initialize model for encoding queries
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Query to search for
query = """
S.No : 1,  

Modules: Portal, 

Sub Module: Customer Rebate, 

User & Role: Customer, 

Priority: High,  

Test Case No: TRC_AT_TC_001,  

Test Case Description: o verify the user is able to create a Customer Rebate Account in the Portal,  

Pre-requisite: NA,  

Test Data: Account Number: 1150037 
	        Account Name: WILLS,  

S.No: 1,  

Test Steps,  

1, Launch the Chrome/Firefox/Edge Browser., 

2, Paste the URL - https://clientportal-qa.trcwebapps.com/#/home, 

3. Click on 'Create a new rebate account' link below the login panel., 

4. Click on 'Create a New Customer Rebate Account' link., 

5. Enter the given Account Number and Account Name., 

6. Fill up the other details., 

7. Click on 'Validate and Proceed' button., 

8. Click on 'Proceed' button., 

9. Enter the valid email address in the Email Address and Confirm Email Address fields., 

10. Enter the Password in the Password and Confirm Password fields., 

11. Click on the 'Proceed' button., 

12. Enter the confirmation code in the Enter the Confirmation Code field., 

13. Click on the 'Confirm Signup'., 

14. Click on the 'Proceed to Login' button., 

15. Enter the Username and Password in the Login Panel., 

16. Click on the 'Login' button., 

Expected Result 

1. The Browser should be launched. 

2. The Portal application should be opened. 

3. The Create a Rebate Account page should be displayed. 

4. The 'Create a New Customer Rebate Account' page should be displayed. 

5. The Account Number and Account Name should be entered. 

6.The other details should be entered. 

7.The "Account Validated Successfully' message should be displayed along with the 'Proceed' button. 

8.The User Registration tab should be displayed with prepopulated details in the First Name, Last Name and Phone Number. 

9. The Email address should be entered. 

10. The Password should be entered. 

11. The Confirmation code tab should be displayed 

12. The Code should be entered. 

13. The "Account Created Successfully' message should be displayed along with the 'Proceed to Login' button. 

14. The Login page should be displayed. 

15. The Credentials should be entered. 

16. The Home page should be displayed. 

 
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


print("Related methods:\n", context)

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
    model="deepseek-coder:6.7b",
    base_url="http://localhost:11434",  # Replace with your local Ollama endpoint if different
    temperature=0.7  # Adjust temperature as needed for creativity vs. precision
)

# Send the prompt to the LLaMA model
response = local_llm([HumanMessage(content=prompt)])

# Print or store the generated test code
print("Generated Test Code:\n", response.content)
