# AI-Based Sales and Inventory Analysis Dashboard for El Yoser

Beginner-friendly internship project for analyzing and visualizing sales/inventory data for a paint bucket company.

## Project Goal
This project helps El Yoser understand:
- total sales performance
- best-selling products
- monthly sales trends
- sales by region
- low stock alerts
- simple AI-based business recommendations (rule-based logic)

## Tech Stack
- Python
- pandas (data analysis)
- matplotlib (charts)
- streamlit (interactive dashboard)

## Project Structure
```text
el-yoser-ai-analysis/
├── sales_data.csv          # sample dataset (80 rows)
├── data_processing.py      # loading, cleaning, analysis functions
├── insights.py             # low stock and recommendation logic
├── main.py                 # console version of the analysis
├── dashboard.py            # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Dataset Columns
The CSV file contains:
- `date`
- `product_name`
- `category`
- `region`
- `units_sold`
- `unit_price`
- `stock_available`

## How to Run

### 1) Create and activate virtual environment (recommended)
On Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Run console analysis
```bash
python main.py
```

### 4) Run Streamlit dashboard
```bash
streamlit run dashboard.py
```

Then open the local URL shown in terminal (usually `http://localhost:8501`).

## What the Dashboard Shows
- **KPIs**: total sales and top product
- **Bar chart**: top products by units sold
- **Line chart**: monthly sales trend
- **Pie chart**: category distribution
- **Low stock alerts**: products below threshold
- **AI-based insights**: automatically generated recommendations

## AI-Based Insights (Simple, Explainable Logic)
This project does not use machine learning. Instead, it uses clear business rules:
- if stock is below threshold -> alert for restocking
- identify top products by sales value
- compare regions and monthly trends
- generate recommendations from these patterns

This makes it easy to explain during a PFA/internship presentation.
