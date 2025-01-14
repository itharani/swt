import openai
from pydantic import BaseModel
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import instructor

client = instructor.from_openai(
        AzureOpenAI(api_key=os.getenv("API_KEY"),
                    api_version=os.getenv("LLM_API_VERSION"),
                    azure_endpoint=os.getenv("BASE_URL"),
                    azure_deployment=os.getenv("MODEL_DEPLOYMENT"),)
    )

# Load API keys from environment variables
openai.api_key = os.getenv("API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

# Initialize GitHub client
# g = Github(github_token)

# Fetch files from the local 'test-files' folder
def fetch_files():
    folder_path = "/Users/Dev/projects/Maybank/swt/testfiles"  # Path to the folder where test files are located
    files = []
    
    # Iterate over files in the directory
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        # Check if it's a .py or .js file
        if (file_name.endswith(".py") or file_name.endswith(".js")) and os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            files.append({'name': file_name, 'content': content})
    
    return files

# Generate test cases using the 'client' instance and the AzureOpenAI model
def generate_test(code_snippet, test_type="unit"):
    prompt = f"""
    Understand the code snippet well and write unit test cases that cover all possible edge cases and scenarios in the manner below:
     Write a comprehensive, almost exhaustive unit test script for the following code:
    ```{code_snippet}```
    Only return the python test script, no extra messages. Inline comments are allowed.
    Add the below snippet at the beginning of the test script:
    ```
    import sys
    import os

    # Walk through all directories starting from the project root and add them to sys.path
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Adjust path to project root

    # Walk through all directories under root_path and add them to sys.path
    for dirpath, dirnames, filenames in os.walk(root_path):
        sys.path.append(dirpath)
    ```
    """
    # Use the client to generate a response from the model
    response = client.chat.completions.create(
        model=os.getenv("model_name"),
        response_model=None,
        messages=[{"role": "system", "content": prompt}],
        temperature=0.1
    )
    print(response.choices[0].message.content)
    test_script = response.choices[0].message.content.strip()
    
    # Remove the markdown code block (```python) if present
    if test_script.startswith("```python"):
        test_script = test_script[9:].strip()  # Remove the "```python" part
    if test_script.endswith("```"):
        test_script = test_script[:-3].strip()  # Remove the closing "```"

    return test_script

# Save generated test script to a file
def save_test(file_name, test_script, test_type="unit"):
    test_dir = f"tests/{test_type}"
    os.makedirs(test_dir, exist_ok=True)
    
    test_file_name = f"{test_dir}/test_{file_name.replace('.py', '').replace('.js', '')}.py"
    with open(test_file_name, "w") as f:
        f.write(test_script)
    print(f"Test script saved as {test_file_name}")

# Generate unit tests for all files in the repo
def generate_tests_for_repo():
    files = fetch_files()
    
    for file in files:
        content = file['content']
        
        # Generate and save only unit tests
        unit_test_script = generate_test(content, test_type="unit")
        save_test(file['name'], unit_test_script, test_type="unit")

if __name__ == "__main__":
    generate_tests_for_repo()
