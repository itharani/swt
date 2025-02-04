import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
import instructor
from typing import Dict
from pathlib import Path

load_dotenv()

def _load_brd(brd_path: str) -> Dict:
    with open(brd_path, "r") as f:
        return json.load(f)

def _scan_codebase(codebase_path: str) -> str:
    code_files = []
    for file_path in Path(codebase_path).rglob("*.py"):
        with open(file_path, "r") as f:
            content = f.read()
            code_files.append(f"File: {file_path}\nContent:\n{content}")
    return "\n\n".join(code_files)

def generate_report():
    system_prompt = open("code_review.md").read()
    message_to_llm = {
        "business_requirements": _load_brd("requirements/brd.json"),
        "codebase": _scan_codebase("src")
    }

    client = instructor.from_openai(
        AzureOpenAI(
            api_key=os.getenv("API_KEY"),
            api_version=os.getenv("LLM_API_VERSION"),
            azure_endpoint=os.getenv("BASE_URL"),
            azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
        )
    )

    response = client.chat.completions.create(
        model=os.getenv("DEFAULT_MODEL"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(message_to_llm, indent=2)}
        ],
        temperature=0.1
    )

    llm_report = response.choices[0].message.content.strip()
    with open("reports/requirement_satisfaction_report.md", "w") as report_file:
        report_file.write(llm_report)

if __name__ == "__main__":
    generate_report()