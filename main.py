from data_processing import load_data, clean_data, analyze_data
from insights import detect_low_stock, top_performing_products, generate_recommendations


def run_console_analysis() -> None:
    """Simple script to test analysis in terminal."""
    file_path = "sales_data.csv"

    # 1) Load and clean data.
    raw_df = load_data(file_path)
    df = clean_data(raw_df)

    # 2) Core analysis.
    results = analyze_data(df)

    print("=== AI-Based Sales and Inventory Analysis ===")
    print(f"Total Sales Value: {results['total_sales']:.2f}")
    print("\nTop 5 Best-Selling Products (by units sold):")
    print(results["best_selling_products"].head(5).to_string(index=False))

    print("\nSales by Region:")
    print(results["sales_by_region"].to_string(index=False))

    # 3) Rule-based insights.
    low_stock = detect_low_stock(df, threshold=40)
    top_products = top_performing_products(df, top_n=3)
    recommendations = generate_recommendations(df)

    print("\nLow Stock Products:")
    if low_stock.empty:
        print("No low stock alerts.")
    else:
        print(low_stock.to_string(index=False))

    print("\nTop Performing Products (by sales value):")
    print(top_products.to_string(index=False))

    print("\nBusiness Recommendations:")
    for i, rec in enumerate(recommendations, start=1):
        print(f"{i}. {rec}")


if __name__ == "__main__":
    run_console_analysis()
