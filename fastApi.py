import base64
import re
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
import requests
from base64 import b64encode
import json
from fastapi import BackgroundTasks
import httpx
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage


app = FastAPI()



# CORS Configuration
orig_main = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=orig_main,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model for Login Request
class LoginRequest(BaseModel):
    username: str
    password: str

# Hardcoded credentials for demo
valid_username = "Indium"
valid_password = "Indium@123"

# Define login route
@app.post("/login")
def login(request: LoginRequest):
    if request.username == valid_username and request.password == valid_password:
        return {"message": "Login successful", "status": "success"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

# Request model for test case generation
class TestCaseRequest(BaseModel):
    selected_model: str
    content: str
    test_scenario: str
    temp: float

# Dictionary to define various test scenarios
test_scenario_dict = {
    'Functional': 'Functional test scenarios',
    'Exploratory': 'Exploratory test scenarios',
    'Performance': 'Performance test scenarios',
    'Security': 'Security test scenarios as per OWASP standards'
}

# Function to generate test cases based on the scenario and content
def generate_test_cases(model, content, test_scenario, temp):
    prompt = [
        {"role": "system", "content": "You are an Experienced Test Manager."},
        {"role": "user", "content": f"Write comprehensive {test_scenario} test scenarios for the following Acceptance Criteria: " + content},
        {"role": "user", "content": f"""Generate {test_scenario_dict[test_scenario]} with:
        1. Objective
        2. Gherkin scripts covering the following aspects:
            - User roles interacting with the system
            - Role-specific actions and behaviors
            - Validation of expected behavior under normal operating conditions
            - Simulation of error conditions, including validation errors, invalid inputs, or system failures."""}
    ]
    
    local_llm = ChatOllama(model=model, base_url="http://localhost:11434", temperature=temp)
    messages = [
        SystemMessage(content=prompt[0]["content"]),
        HumanMessage(content=prompt[1]["content"]),
        HumanMessage(content=prompt[2]["content"])
    ]
    
    response = local_llm.invoke(messages)
    return response.content

# API endpoint for generating test cases
@app.post("/generate-testcases")
def get_test_cases(request: TestCaseRequest):
    content = request.content
    model = request.selected_model
    temp = request.temp
    test_scenario = request.test_scenario
    
    # Generate Gherkin scripts and test cases
    zerkin_script = generate_test_cases(model, content, test_scenario, temp)
    return {"zerkinScript": zerkin_script}

# Function to generate a QA generation prompt
def generate_prompt_forQAGen(
    distribution: Dict[str, int],
    selected_Qtype: List[str],
    questionsWithAns: str,
    context: str
) -> str:
    query = """
    Based on the provided context, generate questions according to the following instructions. Each category must be addressed separately and in order.

    Context: {context}

    Generate questions in the following format, ensuring the exact number for each category is met:
    """

    for qtype in selected_Qtype:
        query += f"\n\t{qtype} :\n\n"
        for level in distribution.keys():
            if distribution.get(level, 0) > 0:
                query += f"""\t- Generate {distribution.get(level)} {level.lower()} level {qtype}
                            - Ensure you generate exactly {distribution.get(level)} questions, no more, no less.\n\n"""

    if questionsWithAns.upper() == "NO":
        query += "\n\tImportant: Do not provide answers to the questions.\n"
    else:
        query += "\n\tImportant: Provide answers to all questions.\n"

    query += """
    Additional Instructions:
    - Generate exactly the number of questions specified for each category and level.
    - Ensure questions cover different aspects of the content.
    - Maintain the categorization as shown above.
    - Do not skip any specified category or level.

    Begin generating questions now: generate the response exactly as mentioned in the prompt without fail.
    """
    return query.format(context=context)

@app.get('/')
def home():
    return {"message": "Welcome to the API!"}

@app.post("/query")
async def query_ollama(
    model: str = Form(...),
    temperature: float = Form(...),
    questionType: str = Form(...),
    numOfQuestions: int = Form(...),
    difficulty: str = Form(...),
    easyPercentage: int = Form(...),
    generateWithAnswers: str = Form(...),
    contentText: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    try:
        context = contentText or url or ""

        distribution = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        if difficulty == 'Easy':
            distribution['Easy'] = numOfQuestions
        elif difficulty == 'Medium':
            distribution['Medium'] = numOfQuestions
        elif difficulty == 'Hard':
            distribution['Hard'] = numOfQuestions

        selected_Qtype = [questionType]
        prompt = generate_prompt_forQAGen(distribution, selected_Qtype, generateWithAnswers, context)

        model_instance = ChatOllama(model=model, temperature=temperature)
        response = model_instance.invoke(prompt)

        return {"response": response.content if hasattr(response, 'content') else str(response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



"---------------------------------------------------------------------"
PAT = ""
ORG = "revathyb"
API_VERSION = "api-version=7.1"
BASE_URL = f"https://dev.azure.com/{ORG}"


class CriteriaRequest(BaseModel):
    user_story_ids: List[int]
    pat: str
    base_url: str
    api_version: str

def get_projects(organization_url, personal_access_token):
    """Fetch list of projects available in the organization."""
    credentials = f":{personal_access_token}"
    credentials_encoded = b64encode(credentials.encode()).decode("ascii")
    headers = {
        "Authorization": f"Basic {credentials_encoded}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f'{organization_url}/_apis/projects',
        headers=headers
    )

    if response.status_code == 200:
        projects = response.json()
        return [project['name'] for project in projects['value']]
    else:
        print(f"Error fetching projects: {response.status_code} - {response.json()}")
        raise HTTPException(status_code=response.status_code, detail=response.json())


@app.get("/projects")
async def fetch_projects():
    """Endpoint to get projects from Azure DevOps."""
    try:
        base_url = f"https://dev.azure.com/{ORG}"
        projects = get_projects(base_url, PAT)
        return {"projects": projects}
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail=str(e))




def get_user_stories(organization_url, personal_access_token, query_params, project_name):
    """This method will return user stories that are present in Azure DevOps."""
    credentials = f":{personal_access_token}"
    credentials_encoded = b64encode(credentials.encode()).decode("ascii")
    headers = {
        "Authorization": f"Basic {credentials_encoded}",
        "Content-Type": "application/json"
    }

    wiql_query = {
        "query": f"Select [System.Id], [System.Title], [System.State] From WorkItems Where [System.WorkItemType] = 'User Story' And [System.TeamProject] = '{project_name}' Order By [System.Id]"
    }

    # Construct the API endpoint for user stories
    api_url = f"{organization_url}/_apis/wit/wiql?{query_params}"

    # Send the POST request with authentication
    response = requests.post(api_url, headers=headers, json=wiql_query)

    user_stories = []
    work_item_ids = []

    if response.status_code == 200:
        work_items = response.json()
        work_item_ids = [item['id'] for item in work_items['workItems']]
        
        if work_item_ids:
            work_items_response = requests.get(
                f'{organization_url}/_apis/wit/workitems?ids={",".join(map(str, work_item_ids))}&{query_params}',
                headers=headers
            )

            if work_items_response.status_code == 200:
                work_items_details = work_items_response.json()
                for work_item in work_items_details['value']:
                    work_item_with_title = f"ID: {work_item['id']}, Title: {work_item['fields']['System.Title']}"
                    user_stories.append(work_item_with_title)
            else:
                raise HTTPException(status_code=work_items_response.status_code, detail="Error fetching work item details.")
        else:
            raise HTTPException(status_code=404, detail="No user stories found.")
    else:
        raise HTTPException(status_code=response.status_code, detail="Error executing WIQL query.")
    return user_stories

@app.get("/user-stories/{project_name}")
async def fetch_user_stories(project_name: str):
    """Endpoint to get user stories from Azure DevOps."""
    try:
        base_url = f"https://dev.azure.com/{ORG}"
        query_params = "api-version=7.1"  # Adjust as needed
        user_stories = get_user_stories(base_url, PAT, query_params, project_name)
        return {"user_stories": user_stories}
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail=str(e))

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

async def fetch_work_item_details(work_item_id, pat, base_url, api_version):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {base64.b64encode(f":{pat}".encode()).decode()}'
    }

    url = f"{base_url}/_apis/wit/workitems/{work_item_id}?api-version={api_version}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching work item {work_item_id}: {response.status_code} - {response.text}")
            raise Exception(f"Error {response.status_code}: {response.text}")

        return response.json()

