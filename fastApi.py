from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
from fastapi.middleware.cors import CORSMiddleware
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
