import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(
    page_title="World Happiness Dashboard",
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
    df = df.rename(columns={"Country name": "Country", "Life Ladder": "Happiness"})
    return df

df = load_data()

# ------------------------------
# Title & Description
# ------------------------------
st.title("🌎 World Happiness Dashboard (2005–2024)")
st.markdown("""
Explore global happiness trends and discover what factors contribute to national well-being 
using data from the **World Happiness Report**.
""")

# ------------------------------
# Sidebar Filters
# ------------------------------
st.sidebar.header("🔍 Filters")

years = sorted(df["year"].unique())
countries = sorted(df["Country"].unique())

# Year range slider
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

# Country multi-select
selected_countries = st.sidebar.multiselect(
    "Select Countries (for comparison)",
    countries,
    default=["United States", "Finland", "Denmark"] if all(c in countries for c in ["United States", "Finland", "Denmark"]) else countries[:3]
)

# Single year for cross-country analysis
selected_year = st.sidebar.selectbox("Select Year (for rankings)", years[-1] if years else 2024)

# Filter data
filtered_df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
year_df = df[df["year"] == selected_year].copy()

# ------------------------------
# Key Metrics
# ------------------------------
st.header("📊 Key Insights")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_happiness = filtered_df["Happiness"].mean()
    st.metric("Average Happiness", f"{avg_happiness:.2f}")

with col2:
    happiest = year_df.nlargest(1, "Happiness")["Country"].values
    st.metric("Happiest Country", happiest[0] if len(happiest) > 0 else "N/A")

with col3:
    total_countries = filtered_df["Country"].nunique()
    st.metric("Countries Analyzed", total_countries)

with col4:
    years_span = year_range[1] - year_range[0] + 1
    st.metric("Years Covered", years_span)

# ------------------------------
# Visualization 1: Top/Bottom Countries
# ------------------------------
st.header(f"🏆 Top 15 Happiest Countries ({selected_year})")

top15 = year_df.nlargest(15, "Happiness").sort_values("Happiness", ascending=True)

fig1 = px.bar(
    top15,
    y="Country",
    x="Happiness",
    orientation='h',
    title=f"Top 15 Happiest Countries in {selected_year}",
    color="Happiness",
    color_continuous_scale="Viridis",
    labels={"Happiness": "Happiness Score"}
)
fig1.update_layout(height=500, showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

# ------------------------------
# Visualization 2: Country Comparison Over Time
# ------------------------------
st.header("📈 Happiness Trends: Country Comparison")

if selected_countries:
    comparison_df = filtered_df[filtered_df["Country"].isin(selected_countries)]
    
    fig2 = px.line(
        comparison_df,
        x="year",
        y="Happiness",
        color="Country",
        title="Happiness Score Trends Over Time",
        markers=True,
        labels={"year": "Year", "Happiness": "Happiness Score"}
    )
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Please select at least one country from the sidebar.")

# ------------------------------
# Visualization 3: Factor Analysis
# ------------------------------
st.header("🔍 Happiness Factor Analysis")

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

# Calculate correlations with happiness
year_df_clean = year_df.dropna(subset=["Happiness"] + factor_cols)
correlations = year_df_clean[factor_cols].corrwith(year_df_clean["Happiness"]).sort_values(ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Correlation with Happiness")
    fig3 = px.bar(
        x=correlations.values,
        y=correlations.index,
        orientation='h',
        title="Factor Correlations with Happiness Score",
        labels={"x": "Correlation", "y": "Factor"},
        color=correlations.values,
        color_continuous_scale="RdYlGn"
    )
    fig3.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("Average Factor Values")
    factor_means = year_df_clean[factor_cols].mean().sort_values(ascending=True)
    
    fig4 = px.bar(
        x=factor_means.values,
        y=factor_means.index,
        orientation='h',
        title=f"Average Factor Values ({selected_year})",
        labels={"x": "Average Value", "y": "Factor"},
        color=factor_means.values,
        color_continuous_scale="Blues"
    )
    fig4.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

# ------------------------------
# World Map Visualization
# ------------------------------
st.header("🗺️ Global Happiness Map")

fig_map = px.choropleth(
    year_df,
    locations="Country",
    locationmode="country names",
    color="Happiness",
    hover_name="Country",
    hover_data=["Happiness", "Log GDP per capita", "Social support"],
    color_continuous_scale="RdYlGn",
    title=f"World Happiness Scores ({selected_year})"
)
fig_map.update_layout(height=500)
st.plotly_chart(fig_map, use_container_width=True)

# ------------------------------
# ML Section: Clustering
# ------------------------------
st.header("🤖 Machine Learning: Country Clustering")

st.markdown("""
Countries are grouped into clusters based on happiness factors using **K-Means clustering**.
This helps identify countries with similar happiness profiles.
""")

# Prepare data for clustering
cluster_features = ["Happiness", "Log GDP per capita", "Social support", 
                   "Healthy life expectancy at birth", "Freedom to make life choices"]

cluster_df = year_df[["Country"] + cluster_features].dropna()

if len(cluster_df) > 0:
    # Number of clusters
    n_clusters = st.slider("Number of Clusters", min_value=2, max_value=6, value=3)
    
    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(cluster_df[cluster_features])
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_df["Cluster"] = kmeans.fit_predict(features_scaled)
    
    # Visualize clusters
    fig5 = px.scatter(
        cluster_df,
        x="Log GDP per capita",
        y="Happiness",
        color="Cluster",
        hover_name="Country",
        size="Social support",
        title=f"Country Clusters (K={n_clusters})",
        labels={"Cluster": "Cluster Group"},
        color_continuous_scale="Set2"
    )
    fig5.update_layout(height=500)
    st.plotly_chart(fig5, use_container_width=True)
    
    # Display cluster statistics
    st.subheader("Cluster Statistics")
    cluster_stats = cluster_df.groupby("Cluster")[cluster_features].mean().round(2)
    st.dataframe(cluster_stats, use_container_width=True)
    
    # Show countries in each cluster
    with st.expander("View Countries by Cluster"):
        for cluster_id in sorted(cluster_df["Cluster"].unique()):
            countries_in_cluster = cluster_df[cluster_df["Cluster"] == cluster_id]["Country"].tolist()
            st.write(f"**Cluster {cluster_id}:** {', '.join(countries_in_cluster)}")

# ------------------------------
# Data Explorer
# ------------------------------
st.header("📋 Data Explorer")

with st.expander("View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name=f"happiness_data_{year_range[0]}-{year_range[1]}.csv",
        mime="text/csv"
    )

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.markdown("""
**Data Source:** [World Happiness Report](https://worldhappiness.report/)  
**Built with:** Streamlit, Plotly, Scikit-learn
""")