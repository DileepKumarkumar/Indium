ADO interface Code:
 
import streamlit as st
from Devops import *
from PIL import Image
 
fav = Image.open("indFav.PNG")
st.set_page_config(page_title="ADO", page_icon = fav, layout="wide")
 
# Initialize state variables
if "org" not in st.session_state:
    st.session_state["org"] = "revathyb"
if "api_version" not in st.session_state:
    st.session_state["api_version"] = "api-version=7.1"
if "project" not in st.session_state:
    st.session_state["project"] = None
if "selected_user_stories" not in st.session_state:
    st.session_state["selected_user_stories"] = None
if "acceptance_criterias" not in st.session_state:
    st.session_state["acceptance_criterias"] = None
# if "formatted_criteria" not in st.session_state:
#     st.session_state["formatted_criteria_list"] = []
if "test_case_scenarios" not in st.session_state:
    st.session_state["test_case_scenarios"] = "Functional"
if "test_cases_list" not in st.session_state:
    st.session_state["test_cases"] = None
if "airecommendation_list" not in st.session_state:
    st.session_state["airecommendation_list"] = None
if "Cretivity" not in st.session_state:
    st.session_state["Cretivity"] = None
if "Selected_model" not in st.session_state:
    st.session_state['Selected_model'] = "OpenAI"
 
if "Selected_format" not in st.session_state:
    st.session_state["Selected_format"] = "Gherkin Format"
 
 
 
# Sidebar controls
org = st.sidebar.selectbox("Select The Organization:", ["revathyb"])
api_version = st.sidebar.selectbox("API Version:", ["api-version=7.1", "api-version=6.0"])
base_url = f"https://dev.azure.com/{org}"
 
pat = ""
st.session_state["org"] = org
st.session_state["api_version"] = api_version
 
project_options = get_projects(base_url, pat, api_version)
project = st.sidebar.selectbox("Project Name:", project_options)
st.session_state["project"] = project
 
user_stories_opts, user_stories_ids = get_user_stories(base_url, pat, api_version, project)
selected_user_stories = st.sidebar.multiselect("Select the User Story:", user_stories_opts)
mode_temperature = 0.3
if st.session_state["selected_user_stories"] != selected_user_stories or st.session_state["Cretivity"] != mode_temperature:
    if "setup" in st.session_state:
        del st.session_state["setup"]
st.session_state["selected_user_stories"] = selected_user_stories
 
st.sidebar.divider()
selected_model = st.sidebar.selectbox("Select The Model:",['OpenAI','mistral','llama3','llama3.1'])
st.session_state['Selected_model'] = selected_model
 
def format_func(value):
    labels = {
        0.0: "Less Creativity",
        0.1: "Very Low Creativity",
        0.2: "Low Creativity",
        0.3: "Slightly Low Creativity",
        0.4: "Moderate Creativity",
        0.5: "Average Creativity",
        0.6: "Above Average Creativity",
        0.7: "Slightly High Creativity",
        0.8: "High Creativity",
        0.9: "Very High Creativity",
        1.0: "Max Creativity"
    }
    return labels.get(value, f"{value:.1f}")
 
 
mode_temperature = st.sidebar.slider('Set The Creativity Level:', 0.0, 1.0, 0.3, 0.1)
 
st.session_state["Cretivity"] = mode_temperature
# Display the custom label based on the slider value
st.sidebar.write('Creativity Level:', format_func(mode_temperature))
 
test_case_scenarios = st.sidebar.selectbox("Select The Test Scenarios:", ["Functional", "Exploratory", "Performance", "Security"])
st.session_state["test_case_scenarios"] = test_case_scenarios
 
st.sidebar.divider()
 
# selected_story_index = user_stories_opts.index(selected_user_stories)
selected_story_indexes = [index for index, element in enumerate(user_stories_opts) if element in selected_user_stories]
# selected_story_id = user_stories_ids[selected_story_index]
selected_story_ids = [user_stories_ids[ind] for ind in selected_story_indexes]
base_url_work_items = f"{base_url}/_apis/wit/workitems/"
 
