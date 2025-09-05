import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import feedparser
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import insert

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = "sqlite:///./procurement_data.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class Procurement(Base):
    __tablename__ = "procurements"
    
    id = Column(String, primary_key=True)
    title = Column(Text)
    description = Column(Text)
    clean_description = Column(Text)
    link = Column(String)
    published = Column(DateTime)
    category = Column(String)
    estimated_value = Column(Float)
    procurer = Column(String)
    county = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Estonian counties mapping
ESTONIAN_COUNTIES = {
    'Harjumaa': ['Tallinn', 'Keila', 'Saue', 'Maardu', 'Paldiski', 'Loksa', 'Kehra', 'Saku', 'Jüri', 'Viimsi', 'Rae', 'Kiili'],
    'Tartumaa': ['Tartu', 'Elva', 'Kallaste', 'Võru', 'Otepää', 'Tõrva', 'Põlva', 'Räpina'],
    'Ida-Virumaa': ['Narva', 'Kohtla-Järve', 'Sillamäe', 'Jõhvi', 'Kiviõli', 'Tapa'],
    'Pärnumaa': ['Pärnu', 'Viljandi', 'Kilingi-Nõmme', 'Sindi', 'Tori'],
    'Lääne-Virumaa': ['Rakvere', 'Tamsalu', 'Kunda', 'Väike-Maarja'],
    'Järvamaa': ['Paide', 'Türi', 'Koigi'],
    'Viljandimaa': ['Viljandi', 'Suure-Jaani', 'Mõisaküla', 'Abja-Paluoja'],
    'Raplamaa': ['Rapla', 'Kohila', 'Märjamaa'],
    'Võrumaa': ['Võru', 'Antsla'],
    'Valgamaa': ['Valga', 'Tõrva', 'Otepää'],
    'Põlvamaa': ['Põlva', 'Räpina'],
    'Jõgevamaa': ['Jõgeva', 'Mustvee'],
    'Läänemaa': ['Haapsalu', 'Lihula'],
    'Saaremaa': ['Kuressaare', 'Orissaare'],
    'Hiiumaa': ['Kärdla']
}

def map_to_county(procurer_text):
    """Map procurer location to Estonian county"""
    if not procurer_text:
        return 'Unknown'
    
    procurer_lower = procurer_text.lower()
    
    # Direct county name matches
    for county in ESTONIAN_COUNTIES.keys():
        if county.lower().replace('maa', '') in procurer_lower:
            return county
    
    # City/location matches
    for county, cities in ESTONIAN_COUNTIES.items():
        for city in cities:
            if city.lower() in procurer_lower:
                return county
    
    # Special cases for common abbreviations
    if any(word in procurer_lower for word in ['tallinn', 'harju']):
        return 'Harjumaa'
    elif any(word in procurer_lower for word in ['tartu']):
        return 'Tartumaa'
    elif any(word in procurer_lower for word in ['narva', 'ida-viru']):
        return 'Ida-Virumaa'
    elif any(word in procurer_lower for word in ['pärnu']):
        return 'Pärnumaa'
    
    return 'Other'
llm = ChatOpenAI(
    model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
    api_key=os.getenv('OPENAI_API_KEY'),
    temperature=0.1
)

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

# Function to translate text using LangChain OpenAI
@st.cache_data(ttl=3600)  # Cache for 1 hour
def translate_text(text):
    try:
        prompt = f"You are a translator. Translate the following Estonian text to English. Keep it concise and professional.\n\n{text[:1000]}"
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Translation error: {str(e)}"

