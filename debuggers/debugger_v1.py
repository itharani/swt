import difflib
import json
import os
import subprocess
import sys
import ast

import openai
from openai import OpenAI
from typing import List, Dict
from termcolor import cprint
from dotenv import load_dotenv
from instructor import from_openai

# Load environment variables
load_dotenv()

client = OpenAI(api_key="sk-170a73cc4f9b49e2b344a57df3efce70", base_url="https://api.deepseek.com")

# Default model is GPT-4
DEFAULT_MODEL = os.getenv("MODEL_NAME")

# Retries for JSON validation, default to 5
VALIDATE_JSON_RETRY = int(os.getenv("VALIDATE_JSON_RETRY", 5))

# System prompt for GPT
with open(os.path.join(os.path.dirname(__file__), "prompt.txt"), "r") as f:
    SYSTEM_PROMPT = f.read()


def capture_traceback(error_message: str) -> str:
    """
    Extract the relevant part of the traceback from Behave output.
    """
    traceback_lines = []
    in_traceback = False
    for line in error_message.splitlines():
        if line.startswith("Traceback (most recent call last):"):
            in_traceback = True
        if in_traceback:
            traceback_lines.append(line)
        if in_traceback and line.strip() == "":
            break
    print(traceback_lines)
    return "\n".join(traceback_lines)


def get_imported_files(test_file: str) -> List[str]:
    """
    Return a list of files imported by the test file.
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
    return imported_files


def run_behave_tests(feature_file: str) -> str:
    """
    Run the Behave tests and capture the output.
    """
    try:
        result = subprocess.check_output(
            ["behave", feature_file],
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as error:
        return error.output.decode("utf-8"), error.returncode
    return result.decode("utf-8"), 0


def json_validated_response(
    model: str, messages: List[Dict], nb_retry: int = VALIDATE_JSON_RETRY
) -> Dict:
    """
    Validate and parse the JSON response from GPT.
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

        if content.startswith("```json") and content.endswith("```"):
            content = content[7:-3].strip()

        try:
            json_response = json.loads(content)
            return json_response
        except json.JSONDecodeError as e:
            cprint(f"JSON decode error: {e}. Retrying...", "red")
            messages.append(
                {
                    "role": "user",
                    "content": "The response could not be parsed. Please reformat it as JSON.",
                }
            )
            nb_retry -= 1
            return json_validated_response(model, messages, nb_retry)
    raise Exception("Failed to retrieve a valid JSON response.")


def send_error_to_gpt(
    feature_file: str,
    imported_files: List[str],
    error_message: str,
    model: str = DEFAULT_MODEL,
) -> Dict:
    """
    Send the error details to GPT for analysis and suggestions.
    """
    traceback = capture_traceback(error_message)

    feature_file_content = open(feature_file).read()
    steps_content= open("generated/steps/payment_processing_7543b8_steps.py").read()

    prompt = f"""
    Here is the error traceback:
    {traceback}

    Here is the feature file content:
    {feature_file_content}

    Here is the steps file content:
    {steps_content}

    Here are the contents of the files/modules imported to the steps:
    """
    # for file in imported_files:
    #     prompt += f"\nFile: {file}\n" + "".join(open(file).readlines())

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    return json_validated_response(model, messages)


def apply_changes(file_path: str, changes: List[Dict]):
    """
    Apply changes suggested by GPT to the specified file.
    """
    with open(file_path, "r") as file:
        original_lines = file.readlines()

    modified_lines = original_lines[:]
    for change in sorted(changes, key=lambda x: x["line"], reverse=True):
        operation = change["operation"]
        line_number = change["line"] - 1  # Convert to 0-based index
        content = change["content"]

        if operation == "Replace":
            modified_lines[line_number] = content + "\n"
        elif operation == "Delete":
            del modified_lines[line_number]
        elif operation == "InsertAfter":
            modified_lines.insert(line_number + 1, content + "\n")

    with open(file_path, "w") as file:
        file.writelines(modified_lines)

    cprint("Changes applied successfully!", "green")


def main(feature_file: str):
    """
    Main function to orchestrate the process.
    """
    test_output, return_code = run_behave_tests(feature_file)
    if return_code != 0:
        cprint("Test failures detected. Analyzing...", "yellow")

        for line in test_output.splitlines():
            if "Traceback" in line:
                error_message = test_output.split("Traceback", 1)[1]
                break

        imported_files = get_imported_files("generated/steps/payment_processing_7543b8_steps.py")
        suggestions = send_error_to_gpt(feature_file, imported_files, error_message)

        cprint("Suggested changes:", "blue")
        print(suggestions)
        print(len(suggestions))
        
        # for change in suggestions["changes"]:
        #     cprint(change, "cyan")

        apply_changes(suggestions["file_path"], suggestions)
    else:
        cprint("All tests passed successfully!", "green")


