"""
Module Name: generate_report.py

This module scans a Python codebase, extracts business requirements from a markdown file, 
and evaluates the code against these requirements using an LLM (Azure OpenAI). 
The generated report is saved as a markdown file.

Features:
- Reads Python files in the 'src' directory and formats them with line numbers.
- Loads business requirements from 'requirements/brd.md'(hardcoded path for simplicity).
- Uses OpenAI (via Azure) to evaluate code against requirements.
- Saves the generated report in 'reports/requirement_satisfaction_report.md'.

Usage:
Run the script directly to generate the report:
    python report_generator.py

Dependencies:
- dotenv
- openai
- instructor
- glob
- os

Author: Tharani
Date: 2025-02-17
"""

import glob
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import instructor

# Load environment variables from .env file
load_dotenv()

def _scan_codebase():
    """
    Reads and formats the Python files in the 'src' directory (and subdirectories) with line numbers for better debugging context.
    
    Returns:
        str: A concatenated string containing filenames and their corresponding content with line numbers.
    """
    code_files = []  # List to store formatted code content
    
    # Glob to find all .py files recursively in the src folder
    for f in glob.glob('src/**/*.py', recursive=True):
        with open(f, 'r') as file:
            # Read the file content and add line numbers
            content = file.readlines()
            formatted_content = "\n".join(f"{i+1}: {line.rstrip()}" for i, line in enumerate(content))  
            code_files.append(f"File: {f}\nContent:\n{formatted_content}") 
    return "\n\n".join(code_files)  

def _load_brd():
    """
    Loads the business requirements from a markdown file.

    Returns:
        str: The content of the 'brd.md' file.
    """
    return open("requirements/brd.md").read()  # Read the business requirement document

def generate_report():
    """
    Generates a report that combines the business requirements and codebase contents.
    The report is sent to an LLM (Language Learning Model) using OpenAI to evaluate the code against business requirements.
    The generated report is saved to a markdown file.
    """
    # Load the system content (system prompt) from the 'report_prompt.md' file
    with open("scripts/generate_report/report_prompt.md", "r") as file:
        system_prompt = file.read()  

    # Load the business requirements from the markdown file
    business_requirements = _load_brd()

    # Scan and format the codebase content with line numbers
    codebase_content = _scan_codebase()

    # Combine business requirements and codebase content to form the user's message to LLM
    message_to_llm = f"Business Requirements:\n{business_requirements}\n\nCodebase:\n{codebase_content}"

    # Initialize the Azure OpenAI client with environment variables
    client = instructor.from_openai(
        AzureOpenAI(
            api_key=os.getenv("API_KEY"),  # API Key for Azure OpenAI
            api_version=os.getenv("LLM_API_VERSION"),  # LLM API version
            azure_endpoint=os.getenv("BASE_URL"),  # Azure endpoint
            azure_deployment=os.getenv("MODEL_DEPLOYMENT"),  # Azure model deployment
        )
    )

    try:
        # Send the message to Azure OpenAI using the client and retrieve the response
        response = client.chat.completions.create(
            model=os.getenv("DEFAULT_MODEL"),  
            response_model=None,
            messages=[
                {"role": "system", "content": system_prompt},  
                {"role": "user", "content": message_to_llm}   
            ],
            temperature=0.1  # Low temperature to reduce creativity and ensure focused output
        )

        # Extract and clean the LLM's response
        llm_report = response.choices[0].message.content.strip()

        # Ensure the 'reports' directory exists
        os.makedirs('reports', exist_ok=True)

        # Define the output file path where the report will be saved
        report_file_path = "reports/requirement_satisfaction_report.md"

        # Write the generated report to the file
        with open(report_file_path, 'w') as report_file:
            report_file.write(llm_report)  # Save the LLM's response to the file

        # Print success message with file location
        print(f"Report generated successfully and saved to {report_file_path}")

    except Exception as e:
        # Catch and display any errors that occur during the report generation process
        print(f"Error generating report: {e}")

# Entry point for the script when executed directly
if __name__ == "__main__":
    generate_report()  # Run the report generation function
