
from pathlib import Path
import argparse, sys
from src.pressure_engine import run_phase2

def main():
    parser = argparse.ArgumentParser(description="Run PRESSURE-X Phase 2 pressure classification.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--report-dir", default="reports")
    args = parser.parse_args()
    result = run_phase2(Path(args.data_dir), Path(args.output_dir), Path(args.report_dir))
    print("PRESSURE-X Phase 2 completed.")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
