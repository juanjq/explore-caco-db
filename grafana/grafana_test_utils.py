import json
from typing import List, Tuple
import pandas as pd
import numpy as np
from datetime import datetime


def save_session(session: dict, path: str):
    # Convert datetimes to ISO format for JSON
    serializable = {}
    for k, v in session.items():
        if isinstance(v, datetime):
            serializable[k] = v.isoformat()
        else:
            serializable[k] = v
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


def load_session(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Try to parse ISO datetimes back to datetime objects
    for k, v in list(data.items()):
        if isinstance(v, str):
            try:
                data[k] = datetime.fromisoformat(v)
            except Exception:
                pass
    return data


def overlay_collections(dfs: List[pd.DataFrame], names: List[str] = None) -> pd.DataFrame:
    """Overlay multiple time-series DataFrames by outer-joining on their datetime index.
    Each DataFrame should have a single value column (or will be reduced to numeric columns).
    Columns will be suffixed with provided names or incremental indices.
    """
    if not dfs:
        return pd.DataFrame()
    if names is None:
        names = [f"c{i}" for i in range(len(dfs))]
    renamed = []
    for df, n in zip(dfs, names):
        d = df.copy()
        # Ensure index is datetime
        if not pd.api.types.is_datetime64_any_dtype(d.index):
            d.index = pd.to_datetime(d.index)
        # If more than one column, take numeric columns only
        numeric_cols = d.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols and len(d.columns) > 0:
            # try to coerce
            d = d.apply(pd.to_numeric, errors="coerce")
            numeric_cols = d.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            # create a single column from first column
            d.columns = [f"{n}"]
        else:
            d = d[numeric_cols].rename(columns={numeric_cols[0]: f"{n}"})
        renamed.append(d[[col for col in d.columns]])
    # Outer join on index
    result = pd.concat(renamed, axis=1, join="outer").sort_index()
    return result


def compute_histogram(df: pd.DataFrame, column: str, bins: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    series = df[column].dropna().values
    counts, edges = np.histogram(series, bins=bins)
    return counts, edges


def resample_df(df: pd.DataFrame, rule: str = "1T", agg: str = "mean") -> pd.DataFrame:
    """Resample a DataFrame with a datetime index.

    rule examples: '1S', '1T', '1H' (per-second, per-minute, per-hour)
    agg: aggregation method name supported by pandas (mean, sum, median)
    """
    d = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(d.index):
        d.index = pd.to_datetime(d.index)
    try:
        res = getattr(d.resample(rule), agg)()
    except Exception:
        # fallback to mean
        res = d.resample(rule).mean()
    return res


def generate_sample_df(name: str = "val", start: str = "2026-02-01 00:00:00", periods: int = 3600, freq: str = "S") -> pd.DataFrame:
    idx = pd.date_range(start=start, periods=periods, freq=freq)
    values = np.sin(np.linspace(0, 20, periods)) + np.random.normal(scale=0.1, size=periods)
    return pd.DataFrame({name: values}, index=idx)