if __name__ == "__main__":

    main("generated/features/payment_processing_7543b8.feature")


# import difflib
# import json
# import os
# import shutil
# import subprocess
# import sys
# import ast
# import glob
# from typing import List, Dict
# from termcolor import cprint
# from dotenv import load_dotenv
# import instructor
# from openai import AzureOpenAI
# from typing import Tuple

# # Load environment variables
# load_dotenv()

# # Set up the Azure OpenAI client
# client = instructor.from_openai(
#     AzureOpenAI(
#         api_key=os.getenv("API_KEY"),
#         api_version=os.getenv("LLM_API_VERSION"),
#         azure_endpoint=os.getenv("BASE_URL"),
#         azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
#     )
# )

# DEFAULT_MODEL = os.environ.get("MODEL_NAME")
# VALIDATE_JSON_RETRY = int(os.getenv("VALIDATE_JSON_RETRY", 5))
# BEHAVE_ARGS = [
#     "generated/features"
# ]

# # Read the system prompt
# with open(os.path.join(os.path.dirname(__file__),"prompt.txt"), "r") as f:
#     SYSTEM_PROMPT = f.read()

# def get_imported_files() -> List[str]:
#     """Get all imported files from step definitions"""
#     imported_files = set()
#     for step_file in glob.glob("generated/steps/*.py"):
#         with open(step_file, "r") as f:
#             tree = ast.parse(f.read())
#             for node in ast.walk(tree):
#                 if isinstance(node, ast.Import):
#                     for alias in node.names:
#                         imported_files.add(alias.name)
#                 elif isinstance(node, ast.ImportFrom):
#                     imported_files.add(node.module)
#     return list(imported_files)

# def run_behave() -> Tuple[str, int]:
#     """Run behave tests and return output/status"""
#     try:
#         result = subprocess.run(
#             ["behave"] + BEHAVE_ARGS,
#             check=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT
#         )
#         return result.stdout.decode("utf-8"), 0
#     except subprocess.CalledProcessError as e:
#         return e.output.decode("utf-8"), e.returncode

# def parse_failed_scenario(error_output: str) -> dict:
#     """Extract failed scenario details from behave output"""
#     failed_scenario = {
#         "feature_file": "",
#         "scenario_name": "",
#         "failed_step": "",
#         "error_message": ""
#     }
    
#     lines = error_output.split("\n")
#     for i, line in enumerate(lines):
#         if line.startswith("Feature:"):
#             failed_scenario["feature_file"] = line.split("#")[-1].strip()
#         elif line.startswith("Scenario:"):
#             failed_scenario["scenario_name"] = line.split(":")[1].strip()
#         elif line.strip().startswith("Then "):
#             failed_scenario["failed_step"] = line.strip()
#         elif "AssertionError" in line or "Error:" in line:
#             failed_scenario["error_message"] = "\n".join(lines[i:i+5])
    
#     return failed_scenario

# def get_relevant_code(failed_scenario: dict) -> str:
#     """Get code context for failed scenario"""
#     code_context = []
    
#     # Get feature file content
#     if os.path.exists(failed_scenario["feature_file"]):
#         with open(failed_scenario["feature_file"]) as f:
#             code_context.append(f"Feature File:\n{f.read()}")
    
#     # Get step implementation
#     step_files = glob.glob("generated/steps/*.py")
#     for step_file in step_files:
#         with open(step_file) as f:
#             content = f.read()
#             if failed_scenario["failed_step"] in content:
#                 code_context.append(f"Step Implementation ({step_file}):\n{content}")
    
#     # Get source code imports
#     for imp in get_imported_files():
#         source_file = f"src/implementation/{imp.replace('.', '/')}.py"
#         if os.path.exists(source_file):
#             with open(source_file) as f:
#                 code_context.append(f"Source Code ({source_file}):\n{f.read()}")
    
#     return "\n\n".join(code_context)

# def json_validated_response(
#     model: str, messages: List[Dict], nb_retry: int = VALIDATE_JSON_RETRY
# ) -> Dict:
#     """
#     This function is needed because the API can return a non-json response.
#     This will run recursively VALIDATE_JSON_RETRY times.
#     If VALIDATE_JSON_RETRY is -1, it will run recursively until a valid json
#     response is returned.
#     """
#     json_response = {}
#     if nb_retry != 0:
#         response = client.chat.completions.create(
#             model=model,
#             response_model=None,
#             messages=messages,
#             temperature=0.1,
#         )
#         messages.append(response.choices[0].message)
#         content = response.choices[0].message.content
        
#         # Check if the content starts and ends with code block markers
#         if content.startswith("```json") and content.endswith("```"):
#             content = content[7:-3].strip()  # Remove the ```json and ``` markers

