import openai
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import instructor

client = instructor.from_openai(
        AzureOpenAI(api_key=os.getenv("api_key"),
                    api_version=os.getenv("llm_api_version"),
                    azure_endpoint=os.getenv("base_url"),
                    azure_deployment=os.getenv("model_deployment"))
    )

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")

# Initialize GitHub client
# g = Github(github_token)

# Fetch files from the local 'test-files' folder
def fetch_files():
    folder_path = "test-files"  # Path to the folder where test files are located
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
    Write a {test_type} test script for the following code:
    ```{code_snippet}```
    """
    # Use the client to generate a response from the model
    response = client.complete(
        prompt=prompt,
        max_tokens=200
    )
    return response['choices'][0]['text']

# Save generated test script to a file
def save_test(file_name, test_script, test_type="unit"):
    test_dir = f"tests/{test_type}"
    os.makedirs(test_dir, exist_ok=True)
    
    test_file_name = f"{test_dir}/test_{file_name.replace('.py', '').replace('.js', '')}.py"
    with open(test_file_name, "w") as f:
        f.write(test_script)
    print(f"Test script saved as {test_file_name}")

# Generate tests for all files in the repo
def generate_tests_for_repo():
    files = fetch_files()
    
    for file in files:
        content = file['content']
        
        # Generate and save unit tests
        unit_test_script = generate_test(content, test_type="unit")
        save_test(file['name'], unit_test_script, test_type="unit")

        # Generate and save integration tests
        integration_test_script = generate_test(content, test_type="integration")
        save_test(file['name'], integration_test_script, test_type="integration")

if __name__ == "__main__":
    generate_tests_for_repo()
