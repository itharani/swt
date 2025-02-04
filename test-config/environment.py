import sys
from pathlib import Path

def before_all(context):
    # Add source directory to PYTHONPATH
    root_dir = Path(__file__).parent.parent
    sys.path.append(str(root_dir / "src"))
    sys.path.append(str(root_dir / "generated/steps"))