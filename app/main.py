import io
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.schemas import EXPECTED_SCHEMA
from app.validator import validate_dataframe

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Data Quality Pipeline",
    description="Upload a CSV and get a data-quality report.",
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
def home():
    """Serve the one-page web UI."""
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/schema")
def get_schema():
    """Show the rules uploaded files are checked against."""
    return EXPECTED_SCHEMA


@app.post("/validate")
async def validate(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content), dtype=str)  # read all as text; we check types ourselves
    except Exception:
        raise HTTPException(status_code=422, detail="Could not parse the file as CSV")
    return validate_dataframe(df)
