"""Audit the recovery candidate using the same source-matching method."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('host_audit', ROOT / 'evals/host-motion-matrix-0.9.1/summarize.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

if __name__ == '__main__':
    audit.main(Path(__file__).with_name('cases.json'),
               ROOT / 'evals/results/host-encoding-0.9.2',
               ROOT / 'dist/combat-director-0.9.2.zip')
