import streamlit as st
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.chat_agent import (
    create_chat_agent, 
    get_county_suggestions, 
    get_category_suggestions,
    format_procurement_result
)

st.set_page_config(
    page_title="HangeGPT - AI Chat Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for chat interface
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
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .user-message {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    .ai-message {
        background: #f3e5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }
    .suggestion-chip {
        display: inline-block;
        background: #f0f0f0;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        cursor: pointer;
        border: 1px solid #ddd;
        transition: all 0.3s;
    }
    .suggestion-chip:hover {
        background: #667eea;
        color: white;
    }
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def initialize_chat_agent():
    """Initialize the chat agent with caching"""
    if 'chat_agent' not in st.session_state:
        with st.spinner('Initializing HangeGPT...'):
            st.session_state.chat_agent = create_chat_agent()
    return st.session_state.chat_agent

def initialize_chat_history():
    """Initialize chat history"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_messages = []

def add_message(role: str, content: str):
    """Add message to chat history"""
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat_messages.append({
        'role': role,
        'content': content,
        'timestamp': timestamp
    })

def display_chat_history():
    """Display the chat history"""
    for message in st.session_state.chat_messages:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="user-message">
                <strong>You ({message['timestamp']}):</strong><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ai-message">
                <strong>HangeGPT ({message['timestamp']}):</strong><br>
                {message['content']}
            </div>
            """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 HangeGPT</h1>
        <h3>AI-Powered Procurement Assistant</h3>
        <p>Ask questions about Estonian procurement data in natural language</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    chat_agent = initialize_chat_agent()
    initialize_chat_history()
    
    # Sidebar with information and suggestions
    with st.sidebar:
        st.markdown("### 💡 What can you ask?")
        
        st.markdown("**Examples:**")
        suggestions = chat_agent.get_suggestions()
        
        for suggestion in suggestions[:5]:
            if st.button(suggestion, key=f"suggestion_{suggestion[:20]}", use_container_width=True):
                # Add suggestion as user message and get response
                add_message('user', suggestion)
                with st.spinner('HangeGPT is thinking...'):
                    response = chat_agent.chat(suggestion, st.session_state.chat_history)
                add_message('assistant', response)
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 🗺️ Counties")
        counties = get_county_suggestions()
        selected_counties = st.multiselect(
            "Filter by county:",
            counties,
            key="county_filter"
        )
        
        st.markdown("### 📂 Categories")
        categories = get_category_suggestions()
        selected_categories = st.multiselect(
            "Filter by category:",
            categories,
            key="category_filter"
        )
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <h4>Chat Sessions</h4>
                <h3 style="color: #667eea;">Active</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            message_count = len(st.session_state.chat_messages)
            st.markdown(f"""
            <div class="stats-card">
                <h4>Messages</h4>
                <h3 style="color: #667eea;">{message_count}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.chat_history = []
            st.rerun()
    
    # Main chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message
    if not st.session_state.chat_messages:
        st.markdown("""
        <div class="ai-message">
            <strong>HangeGPT:</strong><br>
            👋 Hello! I'm HangeGPT, your AI assistant for Estonian procurement data. 
            
            I can help you:
            • Find specific procurements by category, location, or value
            • Analyze procurement trends and statistics  
            • Compare different types of procurements
            • Get insights about procurement patterns
            
            Try asking me something like "Show me all construction procurements in Tallinn" or "What are the highest value IT procurements?"
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    display_chat_history()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("### 💬 Ask HangeGPT")
    
    # Create columns for input and button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your question here...",
            placeholder="e.g., Show me all healthcare procurements in Harjumaa",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send 🚀", use_container_width=True)
    
    # Handle user input
    if send_button and user_input:
        # Add user message
        add_message('user', user_input)
        
        # Get AI response
        with st.spinner('HangeGPT is analyzing your request...'):
            try:
                # Apply filters if selected
                enhanced_query = user_input
                if selected_counties:
                    enhanced_query += f" (focus on counties: {', '.join(selected_counties)})"
                if selected_categories:
                    enhanced_query += f" (focus on categories: {', '.join(selected_categories)})"
                
                response = chat_agent.chat(enhanced_query, st.session_state.chat_history)
                add_message('assistant', response)
                
                # Update chat history for context
                st.session_state.chat_history.extend([
                    {'role': 'user', 'content': user_input},
                    {'role': 'assistant', 'content': response}
                ])
                
            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
                add_message('assistant', error_message)
        
        # Clear input and rerun
        st.session_state.user_input = ""
        st.rerun()
    
    # Quick action buttons
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Latest Procurements", use_container_width=True):
            query = "Show me the latest procurements from today"
            add_message('user', query)
            with st.spinner('Getting latest data...'):
                response = chat_agent.chat(query, st.session_state.chat_history)
                add_message('assistant', response)
            st.rerun()
    
    with col2:
        if st.button("🏗️ Construction Projects", use_container_width=True):
            query = "Show me all construction and infrastructure procurements"
            add_message('user', query)
            with st.spinner('Finding construction projects...'):
                response = chat_agent.chat(query, st.session_state.chat_history)
                add_message('assistant', response)
            st.rerun()
    
    with col3:
        if st.button("💰 High Value Deals", use_container_width=True):
            query = "Show me procurements with values over €100,000"
            add_message('user', query)
            with st.spinner('Finding high value procurements...'):
                response = chat_agent.chat(query, st.session_state.chat_history)
                add_message('assistant', response)
            st.rerun()
    
    with col4:
        if st.button("🏛️ Tallinn Procurements", use_container_width=True):
            query = "Show me all procurements in Tallinn"
            add_message('user', query)
            with st.spinner('Finding Tallinn procurements...'):
                response = chat_agent.chat(query, st.session_state.chat_history)
                add_message('assistant', response)
            st.rerun()
    
    # Tips section
    with st.expander("💡 Tips for better results"):
        st.markdown("""
        **To get the best results from HangeGPT:**
        
        1. **Be specific**: Instead of "show procurements", try "show IT procurements in Tallinn"
        2. **Use filters**: Mention specific counties, categories, or value ranges
        3. **Ask for comparisons**: "Compare construction vs healthcare procurement values"
        4. **Request analysis**: "What are the trends in energy procurements?"
        5. **Time-based queries**: "Show procurements from the last 7 days"
        
        **Supported counties**: Harjumaa, Tartumaa, Ida-Virumaa, Pärnumaa, and 11 others
        
        **Supported categories**: Technology & IT, Healthcare & Medical, Construction & Infrastructure, and 9 others
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🤖 HangeGPT is powered by advanced AI and real-time Estonian procurement data
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

