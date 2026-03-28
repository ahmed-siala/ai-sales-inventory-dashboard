import pandas as pd


def detect_low_stock(df: pd.DataFrame, threshold: int = 40) -> pd.DataFrame:
    """
    Detect products with low remaining stock.
    We use simple rule-based logic (not ML).
    """
    latest_stock = (
        df.sort_values("date")
        .groupby("product_name", as_index=False)
        .last()[["product_name", "stock_available"]]
    )
    return latest_stock[latest_stock["stock_available"] < threshold].sort_values("stock_available")


def top_performing_products(df: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    """Get top products by total sales value."""
    top_products = (
        df.groupby("product_name", as_index=False)["total_value"]
        .sum()
        .sort_values("total_value", ascending=False)
        .head(top_n)
    )
    return top_products


def generate_recommendations(df: pd.DataFrame) -> list:
    """
    Generate simple business recommendations from data patterns.
    This is 'AI-like' rule-based insight generation.
    """
    recommendations = []

    low_stock = detect_low_stock(df)
    top_products = top_performing_products(df, top_n=3)
    region_sales = df.groupby("region")["total_value"].sum().sort_values(ascending=False)
    monthly_sales = df.groupby("month")["total_value"].sum().sort_index()

    if not low_stock.empty:
        names = ", ".join(low_stock["product_name"].head(3).tolist())
        recommendations.append(
            f"Restock low inventory products soon, especially: {names}."
        )
    else:
        recommendations.append("Current stock levels look healthy across products.")

    if not top_products.empty:
        best_name = top_products.iloc[0]["product_name"]
        recommendations.append(
            f"Increase marketing and shelf availability for '{best_name}' because it is the best performer."
        )

    if len(region_sales) > 1:
        best_region = region_sales.index[0]
        weak_region = region_sales.index[-1]
        recommendations.append(
            f"Use the sales strategy from {best_region} to improve performance in {weak_region}."
        )

    if len(monthly_sales) >= 2 and monthly_sales.iloc[-1] < monthly_sales.iloc[-2]:
        recommendations.append(
            "Recent month sales dropped compared to the previous month; consider promotions or bundle offers."
        )
    else:
        recommendations.append(
            "Sales trend is stable or improving; maintain current sales channels and monitor monthly."
        )

    return recommendations
