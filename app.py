import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(
    page_title="World Happiness Dashboard 2023",
    page_icon="😁",
    layout="wide"
)


# ------------------------------
# Load Dataset
# ------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Mushimuche/world-happiness-dashboard/main/World-happiness-report-2023.csv"
    df = pd.read_csv(url, encoding="ISO-8859-1")
    return df

df = load_data()


# ------------------------------
# Title & Description
# ------------------------------
st.title("😁 World Happiness Report 2023")
st.subheader("🧑‍💻 Rui Manuel A. Palabon - BSCS3 Machine Problem 3")
st.markdown("""
See which countries are the happiest in 2023! Compare different countries and learn what makes people happy 😊 or unhappy 😞 around the world.
""")

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("🔍 Filters")

# Regional filter
regions = ["All Regions"] + sorted(df["Regional indicator"].unique().tolist())
selected_region = st.sidebar.selectbox(
    "Filter by Region",
    regions
)

# Apply regional filter
if selected_region != "All Regions":
    df_filtered = df[df["Regional indicator"] == selected_region].copy()
else:
    df_filtered = df.copy()

# Happiness score range filter
min_score = float(df["Ladder score"].min())
max_score = float(df["Ladder score"].max())

score_range = st.sidebar.slider(
    "Happiness Score Range",
    min_value=min_score,
    max_value=max_score,
    value=(min_score, max_score),
    step=0.1
)

# Apply happiness score filter
df_filtered = df_filtered[
    (df_filtered["Ladder score"] >= score_range[0]) & 
    (df_filtered["Ladder score"] <= score_range[1])
]

# GDP filter
if "Log GDP per capita" in df_filtered.columns:
    gdp_min = float(df_filtered["Log GDP per capita"].min())
    gdp_max = float(df_filtered["Log GDP per capita"].max())
    
    gdp_range = st.sidebar.slider(
        "GDP per Capita Range (Log)",
        min_value=gdp_min,
        max_value=gdp_max,
        value=(gdp_min, gdp_max),
        step=0.1
    )
    
    df_filtered = df_filtered[
        (df_filtered["Log GDP per capita"] >= gdp_range[0]) & 
        (df_filtered["Log GDP per capita"] <= gdp_range[1])
    ]

countries = sorted(df_filtered["Country name"].unique())

# Country multi-select
default_countries = ["United States", "Finland", "Denmark", "Japan", "Brazil"]
available_defaults = [c for c in default_countries if c in countries]
if not available_defaults:
    available_defaults = countries[:5] if len(countries) >= 5 else countries

selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare",
    countries,
    default=available_defaults
)

# Reset filters button
if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()

# ------------------------------
# Key Metrics
# ------------------------------
st.header("📊 2023 Global Happiness Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_happiness = df_filtered["Ladder score"].mean()
    st.metric("Global Average", f"{avg_happiness:.2f}")

with col2:
    happiest = df_filtered.nlargest(1, "Ladder score")
    if len(happiest) > 0:
        st.metric("Happiest Country", happiest["Country name"].values[0])
        st.caption(f"Score: {happiest['Ladder score'].values[0]:.2f}")

with col3:
    least_happy = df_filtered.nsmallest(1, "Ladder score")
    if len(least_happy) > 0:
        st.metric("Least Happy Country", least_happy["Country name"].values[0])
        st.caption(f"Score: {least_happy['Ladder score'].values[0]:.2f}")

with col4:
    total_countries = len(df_filtered)
    st.metric("Total Countries", total_countries)

# ------------------------------
# Visualization 1: Top/Bottom Countries
# ------------------------------
st.header("🏆 Happiness Rankings")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Happiest Countries 😸")
    top10 = df_filtered.nlargest(10, "Ladder score").sort_values("Ladder score", ascending=True)
    
    fig1 = px.bar(
        top10,
        y="Country name",
        x="Ladder score",
        orientation='h',
        color="Ladder score",
        color_continuous_scale="Greens",
        labels={"Ladder score": "Happiness Score", "Country name": "Country"}
    )
    fig1.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Bottom 10 Countries 😿")
    bottom10 = df_filtered.nsmallest(10, "Ladder score").sort_values("Ladder score", ascending=False)
    
    fig2 = px.bar(
        bottom10,
        y="Country name",
        x="Ladder score",
        orientation='h',
        color="Ladder score",
        color_continuous_scale="Reds",
        labels={"Ladder score": "Happiness Score", "Country name": "Country"}
    )
    fig2.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------
# World Map Visualization
# ------------------------------
st.header("🗺️ Global Happiness Map")

fig_map = px.choropleth(
    df_filtered,
    locations="Country name",
    locationmode="country names",
    color="Ladder score",
    hover_name="Country name",
    hover_data={
        "Ladder score": ":.2f",
        "Log GDP per capita": ":.2f",
        "Social support": ":.2f",
        "Freedom to make life choices": ":.2f",
        "Regional indicator": True
    },
    color_continuous_scale="RdYlGn",
    title="World Happiness Scores in 2023",
    range_color=[df["Ladder score"].min(), df["Ladder score"].max()]
)
fig_map.update_layout(height=500)
st.plotly_chart(fig_map, use_container_width=True)

# ------------------------------
# Country Comparison
# ------------------------------
st.header("🔍 Compare Selected Countries")
st.subheader("Select countries from the sidebar to compare.")

if selected_countries and len(selected_countries) > 0:
    comparison_df = df[df["Country name"].isin(selected_countries)]
    
    # Sort by happiness for better visualization
    comparison_df = comparison_df.sort_values("Ladder score", ascending=False)
    
    # Bar chart comparison
    fig3 = px.bar(
        comparison_df,
        x="Country name",
        y="Ladder score",
        title="Happiness Score Comparison",
        color="Ladder score",
        color_continuous_scale="Viridis",
        labels={"Ladder score": "Happiness Score", "Country name": "Country"}
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
    "Healthy life expectancy",
    "Freedom to make life choices",
    "Generosity",
    "Perceptions of corruption",
]

factor_labels = {
    "Log GDP per capita": "GDP per Capita",
    "Social support": "Social Support",
    "Healthy life expectancy": "Life Expectancy",
    "Freedom to make life choices": "Freedom of Choice",
    "Generosity": "Generosity",
    "Perceptions of corruption": "Corruption Perception",
}

col1, col2 = st.columns(2)

with col1:
    st.subheader("Factor Correlations")
    
    df_clean = df.dropna(subset=["Ladder score"] + factor_cols_analysis)
    correlations = df_clean[factor_cols_analysis].corrwith(df_clean["Ladder score"]).sort_values(ascending=True)
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
    
    top_countries = df_clean.nlargest(15, original_col)[[original_col, "Country name", "Ladder score"]].sort_values(original_col, ascending=True)
    
    fig_factor = px.bar(
        top_countries,
        y="Country name",
        x=original_col,
        orientation='h',
        title=f"Top 15 Countries: {selected_factor}",
        labels={original_col: selected_factor, "Country name": "Country"},
        color="Ladder score",
        color_continuous_scale="RdYlGn"
    )
    fig_factor.update_layout(height=450, showlegend=True, coloraxis_colorbar=dict(title="Happiness Score"))
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
""")