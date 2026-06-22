import pandas as pd
import numpy as np
from app.analytics.data_analyzer import DataAnalyzer


def test_summary_shape():
    df = pd.DataFrame({
        "sales": [100, 200, 150, 300, 250],
        "region": ["North", "South", "East", "West", "North"],
        "month": [1, 2, 3, 4, 5]
    })
    analyzer = DataAnalyzer()
    analyzer.load_dataframe(df, "test.csv")
    summary = analyzer.get_summary()
    assert summary["shape"]["rows"] == 5
    assert summary["shape"]["columns"] == 3
    assert "sales" in summary["numeric_columns"]
    assert "region" in summary["categorical_columns"]


def test_anomaly_detection():
    df = pd.DataFrame({
        "values": [10, 12, 11, 13, 10, 1000, 9, 11]
    })
    analyzer = DataAnalyzer()
    analyzer.load_dataframe(df, "test.csv")
    anomalies = analyzer.detect_anomalies()
    assert len(anomalies) > 0
    assert anomalies[0]["column"] == "values"


def test_no_anomalies():
    df = pd.DataFrame({
        "values": [10, 11, 10, 12, 11, 10, 11, 12]
    })
    analyzer = DataAnalyzer()
    analyzer.load_dataframe(df, "test.csv")
    anomalies = analyzer.detect_anomalies()
    assert len(anomalies) == 0


def test_missing_values():
    df = pd.DataFrame({
        "a": [1, 2, None, 4],
        "b": ["x", None, "z", "w"]
    })
    analyzer = DataAnalyzer()
    analyzer.load_dataframe(df, "test.csv")
    summary = analyzer.get_summary()
    assert summary["missing_values"]["a"] == 1
    assert summary["missing_values"]["b"] == 1


def test_charts_generated():
    df = pd.DataFrame({
        "sales": [100, 200, 150, 300, 250, 180, 220],
        "cost":  [80,  160, 120, 240, 200, 140, 170],
        "region": ["N", "S", "E", "W", "N", "S", "E"]
    })
    analyzer = DataAnalyzer()
    analyzer.load_dataframe(df, "test.csv")
    charts = analyzer.generate_charts()
    assert len(charts) > 0