# Function to classify procurement with enhanced categories
@st.cache_data(ttl=3600)  # Cache for 1 hour
def classify_procurement(title, description):
    try:
        # Clean description using BeautifulSoup
        soup = BeautifulSoup(description, 'html.parser')
        clean_description = soup.get_text().strip()
        
        prompt = f"""Analyze this Estonian procurement and classify it into the most appropriate category.
        
        Categories:
        - Technology & IT: Software, hardware, IT services, digital solutions, websites, databases
        - Healthcare & Medical: Medical equipment, pharmaceuticals, healthcare services, hospital supplies
        - Construction & Infrastructure: Building construction, roads, bridges, renovation, infrastructure projects
        - Professional Services: Consulting, legal services, accounting, auditing, design services
        - Education & Training: Educational services, training programs, school supplies, educational equipment
        - Transportation: Vehicles, transport services, logistics, public transport
        - Energy & Environment: Energy systems, environmental services, waste management, utilities
        - Security & Defense: Security services, defense equipment, surveillance systems
        - Food & Catering: Food supplies, catering services, restaurant equipment
        - Office & Supplies: Office equipment, furniture, stationery, general supplies
        - Maintenance & Cleaning: Cleaning services, maintenance work, facility management
        - Other: Everything else that doesn't fit the above categories
        
        Title: {title}
        Description: {clean_description[:800]}
        
        Based on the Estonian text, return ONLY the category name (e.g., "Construction & Infrastructure").
        """
        
        response = llm.invoke(f"""You are an expert in Estonian procurement classification. Analyze the text carefully and return only the most appropriate category name.

{prompt}""")
        
        category = response.content.strip()
        
        # Validate category
        valid_categories = [
            "Technology & IT", "Healthcare & Medical", "Construction & Infrastructure",
            "Professional Services", "Education & Training", "Transportation",
            "Energy & Environment", "Security & Defense", "Food & Catering",
            "Office & Supplies", "Maintenance & Cleaning", "Other"
        ]
        
        if category in valid_categories:
            return category
        else:
            return "Other"
            
    except Exception as e:
        print(f"Classification error: {e}")
        return "Other"

# Function to extract value from description
def extract_value(description):
    # Clean description using BeautifulSoup
    soup = BeautifulSoup(description, 'html.parser')
    clean_description = soup.get_text()
    
    # Enhanced patterns for Estonian currency
    patterns = [
        r'(\d+(?:\s?\d{3})*(?:[,\.]\d{2})?)\s*(?:EUR|eurot|€)',
        r'(\d+(?:\s?\d{3})*(?:[,\.]\d{2})?)\s*(?:euro)',
        r'maksumus[:\s]*(\d+(?:\s?\d{3})*(?:[,\.]\d{2})?)',
        r'väärtus[:\s]*(\d+(?:\s?\d{3})*(?:[,\.]\d{2})?)',
        r'hind[:\s]*(\d+(?:\s?\d{3})*(?:[,\.]\d{2})?)',
        r'summa[:\s]*(\d+(?:\s?\d{3})*(?:[,\.]\d{2})?)',
        r'(\d+(?:\s?\d{3})*(?:[,\.]\d{2})?)\s*eur',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_description, re.IGNORECASE)
        if match:
            value_str = match.group(1).replace(' ', '').replace(',', '.')
            try:
                value = float(value_str)
                # Filter out unrealistic values
                if 100 <= value <= 100000000:  # Between 100 EUR and 100M EUR
                    return value
            except:
                continue
    return None

# Function to parse and format description
def parse_description(description):
    """Parse HTML description and extract clean text with proper formatting"""
    try:
        soup = BeautifulSoup(description, 'html.parser')
        
        # Extract clean text
        clean_text = soup.get_text().strip()
        
        # Limit length and add ellipsis
        if len(clean_text) > 300:
            clean_text = clean_text[:300] + "..."
        
        return clean_text
    except:
        return description[:300] + "..." if len(description) > 300 else description

# Function to extract procurement ID from link
def extract_procurement_id(link):
    """Extract procurement ID from the link"""
    try:
        # Pattern for Estonian procurement links
        match = re.search(r'/procurement/(\d+)/', link)
        if match:
            return match.group(1)
        return 'unknown'
    except:
        return 'unknown'

