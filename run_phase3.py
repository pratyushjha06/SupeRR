
from pathlib import Path
import argparse
from src.performance_engine import run_phase3

def main():
    p=argparse.ArgumentParser(description="Run PRESSURE-X Phase 3 player performance analysis.")
    p.add_argument("--input",default="outputs/pressure_classified_deliveries.csv")
    p.add_argument("--output-dir",default="outputs")
    p.add_argument("--report-dir",default="reports")
    a=p.parse_args()
    result=run_phase3(Path(a.input),Path(a.output_dir),Path(a.report_dir))
    print("PRESSURE-X Phase 3 completed.")
    for k,v in result.items(): print(f"{k}: {v}")

if __name__=="__main__": main()
