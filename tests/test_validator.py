import pandas as pd

from app.validator import check_duplicates, check_missing, check_ranges
from app.schemas import EXPECTED_SCHEMA


def test_missing_value_reports_correct_csv_row():
    df = pd.DataFrame({"customer_name": ["Amina", ""]})
    issues = check_missing(df, EXPECTED_SCHEMA)
    assert len(issues) == 1
    assert issues[0]["row"] == 3  # 2nd data row = row 3 in the CSV (header is row 1)


def test_duplicate_flags_only_the_repeat():
    df = pd.DataFrame({"order_id": ["1", "2", "2"]})
    issues = check_duplicates(df, EXPECTED_SCHEMA)
    assert [i["row"] for i in issues] == [4]


def test_range_catches_low_and_high():
    df = pd.DataFrame({"quantity": ["5", "-3", "5000"]})
    issues = check_ranges(df, EXPECTED_SCHEMA)
    assert [i["row"] for i in issues] == [3, 4]
