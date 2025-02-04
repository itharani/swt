import os
import glob
import re
import argparse
from dotenv import load_dotenv
from openai import AzureOpenAI
import instructor
import json
from pathlib import Path
from typing import List, Dict

load_dotenv()

class AITestGenerator:
    def __init__(self):
        self.client = self._setup_azure_client()
        self.brd = self._load_brd("requirements/brd.json")
        self.codebase = self._scan_codebase("src")
        self.ensure_dirs()

    def _setup_azure_client(self):
        return instructor.from_openai(
            AzureOpenAI(
                api_key=os.getenv("API_KEY"),
                api_version=os.getenv("LLM_API_VERSION"),
                azure_endpoint=os.getenv("BASE_URL"),
                azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
            )
        )

    def ensure_dirs(self):
        os.makedirs("generated/features", exist_ok=True)
        os.makedirs("generated/steps", exist_ok=True)
        os.makedirs("generated/contracts", exist_ok=True)

    def generate_bdd_specs(self):
        prompt = f"""
        Generate Gherkin features from:
        - BRD: {json.dumps(self.brd, indent=2)}
        - Codebase: {self.codebase}
        """
        response = self.client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            response_model=None,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        self._save_features(response.choices[0].message.content)

    def generate_step_definitions(self):
        for feature in glob.glob("generated/features/*.feature"):
            with open(feature, "r") as f:
                content = f.read()
                prompt = f"""
                Create Python Behave steps for:
                - Feature: {content}
                - Codebase: {self.codebase}
                """
                response = self.client.chat.completions.create(
                    model=os.getenv("MODEL_NAME"),
                    response_model=None,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                self._save_steps(feature, response.choices[0].message.content)

    def _load_brd(self, brd_path: str) -> Dict:
        with open(brd_path, "r") as f:
            return json.load(f)

    def _scan_codebase(self, codebase_path: str) -> str:
        code_files = []
        for file_path in Path(codebase_path).rglob("*.py"):
            with open(file_path, "r") as f:
                content = f.read()
                code_files.append(f"File: {file_path}\nContent:\n{content}")
        return "\n\n".join(code_files)

    def _save_features(self, content: str):
        features = re.findall(r'```gherkin\n(.*?)```', content, re.DOTALL)
        for idx, feature in enumerate(features):
            feature_path = Path("generated/features") / f"feature_{idx}.feature"
            with open(feature_path, "w") as f:
                f.write(feature.strip())

    def _save_steps(self, feature_file: str, content: str):
        steps_path = Path("generated/steps") / f"{Path(feature_file).stem}_steps.py"
        with open(steps_path, "w") as f:
            f.write(content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true', help='Generate tests from BRD')
    args = parser.parse_args()

    if args.generate:
        generator = AITestGenerator()
        generator.generate_bdd_specs()
        generator.generate_step_definitions()
    else:
        print("ℹ️ No action specified. Use --generate")

if __name__ == "__main__":
    main()