import re
import hashlib
from pathlib import Path

class StepProcessor:
    def __init__(self):
        self.step_registry = {}  # Dictionary to track step tags and their implementations

    def _generate_hash(self, content):
        """Generate a hash for the step function content to detect duplicates."""
        return hashlib.md5(content.encode()).hexdigest()

    def _save_steps(self, feature_file, content):
        """Save Behave step implementations from LLM response and avoid duplicate step ambiguities."""
        try:
            # Extract Python code block from markdown
            code_match = re.search(r'```python\n(.*?)```', content, re.DOTALL)
            if not code_match:
                print(f"⚠️ No Python code found in steps for {feature_file}")
                return
                
            code = code_match.group(1).strip()
            
            # Find all step decorators (e.g., @given, @when, @then)
            step_patterns = re.findall(r'@(given|when|then)\(["\'](.+?)["\']\)', code)

            if not step_patterns:
                print(f"⚠️ No valid step definitions found in {feature_file}")
                return
            
            steps_dir = Path("generated/steps")
            steps_dir.mkdir(parents=True, exist_ok=True)
            
            feature_path = Path(feature_file)
            steps_filename = f"{feature_path.stem}_steps.py"
            steps_path = steps_dir / steps_filename

            imports = (
                "from behave import given, when, then\n"
                "import sys\n"
                "sys.path.append('src/implementation')\n\n"
            )
            
            updated_code = code
            renamed_steps = {}

            for step_type, step_text in step_patterns:
                step_hash = self._generate_hash(step_text)
                
                if step_text in self.step_registry:
                    existing_hash = self._generate_hash(self.step_registry[step_text])
                    new_hash = self._generate_hash(code)
                    
                    if existing_hash != new_hash:  # Different implementation
                        new_step_text = f"{step_text} (variant {step_hash[:6]})"
                        renamed_steps[step_text] = new_step_text
                        updated_code = updated_code.replace(f'@{step_type}("{step_text}")', f'@{step_type}("{new_step_text}")')
                        print(f"🔄 Renamed step: {step_text} -> {new_step_text}")
                
                # Store the step definition
                self.step_registry[step_text] = code
            
            with open(steps_path, 'w') as f:
                f.write(imports + updated_code)
                
            print(f"📝 Saved steps: {steps_path}")

            # Update feature files if necessary
            if renamed_steps:
                self._update_feature_files(renamed_steps)

        except Exception as e:
            print(f"🔥 Failed to save steps: {str(e)}")
            raise

    def _update_feature_files(self, renamed_steps):
        """Update feature files with renamed step tags to maintain consistency."""
        feature_dir = Path("generated/features")

        for feature_file in feature_dir.glob("*.feature"):
            with open(feature_file, "r") as f:
                content = f.read()
            
            updated_content = content
            for old_step, new_step in renamed_steps.items():
                updated_content = updated_content.replace(old_step, new_step)

            if updated_content != content:  # Only overwrite if changes were made
                with open(feature_file, "w") as f:
                    f.write(updated_content)
                print(f"✅ Updated feature file: {feature_file}")

