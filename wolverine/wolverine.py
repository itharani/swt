import difflib
import json
import os
import shutil
import subprocess
import sys
import ast

import openai
from openai import AzureOpenAI
from typing import List, Dict
from termcolor import cprint
from dotenv import load_dotenv
from instructor import from_openai

# Load environment variables
load_dotenv()

# Set up the Azure OpenAI client
client = from_openai(
    AzureOpenAI(
        api_key=os.getenv("API_KEY"),
        api_version=os.getenv("LLM_API_VERSION"),
        azure_endpoint=os.getenv("BASE_URL"),
        azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
    )
)

# Default model is GPT-4
DEFAULT_MODEL = os.environ.get("MODEL_NAME")

# Nb retries for json_validated_response, default to -1, infinite
VALIDATE_JSON_RETRY = int(os.getenv("VALIDATE_JSON_RETRY", 5))

# Read the system prompt
with open(os.path.join(os.path.dirname(__file__), "..", "prompt.txt"), "r") as f:
    SYSTEM_PROMPT = f.read()


def get_imported_files(test_file: str) -> List[str]:
    """
    Given a test file, return a list of files it imports.
    """
    imported_files = []
    with open(test_file, "r") as file:
        tree = ast.parse(file.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_files.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imported_files.append(node.module)
    
    print(f"Imported files: {imported_files}")
    return imported_files


def run_script(script_name: str, script_args: List) -> str:
    """
    If script_name.endswith(".py") then run with python
    else run with node
    """
    script_args = [str(arg) for arg in script_args]
    subprocess_args = (
        [sys.executable, script_name, *script_args]
        if script_name.endswith(".py")
        else ["node", script_name, *script_args]
    )

    try:
        result = subprocess.check_output(subprocess_args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        return error.output.decode("utf-8"), error.returncode
    return result.decode("utf-8"), 0


def json_validated_response(
    model: str, messages: List[Dict], nb_retry: int = VALIDATE_JSON_RETRY
) -> Dict:
    """
    This function is needed because the API can return a non-json response.
    This will run recursively VALIDATE_JSON_RETRY times.
    If VALIDATE_JSON_RETRY is -1, it will run recursively until a valid json
    response is returned.
    """
    json_response = {}
    if nb_retry != 0:
        response = client.chat.completions.create(
            model=model,
            response_model=None,
            messages=messages,
            temperature=0.1,
        )
        messages.append(response.choices[0].message)
        content = response.choices[0].message.content
        
        # Check if the content starts and ends with code block markers
        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3].strip()  # Remove the ```json and ``` markers

        # see if json can be parsed
        try:
            json_start_index = content.index(
                "["
            )  # find the starting position of the JSON data
            json_data = content[
                json_start_index:
            ]  # extract the JSON data from the response string
            json_response = json.loads(json_data)
            return json_response
        except (json.decoder.JSONDecodeError, ValueError) as e:
            cprint(f"{e}. Re-running the query.", "red")
            # debug
            cprint(f"\nGPT RESPONSE:\n\n{content}\n\n", "yellow")
            # append a user message that says the json is invalid
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your response could not be parsed by json.loads. "
                        "Please restate your last message as pure JSON."
                    ),
                }
            )
            # dec nb_retry
            nb_retry -= 1
            # rerun the api call
            return json_validated_response(model, messages, nb_retry)
    
        except Exception as e:
            cprint(f"Unknown error: {e}", "red")
            cprint(f"\nGPT RESPONSE:\n\n{content}\n\n", "yellow")
            raise e
    raise Exception(
        f"No valid json response found after {VALIDATE_JSON_RETRY} tries. Exiting."
    )


