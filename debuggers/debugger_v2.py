import subprocess
import sys
import re
import os
import json
import difflib
from termcolor import cprint
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
import instructor
from typing import List, Dict
import glob

# Load environment variables from .env file
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

# Default model is GPT-4
DEFAULT_MODEL = os.environ.get("MODEL_NAME")

# Number of retries for JSON validation, defaulting to 5 while -1 means infinite retries
VALIDATE_JSON_RETRY = int(os.getenv("VALIDATE_JSON_RETRY", 5))


def json_validated_response(
    model: str, messages: List[Dict], nb_retry: int = VALIDATE_JSON_RETRY
) -> Dict:
    """
    Ensures the API response is a valid JSON object by retrying if necessary.

    Args:
        model (str): The model to use for generating the response.
        messages (List[Dict]): The conversation history with the model.
        nb_retry (int): Number of retry attempts before failing.

    Returns:
        Dict: The parsed JSON response.

    Raises:
        Exception: If no valid JSON response is found after the specified retries.
    """
    json_response = {}
    if nb_retry != 0:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            response_model=None,
            messages=messages,
            temperature=0.1
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


def extract_tracebacks(output):
    """
    Extract all errors that start with 'Traceback (most recent call last):' from the given output.
    Only returns the traceback blocks without including test case details.

    Args:
        output (str): The command line output containing error messages.

    Returns:
        List[str]: A list of extracted traceback error messages.
    """
     # Match 'Traceback' blocks until the first empty line
    tracebacks = re.findall(
        r"Traceback \(most recent call last\):.*?(?=\n\n|\Z)", output, re.DOTALL
    )
    return [tb.strip() for tb in tracebacks]  # Clean up extra spaces


def _scan_codebase():
    """
    Read actual code content with line numbers for better debugging context.
    
    Returns:
        str: The scanned codebase content with line numbers.
    
    """
    code_files = []
    for f in glob.glob('src/**/*.py', recursive=True):
        with open(f, 'r') as file:
            content = file.readlines()
            formatted_content = "\n".join(f"{i+1}: {line.rstrip()}" for i, line in enumerate(content))  
            code_files.append(f"File: {f}\nContent:\n{formatted_content}")
    return "\n\n".join(code_files)


def scan(folder_path, file_extension="*.py"):
    """
    Scans a specified folder for files matching the given extension.
    
    Args:
        folder_path (str): The path of the folder to scan.
        file_extension (str, optional): The file extension to filter by. Defaults to "*.py".

    Returns:
        str: The formatted file contents with line numbers.
    """
    code_files = []
    for file_path in glob.glob(f'{folder_path}/**/{file_extension}', recursive=True):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()  # Limit number of lines for brevity
            formatted_content = "\n".join(f"{i+1}: {line.rstrip()}" for i, line in enumerate(content))
            code_files.append(f"File: {file_path}\nContent:\n{formatted_content}")
    return "\n\n".join(code_files)


def fetch_files(folder_path):
    """
    Retrieves files from a given folder with their content and line numbers.
    
    Args:
        folder_path (str): Path to the folder containing files.

    Returns:
        List[Dict[str, List[Dict[str, str]]]]: A list of dictionaries with file details.
    """

    files = []
    
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'r') as file:
            content = file.readlines()  # Read file line by line
        
        files.append({
            'name': file_path,
            'content': [{'line_number': i + 1, 'text': line} for i, line in enumerate(content)]
            # 'content': content
        })
    
    return files


