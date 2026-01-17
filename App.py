"""
🌌 Exoplanet Discovery Explorer
Professional Streamlit Dashboard for NASA Exoplanet Data
"""

import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
from datetime import datetime

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="🌌 Exoplanet Explorer",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-size: 1.1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============ DATABASE CONNECTION ============
@st.cache_resource
def get_connection():
    """Create database connection with caching"""
    return sqlite3.connect('exoplanets.db', check_same_thread=False)

@st.cache_data(ttl=3600)
def load_data_cached(query):
    """Execute SQL query with caching"""
    conn = get_connection()
    return pd.read_sql_query(query, conn)

# ============ DATA LOADING FUNCTIONS ============
def get_total_stats():
    """Get overall statistics"""
    conn = get_connection()
    
    stats = {
        'total_planets': pd.read_sql("SELECT COUNT(*) as cnt FROM planets", conn).iloc[0]['cnt'],
        'total_stars': pd.read_sql("SELECT COUNT(DISTINCT hostname) as cnt FROM planets", conn).iloc[0]['cnt'],
        'habitable': pd.read_sql("SELECT COUNT(*) as cnt FROM planets WHERE habitability_score > 50", conn).iloc[0]['cnt'],
        'latest_year': pd.read_sql("SELECT MAX(disc_year) as yr FROM planets WHERE disc_year IS NOT NULL", conn).iloc[0]['yr']
    }
    
    return stats

