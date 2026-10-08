"""Core validation logic. Each check is a small function that returns a list
of issues, so they are easy to read, test and extend."""

import pandas as pd

from app.schemas import EXPECTED_SCHEMA


def _issue(check, column, row, message):
    """Build one issue record. `row` is the CSV row number (header = row 1)."""
    return {"check": check, "column": column, "row": row, "message": message}


def check_columns(df, schema):
    issues = []
    for col in schema:
        if col not in df.columns:
            issues.append(_issue("missing_column", col, None, f"Column '{col}' is missing"))
    return issues


def check_missing(df, schema):
    issues = []
    for col, rules in schema.items():
        if col in df.columns and rules.get("required"):
            for idx in df.index[df[col].isna() | (df[col].astype(str).str.strip() == "")]:
                issues.append(_issue("missing_value", col, int(idx) + 2, "Required value is empty"))
    return issues


EMAIL_PATTERN = r"^[\w\.\+\-]+@[\w\-]+\.[\w\.\-]+$"


def check_types(df, schema):
    issues = []
    for col, rules in schema.items():
        if col not in df.columns:
            continue
        kind = rules["type"]
        series = df[col].dropna()
        if kind in ("int", "float"):
            converted = pd.to_numeric(series, errors="coerce")
            bad = series[converted.isna()]
            if kind == "int":
                good = converted.dropna()
                bad = pd.concat([bad, good[good % 1 != 0]])
        elif kind == "date":
            bad = series[pd.to_datetime(series, errors="coerce").isna()]
        elif kind == "email":
            bad = series[~series.astype(str).str.match(EMAIL_PATTERN)]
        else:
            continue
        for idx, val in bad.items():
            issues.append(_issue("invalid_type", col, int(idx) + 2, f"'{val}' is not a valid {kind}"))
    return issues


def check_ranges(df, schema):
    issues = []
    for col, rules in schema.items():
        if col not in df.columns or ("min" not in rules and "max" not in rules):
            continue
        nums = pd.to_numeric(df[col], errors="coerce")
        if "min" in rules:
            for idx in nums[nums < rules["min"]].index:
                issues.append(_issue("out_of_range", col, int(idx) + 2,
                                     f"{nums[idx]} is below minimum {rules['min']}"))
        if "max" in rules:
            for idx in nums[nums > rules["max"]].index:
                issues.append(_issue("out_of_range", col, int(idx) + 2,
                                     f"{nums[idx]} is above maximum {rules['max']}"))
    return issues


def check_allowed_values(df, schema):
    issues = []
    for col, rules in schema.items():
        if col in df.columns and "allowed" in rules:
            bad = df[col].dropna()
            bad = bad[~bad.isin(rules["allowed"])]
            for idx, val in bad.items():
                issues.append(_issue("invalid_value", col, int(idx) + 2,
                                     f"'{val}' not in allowed values {rules['allowed']}"))
    return issues


def check_duplicates(df, schema):
    issues = []
    for col, rules in schema.items():
        if col in df.columns and rules.get("unique"):
            dupes = df[df[col].duplicated(keep="first") & df[col].notna()]
            for idx, val in dupes[col].items():
                issues.append(_issue("duplicate", col, int(idx) + 2, f"Duplicate value '{val}'"))
    return issues


def validate_dataframe(df, schema=EXPECTED_SCHEMA):
    """Run every check and return a summary report."""
    issues = []
    for check in (check_columns, check_missing, check_types,
                  check_ranges, check_allowed_values, check_duplicates):
        issues.extend(check(df, schema))

    bad_rows = {i["row"] for i in issues if i["row"] is not None}
    total = len(df)
    quality_score = round(100 * (1 - len(bad_rows) / total), 1) if total else 0.0

    summary = {}
    for i in issues:
        summary[i["check"]] = summary.get(i["check"], 0) + 1

    return {
        "total_rows": total,
        "rows_with_issues": len(bad_rows),
        "total_issues": len(issues),
        "quality_score": quality_score,
        "passed": len(issues) == 0,
        "issues_by_check": summary,
        "issues": issues,
    }
