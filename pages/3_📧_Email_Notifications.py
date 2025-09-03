import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser
import re
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI()
client.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')

st.set_page_config(page_title="Email Notifications", layout="wide")

def init_email_database():
    """Initialize email notification database"""
    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()
    
    # Email subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            sectors TEXT NOT NULL,
            keywords TEXT,
            min_value INTEGER DEFAULT 0,
            max_value INTEGER DEFAULT 10000000,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_notification TIMESTAMP,
            notification_frequency TEXT DEFAULT 'daily'
        )
    ''')
    
    # Notification history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscription_id INTEGER,
            procurement_id TEXT,
            procurement_title TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            email_status TEXT DEFAULT 'sent',
            FOREIGN KEY (subscription_id) REFERENCES email_subscriptions (id)
        )
    ''')
    
    # Procurement cache for matching
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS procurement_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            procurement_id TEXT UNIQUE,
            title TEXT,
            description TEXT,
            category TEXT,
            estimated_value INTEGER,
            deadline DATE,
            procurer TEXT,
            url TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def classify_procurement(title, description):
    """Classify procurement using OpenAI"""
    try:
        prompt = f"""Classify the following Estonian procurement into one of these categories:
        
        Categories:
        - Construction & Infrastructure
        - Technology & IT
        - Healthcare & Medical
        - Education & Research
        - Energy & Utilities
        - Transportation
        - Environmental Services
        - Professional Services
        - Sports & Recreation
        - Other

        Title: {title}
        Description: {description}

        Return only the category name."""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a procurement classifier."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Other"

