import glob
import os # Assuming you're using OpenAI for the LLM service
from dotenv import load_dotenv

load_dotenv()  

def _scan_codebase():
        """Read actual code content with line numbers for better debugging context."""
        code_files = []
        for f in glob.glob('src/**/*.py', recursive=True):
            with open(f, 'r') as file:
                content = file.readlines()
                formatted_content = "\n".join(f"{i+1}: {line.rstrip()}" for i, line in enumerate(content))  # Limit to first 200 lines for brevity
                code_files.append(f"File: {f}\nContent:\n{formatted_content}")
        return "\n\n".join(code_files)

def _load_brd():
        return open("requirements/brd.md").read()


import os
import instructor
from openai import AzureOpenAI

def generate_report():
    # Load the system content (system prompt) from the code_review.md file
    with open("code_review.md", "r") as file:
        system_prompt = file.read()

    # Load the business requirements prompt
    business_requirements = _load_brd()

    # Scan the codebase
    codebase_content = _scan_codebase()

    # Combine the business requirements and codebase with the user message
    message_to_llm = f"Business Requirements:\n{business_requirements}\n\nCodebase:\n{codebase_content}"

    # Initialize the client using your existing setup
    client = instructor.from_openai(
        AzureOpenAI(
            api_key=os.getenv("API_KEY"),
            api_version=os.getenv("LLM_API_VERSION"),
            azure_endpoint=os.getenv("BASE_URL"),
            azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
        )
    )

    try:
        # Send the message to Azure OpenAI using the client
        response = client.chat.completions.create(
            model=os.getenv("DEFAULT_MODEL"),  # Make sure your model is set in environment variables
            response_model=None,
            messages=[
                {"role": "system", "content": system_prompt},  # System content from the file
                {"role": "user", "content": message_to_llm}   # User content with business requirements and codebase
            ],
            temperature=0.1  # Adjust based on the desired creativity of the response
        )

        # Extract the LLM's response
        llm_report = response.choices[0].message.content.strip()

        # Ensure the reports folder exists
        os.makedirs('reports', exist_ok=True)

        # Define the output file path
        report_file_path = "reports/requirement_satisfaction_report.md"

        # Write the LLM's evaluation to a file
        with open(report_file_path, 'w') as report_file:
            report_file.write(llm_report)

        print(f"Report generated successfully and saved to {report_file_path}")

    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    # This will run the generate_report function when the script is executed directly
    generate_report()