# FastAPI endpoint to fetch acceptance criteria

@app.post("/acceptance-criteria")
async def get_acceptance_criteria(criteria: CriteriaRequest):
    descriptions = []
    acceptance_criterias = []

    for work_item_id in criteria.user_story_ids:
        try:
            # Fetch work item details from Azure DevOps
            work_item_details = await fetch_work_item_details(work_item_id, criteria.pat, criteria.base_url, criteria.api_version)
            
            # Access the fields from the fetched work item details
            fields = work_item_details.get('fields', {})
            description = fields.get('System.Description', 'No description available.')
            acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', 'No acceptance criteria available.')

            descriptions.append(remove_html_tags(description))
            acceptance_criterias.append(remove_html_tags(acceptance_criteria))
        except Exception as e:
            print(f"Error fetching work item {work_item_id}: {str(e)}")
            return {"error": f"Failed to retrieve work item: {work_item_id}"}

    return {"descriptions": descriptions, "acceptance_criterias": acceptance_criterias}




"-----------------------------------------------------------------------------------------------"

class TestCaseRequest(BaseModel):
    plain_text: str
    key: str
    value: str
    selected_model: str
    temperature: float


def complete_chat(api_key, conversation, temp):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": conversation,
        "temperature": temp
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None    

 
 
