import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import sqlite3
import numpy as np

# Import database model
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Home import Procurement, SessionLocal, engine

st.set_page_config(
    page_title="Analytics - Hange AI",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .analytics-section {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data_from_db():
    """Load procurement data from SQLite database"""
    try:
        session = SessionLocal()
        
        # Query all procurements
        procurements = session.query(Procurement).all()
        
        # Convert to DataFrame
        data = []
        for p in procurements:
            data.append({
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'clean_description': p.clean_description,
                'link': p.link,
                'published': p.published,
                'category': p.category,
                'estimated_value': p.estimated_value,
                'procurer': p.procurer,
                'county': p.county,
                'created_at': p.created_at
            })
        
        session.close()
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame()

def get_value_statistics(df):
    """Calculate value distribution statistics"""
    if df.empty or df['estimated_value'].isna().all():
        return None
    
    value_df = df[df['estimated_value'].notna()].copy()
    
    # Create value ranges
    def categorize_value(value):
        if value < 1000:
            return "< €1K"
        elif value < 5000:
            return "€1K - €5K"
        elif value < 25000:
            return "€5K - €25K"
        elif value < 100000:
            return "€25K - €100K"
        elif value < 500000:
            return "€100K - €500K"
        elif value < 1000000:
            return "€500K - €1M"
        else:
            return "> €1M"
    
    value_df['value_range'] = value_df['estimated_value'].apply(categorize_value)
    value_counts = value_df['value_range'].value_counts()
    
    # Order the ranges properly
    range_order = ["< €1K", "€1K - €5K", "€5K - €25K", "€25K - €100K", 
                  "€100K - €500K", "€500K - €1M", "> €1M"]
    value_counts = value_counts.reindex([r for r in range_order if r in value_counts.index])
    
    return value_counts, value_df

def create_time_series_analysis(df):
    """Create time series analysis of procurements"""
    if df.empty or df['published'].isna().all():
        return None
    
    # Convert to datetime and create daily counts
    df['published'] = pd.to_datetime(df['published'])
    daily_counts = df.groupby(df['published'].dt.date).size().reset_index()
    daily_counts.columns = ['date', 'count']
    
    # Create time series plot
    fig = px.line(
        daily_counts, 
        x='date', 
        y='count',
        title='Daily Procurement Publications',
        labels={'count': 'Number of Procurements', 'date': 'Date'}
    )
    fig.update_layout(height=400)
    
    return fig

def create_county_analysis(df):
    """Create detailed county analysis"""
    if df.empty or df['county'].isna().all():
        return None, None
    
    county_stats = df.groupby('county').agg({
        'id': 'count',
        'estimated_value': ['sum', 'mean', 'count']
    }).round(2)
    
    county_stats.columns = ['Total_Procurements', 'Total_Value', 'Avg_Value', 'Value_Count']
    county_stats = county_stats.reset_index()
    county_stats = county_stats.sort_values('Total_Procurements', ascending=False)
    
    # Create county map visualization
    fig_map = px.bar(
        county_stats.head(10),
        x='county',
        y='Total_Procurements',
        title='Top 10 Counties by Procurement Count',
        color='Total_Procurements',
        color_continuous_scale='Viridis'
    )
    fig_map.update_layout(height=400)
    fig_map.update_xaxis(tickangle=45)
    
    return county_stats, fig_map

def create_category_trends(df):
    """Analyze category trends over time"""
    if df.empty:
        return None
    
    df['published'] = pd.to_datetime(df['published'])
    df['month'] = df['published'].dt.to_period('M')
    
    category_trends = df.groupby(['month', 'category']).size().reset_index(name='count')
    category_trends['month'] = category_trends['month'].astype(str)
    
    # Get top 5 categories
    top_categories = df['category'].value_counts().head(5).index.tolist()
    category_trends_filtered = category_trends[category_trends['category'].isin(top_categories)]
    
    fig = px.line(
        category_trends_filtered,
        x='month',
        y='count',
        color='category',
        title='Category Trends Over Time (Top 5 Categories)',
        labels={'count': 'Number of Procurements', 'month': 'Month'}
    )
    fig.update_layout(height=400)
    fig.update_xaxis(tickangle=45)
    
    return fig

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Advanced Analytics</h1>
        <h3>Deep Insights into Estonian Procurement Data</h3>
        <p>Comprehensive analysis of procurement trends, values, and geographic distribution</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data from database
    with st.spinner('Loading data from database...'):
        df = load_data_from_db()
    
    if df.empty:
        st.warning("No data available in database. Please ensure the RSS feed has been processed.")
        return
    
    # Overview metrics
    st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
    st.subheader("📈 Overview Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_procurements = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Procurements</h4>
            <h2 style="color: #667eea;">{total_procurements:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_procurers = df['procurer'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h4>Unique Procurers</h4>
            <h2 style="color: #667eea;">{unique_procurers:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_counties = df['county'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h4>Counties Covered</h4>
            <h2 style="color: #667eea;">{unique_counties}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        value_procurements = df[df['estimated_value'].notna()]
        if not value_procurements.empty:
            total_value = value_procurements['estimated_value'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h4>Total Value</h4>
                <h2 style="color: #667eea;">€{total_value:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <h4>Total Value</h4>
                <h2 style="color: #667eea;">N/A</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Time Series Analysis
    st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
    st.subheader("📅 Time Series Analysis")
    
    time_fig = create_time_series_analysis(df)
    if time_fig:
        st.plotly_chart(time_fig, use_container_width=True)
    else:
        st.info("No time series data available")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Value Distribution Analysis
    st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
    st.subheader("💰 Value Distribution Analysis")
    
    value_stats = get_value_statistics(df)
    if value_stats:
        value_counts, value_df = value_stats
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Value distribution chart
            fig_value = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title="Procurement Value Distribution",
                color=value_counts.values,
                color_continuous_scale='Blues'
            )
            fig_value.update_layout(
                xaxis_title="Value Range",
                yaxis_title="Number of Procurements",
                height=400,
                showlegend=False
            )
            fig_value.update_xaxis(tickangle=45)
            st.plotly_chart(fig_value, use_container_width=True)
        
        with col2:
            # Value statistics
            st.write("**Value Statistics:**")
            st.write(f"- Total procurements with values: {len(value_df):,}")
            st.write(f"- Average value: €{value_df['estimated_value'].mean():,.2f}")
            st.write(f"- Median value: €{value_df['estimated_value'].median():,.2f}")
            st.write(f"- Highest value: €{value_df['estimated_value'].max():,.2f}")
            st.write(f"- Lowest value: €{value_df['estimated_value'].min():,.2f}")
            
            # Top 5 highest value procurements
            st.write("**Top 5 Highest Value Procurements:**")
            top_values = value_df.nlargest(5, 'estimated_value')[['title', 'estimated_value', 'county']]
            for idx, row in top_values.iterrows():
                st.write(f"- €{row['estimated_value']:,.0f} - {row['title'][:50]}... ({row['county']})")
    else:
        st.info("No value data available for analysis")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # County Analysis
    st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
    st.subheader("🗺️ Geographic Distribution Analysis")
    
    county_stats, county_fig = create_county_analysis(df)
    if county_stats is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(county_fig, use_container_width=True)
        
        with col2:
            st.write("**County Statistics:**")
            st.dataframe(county_stats.head(10), use_container_width=True)
    else:
        st.info("No county data available for analysis")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Category Trends
    st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
    st.subheader("📊 Category Trends Analysis")
    
    category_fig = create_category_trends(df)
    if category_fig:
        st.plotly_chart(category_fig, use_container_width=True)
        
        # Category distribution table
        category_dist = df['category'].value_counts().reset_index()
        category_dist.columns = ['Category', 'Count']
        category_dist['Percentage'] = (category_dist['Count'] / category_dist['Count'].sum() * 100).round(2)
        
        st.write("**Category Distribution:**")
        st.dataframe(category_dist, use_container_width=True)
    else:
        st.info("No category trend data available")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data Quality Report
    st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
    st.subheader("🔍 Data Quality Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Completeness:**")
        completeness = {}
        for col in ['title', 'description', 'category', 'estimated_value', 'procurer', 'county']:
            if col in df.columns:
                non_null_count = df[col].notna().sum()
                completeness[col] = f"{non_null_count}/{len(df)} ({non_null_count/len(df)*100:.1f}%)"
        
        for field, stats in completeness.items():
            st.write(f"- {field.title()}: {stats}")
    
    with col2:
        st.write("**Recent Data Updates:**")
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
            recent_updates = df.groupby(df['created_at'].dt.date).size().tail(7)
            for date, count in recent_updates.items():
                st.write(f"- {date}: {count} procurements")
        else:
            st.write("No update tracking available")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

