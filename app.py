import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(
    page_title="World Happiness Dashboard 2023",
    page_icon="🌎",
    layout="wide"
)


# ------------------------------
# Load Dataset
# ------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Mushimuche/world-happiness-dashboard/main/World-happiness-report-updated_2024.csv"
    df = pd.read_csv(url, encoding="ISO-8859-1")
    df = df.rename(columns={
        "Country name": "Country", 
        "Life Ladder": "Happiness",
        "Positive affect": "Positive Emotions",
        "Negative affect": "Negative Emotions"
    })
    # Filter for 2023 only
    df = df[df["year"] == 2023].copy()
    return df

df = load_data()

# ------------------------------
# Title & Description
# ------------------------------
st.title("🌎 World Happiness Report 2023")
st.subheader("🧑‍💻 Rui Manuel A. Palabon - BSCS3 Machine Problem 3")
st.markdown("""
See which countries are the happiest in 2023! Compare different countries and learn what makes people happy 😊 or unhappy 😞 around the world.
""")

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("🔍 Filters")

countries = sorted(df["Country"].unique())

# Country multi-select
selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare",
    countries,
    default=["United States", "Finland", "Denmark", "Japan", "Brazil"] if all(c in countries for c in ["United States", "Finland", "Denmark", "Japan", "Brazil"]) else countries[:5]
)

# ------------------------------
# Key Metrics
# ------------------------------
st.header("📊 2023 Global Happiness Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_happiness = df["Happiness"].mean()
    st.metric("Global Average", f"{avg_happiness:.2f}")

with col2:
    happiest = df.nlargest(1, "Happiness")
    if len(happiest) > 0:
        st.metric("Happiest Country", happiest["Country"].values[0])
        st.caption(f"Score: {happiest['Happiness'].values[0]:.2f}")

with col3:
    least_happy = df.nsmallest(1, "Happiness")
    if len(least_happy) > 0:
        st.metric("Least Happy Country", least_happy["Country"].values[0])
        st.caption(f"Score: {least_happy['Happiness'].values[0]:.2f}")

with col4:
    total_countries = len(df)
    st.metric("Total Countries", total_countries)

# ------------------------------
# Visualization 1: Top/Bottom Countries
# ------------------------------
st.header("🏆 Happiness Rankings")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 15 Happiest Countries")
    top15 = df.nlargest(15, "Happiness").sort_values("Happiness", ascending=True)
    
    fig1 = px.bar(
        top15,
        y="Country",
        x="Happiness",
        orientation='h',
        color="Happiness",
        color_continuous_scale="Greens",
        labels={"Happiness": "Happiness Score"}
    )
    fig1.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Bottom 15 Countries")
    bottom15 = df.nsmallest(15, "Happiness").sort_values("Happiness", ascending=False)
    
    fig2 = px.bar(
        bottom15,
        y="Country",
        x="Happiness",
        orientation='h',
        color="Happiness",
        color_continuous_scale="Reds",
        labels={"Happiness": "Happiness Score"}
    )
    fig2.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------
# World Map Visualization
# ------------------------------
st.header("🗺️ Global Happiness Map")

fig_map = px.choropleth(
    df,
    locations="Country",
    locationmode="country names",
    color="Happiness",
    hover_name="Country",
    hover_data={
        "Happiness": ":.2f",
        "Log GDP per capita": ":.2f",
        "Social support": ":.2f",
        "Freedom to make life choices": ":.2f"
    },
    color_continuous_scale="RdYlGn",
    title="World Happiness Scores in 2023",
    range_color=[df["Happiness"].min(), df["Happiness"].max()]
)
fig_map.update_layout(height=500)
st.plotly_chart(fig_map, use_container_width=True)

# ------------------------------
# Country Comparison
# ------------------------------
st.header("🔍 Compare Selected Countries")
st.subheader("Select countries from the sidebar to compare.")

if selected_countries and len(selected_countries) > 0:
    comparison_df = df[df["Country"].isin(selected_countries)]
    
    # Sort by happiness for better visualization
    comparison_df = comparison_df.sort_values("Happiness", ascending=False)
    
    # Bar chart comparison
    fig3 = px.bar(
        comparison_df,
        x="Country",
        y="Happiness",
        title="Happiness Score Comparison",
        color="Happiness",
        color_continuous_scale="Viridis",
        labels={"Happiness": "Happiness Score"}
    )
    fig3.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)
    
else:
    st.info("👆 Please select countries from the sidebar to compare them.")

# ------------------------------
# Factor Analysis
# ------------------------------
st.header("📈 Happiness Factors Analysis")

factor_cols_analysis = [
    "Log GDP per capita",
    "Social support",
    "Healthy life expectancy at birth",
    "Freedom to make life choices",
    "Generosity",
    "Perceptions of corruption",
    "Positive Emotions",
    "Negative Emotions",
]

factor_labels = {
    "Log GDP per capita": "GDP per Capita",
    "Social support": "Social Support",
    "Healthy life expectancy at birth": "Life Expectancy",
    "Freedom to make life choices": "Freedom of Choice",
    "Generosity": "Generosity",
    "Perceptions of corruption": "Corruption Perception",
    "Positive Emotions": "Positive Emotions",
    "Negative Emotions": "Negative Emotions",
}

col1, col2 = st.columns(2)

with col1:
    st.subheader("Factor Correlations")
    
    df_clean = df.dropna(subset=["Happiness"] + factor_cols_analysis)
    correlations = df_clean[factor_cols_analysis].corrwith(df_clean["Happiness"]).sort_values(ascending=False)
    correlations.index = [factor_labels[col] for col in correlations.index]
    
    fig_corr = px.bar(
        x=correlations.values,
        y=correlations.index,
        orientation='h',
        title="How Factors Relate to Happiness",
        labels={"x": "Correlation with Happiness", "y": "Factor"},
        color=correlations.values,
        color_continuous_scale="RdYlGn"
    )
    fig_corr.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_corr, use_container_width=True)

with col2:
    st.subheader("Explore by Factor")
    
    selected_factor = st.selectbox(
        "Select a factor to explore:",
        options=list(factor_labels.values())
    )
    
    original_col = [k for k, v in factor_labels.items() if v == selected_factor][0]
    
    top_countries = df_clean.nlargest(15, original_col)[[original_col, "Country", "Happiness"]].sort_values(original_col, ascending=True)
    
    fig_factor = px.bar(
        top_countries,
        y="Country",
        x=original_col,
        orientation='h',
        title=f"Top 15 Countries: {selected_factor}",
        labels={original_col: selected_factor},
        color="Happiness",
        color_continuous_scale="Blues"
    )
    fig_factor.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_factor, use_container_width=True)

# Explanation
st.info("""
**Understanding the Factors:**
- **GDP per Capita**: Economic prosperity and standard of living
- **Social Support**: Having someone to count on in times of trouble
- **Life Expectancy**: Expected years of healthy living
- **Freedom of Choice**: Freedom to make key life decisions
- **Generosity**: Recent donations to charity
- **Corruption Perception**: Trust in government and business
- **Positive Emotions**: Daily experiences of joy, laughter, and enjoyment
- **Negative Emotions**: Daily experiences of worry, sadness, and anger
""")
