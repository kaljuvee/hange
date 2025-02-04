import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv
import plotly.express as px

# Load environment variables
load_dotenv()
client = OpenAI()
# Configure OpenAI
client.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # Add fallback model

# Set page config
st.set_page_config(page_title="Estonian Public Procurement Feed", layout="wide")

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
            model=OPENAI_MODEL,  # Use model from env
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

# Main app
st.title("Estonian Public Procurement Feed")

# Fetch RSS feed
try:
    feed = feedparser.parse('https://riigihanked.riik.ee/rhr/api/public/v1/rss')
    
    # Create DataFrame
    data = []
    for entry in feed.entries:
        # Fix creator parsing using dc namespace
        creator = entry.get('dc_creator', '')  # feedparser automatically converts 'dc:creator' to 'dc_creator'
        if not creator:  # fallback in case the format changes
            creator = entry.get('creator', '')
        
        data.append({
            'Title': entry.title,
            'Link': entry.link,
            'Description': entry.description,
            'Published': parse_date(entry.published),
            'Creator': creator,
        })
    
    df = pd.DataFrame(data)
    
    # Display dataset statistics
    st.subheader("Dataset Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Procurements", len(df))
    with col2:
        st.metric("Earliest Date", df['Published'].min().strftime('%Y-%m-%d'))
    with col3:
        st.metric("Latest Date", df['Published'].max().strftime('%Y-%m-%d'))
    
    # Display original data
    st.subheader("Latest Procurements")
    st.dataframe(df)
    
    # Row selection for processing
    row_options = list(range(100, len(df) + 100, 100))
    num_rows = st.selectbox(
        "Select number of rows to process:",
        options=row_options,
        index=0,
        help="Choose how many procurements to classify. Processing more rows will take longer."
    )
    
    # Classification
    if st.button("Classify Procurements"):
        st.info(f"Classifying {num_rows} rows... This may take a moment.")
        # Process only selected number of rows
        df_subset = df.head(num_rows).copy()
        df_subset['Category'] = df_subset.apply(lambda x: classify_procurement(x['Title'], x['Description']), axis=1)
        
        # Store the processed dataframe in session state
        st.session_state['processed_df'] = df_subset
        
        # Default categories for filter
        default_categories = [
            'Professional Services',
            'Technology & IT',
            'Healthcare & Medical',
            'Other'  # Added Other category
        ]
        
        # Get unique categories for multiselect
        all_categories = sorted(df_subset['Category'].unique().tolist())
        
        # Create multiselect filter
        selected_categories = st.multiselect(
            "Filter by Categories:",
            options=all_categories,
            default=default_categories,
            help="Select one or more categories to filter the results"
        )
        
        # Filter dataframe based on selection
        if selected_categories:
            filtered_df = df_subset[df_subset['Category'].isin(selected_categories)]
        else:
            filtered_df = df_subset
        
        # Display filtered dataframe
        st.subheader("Filtered Procurement Categories")
        st.dataframe(filtered_df[['Title', 'Description', 'Category', 'Creator', 'Published']])
        
        # Create category distribution chart
        category_counts = df_subset['Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        
        fig = px.bar(
            category_counts,
            x='Category',
            y='Count',
            title='Distribution of Procurements by Category',
            labels={'Count': 'Number of Procurements', 'Category': 'Procurement Category'},
            color='Category'
        )
        
        # Customize layout
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            height=500
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching or processing the feed: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Data source: Estonian Public Procurement Registry")