if st.button("Fetch Acceptance Criteria"):
    descriptions = get_description(pat, selected_story_ids, base_url_work_items, api_version)
    acceptance_criterias = get_acceptance_criterias(pat, selected_story_ids, base_url_work_items, api_version)
    if len(acceptance_criterias)!=0:
        st.session_state["acceptance_criterias"] = acceptance_criterias
        formatted_criteria_list =[]
        for description, acceptance_criteria in zip(descriptions, acceptance_criterias):
            plain_text_of_DC = remove_html_tags(description)
            plain_text_of_AC = remove_html_tags(acceptance_criteria)
            formatted_criteria_of_DC = plain_text_of_DC.replace("&nbsp;", " ").replace("\n", "<br>")
            formatted_criteria_of_AC = plain_text_of_AC.replace("&nbsp;", " ").replace("\n", "<br>")
            # st.session_state["formatted_criteria"] = formatted_criteria
            formatted_criteria = formatted_criteria_of_DC+"\n"+formatted_criteria_of_AC
            formatted_criteria_list.append(formatted_criteria)
 
        # print(formatted_criteria_list)  
        st.session_state["formatted_criteria_list"] = formatted_criteria_list
 
        for id, criteria in zip(selected_story_ids,formatted_criteria_list):
            st.info(f"### Acceptance Criteria For User Story Id: {id}")
            st.markdown(criteria, unsafe_allow_html=True)
       
        st.session_state["setup"] = True
    else:
        st.write("No acceptance criteria found for the selected user story.")
 
 
if "setup" in st.session_state:
 
    if st.button("Generate Test Cases"):
        formatted_criteria_list = st.session_state["formatted_criteria_list"]
        # print("------------------------")
        # print(formatted_criteria_list)
        # print("------------------------")
        # if formatted_criteria_list is not None:
        # print("formatted criteria list!!")
        api_key = ''
       
        my_dict = {
            'Functional': 'Functional test scenarios',
            'Exploratory': 'Exploratory test scenarios',
            'Performance': 'Performance test scenarios',
            'Security': 'Security test scenarios as per OWASP standards'
        }
 
        airecommendation_list = []
        test_cases_list = []
        if selected_model == "OpenAI":
            for formatted_criteria in formatted_criteria_list:
                airecommendation, test_cases = generate_test_cases(formatted_criteria, api_key, test_case_scenarios,my_dict.get(test_case_scenarios), mode_temperature)
                airecommendation_list.append(airecommendation)
                test_cases_list.append(test_cases)
       
        else:
            for formatted_criteria in formatted_criteria_list:
                airecommendation, test_cases = generate_testCases_ByOllama(formatted_criteria, test_case_scenarios,my_dict.get(test_case_scenarios), selected_model, mode_temperature)
               
                airecommendation_list.append(airecommendation)
                test_cases_list.append(test_cases)
 
        st.session_state["test_cases_list"] = test_cases_list
        st.session_state["airecommendation_list"] = airecommendation_list
 
        for id, airecommendation, test_cases in zip(selected_story_ids, airecommendation_list,test_cases_list):
            st.info(f"### Test Case Scenarios For User Story Id: {id}")
            st.markdown(airecommendation, unsafe_allow_html=True)
            st.info(f"### Test Cases For User Story Id: {id}")
            st.markdown(test_cases, unsafe_allow_html=True)
   
    selected_format = st.sidebar.selectbox("Select The Format For Update:",["Gherkin Format","Text Format"])
   
    if st.button("Update ADO"):
       
        if selected_format:
           
            if st.session_state["Selected_format"] != selected_format:
                if "updateSetup" in st.session_state:
                    del st.session_state["updateSetup"]
       
            st.session_state["Selected_format"] = selected_format
 
            if "updateSetup" not in st.session_state:
                if st.session_state["Selected_format"] == "Gherkin Format":
                    updatedData = st.session_state.get("airecommendation_list")
                else:
                    updatedData = st.session_state.get("test_cases_list")
                # test_cases_list = st.session_state.get("test_cases_list")
                if len(updatedData)!=0:
                    update_response = creatOrUpdatingTestScenarios(pat, base_url_work_items, selected_story_ids, test_case_scenarios, updatedData, api_version)
                    if update_response:
                        st.success("Test Cases Updated Successfully!!😃")
                    else:
                        st.error("Failed To Update Test Cases!!😢")
 
    testUrl = st.sidebar.text_input("Enter Test URL:")
    if st.sidebar.button("Generate Selenium Code"):
        if selected_model == "OpenAI":
            api_key = ''
            seleniumcode = generateSeleniumCode(st.session_state.get("airecommendation_list"), testUrl, api_key, mode_temperature)
            st.session_state["seleniumcode"] = seleniumcode
            for code in seleniumcode:
                st.code(code)
        else:
            seleniumcode = generateSeleniumCode_ByOllama(st.session_state.get("airecommendation_list"), testUrl, selected_model, mode_temperature)
            st.session_state["seleniumcode"] = seleniumcode
            for code in seleniumcode:
                st.code(code)

