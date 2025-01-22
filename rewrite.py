import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("API_KEY"),
    api_version=os.getenv("LLM_API_VERSION"),
    azure_endpoint=os.getenv("BASE_URL"),
    azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
)

def rewrite_code_with_ai(file_path):
    """Analyze and refactor code in the specified file using Azure OpenAI."""
    with open(file_path, 'r') as file:
        original_code = file.read()

    # Prompt to specify code rules and practices
    prompt = f"""
    Refactor the following code while retaining its functionality. Follow these rules:
    1. Maintain readability and use meaningful variable/function names.
    2. Use consistent indentation (4 spaces per level).
    3. Simplify logic without altering functionality.
    4. Use error handling where appropriate.
    5. Remove unnecessary comments and redundant code.
    6. Optimize imports by removing unused ones.
    7. Keep the code modular and reusable.
    8. Do not use backticks or any other syntax to enclose expressions in the code.
    9. The output should be pure Python code without any markdown or code block formatting.

    
    
    {original_code}
    
    """

    # Use Azure OpenAI to refactor the code
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[{"role": "system", "content": prompt}],
        temperature=0.1
    )

    improved_code = response.choices[0].message.content.strip()

    # Save the improved code if it's significantly different
    if improved_code != original_code:
        with open(file_path, 'w') as file:
            file.write(improved_code)
        print(f"Rewritten code saved to {file_path}")
    else:
        print(f"No significant changes made to {file_path}")

def process_rewrite_folder():
    """Process Python files in the 'rewrite folder."""
    rewrite_folder = "rewrite"
    for root, _, files in os.walk(rewrite_folder):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                print(f"Processing file for rewrite: {file_path}")
                rewrite_code_with_ai(file_path)

if __name__ == "__main__":
    process_rewrite_folder()