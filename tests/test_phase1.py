from pathlib import Path
import pandas as pd
from src.data_loader import FILES

def test_expected_source_file_list():
    assert set(FILES) == {
        "competitions.csv", "teams.csv", "matches.csv", "ball_by_ball.csv",
        "competition_team_player_mapping.csv", "playing_eleven.csv"
    }

def test_raw_data_folder_has_expected_csvs():
    root = Path("data/raw")
    assert all((root / name).exists() for name in FILES)