def send_error_to_gpt(
    test_file: str,
    imported_files: List[str],
    args: List,
    error_message: str,
    failed_test_case: str,  # New parameter to pass the failed test case
    model: str = DEFAULT_MODEL,
) -> Dict:
    """
    Send the error, the failed test case, and related imported files to the LLM for suggestions.
    """
    # Extract the failed test case content
    with open(test_file, "r") as f:
        test_file_lines = f.readlines()

    # Search for the failed test case in the script
    test_case_content = []
    inside_failed_test = False
    for line in test_file_lines:
        if failed_test_case in line:  # Start of the failed test case
            inside_failed_test = True
        if inside_failed_test:
            test_case_content.append(line)
            if line.strip() == "":  # Assume a blank line marks the end of the test case
                break

    test_case_with_lines = []
    for i, line in enumerate(test_case_content):
        test_case_with_lines.append(str(i + 1) + ": " + line)
    test_case_with_lines = "".join(test_case_with_lines)

    # Include imported file content as before
    imported_file_contents = {}
    for file in imported_files:
        file_path = os.path.join("testfiles", file + ".py")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                imported_file_contents[file_path] = f.readlines()

    prompt = (
        "Here is the failed test case:\n\n"
        f"{test_case_with_lines}\n\n"
        "Here are the arguments it was provided:\n\n"
        f"{args}\n\n"
        "Here is the error message:\n\n"
        f"{error_message}\n"
        "Here is the code from the imported files:\n\n"
    )

    # Add imported files content to the prompt
    for file_path, file_content in imported_file_contents.items():
        prompt += f"Code from {file_path}:\n"
        for i, line in enumerate(file_content):
            prompt += f"{i + 1}: {line}"

    # Send the prompt to GPT
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    return json_validated_response(model, messages)



def apply_changes(file_path: dict, changes: List, confirm: bool = False):
    """
    Pass changes as loaded json (list of dicts)
    """
    # Extract the actual file path from the response (if it's in dictionary format)
    print(file_path)
    file_path = file_path.get('file', '')

    if not file_path:
        raise ValueError("File path is missing or invalid.")
    
    with open(file_path) as f:
        original_file_lines = f.readlines()

    # Filter out explanation elements
    operation_changes = [change for change in changes if "operation" in change]
    explanations = [
        change["explanation"] for change in changes if "explanation" in change
    ]

    # Sort the changes in reverse line order
    operation_changes.sort(key=lambda x: x["line"], reverse=True)

    file_lines = original_file_lines.copy()
    for change in operation_changes:
        operation = change["operation"]
        line = change["line"]
        content = change["content"]

        if operation == "Replace":
            file_lines[line - 1] = content + "\n"
        elif operation == "Delete":
            del file_lines[line - 1]
        elif operation == "InsertAfter":
            file_lines.insert(line, content + "\n")

    # Print explanations
    cprint("Explanations:", "blue")
    for explanation in explanations:
        cprint(f"- {explanation}", "blue")

    # Display changes diff
    print("\nChanges to be made:")
    diff = difflib.unified_diff(original_file_lines, file_lines, lineterm="")
    for line in diff:
        if line.startswith("+"):
            cprint(line, "green", end="")
        elif line.startswith("-"):
            cprint(line, "red", end="")
        else:
            print(line, end="")

    if confirm:
        # check if user wants to apply changes or exit
        confirmation = input("Do you want to apply these changes? (y/n): ")
        if confirmation.lower() != "y":
            print("Changes not applied")
            sys.exit(0)

    with open(file_path, "w") as f:
        f.writelines(file_lines)
    print("Changes applied.")


def main(test_file, *test_args, revert=False, model=DEFAULT_MODEL, confirm=False):
    if revert:
        backup_file = test_file + ".bak"
        if os.path.exists(backup_file):
            shutil.copy(backup_file, test_file)
            print(f"Reverted changes to {test_file}")
            sys.exit(0)
        else:
            print(f"No backup file found for {test_file}")
            sys.exit(1)

    # Make a backup of the original test file
    shutil.copy(test_file, test_file + ".bak")

    # Get the list of imported files in the test script
    imported_files = get_imported_files(test_file)

    while True:
        output, returncode = run_script(test_file, test_args)

        if returncode == 0:
            cprint("Test ran successfully.", "blue")
            print("Output:", output)
            break

        else:
            cprint("Test failed. Trying to fix...", "blue")
            print("Output:", output)
            json_response = send_error_to_gpt(
                test_file=test_file,
                imported_files=imported_files,
                args=test_args,
                error_message=output,
                model=model,
                failed_test_case=output
            )
            #print(json_response)
            apply_changes(json_response[-1], json_response, confirm=confirm)
            cprint("Changes applied. Rerunning...", "blue")
