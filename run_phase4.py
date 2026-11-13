
from pathlib import Path
from src.rating_engine import run_phase4
if __name__=="__main__":
    result=run_phase4(Path("outputs"),Path("reports"))
    print("PRESSURE-X Phase 4.2 completed.")
    for k,v in result.items(): print(f"{k}: {v}")