#         # see if json can be parsed
#         try:
#             json_start_index = content.index(
#                 "["
#             )  # find the starting position of the JSON data
#             json_data = content[
#                 json_start_index:
#             ]  # extract the JSON data from the response string
#             json_response = json.loads(json_data)
#             return json_response
#         except (json.decoder.JSONDecodeError, ValueError) as e:
#             cprint(f"{e}. Re-running the query.", "red")
#             # debug
#             cprint(f"\nGPT RESPONSE:\n\n{content}\n\n", "yellow")
#             # append a user message that says the json is invalid
#             messages.append(
#                 {
#                     "role": "user",
#                     "content": (
#                         "Your response could not be parsed by json.loads. "
#                         "Please restate your last message as pure JSON."
#                     ),
#                 }
#             )
#             # dec nb_retry
#             nb_retry -= 1
#             # rerun the api call
#             return json_validated_response(model, messages, nb_retry)
    
#         except Exception as e:
#             cprint(f"Unknown error: {e}", "red")
#             cprint(f"\nGPT RESPONSE:\n\n{content}\n\n", "yellow")
#             raise e
#     raise Exception(
#         f"No valid json response found after {VALIDATE_JSON_RETRY} tries. Exiting."
#     )

# def send_error_to_gpt(error_data: dict, model: str = DEFAULT_MODEL) -> Dict:
#     """Send test failure details to GPT"""
#     messages = [
#         {
#             "role": "system",
#             "content": SYSTEM_PROMPT 
#         },

#         {
#             "role": "user",
#             "content": f"Failed Test Details:\n{json.dumps(error_data, indent=2)}\n\n"
#             f"Relevant Code:\n{error_data['code_context']}"
#         }
#     ]
    
#     return json_validated_response(model, messages)

# def apply_fixes(fix_spec: dict):
#     """Apply fixes to different file types"""
#     # Handle list response format
#     print(fix_spec, "fix_spec")
    
    
#     for file_changes in fix_spec:
#         print(file_changes, "file_changes")
#         file_path = file_changes.get("file")
#         # print(file_path, "file_path")
#         if not file_path:
#             cprint("⚠️ Missing file path in fix specification", "red")
#             continue
            
#         # Create directory if needed
#         os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
#         # Read existing content if file exists
#         file_lines = []
#         if os.path.exists(file_path):
#             with open(file_path, "r") as f:
#                 file_lines = f.readlines()
                
#         # Apply operations
#         operations = file_changes.get("operations", [])
#         for op in sorted(operations, key=lambda x: x["line"], reverse=True):
#             line_num = op["line"] - 1  # Convert to 0-based index
#             operation = op["operation"]
#             content = op.get("content", "")
            
#             try:
#                 if operation == "Replace":
#                     file_lines[line_num] = content + "\n"
#                 elif operation == "InsertAfter":
#                     file_lines.insert(line_num + 1, content + "\n")
#                 elif operation == "Delete":
#                     del file_lines[line_num]
#             except IndexError:
#                 cprint(f"⚠️ Invalid line number {line_num+1} in {file_path}", "red")
                
#         # Write modified content
#         with open(file_path, "w") as f:
#             f.writelines(file_lines)
#         cprint(f"✅ Updated {file_path}", "green")

# def main():
#     """Main debugging loop"""
#     # Backup original files
#     shutil.copytree("generated", "generated.bak", dirs_exist_ok=True)
#     shutil.copytree("src", "src.bak", dirs_exist_ok=True)
    
#     iteration = 0
#     max_iterations = 5
    
#     while iteration < max_iterations:
#         iteration += 1
#         cprint(f"\n=== Iteration {iteration} ===", "cyan")
        
#         # Run Behave tests
#         output, returncode = run_behave()
        
#         if returncode == 0:
#             cprint("All tests passed!", "green")
#             return True
        
#         # Parse error output
#         failed_scenario = parse_failed_scenario(output)
#         failed_scenario["code_context"] = get_relevant_code(failed_scenario)
        
#         cprint(f"\nFailed Scenario: {failed_scenario['scenario_name']}", "red")
#         cprint(f"Error: {failed_scenario['error_message']}", "yellow")
        
#         # Get GPT suggestions
#         fix_spec = send_error_to_gpt(failed_scenario)
#         cprint("\nSuggested Fixes:", "blue")
#         print(json.dumps(fix_spec, indent=2))
        
#         # Apply fixes
#         apply_fixes(fix_spec)
        
#         # Confirm changes
#         cprint("\nApplied fixes. Rerunning tests...", "cyan")
    
#     cprint("Max iterations reached. Restoring backups...", "red")
#     shutil.rmtree("generated")
#     shutil.rmtree("src")
#     shutil.move("generated.bak", "generated")
#     shutil.move("src.bak", "src")
#     return False

# if __name__ == "__main__":
#     main()