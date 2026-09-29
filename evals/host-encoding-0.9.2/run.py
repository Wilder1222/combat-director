"""Repeat affected requests on the frozen recovery-guide candidate."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('host_runner', ROOT / 'evals/host-0.9.1/run_routing.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

if __name__ == '__main__':
    raise SystemExit(runner.main(
        Path(__file__).with_name('cases.json'),
        ROOT / 'evals/results/host-encoding-0.9.2',
        ROOT / 'dist/combat-director-0.9.2.zip'))
