import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------
# Load dataset
# ------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Mushimuche/world-happiness-dashboard/main/World-happiness-report-updated_2024.csv"
    return pd.read_csv(url, encoding="ISO-8859-1")

df = load_data()

# Rename for convenience (optional)
df = df.rename(columns={"Country name": "Country", "Life Ladder": "Happiness"})

# ------------------------------
# Title / description
# ------------------------------
st.title("🌎 World Happiness Dashboard (2005–2024)")
st.write("Explore global happiness factors and trends using the World Happiness Report dataset.")

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("Filters")

years = sorted(df["year"].unique())
countries = sorted(df["Country"].unique())

selected_year = st.sidebar.selectbox("Select Year", years)
selected_country = st.sidebar.selectbox("Select Country", countries)

# Filter by selected year
filtered_df = df[df["year"] == selected_year]

# ------------------------------
# Summary Statistics
# ------------------------------
st.subheader(f"📊 Dataset Preview — {selected_year}")
st.dataframe(filtered_df.head())

st.subheader("📈 Summary Statistics")
st.write(filtered_df.describe())

# ------------------------------
# Visualization 1 – Happiness by Country
# ------------------------------
st.subheader(f"🌍 Happiness Scores by Country ({selected_year})")

fig = px.bar(
    filtered_df.sort_values("Happiness", ascending=False),
    x="Country",
    y="Happiness",
    title=f"Happiness Scores in {selected_year}",
)
st.plotly_chart(fig)

# ------------------------------
# Visualization 2 – Trends for Selected Country
# ------------------------------
st.subheader(f"📉 Happiness Trend for {selected_country}")

country_df = df[df["Country"] == selected_country]

fig2 = px.line(
    country_df,
    x="year",
    y="Happiness",
    title=f"Happiness Score Trend: {selected_country}",
    markers=True
)
st.plotly_chart(fig2)

# ------------------------------
# Factors Visualization (Radar or Bar)
# ------------------------------
st.subheader(f"🔍 Factors Affecting Happiness in {selected_year}")

factor_cols = [
    "Log GDP per capita",
    "Social support",
    "Healthy life expectancy at birth",
    "Freedom to make life choices",
    "Generosity",
    "Perceptions of corruption",
    "Positive affect",
    "Negative affect",
]

# Show means for the selected year
factor_means = filtered_df[factor_cols].mean().reset_index()
factor_means.columns = ["Factor", "Value"]

fig3 = px.bar(
    factor_means,
    x="Factor",
    y="Value",
    title="Average Factor Values Across All Countries",
)
st.plotly_chart(fig3)

# ------------------------------
# Optional ML Placeholder
# ------------------------------
st.subheader("🤖 Optional: ML Prediction / Clustering")
st.write("Add your model here later.")