def generate_test_cases_openai(plain_text, api_key, key, value, temp):
    conversation_example = [
        {"role": "system", "content": "You are an Experienced Test Manager."},
        {"role": "user", "content": f"Write comprehensive {key} test scenarios for the following Acceptance Criteria: " + plain_text},
        {"role": "user", "content": f"""Generate {value} test scenarios with:
            1. Objective
            2. Gherkin scripts covering the following aspects:
                - User roles interacting with the system
                - Role-specific actions and behaviors
                - Validation of expected behavior under normal operating conditions
                - Successful completion of common tasks or interactions without encountering errors
                - Simulation of error conditions or unexpected user inputs, including validation errors, invalid inputs, or system failures, and verification of appropriate system responses
                - Exploration of boundary conditions or limits of system functionality, including inputs at the minimum, maximum, or beyond typical ranges, and verification of correct system behavior."""}
    ]
    response = complete_chat(api_key, conversation_example, temp)
    if response:
        airecommendation = response['choices'][0]['message']['content']

        print(airecommendation)

        conversation_testcase = [
            {"role": "system", "content": "You are an Experienced Test Manager."},
            {"role": "user", "content": "Write test cases for each scenario: " + airecommendation},
            {"role": "user", "content": """Generate test cases for each scenario with the format: 
            1. Scenario Objective 
            2. Clear Test Steps with pre-requisites 
            3. Expected Results"""}
        ]
        response = complete_chat(api_key, conversation_testcase, temp)
        if response:
            testcases = response['choices'][0]['message']['content']
            return airecommendation, testcases
    return None, None