def extract_estimated_value(description):
    """Extract estimated value from procurement description"""
    try:
        # Look for EUR amounts in various formats
        patterns = [
            r'(\d+(?:\s?\d{3})*)\s*EUR',
            r'(\d+(?:\s?\d{3})*)\s*€',
            r'EUR\s*(\d+(?:\s?\d{3})*)',
            r'€\s*(\d+(?:\s?\d{3})*)',
            r'(\d+(?:\s?\d{3})*)\s*euro'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(' ', '')
                return int(value_str)
        
        return 0
    except:
        return 0

def send_email_notification(email, procurements, subscription_info):
    """Send email notification to subscriber"""
    try:
        # For demo purposes, we'll just log the email
        # In production, implement actual SMTP sending
        
        email_content = f"""
        Dear Subscriber,
        
        We found {len(procurements)} new procurement opportunities matching your criteria:
        
        Sectors: {subscription_info['sectors']}
        Keywords: {subscription_info.get('keywords', 'Any')}
        Value Range: €{subscription_info['min_value']:,} - €{subscription_info['max_value']:,}
        
        Matching Procurements:
        """
        
        for proc in procurements:
            email_content += f"""
        
        Title: {proc['title']}
        Category: {proc['category']}
        Estimated Value: €{proc['estimated_value']:,}
        Procurer: {proc['procurer']}
        Deadline: {proc['deadline']}
        URL: {proc['url']}
        
        ---
        """
        
        email_content += """
        
        Best regards,
        Hange AI Team
        
        To unsubscribe or modify your preferences, visit: https://hange-ai.streamlit.app/
        """
        
        # Log the email (in production, send via SMTP)
        st.success(f"Email notification prepared for {email} with {len(procurements)} matches")
        
        return True
        
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

def check_procurement_matches():
    """Check for new procurements and send notifications"""
    try:
        # Fetch latest RSS feed
        feed = feedparser.parse('https://riigihanked.riik.ee/rhr/api/public/v1/rss')
        
        conn = sqlite3.connect('procurement.db')
        cursor = conn.cursor()
        
        new_matches = 0
        
        for entry in feed.entries:
            procurement_id = re.search(r'/procurement/(\d+)', entry.link)
            if not procurement_id:
                continue
            
            procurement_id = procurement_id.group(1)
            
            # Check if already processed
            cursor.execute('SELECT id FROM procurement_matches WHERE procurement_id = ?', (procurement_id,))
            if cursor.fetchone():
                continue
            
            # Classify and extract info
            category = classify_procurement(entry.title, entry.description)
            estimated_value = extract_estimated_value(entry.description)
            creator = entry.get('dc_creator', '') or entry.get('creator', '')
            
            # Store procurement
            cursor.execute('''
                INSERT INTO procurement_matches 
                (procurement_id, title, description, category, estimated_value, procurer, url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (procurement_id, entry.title, entry.description, category, estimated_value, creator, entry.link))
            
            # Find matching subscriptions
            cursor.execute('SELECT * FROM email_subscriptions WHERE active = 1')
            subscriptions = cursor.fetchall()
            
            for sub in subscriptions:
                sub_id, email, sectors, keywords, min_val, max_val, active, created_at, last_notif, freq = sub
                
                # Check sector match
                user_sectors = [s.strip() for s in sectors.split(',')]
                if category not in user_sectors:
                    continue
                
                # Check value range
                if estimated_value < min_val or estimated_value > max_val:
                    continue
                
                # Check keywords
                if keywords:
                    keyword_list = [k.strip().lower() for k in keywords.split(',')]
                    text_to_search = (entry.title + ' ' + entry.description).lower()
                    if not any(keyword in text_to_search for keyword in keyword_list):
                        continue
                
                # Check notification frequency
                if last_notif:
                    last_notification = datetime.fromisoformat(last_notif)
                    if freq == 'daily' and (datetime.now() - last_notification).days < 1:
                        continue
                    elif freq == 'weekly' and (datetime.now() - last_notification).days < 7:
                        continue
                
                # Record notification
                cursor.execute('''
                    INSERT INTO notification_history 
                    (subscription_id, procurement_id, procurement_title)
                    VALUES (?, ?, ?)
                ''', (sub_id, procurement_id, entry.title))
                
                # Update last notification time
                cursor.execute('''
                    UPDATE email_subscriptions 
                    SET last_notification = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (sub_id,))
                
                new_matches += 1
        
        conn.commit()
        conn.close()
        
        return new_matches
        
    except Exception as e:
        st.error(f"Error checking matches: {str(e)}")
        return 0

def main():
    init_email_database()
    
    st.title("📧 Email Notification System")
    st.markdown("### Subscribe to procurement alerts tailored to your interests")
    
    # Tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Subscribe", "⚙️ Manage Subscriptions", "📊 Analytics", "🔔 Test Notifications"])
    
    with tab1:
        render_subscription_form()
    
    with tab2:
        render_subscription_management()
    
    with tab3:
        render_analytics()
    
    with tab4:
        render_test_notifications()

def render_subscription_form():
    st.subheader("📝 Create New Subscription")
    
    with st.form("email_subscription"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            
            sectors = st.multiselect(
                "🏢 Sectors of Interest",
                ["Technology & IT", "Healthcare & Medical", "Construction & Infrastructure", 
                 "Professional Services", "Education & Research", "Transportation", 
                 "Energy & Utilities", "Environmental Services", "Sports & Recreation", "Other"],
                default=["Technology & IT"]
            )
            
            keywords = st.text_input(
                "🔍 Keywords (optional)",
                placeholder="software, development, AI, etc.",
                help="Comma-separated keywords to filter procurements"
            )
        
        with col2:
            st.write("**💰 Value Range (EUR)**")
            min_value = st.number_input("Minimum Value", min_value=0, value=10000, step=1000)
            max_value = st.number_input("Maximum Value", min_value=0, value=1000000, step=10000)
            
            frequency = st.selectbox(
                "📅 Notification Frequency",
                ["daily", "weekly"],
                help="How often you want to receive notifications"
            )
            
            st.write("**📋 Subscription Summary**")
            st.info(f"""
            - **Sectors:** {', '.join(sectors) if sectors else 'None selected'}
            - **Keywords:** {keywords if keywords else 'Any'}
            - **Value Range:** €{min_value:,} - €{max_value:,}
            - **Frequency:** {frequency.title()}
            """)
        
        submitted = st.form_submit_button("🔔 Subscribe to Notifications", type="primary")
        
        if submitted:
            if email and sectors:
                try:
                    conn = sqlite3.connect('procurement.db')
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO email_subscriptions 
                        (email, sectors, keywords, min_value, max_value, notification_frequency)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (email, ','.join(sectors), keywords, min_value, max_value, frequency))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Successfully subscribed to email notifications!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Error creating subscription: {str(e)}")
            else:
                st.error("Please provide email address and select at least one sector.")

def render_subscription_management():
    st.subheader("⚙️ Manage Your Subscriptions")
    
    # Email lookup
    lookup_email = st.text_input("Enter your email to manage subscriptions:")
    
    if lookup_email:
        conn = sqlite3.connect('procurement.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_subscriptions WHERE email = ?', (lookup_email,))
        subscription = cursor.fetchone()
        
        if subscription:
            sub_id, email, sectors, keywords, min_val, max_val, active, created_at, last_notif, freq = subscription
            
            st.success(f"Found subscription for {email}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Settings:**")
                st.write(f"- **Sectors:** {sectors}")
                st.write(f"- **Keywords:** {keywords or 'None'}")
                st.write(f"- **Value Range:** €{min_val:,} - €{max_val:,}")
                st.write(f"- **Frequency:** {freq}")
                st.write(f"- **Status:** {'Active' if active else 'Inactive'}")
                st.write(f"- **Created:** {created_at}")
                st.write(f"- **Last Notification:** {last_notif or 'Never'}")
            
            with col2:
                st.write("**Actions:**")
                
                if st.button("🔄 Update Subscription"):
                    st.info("Use the Subscribe tab to update your preferences")
                
                if active:
                    if st.button("⏸️ Pause Notifications"):
                        cursor.execute('UPDATE email_subscriptions SET active = 0 WHERE email = ?', (lookup_email,))
                        conn.commit()
                        st.success("Notifications paused")
                        st.rerun()
                else:
                    if st.button("▶️ Resume Notifications"):
                        cursor.execute('UPDATE email_subscriptions SET active = 1 WHERE email = ?', (lookup_email,))
                        conn.commit()
                        st.success("Notifications resumed")
                        st.rerun()
                
                if st.button("🗑️ Delete Subscription", type="secondary"):
                    cursor.execute('DELETE FROM email_subscriptions WHERE email = ?', (lookup_email,))
                    cursor.execute('DELETE FROM notification_history WHERE subscription_id = ?', (sub_id,))
                    conn.commit()
                    st.success("Subscription deleted")
                    st.rerun()
            
            # Notification history
            st.subheader("📜 Notification History")
            cursor.execute('''
                SELECT procurement_title, sent_at, email_status 
                FROM notification_history 
                WHERE subscription_id = ? 
                ORDER BY sent_at DESC 
                LIMIT 10
            ''', (sub_id,))
            
            history = cursor.fetchall()
            
            if history:
                df_history = pd.DataFrame(history, columns=['Procurement Title', 'Sent At', 'Status'])
                st.dataframe(df_history, use_container_width=True)
            else:
                st.info("No notifications sent yet")
        
        else:
            st.warning("No subscription found for this email address")
        
        conn.close()

def render_analytics():
    st.subheader("📊 Subscription Analytics")
    
    conn = sqlite3.connect('procurement.db')
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_subs = pd.read_sql_query('SELECT COUNT(*) as count FROM email_subscriptions', conn).iloc[0]['count']
        st.metric("📧 Total Subscriptions", total_subs)
    
    with col2:
        active_subs = pd.read_sql_query('SELECT COUNT(*) as count FROM email_subscriptions WHERE active = 1', conn).iloc[0]['count']
        st.metric("✅ Active Subscriptions", active_subs)
    
    with col3:
        total_notifications = pd.read_sql_query('SELECT COUNT(*) as count FROM notification_history', conn).iloc[0]['count']
        st.metric("📬 Total Notifications", total_notifications)
    
    with col4:
        unique_procurements = pd.read_sql_query('SELECT COUNT(DISTINCT procurement_id) as count FROM notification_history', conn).iloc[0]['count']
        st.metric("🏛️ Unique Procurements", unique_procurements)
    
    # Sector distribution
    st.subheader("🏢 Sector Distribution")
    
    try:
        df_subs = pd.read_sql_query('SELECT sectors FROM email_subscriptions WHERE active = 1', conn)
        
        if not df_subs.empty:
            # Parse sectors
            all_sectors = []
            for sectors_str in df_subs['sectors']:
                all_sectors.extend([s.strip() for s in sectors_str.split(',')])
            
            sector_counts = pd.Series(all_sectors).value_counts()
            
            if not sector_counts.empty:
                st.bar_chart(sector_counts)
            else:
                st.info("No sector data available")
        else:
            st.info("No active subscriptions")
    except Exception as e:
        st.error(f"Error loading sector data: {str(e)}")
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    try:
        df_recent = pd.read_sql_query('''
            SELECT DATE(sent_at) as date, COUNT(*) as notifications
            FROM notification_history 
            WHERE sent_at >= date('now', '-30 days')
            GROUP BY DATE(sent_at)
            ORDER BY date DESC
        ''', conn)
        
        if not df_recent.empty:
            st.line_chart(df_recent.set_index('date'))
        else:
            st.info("No recent activity")
    except Exception as e:
        st.error(f"Error loading activity data: {str(e)}")
    
    conn.close()

def render_test_notifications():
    st.subheader("🔔 Test Notification System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Manual Notification Check**")
        
        if st.button("🔍 Check for New Matches", type="primary"):
            with st.spinner("Checking for new procurement matches..."):
                new_matches = check_procurement_matches()
                
            if new_matches > 0:
                st.success(f"Found {new_matches} new matches and sent notifications!")
            else:
                st.info("No new matches found")
        
        st.write("**System Status**")
        
        # Check database status
        try:
            conn = sqlite3.connect('procurement.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM email_subscriptions')
            sub_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM procurement_matches')
            proc_count = cursor.fetchone()[0]
            
            conn.close()
            
            st.success(f"✅ Database connected")
            st.info(f"📊 {sub_count} subscriptions, {proc_count} procurements cached")
            
        except Exception as e:
            st.error(f"❌ Database error: {str(e)}")
    
    with col2:
        st.write("**Send Test Email**")
        
        test_email = st.text_input("Test Email Address")
        
        if st.button("📧 Send Test Email") and test_email:
            # Create sample procurement data
            sample_procurements = [
                {
                    'title': 'IT Services for Government Portal',
                    'category': 'Technology & IT',
                    'estimated_value': 150000,
                    'procurer': 'Ministry of Digital Affairs',
                    'deadline': '2025-10-15',
                    'url': 'https://riigihanked.riik.ee/rhr-web/#/procurement/123456'
                }
            ]
            
            subscription_info = {
                'sectors': 'Technology & IT',
                'keywords': 'IT, software',
                'min_value': 10000,
                'max_value': 1000000
            }
            
            success = send_email_notification(test_email, sample_procurements, subscription_info)
            
            if success:
                st.success("Test email prepared successfully!")
            else:
                st.error("Failed to prepare test email")

if __name__ == "__main__":
    main()

