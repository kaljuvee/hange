import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI()
client.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

st.set_page_config(page_title="Search & Browse", layout="wide")

def extract_procurement_id(url):
    """Extract procurement ID from URL"""
    try:
        match = re.search(r'/procurement/(\d+)', url)
        if match:
            return match.group(1)
        return None
    except:
        return None

def scrape_procurement_page(procurement_id):
    """Scrape detailed information from procurement page"""
    try:
        # Base URL for procurement details
        base_url = f"https://riigihanked.riik.ee/rhr-web/#/procurement/{procurement_id}/general-info"
        
        # For demonstration, return structured data
        # In production, implement full BeautifulSoup scraping
        procurement_data = {
            "id": procurement_id,
            "title": f"Procurement {procurement_id}",
            "status": "Active",
            "procurer": "Sample Organization",
            "deadline": "2025-12-31",
            "estimated_value": "€50,000 - €100,000",
            "cpv_code": "72000000-5",
            "description": "Detailed procurement description would be scraped here...",
            "requirements": [
                "Technical requirement 1",
                "Technical requirement 2", 
                "Legal requirement 1"
            ],
            "documents": [
                {"name": "Technical Specification", "type": "PDF", "size": "2.5 MB"},
                {"name": "Contract Template", "type": "DOCX", "size": "1.2 MB"},
                {"name": "Evaluation Criteria", "type": "PDF", "size": "800 KB"}
            ]
        }
        
        return procurement_data
        
    except Exception as e:
        st.error(f"Error scraping procurement data: {str(e)}")
        return None

def get_xml_data_from_api(year, month):
    """Fetch XML data from Estonian procurement API"""
    try:
        url = f"https://riigihanked.riik.ee:443/rhr/api/public/v1/opendata/notice/{year}/month/{month}/xml"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.content
        else:
            st.warning(f"API returned status code: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Error fetching XML data: {str(e)}")
        return None

def main():
    st.title("🔍 Advanced Search & Browse")
    st.markdown("### Comprehensive procurement search with drill-down capabilities")
    
    # Search options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_method = st.radio(
            "Search Method:",
            ["RSS Feed (Real-time)", "XML API (Historical)", "Direct URL Lookup"],
            horizontal=True
        )
    
    with col2:
        st.info("💡 Use RSS for latest, XML for historical data, or direct URL for specific procurements")
    
    if search_method == "RSS Feed (Real-time)":
        render_rss_search()
    elif search_method == "XML API (Historical)":
        render_xml_search()
    elif search_method == "Direct URL Lookup":
        render_direct_lookup()

def render_rss_search():
    st.subheader("📡 Real-time RSS Feed Search")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        keyword_filter = st.text_input("🔍 Keyword Filter", placeholder="Enter keywords...")
    
    with col2:
        date_filter = st.selectbox(
            "📅 Date Range",
            ["All", "Last 24 hours", "Last 7 days", "Last 30 days"]
        )
    
    with col3:
        max_results = st.number_input("📊 Max Results", min_value=10, max_value=500, value=50)
    
    if st.button("🔍 Search RSS Feed", type="primary"):
        with st.spinner("Fetching and analyzing RSS data..."):
            try:
                # Fetch RSS feed
                feed = feedparser.parse('https://riigihanked.riik.ee/rhr/api/public/v1/rss')
                
                # Process entries
                data = []
                for entry in feed.entries:
                    creator = entry.get('dc_creator', '') or entry.get('creator', '')
                    published_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                    
                    # Apply date filter
                    if date_filter != "All":
                        now = datetime.now()
                        if date_filter == "Last 24 hours" and (now - published_date).days > 1:
                            continue
                        elif date_filter == "Last 7 days" and (now - published_date).days > 7:
                            continue
                        elif date_filter == "Last 30 days" and (now - published_date).days > 30:
                            continue
                    
                    # Apply keyword filter
                    if keyword_filter:
                        if keyword_filter.lower() not in entry.title.lower() and keyword_filter.lower() not in entry.description.lower():
                            continue
                    
                    data.append({
                        'Title': entry.title,
                        'Link': entry.link,
                        'Description': entry.description,
                        'Published': published_date,
                        'Creator': creator,
                        'ID': extract_procurement_id(entry.link)
                    })
                
                df = pd.DataFrame(data[:max_results])
                
                if not df.empty:
                    st.success(f"Found {len(df)} matching procurements")
                    display_procurement_results(df)
                else:
                    st.warning("No procurements found matching your criteria")
                    
            except Exception as e:
                st.error(f"Error searching RSS feed: {str(e)}")

