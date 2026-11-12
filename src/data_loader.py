from pathlib import Path
import pandas as pd

FILES = [
    "competitions.csv", "teams.csv", "matches.csv", "ball_by_ball.csv",
    "competition_team_player_mapping.csv", "playing_eleven.csv",
]

def load_dataset(data_dir="data/raw", nrows=None):
    """Load supplied CSVs. nrows is useful for quick schema inspection."""
    root = Path(data_dir)
    missing = [name for name in FILES if not (root / name).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing required CSV(s) in {root.resolve()}: {', '.join(missing)}"
        )
    frames = {}
    for name in FILES:
        frames[name.removesuffix(".csv")] = pd.read_csv(
            root / name, low_memory=False, nrows=nrows
        )
    return frames