# Function to load and process RSS feed
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_procurement_data():
    try:
        # Check if data exists in session state and is recent
        if 'procurement_data' in st.session_state and 'last_update' in st.session_state:
            last_update = st.session_state['last_update']
            if datetime.now() - last_update < timedelta(minutes=5):
                return st.session_state['procurement_data']
        
        # Load RSS feed
        feed = feedparser.parse('https://riigihanked.riik.ee/rhr/api/public/v1/rss')
        
        procurements = []
        session = SessionLocal()
        
        try:
            for entry in feed.entries:
                # Parse date
                pub_date = parse_date(entry.published)
                
                # Extract value with improved parsing
                estimated_value = extract_value(entry.description)
                
                # Classify procurement with improved categorization
                category = classify_procurement(entry.title, entry.description)
                
                # Parse description properly
                clean_description = parse_description(entry.description)
                
                # Extract procurement ID
                procurement_id = extract_procurement_id(entry.link)
                
                # Extract procurer and map to county
                procurer = entry.get('author', 'Unknown')
                county = map_to_county(procurer)
                
                procurement_data = {
                    'title': entry.title,
                    'description': entry.description,  # Keep original for processing
                    'clean_description': clean_description,  # Clean version for display
                    'link': entry.link,
                    'published': pub_date,
                    'category': category,
                    'estimated_value': estimated_value,
                    'procurer': procurer,
                    'county': county,
                    'id': procurement_id
                }
                
                # Store in database using upsert
                try:
                    stmt = insert(Procurement).values(
                        id=procurement_id,
                        title=entry.title,
                        description=entry.description,
                        clean_description=clean_description,
                        link=entry.link,
                        published=pub_date,
                        category=category,
                        estimated_value=estimated_value,
                        procurer=procurer,
                        county=county
                    )
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['id'],
                        set_=dict(
                            title=stmt.excluded.title,
                            description=stmt.excluded.description,
                            clean_description=stmt.excluded.clean_description,
                            category=stmt.excluded.category,
                            estimated_value=stmt.excluded.estimated_value,
                            procurer=stmt.excluded.procurer,
                            county=stmt.excluded.county
                        )
                    )
                    session.execute(stmt)
                except Exception as db_error:
                    print(f"Database error for procurement {procurement_id}: {db_error}")
                
                procurements.append(procurement_data)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"Error processing feed: {e}")
        finally:
            session.close()
        
        # Create DataFrame
        df = pd.DataFrame(procurements)
        
        # Store in session state with timestamp
        st.session_state['procurement_data'] = df
        st.session_state['last_update'] = datetime.now()
        
        return df
    
    except Exception as e:
        st.error(f"Error loading procurement data: {str(e)}")
        # Return cached data if available, otherwise empty DataFrame
        if 'procurement_data' in st.session_state:
            return st.session_state['procurement_data']
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
        st.subheader("🗺️ Distribution by County")
        if not df.empty:
            county_counts = df['county'].value_counts()
            if not county_counts.empty:
                fig_county = px.bar(
                    x=county_counts.index,
                    y=county_counts.values,
                    title="Procurements by Estonian County",
                    color=county_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig_county.update_layout(
                    xaxis_title="County",
                    yaxis_title="Number of Procurements",
                    height=400,
                    showlegend=False,
                    xaxis={'tickangle': 45}
                )
                st.plotly_chart(fig_county, use_container_width=True)
            else:
                st.info("County data is being processed...")
        else:
            st.info("No county data available")
    
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
            # Create a proper link to the procurement details
            procurement_link = row['link']
            if 'rhr-web' not in procurement_link:
                # Convert API link to web interface link
                procurement_id = row['id']
                procurement_link = f"https://riigihanked.riik.ee/rhr-web/#/procurement/{procurement_id}/general-info"
            
            st.markdown(f"""
            <div class="procurement-card">
                <h4 style="margin-top: 0; color: #1e3a8a;">{row['title']}</h4>
                <p><strong>Procurer:</strong> {row['procurer']}</p>
                <p><strong>Category:</strong> <span class="status-badge status-active">{row['category']}</span></p>
                <p><strong>Published:</strong> {row['published'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['published']) else 'Unknown'}</p>
                {f"<p><strong>Estimated Value:</strong> €{row['estimated_value']:,.0f}</p>" if pd.notna(row['estimated_value']) else ""}
                <p><strong>Description:</strong> {row['clean_description']}</p>
                <a href="{procurement_link}" target="_blank" style="color: #3b82f6; text-decoration: none;">🔗 View Details</a>
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