def render_xml_search():
    st.subheader("📊 Historical XML API Search")
    
    col1, col2 = st.columns(2)
    
    with col1:
        year = st.selectbox("Year", range(2018, 2026), index=7)  # Default to 2025
    
    with col2:
        month = st.selectbox("Month", range(1, 13), index=8)  # Default to September
    
    data_type = st.radio(
        "Data Type:",
        ["Procurement Notices", "Contract Awards"],
        help="Choose between procurement announcements or contract award notices"
    )
    
    if st.button("📥 Fetch XML Data", type="primary"):
        with st.spinner(f"Fetching XML data for {year}-{month:02d}..."):
            xml_data = get_xml_data_from_api(year, month)
            
            if xml_data:
                st.success(f"Successfully fetched XML data ({len(xml_data)} bytes)")
                
                # Parse XML and display summary
                try:
                    from xml.etree import ElementTree as ET
                    root = ET.fromstring(xml_data)
                    
                    # Count elements (simplified parsing)
                    notices = root.findall('.//NOTICE') or root.findall('.//*[contains(local-name(), "NOTICE")]')
                    
                    st.info(f"Found {len(notices)} procurement notices in the XML data")
                    
                    # Option to download XML
                    st.download_button(
                        label="💾 Download XML File",
                        data=xml_data,
                        file_name=f"procurement_{year}_{month:02d}.xml",
                        mime="application/xml"
                    )
                    
                except Exception as e:
                    st.warning(f"Could not parse XML structure: {str(e)}")
                    
                    # Still offer download
                    st.download_button(
                        label="💾 Download Raw XML",
                        data=xml_data,
                        file_name=f"procurement_{year}_{month:02d}.xml",
                        mime="application/xml"
                    )

