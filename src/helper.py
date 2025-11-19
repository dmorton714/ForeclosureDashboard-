from typing import Any, Dict, List, Tuple, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def convert_types(
    df: pd.DataFrame, 
    types: Union[List, Dict[Union[int, str], Any]]
) -> pd.DataFrame:
    """
    Convert DataFrame columns to specified data types.

    This function iterates through a dictionary or list of types and applies
    them to the corresponding columns of a DataFrame.

    Args:
        df: The pandas DataFrame to modify.
        types: A list of types or a dictionary mapping column index/name
               to the target data type.

    Returns:
        The DataFrame with columns converted to the specified types.
    """
    if isinstance(types, list):
        types = {i: t for i, t in enumerate(types)}

    for col, dtype in types.items():
        try:
            col_name = df.columns[col] if isinstance(col, int) else col
            df[col_name] = _convert_series(df[col_name], dtype)
        except Exception as e:
            print(f"Error converting column {col} ({col_name}): {e}")
            raise
    return df


def _convert_series(s: pd.Series, dtype: Any) -> pd.Series:
    """
    Convert a single pandas Series to the target dtype with error handling.

    Args:
        s: The pandas Series to convert.
        dtype: The target data type (e.g., int, str, "datetime64[ns]").

    Returns:
        The converted pandas Series.
    """
    if dtype == "datetime64[ns]":
        return pd.to_datetime(s, errors="coerce", utc=False)
    elif dtype == int:
        # Use nullable integer type to handle potential NaNs
        return pd.to_numeric(s, errors="coerce").astype("Int64")
    elif dtype == float:
        return pd.to_numeric(s, errors="coerce")
    elif dtype == str:
        return s.astype("string")
    else:
        return s.astype(dtype)


def build_address(data: pd.DataFrame) -> pd.DataFrame:
    """
    Build a clean 'Address' column from multiple component columns.

    This function concatenates house number, direction, street name, and
    street type to create a full address. It also cleans up extra whitespace.

    Args:
        data: The DataFrame containing address component columns like
              'House_Nr', 'Dir', 'Street_Name', and 'St_Type'.

    Returns:
        The DataFrame with a new, cleaned 'Address' column.
    """

    data["House_Nr"] = data["House_Nr"].astype(
        str).replace("<NA>", "").replace("nan", "")
    data["Dir"] = data["Dir"].astype(str).replace(
        "<NA>", "").replace("nan", "")
    data["Street_Name"] = (
        data["Street_Name"].astype(str).replace("<NA>", "").replace("nan", "")
    )
    data["St_Type"] = data["St_Type"].astype(
        str).replace("<NA>", "").replace("nan", "")

    data["Zip"] = data["Zip"].fillna(0).astype(int)

    data["Address"] = (
        data["House_Nr"] + " " + data["Dir"] + " " +
        data["Street_Name"] + " " + data["St_Type"]
    )

    data["Address"] = data["Address"].str.replace(
        r"\s+", " ", regex=True).str.strip()

    return data


def safe_mode(series: pd.Series, default: str = "N/A") -> Any:
    """
    Calculate the mode of a series, handling empty or all-NA series gracefully.

    Args:
        series: The pandas Series for which to find the mode.
        default: The default value to return if the series is empty.
                 Defaults to "N/A".

    Returns:
        The most frequent value (mode) in the series, or the default value.
    """
    if series.dropna().empty:
        return default
    mode_vals = series.mode()
    return mode_vals.iloc[0] if not mode_vals.empty else default


@st.cache_data
def load_and_preprocess_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file and perform initial preprocessing.

    This function acts as a pipeline that reads the data, converts data types,
    builds a full address column, and extracts the year from the filing date.
    It is cached to improve app performance.

    Args:
        file_path: The path to the input CSV file.

    Returns:
        A preprocessed pandas DataFrame ready for analysis.
    """
    data = pd.read_csv(file_path)

    data_types = [
        int, str, str, str, int, int, str, int, str, str,
        int, "datetime64[ns]", str, str, "datetime64[ns]", int, str, int,
    ]

    data = convert_types(data, data_types)
    data = build_address(data)

    data["Action_Year"] = data["Action_Filed"].dt.year

    return data


def get_filter_options(df: pd.DataFrame) -> Tuple[List[str], List[int]]:
    """
    Extract unique, sorted lists of options for sidebar filters.

    Args:
        df: The DataFrame from which to extract filter options.

    Returns:
        A tuple containing two lists:
        - A sorted list of unique neighborhood names.
        - A reverse-sorted list of unique action years.
    """
    locations = sorted(df["Neighborhood"].dropna().unique())
    years_sorted = sorted(df["Action_Year"].dropna().unique(), reverse=True)
    return locations, years_sorted


def filter_data(
    df: pd.DataFrame, locations: List[str], years: List[int]
) -> pd.DataFrame:
    """
    Filter the DataFrame based on user selections for location and year.

    Args:
        df: The DataFrame to filter.
        locations: A list of neighborhood names to include.
        years: A list of years to include.

    Returns:
        A new DataFrame containing only the filtered data.
    """
    return df[
        (df["Neighborhood"].isin(locations)) & (df["Action_Year"].isin(years))
    ].copy()


def calculate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate key metrics for the dashboard's top summary cards.

    Args:
        df: The filtered DataFrame to calculate metrics from.

    Returns:
        A dictionary of key metrics including total foreclosures, top zip code,
        peak filing and sale months, and top purchaser.
    """
    df["Foreclosure_Month"] = pd.to_datetime(
        df["Action_Filed"], errors="coerce"
    ).dt.month_name()
    df["Sale_Month"] = pd.to_datetime(
        df["Sale_Date"], errors="coerce"
    ).dt.month_name()

    metrics = {
        "total_foreclosures": len(df),
        "popular_zip": safe_mode(df["Zip"]),
        "popular_foreclosure_month": safe_mode(df["Foreclosure_Month"]),
        "popular_sale_month": safe_mode(df["Sale_Month"]),
        "popular_purchaser": safe_mode(df["Purchaser"]),
    }
    return metrics


def create_bar_chart(df: pd.DataFrame) -> go.Figure:
    """
    Generate a bar chart of foreclosures by neighborhood.

    Args:
        df: The DataFrame containing foreclosure data.

    Returns:
        A Plotly graph object (Figure) representing the bar chart.
    """

    nei_counts = (
        df.groupby("Neighborhood")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    fig = px.bar(
        nei_counts,
        x="Neighborhood",
        y="count",
        title="Foreclosures by Neighborhood",
        labels={"count": "Number of Foreclosures",
                "Neighborhood": "Neighborhood"},
        color_discrete_sequence=["#0083B8"] * len(nei_counts),
        template="plotly_white",
    )
    return fig


def format_data_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare the DataFrame for display in a Streamlit table.

    This function formats date columns to MM/DD/YYYY and selects a specific
    subset of columns for a clean presentation.

    Args:
        df: The DataFrame to format.

    Returns:
        A new, formatted DataFrame ready for display.
    """
    df_display = df.copy()
    df_display["Action_Filed"] = pd.to_datetime(
        df_display["Action_Filed"], errors="coerce"
    ).dt.strftime("%m/%d/%Y")
    df_display["Sale_Date"] = pd.to_datetime(
        df_display["Sale_Date"], errors="coerce"
    ).dt.strftime("%m/%d/%Y")

    display_columns = [
        "Address",
        "Zip",
        "Neighborhood",
        "Action_Filed",
        "Case_Style",
        "Sale_Date",
        "Purchaser",
    ]
    return df_display[display_columns]
