"""Run one frozen matrix request through the existing isolated-host runner."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('host_runner', ROOT / 'evals/host-0.9.1/run_routing.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

if __name__ == '__main__':
    raise SystemExit(runner.main(Path(__file__).with_name('cases.json'), ROOT / 'evals/results/host-motion-matrix-0.9.1'))
