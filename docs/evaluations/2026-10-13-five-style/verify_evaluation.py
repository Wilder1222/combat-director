"""Compatibility entry point; shared audit is read-only unless --out is given."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from audit_prompt_evaluations import main

if __name__ == "__main__":
    raise SystemExit(main(default_directory=Path(__file__).resolve().parent))