def generate_testCases_ByOllama(plain_text, key, value, selected_model, temp):
    pmpt = [
        {"role": "system", "content": "You are an experienced Test Manager responsible for creating comprehensive and high-coverage test scenarios."},
        {"role": "user", "content": f"Generate detailed {key} test scenarios based on the following Acceptance Criteria: " + plain_text},
        {"role": "user", "content": f"""For each test scenario, ensure the following:
        1. **Test Objective**: Clearly describe the purpose of the test.
        2. **Gherkin-style Scripts**: Write Gherkin scripts (Given, When, Then) that cover these areas:
            - **User Roles and Interactions**: Identify the user roles interacting with the system and their respective actions.
            - **Role-Specific Actions**: Define the specific actions and behaviors expected for each role.
            - **Validation of Expected Behaviors**: Validate normal operations and confirm successful task completion without errors.
            - **Error and Exception Handling**: Simulate error conditions, unexpected inputs, and system failures. Ensure validation of error handling, including incorrect inputs and boundary cases.
            - **Boundary Conditions**: Explore edge cases by testing inputs at minimum, maximum, and outside typical ranges to validate system behavior.
            - **Usability and Performance**: Assess usability aspects, including user experience, and evaluate performance and load handling where relevant.
        
         Ensure that the generated {value} test scenarios provide thorough coverage, covering both positive and negative cases, edge conditions, and exceptional circumstances. Increase the scope to cover all potential interactions and system behavior validations.
         """}
    ]

    local_llm = ChatOllama(
        model=selected_model,
        base_url="http://localhost:11434",
        temperature=temp
    )

    # Send the first set of prompts
    messages = [
        SystemMessage(content=pmpt[0]["content"]),
        HumanMessage(content=pmpt[1]["content"]),
        HumanMessage(content=pmpt[2]["content"])
    ]
    
    # Generate Gherkin scripts
    response = local_llm.invoke(messages)
    zerkinScript = response.content

    # Prepare the test case prompt
    testCases_prompt = [
        {"role": "system", "content": "You are an Experienced Test Manager."},
        {"role": "user", "content": "write Testcases for each scenario: " + zerkinScript},
        {"role": "user", "content": """Generate a test cases for each scenario with the format:  1.Scenario Objective 2.Clear Test Steps with pre-requisites 3.Expected Results Template:
            1. Objective:
            - State the objective of the test scenario, focusing on the specific functionality being tested.
    
            2. Test Steps with Pre-requisites:
            - List the sequential steps to execute the test scenario, along with any pre-requisites necessary for the test.
                1. Step 1: [Describe the action or input to be performed and also Specify any necessary pre-conditions if required]
                    
                2. Step 2: [Describe the action or input to be performed and also Specify any necessary pre-conditions if required]
                    
                3. Step 3: [Describe the action or input to be performed and also Specify any necessary pre-conditions if required]
        
                [Continue with additional steps as needed]
    
        3. Expected Results:
        - Define the expected outcomes or behaviors resulting from the execution of the test steps.
            - Expected Result 1: [Describe the expected outcome or behavior]
            - Expected Result 2: [Describe the expected outcome or behavior]
                [Continue with additional expected results as needed]"""}
    ]
    
    # Send the second set of prompts to generate test cases
    messages1 = [
        SystemMessage(content=testCases_prompt[0]["content"]),
        HumanMessage(content=testCases_prompt[1]["content"]),
        HumanMessage(content=testCases_prompt[2]["content"])
    ]

    response1 = local_llm.invoke(messages1)
    testcases = response1.content

    return zerkinScript, testcases

@app.post("/generate-test-cases")
async def generate_test_cases(request: TestCaseRequest):
    try:
        if request.selected_model.lower() == "openai":
            # OpenAI implementation
            api_key = "your_openai_api_key_here"  # Ensure you set your OpenAI API key
            gherkin_script, testcases = generate_test_cases_openai(
                plain_text=request.plain_text,
                api_key=api_key,
                key=request.key,
                value=request.value,
                temp=request.temperature
            )
        else:
            # Ollama implementation
            gherkin_script, testcases = generate_testCases_ByOllama(
                plain_text=request.plain_text,
                key=request.key,
                value=request.value,
                selected_model=request.selected_model,
                temp=request.temperature
            )
        
        if gherkin_script and testcases:
            return {"gherkin_script": gherkin_script, "test_cases": testcases}
        else:
            raise HTTPException(status_code=500, detail="Failed to generate test cases.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")