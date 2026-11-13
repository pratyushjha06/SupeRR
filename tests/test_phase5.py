import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_phase5_outputs_exist_and_cutline_decisions_are_auditable():
    csv_path = ROOT / 'outputs/phase5_cutline_governance_decisions.csv'
    json_path = ROOT / 'outputs/phase5_governance_decisions.json'
    report_path = ROOT / 'reports/phase5_cutline_governance_and_readiness.md'
    assert csv_path.exists() and json_path.exists() and report_path.exists()
    df = pd.read_csv(csv_path)
    assert set(df.role) == {'batter', 'bowler'}
    data = json.loads(json_path.read_text(encoding='utf-8'))
    assert data['practical_tie_tolerance_rating_points'] == 0.001
    assert 'not a statistically estimated confidence interval' in data['important_caveat']


def test_phase5_keeps_batter_incumbent_and_flags_bowler_near_tie():
    df = pd.read_csv(ROOT / 'outputs/phase5_cutline_governance_decisions.csv').set_index('role')
    assert df.loc['batter', 'governance_outcome'] == 'Aiden Markram'
    assert df.loc['bowler', 'strict_score_order'] == 'Anshul Kamboj'
    assert df.loc['bowler', 'governance_outcome'] == 'Sai Kishore'
    assert abs(df.loc['bowler', 'balanced_rating_gap_incumbent_minus_challenger']) <= 0.001
