import json
import openai
from pydantic import BaseModel
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import instructor
import subprocess
import sys


    # Walk through all directories starting from the project root and add them to sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Adjust path to project root

# Walk through all directories under root_path and add them to sys.path
for dirpath, dirnames, filenames in os.walk(root_path):
    sys.path.append(dirpath)

from wolverine import main

load_dotenv()

# Setup instructor and OpenAI API clients
client = instructor.from_openai(
    AzureOpenAI(
        api_key=os.getenv("API_KEY"),
        api_version=os.getenv("LLM_API_VERSION"),
        azure_endpoint=os.getenv("BASE_URL"),
        azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
    )
)

# Load API keys from environment variables
openai.api_key = os.getenv("API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

# Fetch files from the local 'test-files' folder
def fetch_files():
    folder_path = "testfiles"  # Path to the folder where test files are located
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
        model=os.getenv("MODEL_NAME"),
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
    
    test_file_name = f"{test_dir}/{file_name.replace('.py', '').replace('.js', '')}_test.py"
    with open(test_file_name, "w") as f:
        f.write(test_script)
    print(f"Test script saved as {test_file_name}")

def generate_commit_message(changes):
    """
    Sends the changes to the Azure OpenAI client and generates a short commit message.
    """
    prompt = (
        f"The following is a code change: {changes}\n"
        "Generate a short and meaningful git commit message summarizing this change:"
    )
    
    try:
        # Call Azure OpenAI's GPT model
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            response_model=None,
             messages=[{"role": "system", "content": "You are a helpful assistant for writing commit messages."},
                      {"role": "user", "content": prompt}],
            temperature=0.1
        )
        # Extract the generated commit message
        commit_message = response.choices[0].message.content.strip()
        return commit_message
    
    except Exception as e:
        print(f"Error generating commit message: {e}")
        return None
    
# Run unit tests with Wolverine
def run_tests():
    test_dir = "tests/unit"
    test_files = [os.path.join(test_dir, f) for f in os.listdir(test_dir) if f.endswith("_test.py")]

    for test_file in test_files:
        print(f"Running test: {test_file}")
        fixed = main(test_file)

        print(fixed, "fixed")

        if fixed != None:
            # Check if the fix solved the issue
            if fixed["solved"] == True:
                print(f"Fix applied successfully for {test_file}")
                commit_message = generate_commit_message(fixed["fix"])
                # Run the git commit command
                subprocess.run(["git", "commit", "-am", commit_message], check=True)
                # git commit message for the fixed["fix"] fix for file fixed["file"]
            else:
                print(f"Fix did not solve the issue for {test_file}.")
    
# Generate unit tests for all files in the repo and run them
def generate_and_run_tests():
    files = fetch_files()
    
    for file in files:
        content = file['content']
        original_filename = file['name']
        
        test_file_name = f"tests/unit/{original_filename.replace('.py', '').replace('.js', '')}_test.py"

        # Check if the test file already exists, skip if exists
        if os.path.exists(test_file_name):
            print(f"Skipping {original_filename}: Test file already exists.")
            continue  

        # Generate and save only unit tests
        unit_test_script = generate_test(content, test_type="unit")
        save_test(file['name'], unit_test_script, test_type="unit")
    
    # Run all generated unit tests
    run_tests()

if __name__ == "__main__":
    generate_and_run_tests()