Azure DevOps Services | Microsoft Azure
Plan smarter, collaborate better, and ship faster with Azure DevOps Services, formerly known as Visual Studio Team Services. Get agile tools, CI/CD, and more.
 
Devops.py code: 
 
import requests
import json
from base64 import b64encode
import re
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
import unittest
import pytest
import time
 
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
 
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# import time
 
def get_projects(organization_url,personal_access_token,query_params):
    """This method will return list of projects which are available in the organization"""
    credentials = f":{personal_access_token}"
    credentials_encoded = b64encode(credentials.encode()).decode("ascii")
    headers = {
        "Authorization": f"Basic {credentials_encoded}",
        "Content-Type": "application/json"
    }
 
    response = requests.get(
        f'{organization_url}/_apis/projects?{query_params}',
        headers=headers
    )
    list_of_projects =[]
    if response.status_code == 200:
        projects = response.json()
        for project in projects['value']:
            # print(f"ID: {project['id']}, Name: {project['name']}, State: {project['state']}")
            list_of_projects.append(f"{project['name']}")
    else:
        print(f"Error fetching projects: {response.status_code}")
        print(response.json())
   
    return list_of_projects
 
 
def get_user_stories(organization_url,personal_access_token,query_params,project_name):
    """This medthod will return user stories that are present in Azure Devops"""
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
 
    # Send the GET request with authentication
    response = requests.post(api_url, headers=headers,json=wiql_query)
 
    user_stories = []
 
    if response.status_code == 200:
        work_items = response.json()
        # print("\n-----------------------------")
        # print(work_items)
        # print("------------------------------\n")
        work_item_ids = [item['id'] for item in work_items['workItems']]
        print(work_item_ids)
        if work_item_ids:
            work_items_response = requests.get(
                f'{organization_url}/_apis/wit/workitems?ids={",".join(map(str, work_item_ids))}&{query_params}',
                headers=headers
            )
 
            if work_items_response.status_code == 200:
                work_items_details = work_items_response.json()
                for work_item in work_items_details['value']:
                    work_item_with_title = f"ID: {work_item['id']}, Title: {work_item['fields']['System.Title']}"
                    # print(work_item_with_title)
                    user_stories.append(work_item_with_title)
            else:
                print(f"Error fetching work item details: {work_items_response.status_code}")
        else:
            print("No user stories found.")
    else:
        print(f"Error executing WIQL query: {response.status_code}")
   
    return user_stories, work_item_ids
 
def get_description(personal_access_token,work_item_ids, base_url_work_items, api_version):
    credentials = f":{personal_access_token}"
    credentials_encoded = b64encode(credentials.encode()).decode("ascii")
    headers = {
        "Authorization": f"Basic {credentials_encoded}",
        "Content-Type": "application/json"
    }
    descriptionsList = []
    for work_item_id in work_item_ids:
        work_item_url = f"{base_url_work_items}/{work_item_id}?"
        query_params = api_version
        response = requests.get(work_item_url, headers=headers, params=query_params)
        if response.status_code == 200:
            work_item_details = response.json()
            # description = work_item_details['fields']['Microsoft.VSTS.Common.Description']
            fields = work_item_details.get('fields', {})
            # print(fields)
            description = fields.get('System.Description', 'No description available.')
            # print("\n"+description)
            descriptionsList.append(description)
           
        else:
            print(f"Failed to retrieve details for Work Item ID: {work_item_id}. Status code: {response.status_code}")
   
    return descriptionsList
 
 
