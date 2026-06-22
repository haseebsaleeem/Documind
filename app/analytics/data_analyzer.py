from typing import Dict, Any, List, Optional
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from app.config import config


class DataAnalyzer:
    """
    Automated CSV/Excel analytics engine with AI-powered insights.
    Uses direct REST API calls to Gemini — no SDK required.
    """

    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.base_url = config.GEMINI_BASE_URL
        self.df: Optional[pd.DataFrame] = None
        self.filename: str = ""

    # ------------------------------------------------------------------ #
    #  LLM                                                                 #
    # ------------------------------------------------------------------ #

    def _generate(self, prompt: str) -> str:
        """Call Gemini REST API directly."""
        url = f"{self.base_url}/{config.GEMINI_MODEL}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2048
            }
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[DataAnalyzer] LLM error: {e}")
            return f"Could not generate AI insights: {str(e)}"

    # ------------------------------------------------------------------ #
    #  DATA LOADING                                                        #
    # ------------------------------------------------------------------ #

    def load(self, file_path: str) -> Dict[str, Any]:
        """Load CSV or Excel file from disk path."""
        try:
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
            elif file_path.endswith((".xlsx", ".xls")):
                self.df = pd.read_excel(file_path)
            else:
                return {"success": False, "error": "Unsupported file type."}
            self.filename = file_path
            return {"success": True, "rows": len(self.df), "columns": len(self.df.columns)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_dataframe(self, df: pd.DataFrame, name: str = "uploaded"):
        """Load from an already-parsed DataFrame."""
        self.df = df
        self.filename = name

    # ------------------------------------------------------------------ #
    #  ANALYSIS                                                            #
    # ------------------------------------------------------------------ #

    def get_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics."""
        if self.df is None:
            return {}

        numeric_cols = self.df.select_dtypes(
            include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(
            include=["object", "category"]).columns.tolist()
        date_cols = self.df.select_dtypes(
            include=["datetime64"]).columns.tolist()

        summary = {
            "shape": {"rows": len(self.df), "columns": len(self.df.columns)},
            "columns": list(self.df.columns),
            "dtypes": self.df.dtypes.astype(str).to_dict(),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "date_columns": date_cols,
            "missing_values": self.df.isnull().sum().to_dict(),
            "missing_percent": (self.df.isnull().sum() / len(self.df) * 100).round(2).to_dict(),
            "duplicate_rows": int(self.df.duplicated().sum()),
        }

        if numeric_cols:
            desc = self.df[numeric_cols].describe().round(4)
            summary["statistics"] = desc.to_dict()

        return summary

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect statistical anomalies using IQR method."""
        if self.df is None:
            return []

        anomalies = []
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            series = self.df[col].dropna()
            if len(series) < 4:
                continue
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = series[(series < lower) | (series > upper)]

            if len(outliers) > 0:
                anomalies.append({
                    "column": col,
                    "outlier_count": len(outliers),
                    "outlier_percent": round(len(outliers) / len(series) * 100, 2),
                    "lower_bound": round(lower, 4),
                    "upper_bound": round(upper, 4),
                    "sample_outliers": outliers.head(3).tolist()
                })

        return anomalies

    def generate_charts(self) -> List[go.Figure]:
        """Auto-generate relevant charts based on data types."""
        if self.df is None:
            return []

        charts = []
        numeric_cols = self.df.select_dtypes(
            include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(
            include=["object"]).columns.tolist()

        # 1. Distribution histograms for numeric columns
        for col in numeric_cols[:3]:
            fig = px.histogram(
                self.df, x=col, nbins=30,
                title=f"Distribution: {col}",
                color_discrete_sequence=["#6366f1"]
            )
            fig.update_layout(template="plotly_dark",
                              paper_bgcolor="rgba(0,0,0,0)")
            charts.append(fig)

        # 2. Correlation heatmap
        if len(numeric_cols) >= 2:
            corr = self.df[numeric_cols].corr().round(2)
            fig = go.Figure(data=go.Heatmap(
                z=corr.values,
                x=list(corr.columns),
                y=list(corr.index),
                colorscale="RdBu",
                text=corr.values.round(2),
                texttemplate="%{text}"
            ))
            fig.update_layout(
                title="Correlation Heatmap",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            charts.append(fig)

        # 3. Bar chart: top categorical vs numeric
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            top = self.df.groupby(
                cat_col)[num_col].mean().nlargest(10).reset_index()
            fig = px.bar(
                top, x=cat_col, y=num_col,
                title=f"Average {num_col} by {cat_col}",
                color=num_col,
                color_continuous_scale="Viridis"
            )
            fig.update_layout(template="plotly_dark",
                              paper_bgcolor="rgba(0,0,0,0)")
            charts.append(fig)

        # 4. Box plots for outlier visualization
        if numeric_cols:
            fig = go.Figure()
            for col in numeric_cols[:4]:
                fig.add_trace(go.Box(y=self.df[col].dropna(), name=col))
            fig.update_layout(
                title="Outlier Analysis (Box Plots)",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            charts.append(fig)

        # 5. Missing values chart
        missing = self.df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) > 0:
            fig = px.bar(
                x=list(missing.index),
                y=list(missing.values),
                title="Missing Values per Column",
                labels={"x": "Column", "y": "Missing Count"},
                color=list(missing.values),
                color_continuous_scale="Reds"
            )
            fig.update_layout(template="plotly_dark",
                              paper_bgcolor="rgba(0,0,0,0)")
            charts.append(fig)

        return charts

    def ai_insights(self) -> str:
        """Use Gemini to generate natural language insights about the data."""
        if self.df is None:
            return "No data loaded."

        summary = self.get_summary()
        anomalies = self.detect_anomalies()

        stats_text = ""
        if "statistics" in summary:
            for col, stats in list(summary["statistics"].items())[:5]:
                mean_val = stats.get('mean', 0)
                std_val = stats.get('std', 0)
                min_val = stats.get('min', 0)
                max_val = stats.get('max', 0)
                stats_text += f"\n{col}: mean={mean_val:.2f}, std={std_val:.2f}, min={min_val}, max={max_val}"

        anomaly_text = ""
        for a in anomalies:
            anomaly_text += f"\n- {a['column']}: {a['outlier_count']} outliers ({a['outlier_percent']}%)"

        prompt = f"""You are a senior data analyst. Analyze the following dataset summary and provide actionable insights.

Dataset: {self.filename}
Shape: {summary['shape']['rows']} rows x {summary['shape']['columns']} columns
Columns: {', '.join(summary['columns'][:15])}
Numeric columns: {', '.join(summary['numeric_columns'][:8])}
Categorical columns: {', '.join(summary['categorical_columns'][:5])}
Missing values total: {sum(v for v in summary['missing_values'].values() if v > 0)}
Duplicate rows: {summary['duplicate_rows']}

Key Statistics:
{stats_text if stats_text else "No numeric statistics available."}

Anomalies detected:
{anomaly_text if anomaly_text else "None detected"}

Provide a professional analysis with these sections:
1. Data Quality Assessment
2. Key Trends and Patterns
3. Anomalies and Concerns
4. Business Recommendations
5. Suggested Further Analysis

Be specific, professional, and data-driven."""

        return self._generate(prompt)
