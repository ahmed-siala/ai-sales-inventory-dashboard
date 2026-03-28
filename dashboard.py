import matplotlib.pyplot as plt
import streamlit as st

from data_processing import analyze_data, clean_data, load_data
from insights import detect_low_stock, generate_recommendations, top_performing_products


st.set_page_config(page_title="El Yoser Dashboard", layout="wide")

st.markdown(
    """
    <style>
        .stApp {background-color: #0F172A; color: #E2E8F0;}
        h1, h2, h3 {color: #F8FAFC;}
        [data-testid="stSidebar"] {background-color: #111827;}
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #1E293B 0%, #0B1220 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px;
        }
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            border: 1px solid #334155;
            background: #1E293B;
            color: #E2E8F0;
            font-weight: 600;
            padding: 10px 6px;
        }
        div.stButton > button:hover {
            border-color: #38BDF8;
            color: #38BDF8;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

plt.style.use("dark_background")
ACCENT_BLUE = "#38BDF8"
ACCENT_GREEN = "#34D399"
ACCENT_ORANGE = "#FB923C"
ACCENT_PURPLE = "#A78BFA"


def get_filtered_data():
    df = clean_data(load_data("sales_data.csv"))

    st.sidebar.header("🎛️ Filters")
    all_products = sorted(df["product_name"].dropna().unique().tolist())
    all_regions = sorted(df["region"].dropna().unique().tolist())

    selected_products = st.sidebar.multiselect(
        "Select Product(s)",
        options=all_products,
        default=all_products,
        key="filter_products_topnav",
    )
    selected_regions = st.sidebar.multiselect(
        "Select Region(s)",
        options=all_regions,
        default=all_regions,
        key="filter_regions_topnav",
    )

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filter_dates_topnav",
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    filtered_df = df[
        (df["product_name"].isin(selected_products))
        & (df["region"].isin(selected_regions))
        & (df["date"].dt.date >= start_date)
        & (df["date"].dt.date <= end_date)
    ]
    return filtered_df


def show_kpis(results, filtered_df):
    st.markdown("### 📌 KPI Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sales", f"EGP {results['total_sales']:,.0f}")
    c2.metric("Top Product", str(results["best_selling_products"].iloc[0]["product_name"]))
    c3.metric("Average Sales / Transaction", f"EGP {filtered_df['total_value'].mean():,.0f}")


def show_top_products_chart(results):
    st.markdown("#### 🏆 Top Products")
    top_products = results["best_selling_products"].head(5)
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#0F172A")
    ax.bar(top_products["product_name"], top_products["units_sold"], color=ACCENT_BLUE, edgecolor="#E2E8F0", linewidth=0.6)
    ax.set_xlabel("Product", color="#E2E8F0")
    ax.set_ylabel("Units Sold", color="#E2E8F0")
    ax.set_title("Top 5 Best-Selling Products", color="#F8FAFC", pad=10)
    ax.tick_params(axis="x", rotation=22, colors="#CBD5E1")
    ax.tick_params(axis="y", colors="#CBD5E1")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    st.pyplot(fig, width="stretch")


def show_monthly_sales_chart(results):
    st.markdown("#### 📈 Monthly Sales Trend")
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#0F172A")
    ax.plot(results["monthly_sales"]["month"], results["monthly_sales"]["total_value"], marker="o", linewidth=2.4, color=ACCENT_GREEN)
    ax.fill_between(results["monthly_sales"]["month"], results["monthly_sales"]["total_value"], color=ACCENT_GREEN, alpha=0.15)
    ax.set_xlabel("Month", color="#E2E8F0")
    ax.set_ylabel("Sales Value", color="#E2E8F0")
    ax.set_title("Monthly Sales Value", color="#F8FAFC", pad=10)
    ax.tick_params(axis="x", rotation=22, colors="#CBD5E1")
    ax.tick_params(axis="y", colors="#CBD5E1")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    st.pyplot(fig, width="stretch")


def show_category_pie(results):
    st.markdown("#### 🧩 Category Distribution")
    fig, ax = plt.subplots(figsize=(6, 5), facecolor="#0F172A")
    ax.pie(
        results["category_distribution"]["units_sold"],
        labels=results["category_distribution"]["category"],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "#0F172A", "linewidth": 1},
        colors=[ACCENT_BLUE, ACCENT_ORANGE, ACCENT_PURPLE, ACCENT_GREEN],
        textprops={"color": "#E2E8F0"},
    )
    ax.set_title("Sales by Category", color="#F8FAFC", pad=10)
    st.pyplot(fig, width="stretch")


def page_home():
    st.markdown("### 👋 Home")
    st.info("Use the top menu to switch between sections.")
    st.success("Filters from the sidebar apply to all pages.")


def page_dashboard(results, filtered_df):
    st.markdown("### 📊 Dashboard")
    show_kpis(results, filtered_df)
    left, right = st.columns(2)
    with left:
        show_top_products_chart(results)
    with right:
        show_monthly_sales_chart(results)


def page_sales(results):
    st.markdown("### 📈 Sales")
    left, right = st.columns(2)
    with left:
        show_top_products_chart(results)
    with right:
        show_monthly_sales_chart(results)
    show_category_pie(results)
    st.markdown("#### 🌍 Sales by Region")
    st.dataframe(results["sales_by_region"], width="stretch")


def page_inventory(filtered_df):
    st.markdown("### 📦 Inventory")
    low_stock_df = detect_low_stock(filtered_df, threshold=40)
    if low_stock_df.empty:
        st.success("All product stock levels are healthy.")
    else:
        st.warning("Low stock products detected. Consider restocking soon.")
        st.dataframe(low_stock_df, width="stretch")


def page_ai_insights(filtered_df):
    st.markdown("### 🤖 AI Insights")
    st.markdown("#### 🚀 Top Performing Products")
    st.info("Products with highest total sales value in selected filters.")
    st.dataframe(top_performing_products(filtered_df, top_n=5), width="stretch")
    st.markdown("#### 💡 Recommendations")
    for item in generate_recommendations(filtered_df):
        if "Restock" in item or "dropped" in item:
            st.warning(item)
        elif "best performer" in item or "improving" in item:
            st.success(item)
        else:
            st.info(item)


st.title("AI-Based Sales and Inventory Analysis Dashboard for El Yoser")
st.caption("Professional dashboard for sales and inventory monitoring.")

if "top_page" not in st.session_state:
    st.session_state.top_page = "Home"

n1, n2, n3, n4, n5 = st.columns(5)
with n1:
    if st.button("Home", key="nav_home_btn"):
        st.session_state.top_page = "Home"
with n2:
    if st.button("Dashboard", key="nav_dashboard_btn"):
        st.session_state.top_page = "Dashboard"
with n3:
    if st.button("Sales", key="nav_sales_btn"):
        st.session_state.top_page = "Sales"
with n4:
    if st.button("Inventory", key="nav_inventory_btn"):
        st.session_state.top_page = "Inventory"
with n5:
    if st.button("AI Insights", key="nav_ai_btn"):
        st.session_state.top_page = "AI Insights"

st.write("")

filtered_data = get_filtered_data()
if filtered_data.empty:
    st.warning("No data matches your selected filters. Please adjust the sidebar options.")
    st.stop()

analysis_results = analyze_data(filtered_data)
active_page = st.session_state.top_page

if active_page == "Home":
    page_home()
elif active_page == "Dashboard":
    page_dashboard(analysis_results, filtered_data)
elif active_page == "Sales":
    page_sales(analysis_results)
elif active_page == "Inventory":
    page_inventory(filtered_data)
elif active_page == "AI Insights":
    page_ai_insights(filtered_data)
import matplotlib.pyplot as plt
import streamlit as st

from data_processing import analyze_data, clean_data, load_data
from insights import detect_low_stock, generate_recommendations, top_performing_products


st.set_page_config(page_title="El Yoser Dashboard", layout="wide")

st.markdown(
    """
    <style>
        .stApp {background-color: #0F172A; color: #E2E8F0;}
        h1, h2, h3 {color: #F8FAFC;}
        [data-testid="stSidebar"] {background-color: #111827;}
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #1E293B 0%, #0B1220 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

plt.style.use("dark_background")
ACCENT_BLUE = "#38BDF8"
ACCENT_GREEN = "#34D399"
ACCENT_ORANGE = "#FB923C"
ACCENT_PURPLE = "#A78BFA"


def get_filtered_data():
    df = clean_data(load_data("sales_data.csv"))

    st.sidebar.header("🧭 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Home", "Dashboard Overview", "Sales Analysis", "Inventory / Stock Alerts", "AI Insights"],
        key="nav_page_unique",
    )

    st.sidebar.header("🎛️ Filters")
    all_products = sorted(df["product_name"].dropna().unique().tolist())
    all_regions = sorted(df["region"].dropna().unique().tolist())

    selected_products = st.sidebar.multiselect(
        "Select Product(s)",
        options=all_products,
        default=all_products,
        key="sidebar_filter_products_unique",
    )
    selected_regions = st.sidebar.multiselect(
        "Select Region(s)",
        options=all_regions,
        default=all_regions,
        key="sidebar_filter_regions_unique",
    )

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="sidebar_filter_dates_unique",
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    filtered_df = df[
        (df["product_name"].isin(selected_products))
        & (df["region"].isin(selected_regions))
        & (df["date"].dt.date >= start_date)
        & (df["date"].dt.date <= end_date)
    ]
    return page, filtered_df


def show_kpis(results, filtered_df):
    st.markdown("### 📌 KPI Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sales", f"EGP {results['total_sales']:,.0f}")
    c2.metric("Top Product", str(results["best_selling_products"].iloc[0]["product_name"]))
    c3.metric("Average Sales / Transaction", f"EGP {filtered_df['total_value'].mean():,.0f}")


def show_top_products_chart(results):
    st.markdown("#### 🏆 Top Products")
    top_products = results["best_selling_products"].head(5)
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#0F172A")
    ax.bar(top_products["product_name"], top_products["units_sold"], color=ACCENT_BLUE, edgecolor="#E2E8F0", linewidth=0.6)
    ax.set_xlabel("Product", color="#E2E8F0")
    ax.set_ylabel("Units Sold", color="#E2E8F0")
    ax.set_title("Top 5 Best-Selling Products", color="#F8FAFC", pad=10)
    ax.tick_params(axis="x", rotation=22, colors="#CBD5E1")
    ax.tick_params(axis="y", colors="#CBD5E1")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    st.pyplot(fig, width="stretch")


def show_monthly_sales_chart(results):
    st.markdown("#### 📈 Monthly Sales Trend")
    fig, ax = plt.subplots(figsize=(7, 4), facecolor="#0F172A")
    ax.plot(results["monthly_sales"]["month"], results["monthly_sales"]["total_value"], marker="o", linewidth=2.4, color=ACCENT_GREEN)
    ax.fill_between(results["monthly_sales"]["month"], results["monthly_sales"]["total_value"], color=ACCENT_GREEN, alpha=0.15)
    ax.set_xlabel("Month", color="#E2E8F0")
    ax.set_ylabel("Sales Value", color="#E2E8F0")
    ax.set_title("Monthly Sales Value", color="#F8FAFC", pad=10)
    ax.tick_params(axis="x", rotation=22, colors="#CBD5E1")
    ax.tick_params(axis="y", colors="#CBD5E1")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    st.pyplot(fig, width="stretch")


def show_category_pie(results):
    st.markdown("#### 🧩 Category Distribution")
    fig, ax = plt.subplots(figsize=(6, 5), facecolor="#0F172A")
    ax.pie(
        results["category_distribution"]["units_sold"],
        labels=results["category_distribution"]["category"],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "#0F172A", "linewidth": 1},
        colors=[ACCENT_BLUE, ACCENT_ORANGE, ACCENT_PURPLE, ACCENT_GREEN],
        textprops={"color": "#E2E8F0"},
    )
    ax.set_title("Sales by Category", color="#F8FAFC", pad=10)
    st.pyplot(fig, width="stretch")


def page_home():
    st.title("AI-Based Sales and Inventory Analysis Dashboard for El Yoser")
    st.caption("Professional dashboard for sales and inventory monitoring.")
    st.markdown("### 👋 Home")
    st.info("Use the sidebar to navigate between pages.")
    st.success("Filters apply to all pages (product, region, and date range).")


def page_dashboard_overview(results, filtered_df):
    st.title("Dashboard Overview")
    show_kpis(results, filtered_df)
    left, right = st.columns(2)
    with left:
        show_top_products_chart(results)
    with right:
        show_monthly_sales_chart(results)


def page_sales_analysis(results):
    st.title("Sales Analysis")
    left, right = st.columns(2)
    with left:
        show_top_products_chart(results)
    with right:
        show_monthly_sales_chart(results)
    show_category_pie(results)
    st.markdown("#### 🌍 Sales by Region")
    st.dataframe(results["sales_by_region"], width="stretch")


def page_inventory(filtered_df):
    st.title("Inventory / Stock Alerts")
    low_stock_df = detect_low_stock(filtered_df, threshold=40)
    if low_stock_df.empty:
        st.success("All product stock levels are healthy.")
    else:
        st.warning("Low stock products detected. Consider restocking soon.")
        st.dataframe(low_stock_df, width="stretch")


def page_ai_insights(filtered_df):
    st.title("AI Insights")
    st.markdown("#### 🚀 Top Performing Products")
    st.info("Products with highest total sales value in selected filters.")
    st.dataframe(top_performing_products(filtered_df, top_n=5), width="stretch")
    st.markdown("#### 💡 AI-Based Recommendations")
    for item in generate_recommendations(filtered_df):
        if "Restock" in item or "dropped" in item:
            st.warning(item)
        elif "best performer" in item or "improving" in item:
            st.success(item)
        else:
            st.info(item)


selected_page, filtered_data = get_filtered_data()

if filtered_data.empty:
    st.warning("No data matches your selected filters. Please adjust the sidebar options.")
    st.stop()

analysis_results = analyze_data(filtered_data)

if selected_page == "Home":
    page_home()
elif selected_page == "Dashboard Overview":
    page_dashboard_overview(analysis_results, filtered_data)
elif selected_page == "Sales Analysis":
    page_sales_analysis(analysis_results)
elif selected_page == "Inventory / Stock Alerts":
    page_inventory(filtered_data)
elif selected_page == "AI Insights":
    page_ai_insights(filtered_data)

