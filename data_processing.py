import pandas as pd


def load_data(file_path: str) -> pd.DataFrame:
    """Load CSV data into a pandas DataFrame."""
    return pd.read_csv(file_path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean data with beginner-friendly steps:
    - convert date column
    - fix numeric types
    - fill missing values
    - create total_value column
    """
    cleaned = df.copy()

    # Convert date text to datetime for monthly analysis.
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    # Ensure numeric fields are numbers.
    cleaned["units_sold"] = pd.to_numeric(cleaned["units_sold"], errors="coerce")
    cleaned["unit_price"] = pd.to_numeric(cleaned["unit_price"], errors="coerce")
    cleaned["stock_available"] = pd.to_numeric(cleaned["stock_available"], errors="coerce")

    # Fill missing text fields with clear placeholders.
    cleaned["product_name"] = cleaned["product_name"].fillna("Unknown Product")
    cleaned["category"] = cleaned["category"].fillna("Unknown Category")
    cleaned["region"] = cleaned["region"].fillna("Unknown Region")

    # Fill missing numeric values with safe defaults.
    cleaned["units_sold"] = cleaned["units_sold"].fillna(0)
    cleaned["unit_price"] = cleaned["unit_price"].fillna(0.0)
    cleaned["stock_available"] = cleaned["stock_available"].fillna(0)

    # Remove rows where date could not be parsed.
    cleaned = cleaned.dropna(subset=["date"])

    # Create a total value per row: units_sold * unit_price.
    cleaned["total_value"] = cleaned["units_sold"] * cleaned["unit_price"]

    # Add month column for trend charts.
    cleaned["month"] = cleaned["date"].dt.to_period("M").astype(str)

    return cleaned


def analyze_data(df: pd.DataFrame) -> dict:
    """Return key analysis outputs used by console script and dashboard."""
    total_sales = df["total_value"].sum()

    best_selling_products = (
        df.groupby("product_name", as_index=False)["units_sold"]
        .sum()
        .sort_values("units_sold", ascending=False)
    )

    monthly_sales = (
        df.groupby("month", as_index=False)["total_value"]
        .sum()
        .sort_values("month")
    )

    sales_by_region = (
        df.groupby("region", as_index=False)["total_value"]
        .sum()
        .sort_values("total_value", ascending=False)
    )

    category_distribution = (
        df.groupby("category", as_index=False)["units_sold"]
        .sum()
        .sort_values("units_sold", ascending=False)
    )

    return {
        "total_sales": total_sales,
        "best_selling_products": best_selling_products,
        "monthly_sales": monthly_sales,
        "sales_by_region": sales_by_region,
        "category_distribution": category_distribution,
    }
