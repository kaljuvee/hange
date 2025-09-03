import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()
client = OpenAI()
# Configure OpenAI
client.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# Set page config
st.set_page_config(
    page_title="Estonian Public Procurement AI Platform", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
def init_database():
    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            sectors TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS procurement_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_id TEXT UNIQUE NOT NULL,
            title TEXT,
            description TEXT,
            url TEXT,
            details TEXT,
            documents TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to parse date
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    except:
        return None

# Function to translate text using OpenAI
def translate_text(text):
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a translator. Translate the following Estonian text to English:"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Translation error: {str(e)}"

# Function to classify procurement
def classify_procurement(title, description):
    try:
        prompt = f"""Classify the following Estonian procurement into one of these categories. 
        Analyze the Estonian text directly without translation.
        
        Categories:
        - Construction & Infrastructure (Ehitus & Infrastruktuur)
        - Technology & IT (Tehnoloogia & IT)
        - Healthcare & Medical (Tervishoid & Meditsiin)
        - Education & Research (Haridus & Teadus)
        - Energy & Utilities (Energia & Kommunaalteenused)
        - Transportation (Transport)
        - Environmental Services (Keskkonnateenus)
        - Professional Services (Professionaalsed Teenused)
        - Sports & Recreation (Sport & Vaba Aeg)
        - Other (Muu)

        Title: {title}
        Description: {description}

        Return only the category name in English."""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a procurement classifier who understands Estonian language."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Classification error: {str(e)}"

# Function to extract procurement ID from URL
def extract_procurement_id(url):
    try:
        # Extract ID from URL like https://riigihanked.riik.ee/rhr-web/#/procurement/9262944/general-info
        match = re.search(r'/procurement/(\d+)', url)
        if match:
            return match.group(1)
        return None
    except:
        return None

# Function to scrape procurement details
def scrape_procurement_details(procurement_id):
    try:
        # Check cache first
        conn = sqlite3.connect('procurement.db')
        cursor = conn.cursor()
        cursor.execute('SELECT details, documents FROM procurement_cache WHERE procurement_id = ?', (procurement_id,))
        cached = cursor.fetchone()
        
        if cached:
            conn.close()
            return cached[0], cached[1]
        
        # Scrape from website
        base_url = f"https://riigihanked.riik.ee/rhr-web/#/procurement/{procurement_id}"
        
        # For now, return placeholder data - in production, implement full scraping
        details = {
            "general_info": f"Detailed information for procurement {procurement_id}",
            "procurer": "Sample Procurer",
            "status": "Active",
            "deadline": "2025-12-31",
            "value": "€100,000"
        }
        
        documents = [
            {"name": "Technical Specification", "type": "PDF", "url": f"{base_url}/documents/tech_spec.pdf"},
            {"name": "Contract Template", "type": "DOCX", "url": f"{base_url}/documents/contract.docx"}
        ]
        
        # Cache the results
        cursor.execute('''
            INSERT OR REPLACE INTO procurement_cache 
            (procurement_id, details, documents) 
            VALUES (?, ?, ?)
        ''', (procurement_id, str(details), str(documents)))
        conn.commit()
        conn.close()
        
        return details, documents
        
    except Exception as e:
        st.error(f"Error scraping procurement details: {str(e)}")
        return None, None

# Sidebar for navigation
def render_sidebar():
    st.sidebar.title("🏛️ Hange AI")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Home", "🔍 Search & Browse", "📧 Email Notifications", "📄 Documents", "📊 Analytics"]
    )
    
    st.sidebar.markdown("---")
    
    # Quick filters
    st.sidebar.subheader("Quick Filters")
    
    sectors = st.sidebar.multiselect(
        "Sectors of Interest:",
        ["Technology & IT", "Healthcare & Medical", "Construction & Infrastructure", 
         "Professional Services", "Education & Research", "Transportation", 
         "Energy & Utilities", "Environmental Services", "Sports & Recreation", "Other"],
        default=["Technology & IT", "Professional Services"]
    )
    
    value_range = st.sidebar.slider(
        "Value Range (€)",
        min_value=0,
        max_value=1000000,
        value=(10000, 500000),
        step=10000
    )
    
    return page, sectors, value_range

# Main app
def main():
    init_database()
    
    # Render sidebar
    page, sectors, value_range = render_sidebar()
    
    if page == "🏠 Home":
        render_home_page(sectors, value_range)
    elif page == "🔍 Search & Browse":
        render_search_page()
    elif page == "📧 Email Notifications":
        render_email_page()
    elif page == "📄 Documents":
        render_documents_page()
    elif page == "📊 Analytics":
        render_analytics_page()

