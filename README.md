# Data Quality Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688)
![Pandas](https://img.shields.io/badge/Pandas-150458)
![Tests](https://img.shields.io/badge/tests-pytest-brightgreen)

Bad data quietly breaks reports, dashboards and decisions. This project is a small web service
that checks a CSV file against a defined schema and returns a clear quality report: which rows
are wrong, why, and an overall quality score.

**Live demo:** **Live demo:** https://data-quality-pipeline-zggd.onrender.com/ _(free hosting: the first load after a quiet period can take about a minute)_

## What it checks

| Check | Example it catches |
|-------|--------------------|
| Missing columns / empty values | A required `customer_name` left blank |
| Wrong data types | `abc` in a price column, `not-a-date` in a date column |
| Invalid emails | `john@example` (no domain extension) |
| Out-of-range values | Quantity of `-3` or `5000` (allowed: 1 to 1000) |
| Disallowed categories | Country `Narnia` (not in the allowed list) |
| Duplicates | The same `order_id` appearing twice |

## How it works

1. A user uploads a CSV through the web page or the `/validate` API endpoint.
2. The file is read as plain text, so no type guessing hides errors.
3. Six small checks run against the rules in `app/schemas.py`.
4. The response is a JSON report with a quality score, a count per problem type, and every
   issue listed by CSV row number.

## Project structure

## Run locally

```bash
git clone https://github.com/Naisiae/Data-quality-pipeline.git
cd Data-quality-pipeline
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and drop in a file from `sample_data/`.
Interactive API docs are at http://127.0.0.1:8000/docs.

## Run the tests

```bash
pytest -v
```

## API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Web UI |
| GET | `/health` | Service health check |
| GET | `/schema` | The rules files are checked against |
| POST | `/validate` | Upload a CSV, receive the quality report |

Example:
```bash
curl -F "file=@sample_data/corrupt_dataset.csv" http://127.0.0.1:8000/validate
```

## Use it on your own data

Edit `app/schemas.py` to describe your columns (type, required, unique, min/max, allowed values).
No other code changes are needed.

## Author

Lilian Naisiae