# ============ MAIN APP ============
def main():
    
    # Header
    st.markdown('<h1 class="main-header">🌌 Exoplanet Discovery Explorer</h1>', unsafe_allow_html=True)
    st.markdown("### Explore 10,000+ Confirmed Exoplanets from NASA's Archive")
    st.markdown("---")
    
    # ============ SIDEBAR ============
    with st.sidebar:
        st.image("https://science.nasa.gov/wp-content/uploads/2023/09/nasa-logo-web-rgb.png", width=180)
        
        st.markdown("## 🎯 Navigation")
        page = st.radio(
            "Choose a page:",
            ["🏠 Dashboard", "🔍 Explorer", "📊 Analytics", "🌟 Top Discoveries", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📈 Quick Stats")
        
        stats = get_total_stats()
        st.metric("Total Planets", f"{stats['total_planets']:,}")
        st.metric("Host Stars", f"{stats['total_stars']:,}")
        st.metric("Potentially Habitable", f"{stats['habitable']:,}")
        
        st.markdown("---")
        st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d')}*")
    
    # ============ PAGE ROUTING ============
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🔍 Explorer":
        show_explorer()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "🌟 Top Discoveries":
        show_top_discoveries()
    else:
        show_about()


# ============ PAGE 1: DASHBOARD ============
def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    stats = get_total_stats()
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🪐 Total Planets", f"{stats['total_planets']:,}")
    with col2:
        st.metric("⭐ Host Stars", f"{stats['total_stars']:,}")
    with col3:
        st.metric("🌍 Habitable Candidates", f"{stats['habitable']:,}")
    with col4:
        st.metric("📅 Latest Discovery", int(stats['latest_year']))
    
    st.markdown("---")
    
    # Two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Discoveries Over Time")
        
        timeline_query = """
        SELECT disc_year as year, COUNT(*) as count
        FROM planets
        WHERE disc_year IS NOT NULL AND disc_year >= 1990
        GROUP BY disc_year
        ORDER BY disc_year
        """
        timeline_df = load_data_cached(timeline_query)
        
        chart = alt.Chart(timeline_df).mark_area(
            color='lightblue',
            line={'color': 'steelblue'},
            opacity=0.7
        ).encode(
            x=alt.X('year:Q', title='Year'),
            y=alt.Y('count:Q', title='Discoveries'),
            tooltip=['year', 'count']
        ).properties(height=350).interactive()
        
        st.altair_chart(chart, use_container_width=True)
    
    with col2:
        st.subheader("🔬 Discovery Methods")
        
        methods_query = """
        SELECT discoverymethod as method, COUNT(*) as count
        FROM planets
        WHERE discoverymethod IS NOT NULL
        GROUP BY discoverymethod
        ORDER BY count DESC
        LIMIT 8
        """
        methods_df = load_data_cached(methods_query)
        
        chart = alt.Chart(methods_df).mark_bar().encode(
            x=alt.X('count:Q', title='Number of Planets'),
            y=alt.Y('method:N', title='Method', sort='-x'),
            color=alt.Color('count:Q', scale=alt.Scale(scheme='viridis')),
            tooltip=['method', 'count']
        ).properties(height=350).interactive()
        
        st.altair_chart(chart, use_container_width=True)
    
    # Planet types distribution
    st.markdown("---")
    st.subheader("🪐 Planet Type Distribution")
    
    types_query = """
    SELECT planet_type, COUNT(*) as count
    FROM planets
    WHERE planet_type IS NOT NULL AND planet_type != 'Unknown'
    GROUP BY planet_type
    ORDER BY count DESC
    """
    types_df = load_data_cached(types_query)
    
    chart = alt.Chart(types_df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta('count:Q'),
        color=alt.Color('planet_type:N', legend=alt.Legend(title="Planet Type")),
        tooltip=['planet_type', 'count']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)


# ============ PAGE 2: EXPLORER ============
def show_explorer():
    st.header("🔍 Exoplanet Data Explorer")
    st.markdown("Filter and search through the complete exoplanet database")
    
    # Filters
    st.subheader("🎛️ Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        discovery_methods = load_data_cached("SELECT DISTINCT discoverymethod FROM planets WHERE discoverymethod IS NOT NULL")
        selected_methods = st.multiselect(
            "Discovery Method",
            options=discovery_methods['discoverymethod'].tolist(),
            default=[]
        )
        
        year_range = st.slider(
            "Discovery Year",
            min_value=1990,
            max_value=2025,
            value=(2000, 2025)
        )
    
    with col2:
        radius_range = st.slider(
            "Radius (Earth radii)",
            min_value=0.0,
            max_value=25.0,
            value=(0.0, 25.0),
            step=0.5
        )
        
        temp_range = st.slider(
            "Temperature (K)",
            min_value=0,
            max_value=3000,
            value=(0, 3000),
            step=50
        )
    
    with col3:
        planet_types = load_data_cached("SELECT DISTINCT planet_type FROM planets WHERE planet_type IS NOT NULL")
        selected_types = st.multiselect(
            "Planet Type",
            options=planet_types['planet_type'].tolist(),
            default=[]
        )
        
        min_habitability = st.slider(
            "Minimum Habitability Score",
            min_value=0,
            max_value=100,
            value=0,
            step=10
        )
    
    # Build query based on filters
    query = """
    SELECT 
        pl_name as "Planet Name",
        hostname as "Host Star",
        discoverymethod as "Method",
        disc_year as "Year",
        planet_type as "Type",
        pl_rade as "Radius (R⊕)",
        pl_masse as "Mass (M⊕)",
        pl_eqt as "Temp (K)",
        pl_orbper as "Period (days)",
        habitability_score as "Habitability"
    FROM planets
    WHERE 1=1
    """
    
    conditions = []
    if selected_methods:
        methods_str = "','".join(selected_methods)
        conditions.append(f"discoverymethod IN ('{methods_str}')")
    
    conditions.append(f"disc_year BETWEEN {year_range[0]} AND {year_range[1]}")
    conditions.append(f"pl_rade BETWEEN {radius_range[0]} AND {radius_range[1]}")
    conditions.append(f"pl_eqt BETWEEN {temp_range[0]} AND {temp_range[1]}")
    
    if selected_types:
        types_str = "','".join(selected_types)
        conditions.append(f"planet_type IN ('{types_str}')")
    
    conditions.append(f"habitability_score >= {min_habitability}")
    
    if conditions:
        query += " AND " + " AND ".join(conditions)
    
    query += " ORDER BY disc_year DESC, habitability_score DESC LIMIT 1000"
    
    # Execute and display
    df = load_data_cached(query)
    
    st.markdown(f"### 📋 Results: {len(df)} planets found")
    
    if len(df) > 0:
        # Display options
        col1, col2 = st.columns([3, 1])
        with col1:
            st.dataframe(df, use_container_width=True, height=500)
        with col2:
            st.markdown("### 📥 Export")
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"exoplanets_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            st.markdown("### 📊 Summary")
            st.metric("Average Radius", f"{df['Radius (R⊕)'].mean():.2f} R⊕")
            st.metric("Average Temp", f"{df['Temp (K)'].mean():.0f} K")
            st.metric("Avg Habitability", f"{df['Habitability'].mean():.0f}")
    else:
        st.warning("No planets match your filters. Try adjusting the criteria.")


# ============ PAGE 3: ANALYTICS ============
def show_analytics():
    st.header("📊 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🌍 Habitability", "⭐ Stars"])
    
    with tab1:
        st.subheader("Discovery Trends Analysis")
        
        # Discoveries by era
        era_query = """
        SELECT discovery_era, COUNT(*) as count
        FROM planets
        WHERE discovery_era IS NOT NULL
        GROUP BY discovery_era
        ORDER BY discovery_era
        """
        era_df = load_data_cached(era_query)
        
        chart = alt.Chart(era_df).mark_bar(size=50).encode(
            x=alt.X('discovery_era:N', title='Era'),
            y=alt.Y('count:Q', title='Discoveries'),
            color=alt.value('steelblue'),
            tooltip=['discovery_era', 'count']
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
    
    with tab2:
        st.subheader("Habitability Analysis")
        
        # Habitability distribution
        hab_query = """
        SELECT habitability_score, COUNT(*) as count
        FROM planets
        GROUP BY habitability_score
        ORDER BY habitability_score
        """
        hab_df = load_data_cached(hab_query)
        
        chart = alt.Chart(hab_df).mark_bar().encode(
            x=alt.X('habitability_score:Q', title='Habitability Score', bin=alt.Bin(step=10)),
            y=alt.Y('count():Q', title='Number of Planets'),
            color=alt.condition(
                alt.datum.habitability_score > 50,
                alt.value('green'),
                alt.value('gray')
            ),
            tooltip=['habitability_score', 'count']
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
        
        # Most habitable planets
        st.markdown("### 🌍 Most Habitable Candidates")
        top_hab_query = """
        SELECT pl_name, hostname, pl_rade, pl_eqt, habitability_score
        FROM planets
        WHERE habitability_score > 50
        ORDER BY habitability_score DESC
        LIMIT 15
        """
        top_hab_df = load_data_cached(top_hab_query)
        st.dataframe(top_hab_df, use_container_width=True)
    
    with tab3:
        st.subheader("Multi-Planet Systems")
        
        # Systems with most planets
        systems_query = """
        SELECT hostname, planet_count
        FROM stars
        WHERE planet_count > 1
        ORDER BY planet_count DESC
        LIMIT 20
        """
        systems_df = load_data_cached(systems_query)
        
        chart = alt.Chart(systems_df).mark_bar().encode(
            y=alt.Y('hostname:N', title='Star System', sort='-x'),
            x=alt.X('planet_count:Q', title='Number of Planets'),
            color=alt.Color('planet_count:Q', scale=alt.Scale(scheme='plasma')),
            tooltip=['hostname', 'planet_count']
        ).properties(height=500)
        
        st.altair_chart(chart, use_container_width=True)


# ============ PAGE 4: TOP DISCOVERIES ============
def show_top_discoveries():
    st.header("🌟 Notable Discoveries")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Hottest Planets")
        hot_query = """
        SELECT pl_name, hostname, pl_eqt as temp, disc_year
        FROM planets
        WHERE pl_eqt IS NOT NULL
        ORDER BY pl_eqt DESC
        LIMIT 10
        """
        hot_df = load_data_cached(hot_query)
        st.dataframe(hot_df, use_container_width=True)
        
        st.subheader("❄️ Coldest Planets")
        cold_query = """
        SELECT pl_name, hostname, pl_eqt as temp, disc_year
        FROM planets
        WHERE pl_eqt IS NOT NULL AND pl_eqt > 0
        ORDER BY pl_eqt ASC
        LIMIT 10
        """
        cold_df = load_data_cached(cold_query)
        st.dataframe(cold_df, use_container_width=True)
    
    with col2:
        st.subheader("🪐 Largest Planets")
        large_query = """
        SELECT pl_name, hostname, pl_rade as radius, disc_year
        FROM planets
        WHERE pl_rade IS NOT NULL
        ORDER BY pl_rade DESC
        LIMIT 10
        """
        large_df = load_data_cached(large_query)
        st.dataframe(large_df, use_container_width=True)
        
        st.subheader("🏃 Fastest Orbits")
        fast_query = """
        SELECT pl_name, hostname, pl_orbper as period, disc_year
        FROM planets
        WHERE pl_orbper IS NOT NULL AND pl_orbper > 0
        ORDER BY pl_orbper ASC
        LIMIT 10
        """
        fast_df = load_data_cached(fast_query)
        st.dataframe(fast_df, use_container_width=True)


# ============ PAGE 5: ABOUT ============
def show_about():
    st.header("ℹ️ About This Project")
    
    st.markdown("""
    ## 🌌 Exoplanet Discovery Explorer
    
    This interactive dashboard provides comprehensive insights into confirmed exoplanets
    from NASA's Exoplanet Archive.
    
    ### 📊 Features
    - **10,000+ Exoplanets**: Complete database of confirmed discoveries
    - **Interactive Filters**: Explore by size, temperature, discovery method, and more
    - **Habitability Scoring**: Custom metric to identify potentially habitable worlds
    - **Advanced Analytics**: Trends, statistics, and correlations
    - **Real-time Visualizations**: Dynamic charts built with Altair
    
    ### 🔬 Data Source
    All data is sourced from the [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/),
    maintained by Caltech/IPAC under contract with NASA.
    
    ### 📖 Habitability Score Explained
    Our custom habitability score (0-100) considers:
    - **Radius**: 0.5-2 Earth radii (35 points)
    - **Temperature**: 200-350 K (40 points)
    - **Orbital Period**: 200-500 days (25 points)
    
    Planets scoring above 50 are considered potentially habitable candidates.
    
    ### 🛠️ Built With
    - **Python**: Data processing and analysis
    - **Streamlit**: Web framework
    - **SQLite**: Database management
    - **Altair**: Interactive visualizations
    - **Pandas**: Data manipulation
    
    ### 📫 Contact
    Created as part of a space data exploration project.
    
    ---
    *Last updated: {0}*
    """.format(datetime.now().strftime('%B %d, %Y')))


# ============ RUN APP ============
if __name__ == "__main__":
    main()
