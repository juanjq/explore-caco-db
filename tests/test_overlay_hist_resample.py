import numpy as np
from grafana_test_utils import generate_sample_df, overlay_collections, compute_histogram, resample_df


def test_overlay_and_histogram_and_resample():
    df1 = generate_sample_df("a", periods=120, freq="S")
    df2 = generate_sample_df("b", periods=120, freq="S")
    combined = overlay_collections([df1, df2], names=["A", "B"])
    assert "A" in combined.columns and "B" in combined.columns

    counts, edges = compute_histogram(df1, "a", bins=10)
    assert counts.sum() == len(df1.dropna())

    resampled = resample_df(df1, rule="1T", agg="mean")
    # 120 seconds resampled per minute should produce <= 2 rows
    assert len(resampled) <= 2