def render_home_page(sectors, value_range):
    st.title("🇪🇪 Estonian Public Procurement AI Platform")
    st.markdown("### Intelligent procurement search with AI-powered insights")
    
    # Fetch RSS feed
    try:
        with st.spinner("Loading latest procurements..."):
            feed = feedparser.parse('https://riigihanked.riik.ee/rhr/api/public/v1/rss')
        
        # Create DataFrame
        data = []
        for entry in feed.entries:
            creator = entry.get('dc_creator', '')
            if not creator:
                creator = entry.get('creator', '')
            
            data.append({
                'Title': entry.title,
                'Link': entry.link,
                'Description': entry.description,
                'Published': parse_date(entry.published),
                'Creator': creator,
                'ID': extract_procurement_id(entry.link)
            })
        
        df = pd.DataFrame(data)
        
        # Display dataset statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Procurements", len(df))
        with col2:
            st.metric("📅 Latest Date", df['Published'].max().strftime('%Y-%m-%d') if not df.empty else "N/A")
        with col3:
            st.metric("🏢 Unique Procurers", df['Creator'].nunique())
        with col4:
            st.metric("🔄 Updated", "Real-time")
        
        # Enhanced procurement display with drill-down
        st.subheader("🔍 Latest Procurements")
        
        # Row selection for processing
        row_options = [50, 100, 200, 500]
        num_rows = st.selectbox(
            "Number of procurements to analyze:",
            options=row_options,
            index=1,
            help="Choose how many procurements to classify and analyze."
        )
        
        # Classification and display
        if st.button("🤖 Analyze with AI", type="primary"):
            with st.spinner(f"Analyzing {num_rows} procurements with AI..."):
                df_subset = df.head(num_rows).copy()
                
                # Add progress bar
                progress_bar = st.progress(0)
                
                categories = []
                for i, row in df_subset.iterrows():
                    category = classify_procurement(row['Title'], row['Description'])
                    categories.append(category)
                    progress_bar.progress((i + 1) / len(df_subset))
                
                df_subset['Category'] = categories
                st.session_state['processed_df'] = df_subset
                progress_bar.empty()
        
        # Display processed results
        if 'processed_df' in st.session_state:
            df_processed = st.session_state['processed_df']
            
            # Filter by selected sectors
            if sectors:
                df_filtered = df_processed[df_processed['Category'].isin(sectors)]
            else:
                df_filtered = df_processed
            
            # Display filtered results with drill-down capability
            st.subheader(f"📊 Analyzed Results ({len(df_filtered)} procurements)")
            
            for idx, row in df_filtered.iterrows():
                with st.expander(f"🏛️ {row['Title'][:100]}..." if len(row['Title']) > 100 else row['Title']):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Category:** {row['Category']}")
                        st.write(f"**Procurer:** {row['Creator']}")
                        st.write(f"**Published:** {row['Published'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Description:** {row['Description'][:300]}...")
                    
                    with col2:
                        if st.button(f"🔍 View Details", key=f"details_{idx}"):
                            if row['ID']:
                                st.session_state['selected_procurement'] = row['ID']
                                st.rerun()
                        
                        if st.button(f"🌐 Open Original", key=f"original_{idx}"):
                            st.markdown(f"[Open in new tab]({row['Link']})")
            
            # Category distribution chart
            if not df_filtered.empty:
                st.subheader("📈 Category Distribution")
                category_counts = df_filtered['Category'].value_counts().reset_index()
                category_counts.columns = ['Category', 'Count']
                
                fig = px.pie(
                    category_counts,
                    values='Count',
                    names='Category',
                    title='Distribution of Procurements by Category'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed view if procurement selected
        if 'selected_procurement' in st.session_state:
            show_procurement_details(st.session_state['selected_procurement'])
        
    except Exception as e:
        st.error(f"Error loading procurement data: {str(e)}")

def show_procurement_details(procurement_id):
    st.markdown("---")
    st.subheader(f"🔍 Detailed View: Procurement {procurement_id}")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("⬅️ Back to List"):
            del st.session_state['selected_procurement']
            st.rerun()
    
    with col1:
        st.write(f"**Procurement ID:** {procurement_id}")
    
    # Fetch detailed information
    with st.spinner("Loading detailed information..."):
        details, documents = scrape_procurement_details(procurement_id)
    
    if details:
        # Display details in tabs
        tab1, tab2, tab3 = st.tabs(["📋 General Info", "📄 Documents", "🤖 AI Analysis"])
        
        with tab1:
            st.json(details)
        
        with tab2:
            if documents:
                st.write("**Available Documents:**")
                for doc in eval(documents) if isinstance(documents, str) else documents:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"📄 {doc['name']}")
                    with col2:
                        st.write(doc['type'])
                    with col3:
                        st.button("📥 Download", key=f"download_{doc['name']}")
            else:
                st.info("No documents available")
        
        with tab3:
            if st.button("🤖 Generate AI Summary"):
                with st.spinner("Generating AI analysis..."):
                    # Placeholder for AI analysis
                    st.write("**AI Analysis:**")
                    st.write("This procurement appears to be for...")
                    st.write("**Key Requirements:**")
                    st.write("- Requirement 1")
                    st.write("- Requirement 2")
                    st.write("**Recommendation:**")
                    st.write("Based on the analysis, this procurement is suitable for...")

def render_search_page():
    st.title("🔍 Advanced Search & Browse")
    st.write("Advanced search functionality will be implemented here.")

def render_email_page():
    st.title("📧 Email Notifications")
    
    st.write("### Subscribe to Procurement Alerts")
    
    with st.form("email_subscription"):
        email = st.text_input("Email Address")
        sectors = st.multiselect(
            "Select Sectors of Interest:",
            ["Technology & IT", "Healthcare & Medical", "Construction & Infrastructure", 
             "Professional Services", "Education & Research", "Transportation", 
             "Energy & Utilities", "Environmental Services", "Sports & Recreation", "Other"]
        )
        
        if st.form_submit_button("Subscribe"):
            if email and sectors:
                try:
                    conn = sqlite3.connect('procurement.db')
                    cursor = conn.cursor()
                    cursor.execute(
                        'INSERT OR REPLACE INTO email_subscriptions (email, sectors) VALUES (?, ?)',
                        (email, ','.join(sectors))
                    )
                    conn.commit()
                    conn.close()
                    st.success("Successfully subscribed to email notifications!")
                except Exception as e:
                    st.error(f"Error subscribing: {str(e)}")
            else:
                st.error("Please provide email and select at least one sector.")

def render_documents_page():
    st.title("📄 Document Processing")
    st.write("Document processing and form generation will be implemented here.")

def render_analytics_page():
    st.title("📊 Analytics Dashboard")
    st.write("Analytics and reporting features will be implemented here.")

if __name__ == "__main__":
    main()

