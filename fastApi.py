from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional, List, Dict
from langchain_community.chat_models import ChatOllama
from fastapi.middleware.cors import CORSMiddleware

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
        # Extract the context
        context = contentText or url or ""

        # Define the distribution based on the selected difficulty
        distribution = {'Easy': 0, 'Medium': 0, 'Hard': 0}

        if difficulty == 'Easy':
            distribution['Easy'] = numOfQuestions
        elif difficulty == 'Medium':
            distribution['Medium'] = numOfQuestions
        elif difficulty == 'Hard':
            distribution['Hard'] = numOfQuestions

        selected_Qtype = [questionType]

        # Generate the prompt using the function
        prompt = generate_prompt_forQAGen(distribution, selected_Qtype, generateWithAnswers, context)

        # Log the generated prompt for debugging
        print("Generated Prompt:", prompt)

        # Initialize the model
        model_instance = ChatOllama(model=model, temperature=temperature)
        response = model_instance.invoke(prompt)

        # Return the formatted response
        return {"response": response.content if hasattr(response, 'content') else str(response)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



class LoginRequest(BaseModel):
    username: str
    password: str

# Hardcoded credentials
valid_username = "Indium"
valid_password = "Indium@123"

# Define a login route
@app.post("/login")
def login(request: LoginRequest):
    # Check if the provided credentials are correct
    if request.username == valid_username and request.password == valid_password:
        return {"message": "Login successful", "status": "success"}
    else:
        # Raise an HTTP exception if the credentials are incorrect
        raise HTTPException(status_code=401, detail="Invalid username or password")