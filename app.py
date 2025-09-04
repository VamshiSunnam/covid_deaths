import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")

st.title("🌍 COVID-19 Dashboard (OWID Dataset)")

# Sidebar: load data
with st.sidebar:
    st.header("Upload or use local file")
    default_path = "data/owid-covid-data.csv"
    file_choice = st.radio("Data source", ["Local file", "Upload"], key="data_source_radio")
    if file_choice == "Local file":
        data_path = st.text_input("Dataset path", value=default_path)
        df = pd.read_csv(data_path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        uploaded = st.file_uploader("Upload CSV", type="csv")
        if uploaded is not None:
            df = pd.read_csv(uploaded)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
        else:
            st.stop()


st.success(f"Loaded {len(df):,} rows, {len(df.columns)} columns")

# --- Starter Graphs Section ---
st.header("📊 COVID-19 Data Visualizations")

# Dropdown for country selection
country = st.selectbox("Choose a country", df["location"].unique(), index=0)

# Filter dataset for that country
country_df = df[df["location"] == country]

# Line chart: Total cases over time
fig_cases = px.line(
    country_df,
    x="date",
    y="total_cases",
    title=f"Total COVID-19 Cases in {country}",
    labels={"total_cases": "Total Cases", "date": "Date"}
)
st.plotly_chart(fig_cases, use_container_width=True)

# Line chart: Total deaths over time
fig_deaths = px.line(
    country_df,
    x="date",
    y="total_deaths",
    title=f"Total COVID-19 Deaths in {country}",
    labels={"total_deaths": "Total Deaths", "date": "Date"}
)
st.plotly_chart(fig_deaths, use_container_width=True)

# Bar chart: New cases per day
fig_new_cases = px.bar(
    country_df,
    x="date",
    y="new_cases",
    title=f"New Daily COVID-19 Cases in {country}",
    labels={"new_cases": "New Cases", "date": "Date"}
)
st.plotly_chart(fig_new_cases, use_container_width=True)


# Scatter plot: Cases vs Deaths
scatter_df = df.dropna(subset=["population"])
fig_scatter = px.scatter(
    scatter_df,
    x="total_cases",
    y="total_deaths",
    color="continent",
    title="Cases vs Deaths by Country",
    hover_name="location",
    size="population",
    log_x=True,
    log_y=True
)
st.plotly_chart(fig_scatter, use_container_width=True)

# --- Additional Creative Visualizations ---
st.header("✨ More COVID-19 Insights")

# Pie chart: Proportion of deaths vs recoveries (approximate)
if "total_deaths" in df.columns and "total_cases" in df.columns:
    total_deaths = df["total_deaths"].sum()
    total_cases = df["total_cases"].sum()
    total_recovered = max(total_cases - total_deaths, 0)
    fig_pie = px.pie(
        names=["Deaths", "Recovered/Other"],
        values=[total_deaths, total_recovered],
        title="Proportion of Deaths vs Recovered/Other (Global)"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Heatmap: Correlation between numeric columns
import numpy as np
numeric_cols = df.select_dtypes(include=np.number).columns
if len(numeric_cols) > 1:
    st.subheader("Correlation Heatmap (Numeric Columns)")
    corr = df[numeric_cols].corr()
    import plotly.figure_factory as ff
    fig_heatmap = ff.create_annotated_heatmap(
        z=corr.values,
        x=list(corr.columns),
        y=list(corr.index),
        colorscale='Viridis',
        showscale=True
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Top 10 countries by total cases
st.subheader("Top 10 Countries by Total Cases")
latest_date = df["date"].max()
latest_df = df[df["date"] == latest_date]
top10 = latest_df.groupby("location")["total_cases"].max().nlargest(10).reset_index()
if pd.api.types.is_datetime64_any_dtype(df["date"]):
    latest_date_str = latest_date.date()
else:
    latest_date_str = str(latest_date)
fig_top10 = px.bar(
    top10,
    x="location",
    y="total_cases",
    title=f"Top 10 Countries by Total Cases as of {latest_date_str}",
    color="total_cases",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig_top10, use_container_width=True)

# Area chart: New cases and new deaths over time (selected country)
if "new_cases" in country_df.columns and "new_deaths" in country_df.columns:
    st.subheader(f"New Cases vs New Deaths Over Time in {country}")
    fig_area = px.area(
        country_df,
        x="date",
        y=["new_cases", "new_deaths"],
        title=f"New Cases vs New Deaths in {country}",
        labels={"value": "Count", "date": "Date", "variable": "Metric"}
    )
    st.plotly_chart(fig_area, use_container_width=True)

# Summary statistics
st.subheader("Summary Statistics (Filtered Data)")
st.write(country_df.describe(include='all'))

# Ensure date parsing
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Sidebar selections
with st.sidebar:
    st.header("Chart options")
    date_col = "date" if "date" in df.columns else None

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    metric = st.selectbox("Metric (y-axis)", numeric_cols, index=numeric_cols.index("new_deaths") if "new_deaths" in numeric_cols else 0)

    category = st.selectbox("Group by (x-axis / color)", ["location","continent","iso_code"])

    # Filters
    st.header("Filters")
    locations = st.multiselect("Select locations", sorted(df["location"].dropna().unique()), default=["India","United States"])
    df = df[df["location"].isin(locations)]

    if date_col:
        min_date, max_date = df[date_col].min(), df[date_col].max()
        date_range = st.date_input("Date range", value=(min_date, max_date))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df = df[(df[date_col] >= start) & (df[date_col] <= end)]

# KPIs
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Rows (filtered)", f"{len(df):,}")
col2.metric(f"Total {metric}", f"{df[metric].sum():,.0f}")
col3.metric(f"Average {metric}", f"{df[metric].mean():,.2f}")

st.divider()

# Time series chart
with st.sidebar:
    st.header("Upload or use local file")
    default_path = "CovidDeaths.csv"
    file_choice = st.radio("Data source", ["Local file", "Upload"])
    if file_choice == "Local file":
        data_path = st.text_input("Dataset path", value=default_path)
        try:
            df = pd.read_csv(data_path)
        except Exception as e:
            st.error(f"Failed to load {data_path}: {e}")
            st.stop()
    else:
        uploaded = st.file_uploader("Upload CSV", type="csv")
        if uploaded is not None:
            df = pd.read_csv(uploaded)
        else:
            st.stop()
    st.subheader(f"🗺️ Map of {metric}")
    latest = df.sort_values(date_col).groupby("location").tail(1)
    fig_map = px.choropleth(
        latest, locations="iso_code", color=metric,
        hover_name="location", projection="natural earth",
        title=f"Latest {metric} per country"
    )
    st.plotly_chart(fig_map, use_container_width=True)