def send_error_to_gpt(tracebacks):
    """
    Sends traceback errors to GPT for debugging and applying necessary fixes.
    
    Args:
        tracebacks (List[str]): A list of traceback error messages.
    """

    ####################################### HARD CODED FILE PATHS ################################
    feature_folder = "generated/features"
    steps_folder = "generated/steps"

    features_content = fetch_files(feature_folder)
    steps_content = scan(steps_folder)
    brd_content = scan("requirements")
    codebase = _scan_codebase()
    ####################################### HARD CODED FILE PATHS ################################
    
    prompt = f"""    
        Analyze the following errors from a Behavior Driven Development (BDD) pipeline. If an "AmbiguousStep" error is found, identify the conflicting steps, update the tag of the duplicate step to resolve the conflict, and ensure that these tag changes are applied consistently across the relevant feature files.

    ### Provided Information:
    1. Tracebacks/Error Logs: {tracebacks}
    2. Feature File Content: {features_content}
    3. Steps File Content: {steps_content}
    4. Codebase: {codebase}
    5. Business Requirements: {brd_content}

    ### Your Tasks:
    1. Analyze Feature File, Steps file, Codebase Alignment and Business Requirements:
        - For each failed feature/step, cross-check the feature file and step file with the corresponding codebase. If the code implementation does not fully meet the corresponding business requirements hence causing some steps to fail, propose necessary fixes to align the code with the requirements. Prioritise making relevant changes in the CODEBASE mainly in order to make cases pass.
        - Religiously check all the failed steps against the business requirements and be cautious in identifying implmentation code from the codebase that doesnt match the business requirements.

    2. AmbiguousStep Error Resolution:
        - If the error is related to an "AmbiguousStep," locate the conflicting step definitions. Modify the duplicate step tags in the feature files and steps file to avoid any conflicts and apply these changes consistently throughout the codebase and feature files.

    ### Goal:
    Ensure that all the feature files and codebase are fully aligned with the business requirements, fixing any discrepancies or errors that prevent successful execution of the BDD pipeline.

    """

    with open(os.path.join(os.path.dirname(__file__),"prompt.txt"), "r") as f:
        SYSTEM_PROMPT = f.read()


    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        response_model=None,
        messages=[
            {"role" : "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    print("\n=== GPT Response ===")
    content = response.choices[0].message.content
   
    # Check if the content starts and ends with code block markers
    if content.startswith("```json") and content.endswith("```"):
        content = content[7:-3].strip()  # Remove the ```json and ``` markers

    changes_by_file = json.loads(content).get("files", {})

    # Apply changes grouped by file
    apply_changes(changes_by_file, confirm=True)


def apply_changes(changes_by_file: Dict[str, Dict], confirm: bool = False):
    """
    Applies changes grouped by file.

    Args:
        changes_by_file (dict): A dictionary where keys are file paths, and values contain:
            - 'explanations': List of explanations for changes.
            - 'changes': List of change dictionaries with operation, line, and content.
        confirm (bool): Whether to ask for confirmation before applying changes.

    Returns:
        dict: The applied fixes and whether the issues were resolved.
    """
    for file_path, file_data in changes_by_file.items():
        explanations = file_data.get("explanations", [])
        operation_changes = file_data.get("changes", [])

        if not operation_changes:
            print(f"No changes needed for {file_path}")
            continue

        with open(file_path) as f:
            original_file_lines = f.readlines()

        # Sort the changes in reverse line order (to avoid shifting issues)
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
        cprint(f"\n=== Changes for {file_path} ===", "cyan")
        for explanation in explanations:
            cprint(f"- {explanation}", "blue")

        # Show changes using a unified diff
        print("\nChanges to be made:")
        diff = difflib.unified_diff(original_file_lines, file_lines, lineterm="")
        for line in diff:
            if line.startswith("+"):
                cprint(line, "green", end="")
            elif line.startswith("-"):
                cprint(line, "red", end="")
            else:
                print(line, end="")

        # Apply changes if confirmed
        # if confirm:
        #     confirmation = input(f"Do you want to apply these changes to {file_path}? (y/n): ")
        #     if confirmation.lower() != "y":
        #         print(f"Skipping changes for {file_path}")
        #         continue

        with open(file_path, "w") as f:
            f.writelines(file_lines)
        print(f"Changes applied to {file_path}.")

    return {"fixes": changes_by_file, "solved": False}
  # Initially assume the fix didn't solve the issue (used to track/flag succcessful fixes)


def main():
    """
    Run Behave tests for all feature files in the 'generated/features' directory.
    Try running the tests up to 6 times. If they don't pass, generate a failure report and stop after the last attempt.
    """
    feature_dir = "generated/features"
    max_retries = 10
    attempt = 0
    last_failure_report = ""

    while attempt < max_retries:
        try:
            attempt += 1
            print(f"Attempt {attempt}/{max_retries} to run Behave tests...")
            result = subprocess.run(["behave", feature_dir], capture_output=True, text=True, check=True)
            print(result.stdout)
            # If tests pass, break out of the loop
            print("Behave tests passed successfully!")
            break

        except subprocess.CalledProcessError as error:
            error_message = error.stdout + error.stderr
            print(f"Behave tests failed with return code {error.returncode}")
            print(error_message)

            # Store the failure report for the last attempt
            last_failure_report = error_message

            # Send tracebacks or error message to GPT for analysis
            send_error_to_gpt(error_message)

            if attempt == max_retries:
                print(f"Test failed after {max_retries} attempts.")
                print(f"Final failure report: \n{last_failure_report}")
                # Break the loop only after the last attempt
                break

        except Exception as e:
            print(f"An error occurred while running Behave: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
