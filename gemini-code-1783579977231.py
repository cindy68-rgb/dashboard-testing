import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick

# -----------------------------------------------------------------------------
# 1. Page Configuration & Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sales & Pricing Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# Set global plotting configurations matching your branding preference
plt.rcParams['figure.figsize'] = (14, 6)
sns.set_theme(style="whitegrid")

CATEGORY_COLORS = {
    'Office Supplies': '#4ca6a4', 
    'Technology': '#f48c06', 
    'Furniture': '#5c7aff'
}

# -----------------------------------------------------------------------------
# 2. Optimized Data Loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Utilizing Latin1 encoding to capture special typography characters
    df = pd.read_csv('mock_dataset.csv', encoding='latin1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['YearMonth'] = df['Order Date'].dt.to_period('M').dt.to_timestamp()
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Error loading 'mock_dataset.csv'. Please verify that the file is in the same directory.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. Sidebar Filtering Options
# -----------------------------------------------------------------------------
st.sidebar.header("🎛️ Filter Controls")

# Date range selectors
min_date = df['Order Date'].min().to_pydatetime()
max_date = df['Order Date'].max().to_pydatetime()

start_date, end_date = st.sidebar.date_input(
    "Select Order Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Category multi-select
categories = df['Product Category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=categories,
    default=categories
)

# Apply runtime dataframe scoping
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(start_date)) & 
    (df['Order Date'] <= pd.to_datetime(end_date)) & 
    (df['Product Category'].isin(selected_categories))
]

# -----------------------------------------------------------------------------
# 4. Main Executive KPI Banner
# -----------------------------------------------------------------------------
st.title("📊 Sales & Pricing Performance Dashboard")
st.markdown("An interactive operational deep-dive exploring trends, margins, and structural discount parameters.")
st.write("---")

if filtered_df.empty:
    st.warning("No data points fit the current sidebar filter settings.")
    st.stop()

# Calculate dynamic high-level statistics
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0
avg_discount = filtered_df['Discount'].mean() * 100

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
kpi_col1.metric("Gross Sales Revenue", f"${total_sales:,.2f}")
kpi_col2.metric("Net Operational Profit", f"${total_profit:,.2f}")
kpi_col3.metric("Aggregate Profit Margin", f"{avg_margin:.2f}%")
kpi_col4.metric("Avg applied Discount", f"{avg_discount:.2f}%")

st.write("---")

# -----------------------------------------------------------------------------
# 5. Visualizations Section (Using Seaborn)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📉 Monthly Sales Trends", "🏷️ Pricing & Discounts", "📋 Tabular Performance Summary"])

with tab1:
    st.subheader("Monthly Sales Volatility Over Time")
    st.markdown("Tracks time-series aggregation to expose peak-and-trough cyclical vectors.")
    
    # Process lineplot metrics
    monthly_sales = filtered_df.groupby(['YearMonth', 'Product Category'])['Sales'].sum().reset_index()
    
    fig1, ax1 = plt.subplots(figsize=(15, 6))
    sns.lineplot(
        data=monthly_sales, 
        x='YearMonth', 
        y='Sales', 
        hue='Product Category', 
        marker='o', 
        linewidth=2.5,
        palette=CATEGORY_COLORS,
        ax=ax1
    )
    ax1.set_title('Monthly Revenue Tracking via Product Class Segmentations', fontsize=14, fontweight='bold', pad=10)
    ax1.set_xlabel('Order Date Window')
    ax1.set_ylabel('Total Revenue ($)')
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with tab2:
    st.subheader("Discount Structure Distributions")
    st.markdown("Highlights promotional variations across sectors using structured categorical mappings.")
    
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.boxplot(
        data=filtered_df,
        x='Product Category',
        y='Discount',
        palette=CATEGORY_COLORS,
        hue='Product Category',
        ax=ax2
    )
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax2.set_title('Comparative Range Variations and Outlier Parameters', fontsize=14, fontweight='bold', pad=10)
    ax2.set_xlabel('Product Category Group')
    ax2.set_ylabel('Applied Promotional Markdown Rate (%)')
    st.pyplot(fig2)

with tab3:
    st.subheader("Categorized Financial Ledger Matrix")
    
    # Grid summary math calculation
    cat_summary = filtered_df.groupby('Product Category').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Profit', 'sum'),
        Mean_Discount=('Discount', 'mean')
    ).reset_index()
    
    cat_summary['Margin (%)'] = (cat_summary['Total_Profit'] / cat_summary['Total_Sales']) * 100
    cat_summary['Mean_Discount'] = cat_summary['Mean_Discount'] * 100
    
    # Pretty printing mapping adjustments
    cat_summary.columns = ['Product Category', 'Total Revenue', 'Net Profit', 'Average Discount (%)', 'Net Margin (%)']
    st.dataframe(
        cat_summary.style.format({
            'Total Revenue': '${:,.2f}',
            'Net Profit': '${:,.2f}',
            'Average Discount (%)': '{:.2f}%',
            'Net Margin (%)': '{:.2f}%'
        }),
        use_container_width=True
    )