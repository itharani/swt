import os
import glob
import re
import argparse
from dotenv import load_dotenv
import instructor
from openai import AzureOpenAI
from pathlib import Path
from step_processor import StepProcessor

class AITestGenerator:
    def __init__(self):
        load_dotenv()  
        self.client = self._setup_azure_client()
        self.brd = self._load_brd()
        self.report = self._load_report()
        self.codebase = self._scan_codebase()
        self.ensure_dirs()
        self.step_processor = StepProcessor()


    def _setup_azure_client(self):
        """Configure Azure OpenAI client with instructor"""
        return instructor.from_openai(
            AzureOpenAI(
                api_key=os.getenv("API_KEY"),
                api_version=os.getenv("LLM_API_VERSION"),
                azure_endpoint=os.getenv("BASE_URL"),
                azure_deployment=os.getenv("MODEL_DEPLOYMENT"),
            )
        )

    def ensure_dirs(self):
        """Create required directory structure"""
        os.makedirs("generated/features", exist_ok=True)
        os.makedirs("generated/steps", exist_ok=True)
        os.makedirs("generated/contracts", exist_ok=True)
        print("📁 Created directory structure")

    def generate_bdd_specs(self):
        print(self.report)
        """Generate Gherkin features using Azure OpenAI"""
        print("🛠️ Generating BDD features from BRD...")
        prompt = f"""
        Generate Gherkin features from these requirements for the following codebase. 
        Please pay extra attention to the evaluation report below and make sure to add Gherkin features that explicitly flag the FUNCTIONAL REQUIREMENTS that are partially unsatisfied or not satisfied at all, specifically those marked as CRITICAL or MODERATE in the report.
        requirements: {self.brd}
        codebase: {self.codebase}
        evaluation report: {self.report}
        
        Format requirements:
        - All the business requirements should be consolidated into only one .feature file.
        - Use Markdown code fences with language tag.
        - File names should match requirement IDs.
        - Include clear and concise step definitions that map to existing methods.
        - Do not generate overlapping steps that could potentially have different definition and context to avoid AmbiguousStep Error
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
        """Generate Behave steps using Azure client"""
        print("\n🛠️ Generating step definitions...")
        for feature in glob.glob("generated/features/*.feature"):
            with open(feature) as f:
                content = f.read()
                prompt = f"""
                Create Python Behave steps for this feature based on the following codebase:
                feature content: {content}
                entire codebase: {self.codebase}
                evaluation report: {self.report}
                
                Code location: src/implementation/
                Output format: Python code in markdown block

                Constraints:
                1. Only use methods or functions that exist in the codebase provided to you.
                2. Strictly do not generate steps that reference methods, functions or attributes not present in the codebase.
                3. Strictly ensure that each step definition is distinct and does not overlap with others.
                4. If the logic for 2 or more steps is the same, combine them into a single step definition.
                5. Use realistic and testable scenarios based on the available methods.
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
        return open("requirements/brd.md").read()
    

    def _load_report(self):
        """
        Load all files in the 'report' folder that end with 'report.md'.
        """
        report_folder = "reports"
        report_files = glob.glob(f"{report_folder}/*report.md")

        all_reports = []
        for report_file in report_files:
            try:
                with open(report_file, 'r') as file:
                    report_content = file.read()
                    all_reports.append((report_file, report_content))  # Store file path and content
            except Exception as e:
                print(f"Error reading {report_file}: {e}")
        
        print(all_reports)
        return all_reports
        
    def _scan_codebase(self):
        """Read actual code content with line numbers for better debugging context."""
        code_files = []
        for f in glob.glob('src/**/*.py', recursive=True):
            with open(f, 'r') as file:
                content = file.readlines()
                formatted_content = "\n".join(f"{i+1}: {line.rstrip()}" for i, line in enumerate(content))  # Limit to first 200 lines for brevity
                code_files.append(f"File: {f}\nContent:\n{formatted_content}")
        return "\n\n".join(code_files)

    def _save_features(self, content):
        """Extract and save Gherkin features from LLM response"""
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
                filepath = feature_dir / filename

                versioned_path = feature_dir / f"{filename[:-8]}.feature"
                with open(versioned_path, 'w') as f:
                    f.write(feature.strip())

                print(f"📄 Saved feature: {versioned_path}")

        except Exception as e:
            print(f"🔥 Failed to save features: {str(e)}")
            raise

    def _save_steps(self, feature_file, content):
        """Save Behave step implementations from LLM response"""
        try:
            # Extract Python code block from markdown
            code_match = re.search(r'```python\n(.*?)```', content, re.DOTALL)
            if not code_match:
                print(f"⚠️ No Python code found in steps for {feature_file}")
                return
                
            code = code_match.group(1).strip()
            
            # Create steps directory if not exists
            steps_dir = Path("generated/steps")
            steps_dir.mkdir(parents=True, exist_ok=True)

            # Generate steps filename from feature filename
            feature_path = Path(feature_file)
            steps_filename = f"{feature_path.stem}_steps.py"
            steps_path = steps_dir / steps_filename

            # Add import safety checks
            imports = (
                "from behave import given, when, then\n"
                "import sys\n"
                "sys.path.append('src/implementation')\n\n"
            )
            
            with open(steps_path, 'w') as f:
                f.write(imports + code)
                
            print(f"📝 Saved steps: {steps_path}")
            
            # Validate step implementation
            self._validate_steps(steps_path)

        except Exception as e:
            print(f"🔥 Failed to save steps: {str(e)}")
            raise

    def _validate_steps(self, steps_path):
        """Basic validation of generated steps"""
        try:
            with open(steps_path) as f:
                content = f.read()
                
            required_elements = [
                'from behave import',
                '@given', '@when', '@then',
                'def step_impl'
            ]
            
            for element in required_elements:
                if element not in content:
                    print(f"⚠️ Potential issue in {steps_path}: Missing {element}")
                    return False
                    
            return True
            
        except Exception as e:
            print(f"⚠️ Step validation failed: {str(e)}")
            return False


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
