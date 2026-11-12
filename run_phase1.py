from src.audit import run_audit
from src.explore import run_exploration
import json

if __name__ == "__main__":
    audit = run_audit()
    eda = run_exploration()
    print("\\nPHASE 1 COMPLETE")
    print("Audit summary:")
    print(json.dumps({
        "tables": {k: {"rows": v["rows"], "columns": v["columns"]} for k,v in audit["tables"].items()},
        "coverage": audit["coverage_checks"],
        "date_range": audit["date_range"],
        "eda_player_counts": {
            "batters": eda["unique_batters_in_delivery_data"],
            "bowlers": eda["unique_bowlers_in_delivery_data"],
            "playing_eleven_players": eda["unique_players_in_playing_eleven"]
        }
    }, indent=2))
    print("\\nDetailed outputs saved in outputs/")
