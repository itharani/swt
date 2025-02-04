import subprocess
import sys
import re
import os
import json
import difflib
from termcolor import cprint
from dotenv import load_dotenv
from openai import AzureOpenAI
import instructor
from typing import List, Dict, Optional
from pathlib import Path
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

load_dotenv()

# Set up the Azure OpenAI client
client = instructor.from_openai(
    AzureOpenAI(
        api_key=os.getenv("API_KEY"),
        api_version=os.getenv("LLM_API_VERSION"),
        azure_endpoint=os.getenv("BASE_URL"),
        azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
    )
)

DEFAULT_MODEL = os.getenv("MODEL_NAME")
VALIDATE_JSON_RETRY = int(os.getenv("VALIDATE_JSON_RETRY", 5))

def json_validated_response(
    model: str, messages: List[Dict], nb_retry: int = VALIDATE_JSON_RETRY
) -> Dict:
    """
    Ensure the LLM response is valid JSON.
    """
    if nb_retry == 0:
        raise Exception("No valid JSON response after retries.")
    
    response = client.chat.completions.create(
        model=model,
        response_model=None,
        messages=messages,
        temperature=0.1
    )
    content = response.choices[0].message.content

    try:
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3].strip()
        return json.loads(content)
    except json.JSONDecodeError:
        messages.append({"role": "user", "content": "Your response must be valid JSON."})
        return json_validated_response(model, messages, nb_retry - 1)

def extract_tracebacks(output: str) -> List[str]:
    """
    Extract tracebacks from test output.
    """
    return re.findall(r"Traceback \(most recent call last\):.*?(?=\n\n|\Z)", output, re.DOTALL)

def load_business_rules(brd_path: str) -> Dict:
    """
    Load business rules from a BRD file.
    """
    with open(brd_path, "r") as f:
        return json.load(f)  # Assume BRD is in JSON format

def retrieve_relevant_code_snippets(tracebacks: List[str], codebase_path: str) -> List[str]:
    """
    Use RAG to retrieve relevant code snippets.
    """
    documents = []
    for file_path in Path(codebase_path).rglob("*.py"):
        with open(file_path, "r") as f:
            content = f.read()
            documents.append({"file": str(file_path), "content": content})
    
    vector_db = FAISS.from_documents(documents, OpenAIEmbeddings())
    return [doc["content"] for doc in vector_db.similarity_search("\n".join(tracebacks), k=3)]

def send_error_to_gpt(tracebacks: List[str], brd_path: str, codebase_path: str) -> Dict:
    """
    Send error details to GPT for debugging.
    """
    error_context = {
        "tracebacks": tracebacks,
        "business_rules": load_business_rules(brd_path),
        "codebase_snippets": retrieve_relevant_code_snippets(tracebacks, codebase_path)
    }

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        response_model=None,
        messages=[
            {"role": "system", "content": "Analyze errors and suggest fixes."},
            {"role": "user", "content": json.dumps(error_context, indent=2)}
        ],
        temperature=0.1
    )
    return json_validated_response(DEFAULT_MODEL, response.choices[0].message.content)

def apply_changes(changes_by_file: Dict[str, Dict], confirm: bool = False) -> Dict:
    """
    Apply changes to files.
    """
    for file_path, file_data in changes_by_file.items():
        with open(file_path, "r") as f:
            original_lines = f.readlines()

        new_lines = original_lines.copy()
        for change in file_data.get("changes", []):
            operation, line, content = change["operation"], change["line"], change["content"]
            if operation == "Replace":
                new_lines[line - 1] = content + "\n"
            elif operation == "Delete":
                del new_lines[line - 1]
            elif operation == "InsertAfter":
                new_lines.insert(line, content + "\n")

        if confirm:
            diff = difflib.unified_diff(original_lines, new_lines, lineterm="")
            for line in diff:
                if line.startswith("+"):
                    cprint(line, "green", end="")
                elif line.startswith("-"):
                    cprint(line, "red", end="")
                else:
                    print(line, end="")
            if input("Apply changes? (y/n): ").lower() != "y":
                continue

        with open(file_path, "w") as f:
            f.writelines(new_lines)

    return {"fixes": changes_by_file, "solved": False}

def main():
    feature_dir = "generated/features"
    max_retries = 10
    attempt = 0

    while attempt < max_retries:
        attempt += 1
        print(f"Attempt {attempt}/{max_retries} to run Behave tests...")
        result = subprocess.run(["behave", feature_dir], capture_output=True, text=True)

        if result.returncode == 0:
            print("Behave tests passed successfully!")
            break

        tracebacks = extract_tracebacks(result.stderr)
        if not tracebacks:
            print("No tracebacks found in test output.")
            break

        fixes = send_error_to_gpt(tracebacks, "requirements/brd.json", "src")
        apply_changes(fixes, confirm=True)

        if attempt == max_retries:
            print(f"Test failed after {max_retries} attempts.")
            break

if __name__ == "__main__":
    main()