def get_acceptance_criterias(personal_access_token,work_item_ids, base_url_work_items, api_version):
    credentials = f":{personal_access_token}"
    credentials_encoded = b64encode(credentials.encode()).decode("ascii")
    headers = {
        "Authorization": f"Basic {credentials_encoded}",
        "Content-Type": "application/json"
    }
 
    # Iterate through each work item ID and fetch its details
    acceptance_criterias = []
    for work_item_id in work_item_ids:
        work_item_url = f"{base_url_work_items}/{work_item_id}?"
        query_params = api_version
        response = requests.get(work_item_url, headers=headers, params=query_params)
       
        if response.status_code == 200:
            work_item_details = response.json()
            acceptance_criteria = work_item_details['fields']['Microsoft.VSTS.Common.AcceptanceCriteria']
            fields = work_item_details.get('fields', {})
           
            acceptance_criterias.append(acceptance_criteria)
           
        else:
            print(f"Failed to retrieve details for Work Item ID: {work_item_id}. Status code: {response.status_code}")
   
    return acceptance_criterias
 
def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
 
 
def complete_chat(api_key, conversation, temp):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }
    payload = {
    "model": "gpt-3.5-turbo",  
    "messages": conversation,
    "temperature": temp  # Add the temperature parameter here
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
 
 
def generate_test_cases(plain_text, api_key,key,value, temp):
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
            - Exploration of boundary conditions or limits of system functionality, including inputs at the minimum, maximum, or beyond typical ranges, and verification of correct system behavior."""
    }
    ]
    response = complete_chat(api_key, conversation_example,temp)
    if response:
        airecommendation = response['choices'][0]['message']['content']
        #print(airecommendation)
      #  result = Itereatechat(org,pat,project,api_version,airecommendation,key)
    conversation_testcase = [
    {"role": "system", "content": "You are a Experienced Test Manager."},
    {"role": "user", "content": "write a Testcases for each  scenarios: " + airecommendation},
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
    response = complete_chat(api_key, conversation_testcase,temp)
    if response:
        testcase = response['choices'][0]['message']['content']
   
    return airecommendation, testcase
   
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
           
    Ensure that the generated {value} test scenarios provide thorough coverage, covering both positive and negative cases, edge conditions, and exceptional circumstances. Increase the scope to cover all potential interactions and system behavior validations."""
    }
   ]
 
 
    local_llm = ChatOllama(
            model = selected_model,
            base_url = "http://localhost:11434",
            temperature = temp)
   
    messages = [
        SystemMessage(content=pmpt[0]["content"]),
        HumanMessage(content=pmpt[1]["content"]),
        HumanMessage(content=pmpt[2]["content"])
    ]
 
    # Generate the response
    response = local_llm.invoke(messages)
 
    # Print the response
    # print(response.content)
    zerkinScript = response.content
   
    testCases_prompt = [
    {"role": "system", "content": "You are a Experienced Test Manager."},
    {"role": "user", "content": "write a Testcases for each  scenarios: " + zerkinScript},
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
 
    messages1 = [
        SystemMessage(content=testCases_prompt[0]["content"]),
        HumanMessage(content=testCases_prompt[1]["content"]),
        HumanMessage(content=testCases_prompt[2]["content"])
    ]
    # Generate the response
    response1 = local_llm.invoke(messages1) #uncomment this for test case generation
    # Print the response
    # print(response1.content)
    testcases = response1.content
 
    return zerkinScript ,testcases
 
def generate_json_data(custom_field, airecommendation):
    if custom_field == "Security":
        data = [
            {
                "op": "replace",
                "path": "/fields/Custom.SecurityTestScenarios",
                "value": airecommendation.replace("\n", "<br>").replace("*", "")
            }
        ]
    else:
        data = [
            {
                "op": "replace",
                "path": "/fields/Custom.FunctionalTestScenarios",
                "value": airecommendation.replace("\n", "<br>").replace("*", "")
            }
        ]
    return json.dumps(data)
 
 
def creatOrUpdatingTestScenarios(personal_access_token, base_url, work_item_ids, test_case_scenario, testCasesList, api_version):
    credentials = f":{personal_access_token}"
    credentials_encoded = b64encode(credentials.encode()).decode("ascii")
    headers = {
        "Authorization": f"Basic {credentials_encoded}",
        "Content-Type": "application/json-patch+json"
    }
    print(work_item_ids)
    all_updates_successful = True
 
    for workId, testCases in zip(work_item_ids,testCasesList):
        json_data = generate_json_data(test_case_scenario, testCases)
        print(f"Updating work item ID {workId} with scenario {test_case_scenario}")
        url = f"{base_url}/{workId}?{api_version}"
        response = requests.patch(url, headers=headers, data=json_data)
       
        print(f"HTTP Status Code for Work Item ID {workId}: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"Error response: {response.json()}")
            all_updates_successful = False
 
    return all_updates_successful
 
def generateSeleniumCode(gherkin_script_list, test_url, api_key, temp):
    javacodelist =[]
    for gherkin_script in gherkin_script_list:

        prompt = [
        {"role": "system", "content": "You are an Experienced Test Manager."},
        {"role": "user", "content": f"Generate Selenium test code based on the following Gherkin script and test URL, Do not include any code block markers like ```python or ``` in your response code. Ensure that the code is plain text"},
        {"role": "user", "content": f"""
            Test URL: {test_url}
 
            {gherkin_script}
 
            Generate Python Selenium code that:
            1. Includes setup and teardown methods for WebDriver initialization and cleanup.
            2. Identifies the necessary web elements using appropriate locators (id, name, class, xpath, etc.).
            3. Interacts with the elements using WebDriver methods like `send_keys` and `click`.
            4. Uses assertions to validate expected outcomes.
            5. Contains comments explaining each step for clarity.
           
        """}
        ]
 
        response = complete_chat(api_key, prompt,temp)
        # st.write(response)
        if response:
            seleniumcode = response['choices'][0]['message']['content']
            javacodelist.append(seleniumcode)
 
       
    return javacodelist
 
def generateSeleniumCode_ByOllama(gherkin_script_list, test_url, selected_model, temp):
    javacodelist =[]
    for gherkin_script in gherkin_script_list:
       
        prompt = [
        {"role": "system", "content": "You are an Experienced Test Manager."},
        {"role": "user", "content": f"Generate Selenium test code based on the following Gherkin script and test URL, Do not include any code block markers like ```python or ``` in your response code. Ensure that the code is plain text"},
        {"role": "user", "content": f"""
            Test URL: {test_url}
 
            {gherkin_script}
 
            Generate Python Selenium code that:
            1. Includes setup and teardown methods for WebDriver initialization and cleanup.
            2. Identifies the necessary web elements using appropriate locators (id, name, class, xpath, etc.).
            3. Interacts with the elements using WebDriver methods like `send_keys` and `click`.
            4. Uses assertions to validate expected outcomes.
            5. Contains comments explaining each step for clarity.
           
        """}
        ]
 
        local_llm = ChatOllama(
            model = selected_model,
            base_url = "http://localhost:11434",
            temperature = temp)
   
        messages = [
            SystemMessage(content=prompt[0]["content"]),
            HumanMessage(content=prompt[1]["content"]),
            HumanMessage(content=prompt[2]["content"])
        ]
 
        # Generate the response
        response = local_llm.invoke(messages)
 
        if response:
            seleniumcode = response.content
            javacodelist.append(seleniumcode)
 
       
    return javacodelist
 
def execute_selenium_code(code_str, url):
    try:
        # Define the local scope dictionary to pass URL and capture variables
        local_scope = {"url": url}
        code_str = """path = "C:\\drivers\\chromedriver.exe" \n""" + code_str
        print(code_str)
       
        # Executing the passed code string in the local scope
        exec(code_str, globals(), local_scope)
       
        # Capture any outputs or results from the local scope if needed
        result = local_scope.get("result", "No result returned")
       
        return result
    except Exception as e:
        return f"An error occurred: {e}"
 
def get_selenium_code():
   
 return """
# Scenario 1
service = ChromeService(executable_path=path)
driver = webdriver.Chrome(service=service)
driver.maximize_window()
try:
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 0);")
 
    time.sleep(4)
    input_Form = driver.find_element(By.XPATH, "//div[@id='navbar-brand-centered']//ul//li//a[contains(text(),'Input Forms')]")
    input_Form.click()
    time.sleep(4)
 
    simple_Form = driver.find_element(By.XPATH, "//ul[@class='dropdown-menu']//a[text()='Simple Form Demo']")
    simple_Form.click()
    time.sleep(4)
 
    header_Msg = driver.find_element(By.XPATH, '//h3')
    single_input = driver.find_element(By.XPATH, "//div[text()='Single Input Field']")
    two_input = driver.find_element(By.XPATH, "//div[text()='Two Input Fields']")
    time.sleep(4)
 
    assert (header_Msg.is_displayed()) & (header_Msg.text == "This would be your first example to start with Selenium."), "Header Msg not displaying as expected"
    print("Header Msg is displaying as expected")
    assert single_input.is_displayed(), "Single input field not displaying as expected"
    print("Single input field is displaying as expected")
    assert two_input.is_displayed(), "Two input fields not displaying as expected"
    print("Two input fields is displaying as expected")
 
except AssertionError as e:
    print(f"Assertion Error: {e}")
 
finally:
    driver.quit()
 
# Scenario 2
service = ChromeService(executable_path=path)
driver = webdriver.Chrome(service=service)
driver.maximize_window()
try:
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 0);")
 
    time.sleep(4)
    input_Form = driver.find_element(By.XPATH, "//div[@id='navbar-brand-centered']//ul//li//a[contains(text(),'Input Forms')]")
    input_Form.click()
    time.sleep(4)
 
    simple_Form = driver.find_element(By.XPATH, "//ul[@class='dropdown-menu']//a[text()='Simple Form Demo']")
    simple_Form.click()
    time.sleep(4)
 
    single_input = driver.find_element(By.XPATH, "//div[text()='Single Input Field']")
    time.sleep(4)
    assert single_input.is_displayed(), "Single input field not displaying as expected"
    print("Single input field is displaying as expected")
 
    single = driver.find_element(By.XPATH, "//input[@id='user-message']")
    input_Text = "Hello World"
    single.send_keys(input_Text)
    time.sleep(2)
    show_Msg = driver.find_element(By.XPATH, "//button[text()='Show Message']")
    show_Msg.click()
    time.sleep(2)
 
    msg = driver.find_element(By.XPATH, "//label[text()='Your Message: ']//following-sibling::span")
    assert msg.text == input_Text, "Entered message not displaying as Expected"
    print("Entered message displaying as Expected")
 
except AssertionError as e:
    print(f"Assertion Error: {e}")
 
finally:
    driver.quit()
 
# Scenario 3
service = ChromeService(executable_path=path)
driver = webdriver.Chrome(service=service)
driver.maximize_window()
try:
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 0);")
 
    time.sleep(4)
    input_Form = driver.find_element(By.XPATH, "//div[@id='navbar-brand-centered']//ul//li//a[contains(text(),'Input Forms')]")
    input_Form.click()
    time.sleep(4)
 
    simple_Form = driver.find_element(By.XPATH, "//ul[@class='dropdown-menu']//a[text()='Simple Form Demo']")
    simple_Form.click()
    time.sleep(4)
 
    two_input = driver.find_element(By.XPATH, "//div[text()='Two Input Fields']")
    time.sleep(4)
    assert two_input.is_displayed(), "Two input field not displaying as expected"
    print("Two input field is displaying as expected")
 
    val_1 = 370
    val_2 = 580
    two_input_text1 = driver.find_element(By.XPATH, "//input[@id='value1']")
    two_input_text2 = driver.find_element(By.XPATH, "//input[@id='value2']")
 
    two_input_text1.send_keys(str(val_1))
    time.sleep(2)
 
    two_input_text2.send_keys(str(val_2))
    time.sleep(2)
 
    get_Total = driver.find_element(By.XPATH, "//button[text()='Get Total']")
    get_Total.click()
    time.sleep(2)
 
    msg_Total = driver.find_element(By.XPATH, "//label[text()=' Total a + b = ']//following-sibling::span")
    print(f"Expected : {val_1 + val_2}")
    print(f"Actual : {msg_Total.text}")
    assert msg_Total.text == str(val_1 + val_2), "Sum of the input values displaying below the button not as expected"
    print("sum of the input values display in below the button as Expected")
 
except AssertionError as e:
    print(f"Assertion Error: {e}")
finally:
    driver.quit()

TestCaseGenerator: 
 
import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from PIL import Image
# from langchain.docstore.document import Document
import hashlib
 
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
 
fav = Image.open("indFav.PNG")
st.set_page_config(page_title="AI-TCGen", page_icon = fav, layout="wide")
 
st.markdown("""<style>
#ai-tcgen {
        text-align: center;
        # background-color: #EBEBEB;
    }
</style>""",unsafe_allow_html=True)
 
st.title("AI-TCGen")
 
model_options = ["mistral", "llama3","llama3.1"]
selected_model = st.sidebar.selectbox("Select the Model: ", model_options)
temp = st.sidebar.slider('Set The Creativity Level:', 0.0, 1.0, 0.5, 0.1)
 
def format_func(value):
    labels = {
        0.0: "Less Creativity",
        0.1: "Very Low Creativity",
        0.2: "Low Creativity",
        0.3: "Slightly Low Creativity",
        0.4: "Moderate Creativity",
        0.5: "Average Creativity",
        0.6: "Above Average Creativity",
        0.7: "Slightly High Creativity",
        0.8: "High Creativity",
        0.9: "Very High Creativity",
        1.0: "Max Creativity"
    }
    return labels.get(value, f"{value:.1f}")
 
st.sidebar.write('Creativity Level:', format_func(temp))
 
if "model" not in st.session_state:
    st.session_state["model"] = selected_model
if "temperature" not in st.session_state:
    st.session_state["temperature"] = temp
 
def get_content_hash(content):
    """Generate a hash for the given content."""
    return hashlib.md5(content.encode()).hexdigest()
 
 
def get_generated_testcases(selected_model, plain_text, key, value, temp):
    pmpt = [
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
            - Exploration of boundary conditions or limits of system functionality, including inputs at the minimum, maximum, or beyond typical ranges, and verification of correct system behavior."""
    }
    ]
 
    local_llm = ChatOllama(
            model = selected_model,
            base_url = "http://localhost:11434",
            temperature = temp)
   
    messages = [
        SystemMessage(content=pmpt[0]["content"]),
        HumanMessage(content=pmpt[1]["content"]),
        HumanMessage(content=pmpt[2]["content"])
    ]
 
    # Generate the response
    response = local_llm.invoke(messages)
 
    # Print the response
    # print(response.content)
    zerkinScript = response.content
   
    testCases_prompt = [
    {"role": "system", "content": "You are a Experienced Test Manager."},
    {"role": "user", "content": "write a Testcases for each  scenarios: " + zerkinScript},
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
 
    messages1 = [
        SystemMessage(content=testCases_prompt[0]["content"]),
        HumanMessage(content=testCases_prompt[1]["content"]),
        HumanMessage(content=testCases_prompt[2]["content"])
    ]
    # Generate the response
    response1 = local_llm.invoke(messages1)
    # Print the response
    # print(response1.content)
    testcases = response1.content
 
    return zerkinScript,testcases
 
 
content = st.text_area("Enter content:", height=200,max_chars=5000)
content_hash = get_content_hash(content)
st.sidebar.divider()
test_case_scenarios = st.sidebar.selectbox("Select The Test Scenarios:", ["Functional", "Exploratory", "Performance", "Security"])
 
st.session_state["test_case_scenarios"] = test_case_scenarios
 
ack = st.button("Generate Test Cases")
 
if ack:
   
    my_dict = {
        'Functional': 'Functional test scenarios',
        'Exploratory': 'Exploratory test scenarios',
        'Performance': 'Performance test scenarios',
        'Security': 'Security test scenarios as per OWASP standards'
    }
    zerkinScript, test_cases = get_generated_testcases(selected_model, content, test_case_scenarios, my_dict.get(test_case_scenarios), temp)
 
    st.info(f"### Test Case Scenarios For The Given User Story")
    st.markdown(zerkinScript, unsafe_allow_html=True)
    st_copy_to_clipboard(zerkinScript)
    st.info(f"### Test Cases For The Given User Story")
    st.markdown(test_cases, unsafe_allow_html=True)
    st_copy_to_clipboard(test_cases)
 
 
 
 
 
 
 
st.sidebar.divider()
img = Image.open("indiumLogo.PNG")
st.sidebar.image(img, width=200)
st.sidebar.write("**Powered by Indium Software**")
 