def render_direct_lookup():
    st.subheader("🎯 Direct Procurement Lookup")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        procurement_url = st.text_input(
            "Procurement URL or ID:",
            placeholder="https://riigihanked.riik.ee/rhr-web/#/procurement/9262944/general-info or just 9262944",
            help="Enter full URL or just the procurement ID number"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        lookup_button = st.button("🔍 Lookup", type="primary")
    
    if lookup_button and procurement_url:
        # Extract ID from URL or use direct ID
        procurement_id = extract_procurement_id(procurement_url) or procurement_url.strip()
        
        if procurement_id and procurement_id.isdigit():
            with st.spinner(f"Looking up procurement {procurement_id}..."):
                procurement_data = scrape_procurement_page(procurement_id)
                
                if procurement_data:
                    display_detailed_procurement(procurement_data)
                else:
                    st.error("Could not fetch procurement details")
        else:
            st.error("Please enter a valid procurement URL or ID")

def display_procurement_results(df):
    """Display procurement results with drill-down capability"""
    
    st.subheader(f"📋 Search Results ({len(df)} procurements)")
    
    # Display options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        view_mode = st.radio("View Mode:", ["Compact List", "Detailed Cards"], horizontal=True)
    
    with col2:
        sort_by = st.selectbox("Sort by:", ["Published Date", "Title", "Creator"])
    
    # Sort dataframe
    if sort_by == "Published Date":
        df = df.sort_values('Published', ascending=False)
    elif sort_by == "Title":
        df = df.sort_values('Title')
    elif sort_by == "Creator":
        df = df.sort_values('Creator')
    
    if view_mode == "Compact List":
        # Compact table view
        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.write(f"**{row['Title'][:80]}{'...' if len(row['Title']) > 80 else ''}**")
                st.caption(f"👤 {row['Creator']} | 📅 {row['Published'].strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                if st.button("🔍 Details", key=f"details_compact_{idx}"):
                    if row['ID']:
                        st.session_state[f'show_details_{row["ID"]}'] = True
                        st.rerun()
            
            with col3:
                st.link_button("🌐 Original", row['Link'])
            
            st.divider()
    
    else:
        # Detailed cards view
        for idx, row in df.iterrows():
            with st.expander(f"🏛️ {row['Title']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Procurer:** {row['Creator']}")
                    st.write(f"**Published:** {row['Published'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Description:** {row['Description'][:200]}{'...' if len(row['Description']) > 200 else ''}")
                
                with col2:
                    if st.button("🔍 Drill Down", key=f"drill_{idx}"):
                        if row['ID']:
                            st.session_state[f'show_details_{row["ID"]}'] = True
                            st.rerun()
                    
                    st.link_button("🌐 Open Original", row['Link'])
    
    # Show detailed views if requested
    for idx, row in df.iterrows():
        if f'show_details_{row["ID"]}' in st.session_state and st.session_state[f'show_details_{row["ID"]}']:
            display_detailed_procurement_modal(row['ID'])

def display_detailed_procurement_modal(procurement_id):
    """Display detailed procurement information in a modal-like format"""
    
    st.markdown("---")
    st.subheader(f"🔍 Detailed View: Procurement {procurement_id}")
    
    col1, col2 = st.columns([4, 1])
    
    with col2:
        if st.button("❌ Close Details", key=f"close_{procurement_id}"):
            del st.session_state[f'show_details_{procurement_id}']
            st.rerun()
    
    with st.spinner("Loading detailed information..."):
        procurement_data = scrape_procurement_page(procurement_id)
    
    if procurement_data:
        display_detailed_procurement(procurement_data)

def display_detailed_procurement(procurement_data):
    """Display comprehensive procurement details"""
    
    # Header information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📋 Procurement ID", procurement_data['id'])
    
    with col2:
        st.metric("📊 Status", procurement_data['status'])
    
    with col3:
        st.metric("💰 Estimated Value", procurement_data['estimated_value'])
    
    # Detailed information in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 General Info", "📄 Documents", "📝 Requirements", "🤖 AI Analysis"])
    
    with tab1:
        st.write(f"**Title:** {procurement_data['title']}")
        st.write(f"**Procurer:** {procurement_data['procurer']}")
        st.write(f"**Deadline:** {procurement_data['deadline']}")
        st.write(f"**CPV Code:** {procurement_data['cpv_code']}")
        st.write(f"**Description:** {procurement_data['description']}")
    
    with tab2:
        st.subheader("📄 Available Documents")
        
        if procurement_data['documents']:
            for doc in procurement_data['documents']:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"📄 {doc['name']}")
                
                with col2:
                    st.write(doc['type'])
                
                with col3:
                    st.write(doc['size'])
                
                with col4:
                    if st.button("📥 Fetch", key=f"fetch_{doc['name']}"):
                        st.info("Document fetching will be implemented in the next phase")
        else:
            st.info("No documents available")
    
    with tab3:
        st.subheader("📝 Requirements")
        
        if procurement_data['requirements']:
            for i, req in enumerate(procurement_data['requirements'], 1):
                st.write(f"{i}. {req}")
        else:
            st.info("No specific requirements listed")
    
    with tab4:
        st.subheader("🤖 AI Analysis")
        
        if st.button("Generate AI Analysis", key=f"ai_analysis_{procurement_data['id']}"):
            with st.spinner("Generating AI analysis..."):
                # Placeholder for AI analysis
                st.write("**🎯 Suitability Score:** 85/100")
                st.write("**📊 Complexity Level:** Medium")
                st.write("**⏱️ Estimated Preparation Time:** 2-3 weeks")
                st.write("**💡 Key Insights:**")
                st.write("- This procurement focuses on technical services")
                st.write("- Moderate competition expected")
                st.write("- Standard documentation requirements")
                st.write("**⚠️ Recommendations:**")
                st.write("- Prepare technical specifications early")
                st.write("- Review similar past procurements")
                st.write("- Consider partnership opportunities")

if __name__ == "__main__":
    main()

