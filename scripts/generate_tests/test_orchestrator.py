"""
Module Name: test_orchestrator.py

This module provides functionality for automatically generating BDD (Behavior-Driven Development) 
test cases and step definitions using an AI-powered pipeline. 

Features:
- Loads environment variables and initializes the Azure OpenAI client.
- Parses Business Requirement Documents (BRD) and evaluation reports.
- Scans the codebase for Python files to extract context.
- Generates Gherkin BDD features based on business requirements and codebase.
- Creates Behave step definitions from the generated BDD features.
- Ensures the generated test cases are aligned with business logic and existing code.

Usage:
    Run this script with the `--generate` argument to trigger the test generation process.

Dependencies:
- os
- glob
- re
- argparse
- dotenv
- instructor
- AzureOpenAI
- pathlib
- StepProcessor
"""

import os
import glob
import re
import argparse
from dotenv import load_dotenv
import instructor
from openai import AzureOpenAI
from pathlib import Path
from scripts.generate_tests.step_processor import StepProcessor

class AITestGenerator:
    """
    AITestGenerator automates the generation of BDD test specifications and step definitions 
    from business requirements, leveraging an AI-powered pipeline.

    Attributes:
        client (AzureOpenAI): Configured OpenAI client for AI-based processing.
        brd (str): Business Requirement Document content.
        report (list): Evaluation report highlighting functional requirement gaps.
        codebase (str): Scanned Python codebase for generating test cases.
        step_processor (StepProcessor): Utility for handling step definitions.
    """

    def __init__(self):
        """
        Initializes the AITestGenerator, setting up the necessary components:
        - Load environment variables from .env file.
        - Set up the Azure OpenAI client.
        - Load the BRD (Business Requirement Document).
        - Load the evaluation report.
        - Scan the codebase for relevant files.
        - Ensure required directories are created.
        - Initialize StepProcessor for handling step definitions.
        """
        load_dotenv()
        self.client = self._setup_azure_client()
        self.brd = self._load_brd()
        self.report = self._load_report()
        self.codebase = self._scan_codebase()
        self.ensure_dirs()
        self.step_processor = StepProcessor()

    def _setup_azure_client(self):
        """
        Configures and initializes the Azure OpenAI client using environment variables.

        Returns:
            AzureOpenAI: The configured Azure OpenAI client.
        """
        return instructor.from_openai(
            AzureOpenAI(
                api_key=os.getenv("API_KEY"),
                api_version=os.getenv("LLM_API_VERSION"),
                azure_endpoint=os.getenv("BASE_URL"),
                azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
            )
        )

    def ensure_dirs(self):
        """
        Ensures the existence of required directories for storing generated BDD features and step definitions.

        Returns:
            None
        """
        os.makedirs("generated/features", exist_ok=True)
        os.makedirs("generated/steps", exist_ok=True)
        print("📁 Created directory structure")

    def generate_bdd_specs(self):
        """
        Generates Gherkin BDD features from the BRD using the Azure OpenAI model.
        The evaluation report is considered to prioritize generating test cases for critical and moderate issues.

        Returns:
            None
        """
        print("🛠️ Generating BDD features from BRD...")
        prompt = f"""
        Generate Gherkin features from these requirements for the following codebase.
        Ensure critical and moderate functional gaps flagged in the evaluation report are covered.
        requirements: {self.brd}
        codebase: {self.codebase}
        evaluation report: {self.report}
        """
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("MODEL_NAME"),
                response_model=None,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            test_script = response.choices[0].message.content.strip()
            self._save_features(test_script)
            print("✅ Generated BDD features")
        except Exception as e:
            print(f"❌ Feature generation failed: {str(e)}")
            raise

    def generate_step_definitions(self):
        """
        Generates Behave step definitions from the Gherkin feature files.

        Returns:
            None
        """
        print("\n🛠️ Generating step definitions...")
        for feature in glob.glob("generated/features/*.feature"):
            with open(feature) as f:
                content = f.read()
                prompt = f"""
                Create Python Behave steps for this feature based on the following codebase.
                feature content: {content}
                entire codebase: {self.codebase}
                evaluation report: {self.report}
                """
                response = self.client.chat.completions.create(
                    model=os.getenv("MODEL_NAME"),
                    response_model=None,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                self.step_processor._save_steps(feature, response.choices[0].message.content)
        print("✅ Generated step definitions")

    def _load_brd(self):
        """
        Loads the Business Requirement Document (BRD) from a file.

        Returns:
            str: The content of the BRD file.
        """
        return open("requirements/brd.md").read()

    def _load_report(self):
        """
        Loads all report files in the 'reports' directory ending with 'report.md'.

        Returns:
            list: A list of tuples (report file path, content).
        """
        report_files = glob.glob("reports/*report.md")
        all_reports = []
        for report_file in report_files:
            try:
                with open(report_file, 'r') as file:
                    all_reports.append((report_file, file.read()))
            except Exception as e:
                print(f"Error reading {report_file}: {e}")
        return all_reports

    def _scan_codebase(self):
        """
        Scans the codebase for Python files and formats their content with line numbers.

        Returns:
            str: The formatted content of all Python files in the codebase.
        """
        code_files = []
        for f in glob.glob('src/**/*.py', recursive=True):
            with open(f, 'r') as file:
                content = file.readlines()
                formatted_content = "\n".join(f"{i+1}: {line.rstrip()}" for i, line in enumerate(content))
                code_files.append(f"File: {f}\nContent:\n{formatted_content}")
        return "\n\n".join(code_files)

    def _save_features(self, content):
        """
        Saves the generated Gherkin feature content into '.feature' files.

        Args:
            content (str): The Gherkin feature content.

        Returns:
            None
        """
        try:
            features = re.findall(r'```gherkin\n(.*?)```', content, re.DOTALL)
            if not features:
                print("⚠️ No Gherkin features found in LLM response")
                return

            feature_dir = Path("generated/features")
            feature_dir.mkdir(parents=True, exist_ok=True)

            for idx, feature in enumerate(features, 1):
                title_match = re.search(r'Feature:\s*(.+?)\n', feature)
                title = title_match.group(1).strip() if title_match else f"feature_{idx}"
                filename = re.sub(r'[^a-zA-Z0-9]+', '_', title).lower() + ".feature"
                with open(feature_dir / filename, 'w') as f:
                    f.write(feature.strip())

                print(f"📄 Saved feature: {filename}")

        except Exception as e:
            print(f"🔥 Failed to save features: {str(e)}")
            raise

def main():
    """
    Parses command-line arguments and triggers test generation when '--generate' is passed.

    Returns:
        None
    """
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
