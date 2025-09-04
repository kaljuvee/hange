import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import json
from enhanced_document_processor import EnhancedDocumentProcessor

# Load environment variables
load_dotenv()
client = OpenAI()
client.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')

# Set page config
st.set_page_config(
    page_title="Hange AI - Estonian Procurement Intelligence Platform", 
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
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
        border-left: 4px solid #3b82f6;
    }
    .procurement-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-active { background-color: #dcfce7; color: #166534; }
    .status-deadline { background-color: #fef3c7; color: #92400e; }
    .status-closed { background-color: #fee2e2; color: #991b1b; }
    .confidence-high { color: #059669; font-weight: bold; }
    .confidence-medium { color: #d97706; font-weight: bold; }
    .confidence-low { color: #dc2626; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize enhanced document processor
@st.cache_resource
def get_document_processor():
    return EnhancedDocumentProcessor()

# Function to parse date
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    except:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None

# Function to translate text using OpenAI
@st.cache_data(ttl=3600)  # Cache for 1 hour
def translate_text(text):
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a translator. Translate the following Estonian text to English. Keep it concise and professional."},
                {"role": "user", "content": text[:1000]}  # Limit text length
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Translation error: {str(e)}"

# Function to classify procurement with enhanced categories
@st.cache_data(ttl=3600)  # Cache for 1 hour
def classify_procurement(title, description):
    try:
        prompt = f"""Classify the following Estonian procurement into one of these categories. 
        Analyze the Estonian text directly without translation.
        
        Categories:
        - Technology & IT (Tehnoloogia & IT)
        - Healthcare & Medical (Tervishoid & Meditsiin)
        - Construction & Infrastructure (Ehitus & Infrastruktuur)
        - Professional Services (Erialateenused)
        - Education & Training (Haridus & Koolitus)
        - Transportation (Transport)
        - Energy & Environment (Energia & Keskkond)
        - Security & Defense (Turvalisus & Kaitse)
        - Other (Muu)
        
        Title: {title}
        Description: {description[:500]}
        
        Return only the category name in English (e.g., "Technology & IT").
        """
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert in Estonian procurement classification. Return only the category name."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Other"

# Function to extract value from description
def extract_value(description):
    import re
    # Look for Estonian currency patterns
    patterns = [
        r'(\d+(?:\s?\d{3})*(?:,\d{2})?)\s*(?:EUR|eurot|€)',
        r'(\d+(?:\s?\d{3})*(?:,\d{2})?)\s*(?:euro)',
        r'maksumus[:\s]*(\d+(?:\s?\d{3})*(?:,\d{2})?)',
        r'väärtus[:\s]*(\d+(?:\s?\d{3})*(?:,\d{2})?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(' ', '').replace(',', '.')
            try:
                return float(value_str)
            except:
                continue
    return None

# Function to load and process RSS feed
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_procurement_data():
    try:
        # Load RSS feed
        feed = feedparser.parse('https://riigihanked.riik.ee/rhr/api/public/v1/rss')
        
        procurements = []
        for entry in feed.entries:
            # Parse date
            pub_date = parse_date(entry.published)
            
            # Extract value
            estimated_value = extract_value(entry.description)
            
            # Classify procurement
            category = classify_procurement(entry.title, entry.description)
            
            procurement = {
                'title': entry.title,
                'description': entry.description,
                'link': entry.link,
                'published': pub_date,
                'category': category,
                'estimated_value': estimated_value,
                'procurer': entry.get('author', 'Unknown'),
                'id': entry.link.split('/')[-2] if '/' in entry.link else 'unknown'
            }
            procurements.append(procurement)
        
        return pd.DataFrame(procurements)
    
    except Exception as e:
        st.error(f"Error loading procurement data: {str(e)}")
        return pd.DataFrame()

# Function to get procurement statistics
def get_procurement_stats(df):
    if df.empty:
        return {
            'total_procurements': 0,
            'latest_date': 'N/A',
            'unique_procurers': 0,
            'total_value': 0,
            'avg_value': 0
        }
    
    # Calculate statistics
    total_procurements = len(df)
    latest_date = df['published'].max().strftime('%Y-%m-%d') if df['published'].notna().any() else 'N/A'
    unique_procurers = df['procurer'].nunique()
    
    # Value statistics
    value_df = df[df['estimated_value'].notna()]
    total_value = value_df['estimated_value'].sum() if not value_df.empty else 0
    avg_value = value_df['estimated_value'].mean() if not value_df.empty else 0
    
    return {
        'total_procurements': total_procurements,
        'latest_date': latest_date,
        'unique_procurers': unique_procurers,
        'total_value': total_value,
        'avg_value': avg_value
    }

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Hange AI</h1>
        <h3>Estonian Public Procurement Intelligence Platform</h3>
        <p>AI-powered procurement search with intelligent insights and automated document processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading latest procurement data...'):
        df = load_procurement_data()
    
    if df.empty:
        st.error("Unable to load procurement data. Please check your internet connection.")
        return
    
    # Get statistics
    stats = get_procurement_stats(df)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📋 Total Procurements</h3>
            <h2 style="color: #3b82f6; margin: 0;">{stats['total_procurements']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅 Latest Date</h3>
            <h2 style="color: #059669; margin: 0;">{stats['latest_date']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏢 Unique Procurers</h3>
            <h2 style="color: #dc2626; margin: 0;">{stats['unique_procurers']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Total Value</h3>
            <h2 style="color: #7c3aed; margin: 0;">€{stats['total_value']:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Analytics section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Procurement Categories")
        if not df.empty:
            category_counts = df['category'].value_counts()
            fig_pie = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Distribution by Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📈 Value Distribution")
        if not df.empty and df['estimated_value'].notna().any():
            value_df = df[df['estimated_value'].notna()]
            fig_hist = px.histogram(
                value_df,
                x='estimated_value',
                title="Estimated Value Distribution",
                nbins=20,
                color_discrete_sequence=['#3b82f6']
            )
            fig_hist.update_layout(
                xaxis_title="Estimated Value (EUR)",
                yaxis_title="Count",
                height=400
            )
            st.plotly_chart(fig_hist, use_container_width=True)
    
    # Timeline chart
    st.subheader("📅 Procurement Timeline")
    if not df.empty and df['published'].notna().any():
        timeline_df = df[df['published'].notna()].copy()
        timeline_df['date'] = timeline_df['published'].dt.date
        daily_counts = timeline_df.groupby('date').size().reset_index(name='count')
        
        fig_timeline = px.line(
            daily_counts,
            x='date',
            y='count',
            title="Daily Procurement Publications",
            markers=True,
            color_discrete_sequence=['#059669']
        )
        fig_timeline.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Procurements",
            height=300
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("---")
    
    # Recent procurements
    st.subheader("🔍 Latest Procurements")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("Filter by Category", categories)
    
    with col2:
        min_value = st.number_input("Minimum Value (EUR)", min_value=0, value=0, step=1000)
    
    with col3:
        max_value = st.number_input("Maximum Value (EUR)", min_value=0, value=1000000, step=10000)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    if min_value > 0:
        filtered_df = filtered_df[
            (filtered_df['estimated_value'].isna()) | 
            (filtered_df['estimated_value'] >= min_value)
        ]
    
    if max_value < 1000000:
        filtered_df = filtered_df[
            (filtered_df['estimated_value'].isna()) | 
            (filtered_df['estimated_value'] <= max_value)
        ]
    
    # Display filtered procurements
    st.write(f"Showing {len(filtered_df)} of {len(df)} procurements")
    
    for idx, row in filtered_df.head(10).iterrows():
        with st.container():
            st.markdown(f"""
            <div class="procurement-card">
                <h4 style="margin-top: 0; color: #1e3a8a;">{row['title']}</h4>
                <p><strong>Procurer:</strong> {row['procurer']}</p>
                <p><strong>Category:</strong> <span class="status-badge status-active">{row['category']}</span></p>
                <p><strong>Published:</strong> {row['published'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['published']) else 'Unknown'}</p>
                {f"<p><strong>Estimated Value:</strong> €{row['estimated_value']:,.0f}</p>" if pd.notna(row['estimated_value']) else ""}
                <p><strong>Description:</strong> {row['description'][:200]}...</p>
                <a href="{row['link']}" target="_blank" style="color: #3b82f6; text-decoration: none;">🔗 View Details</a>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 2rem;">
        <p>🤖 Powered by Hange AI | Real-time data from Estonian Public Procurement Registry</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()

