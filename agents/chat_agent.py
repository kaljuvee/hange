import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, and_, or_
import feedparser

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# Import database models
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Home import Procurement, SessionLocal, ESTONIAN_COUNTIES

class ChatState(TypedDict):
    messages: List[Any]
    query_results: Optional[Dict]
    user_intent: Optional[str]
    
class HangeGPTAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.session = SessionLocal()
        self.graph = self._create_graph()
        
    def _create_graph(self):
        """Create the LangGraph workflow"""
        workflow = StateGraph(ChatState)
        
        # Add nodes
        workflow.add_node("analyze_intent", self.analyze_intent)
        workflow.add_node("query_database", self.query_database)
        workflow.add_node("query_rss_cache", self.query_rss_cache)
        workflow.add_node("generate_response", self.generate_response)
        
        # Add edges
        workflow.set_entry_point("analyze_intent")
        workflow.add_conditional_edges(
            "analyze_intent",
            self.route_query,
            {
                "database": "query_database",
                "rss": "query_rss_cache",
                "both": "query_database"
            }
        )
        workflow.add_edge("query_database", "generate_response")
        workflow.add_edge("query_rss_cache", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def analyze_intent(self, state: ChatState) -> ChatState:
        """Analyze user intent and determine query strategy"""
        user_message = state["messages"][-1].content
        
        intent_prompt = f"""
        Analyze this user query about Estonian procurement data and determine the intent:
        
        Query: "{user_message}"
        
        Determine:
        1. What type of data they want (categories, locations, values, dates, etc.)
        2. Any specific filters (city, county, category, value range, time period)
        3. Whether they want recent data (RSS) or historical analysis (database)
        
        Return a JSON object with:
        {{
            "intent": "search|analyze|compare|summarize",
            "data_source": "database|rss|both",
            "filters": {{
                "category": "category_name or null",
                "county": "county_name or null", 
                "city": "city_name or null",
                "value_min": number or null,
                "value_max": number or null,
                "days_back": number or null
            }},
            "output_type": "list|summary|chart|table"
        }}
        """
        
        response = self.llm.invoke([SystemMessage(content=intent_prompt)])
        
        try:
            intent_data = json.loads(response.content)
            state["user_intent"] = intent_data
        except:
            # Fallback intent
            state["user_intent"] = {
                "intent": "search",
                "data_source": "both",
                "filters": {},
                "output_type": "list"
            }
        
        return state
    
    def route_query(self, state: ChatState) -> str:
        """Route query based on analyzed intent"""
        intent = state.get("user_intent", {})
        data_source = intent.get("data_source", "both")
        
        if data_source == "rss":
            return "rss"
        elif data_source == "database":
            return "database"
        else:
            return "both"
    
    def query_database(self, state: ChatState) -> ChatState:
        """Query the SQLite database based on filters"""
        intent = state.get("user_intent", {})
        filters = intent.get("filters", {})
        
        try:
            query = self.session.query(Procurement)
            
            # Apply filters
            if filters.get("category"):
                query = query.filter(Procurement.category.ilike(f"%{filters['category']}%"))
            
            if filters.get("county"):
                query = query.filter(Procurement.county.ilike(f"%{filters['county']}%"))
            
            if filters.get("city"):
                query = query.filter(Procurement.procurer.ilike(f"%{filters['city']}%"))
            
            if filters.get("value_min"):
                query = query.filter(Procurement.estimated_value >= filters['value_min'])
            
            if filters.get("value_max"):
                query = query.filter(Procurement.estimated_value <= filters['value_max'])
            
            if filters.get("days_back"):
                cutoff_date = datetime.now() - timedelta(days=filters['days_back'])
                query = query.filter(Procurement.published >= cutoff_date)
            
            # Execute query
            results = query.limit(50).all()
            
            # Convert to dict format
            db_results = []
            for r in results:
                db_results.append({
                    'id': r.id,
                    'title': r.title,
                    'clean_description': r.clean_description,
                    'category': r.category,
                    'county': r.county,
                    'estimated_value': r.estimated_value,
                    'procurer': r.procurer,
                    'published': r.published.isoformat() if r.published else None,
                    'link': r.link
                })
            
            state["query_results"] = {
                "database": db_results,
                "count": len(db_results)
            }
            
        except Exception as e:
            state["query_results"] = {
                "database": [],
                "error": str(e),
                "count": 0
            }
        
        return state
    
    def query_rss_cache(self, state: ChatState) -> ChatState:
        """Query the RSS feed cache for recent data"""
        intent = state.get("user_intent", {})
        filters = intent.get("filters", {})
        
        try:
            # Load RSS feed
            feed = feedparser.parse('https://riigihanked.riik.ee/rhr/api/public/v1/rss')
            
            rss_results = []
            for entry in feed.entries[:50]:  # Limit to recent 50
                # Apply basic filters
                include = True
                
                if filters.get("category"):
                    if filters["category"].lower() not in entry.title.lower() and \
                       filters["category"].lower() not in entry.description.lower():
                        include = False
                
                if filters.get("city"):
                    if filters["city"].lower() not in entry.get('author', '').lower():
                        include = False
                
                if include:
                    rss_results.append({
                        'title': entry.title,
                        'description': entry.description[:300] + "..." if len(entry.description) > 300 else entry.description,
                        'link': entry.link,
                        'published': entry.published,
                        'procurer': entry.get('author', 'Unknown')
                    })
            
            if "query_results" not in state:
                state["query_results"] = {}
            
            state["query_results"]["rss"] = rss_results
            state["query_results"]["rss_count"] = len(rss_results)
            
        except Exception as e:
            if "query_results" not in state:
                state["query_results"] = {}
            state["query_results"]["rss"] = []
            state["query_results"]["rss_error"] = str(e)
            state["query_results"]["rss_count"] = 0
        
        return state
    
    def generate_response(self, state: ChatState) -> ChatState:
        """Generate natural language response based on query results"""
        user_message = state["messages"][-1].content
        query_results = state.get("query_results", {})
        intent = state.get("user_intent", {})
        
        # Prepare context for response generation
        context = {
            "user_query": user_message,
            "intent": intent,
            "results": query_results
        }
        
        response_prompt = f"""
        You are HangeGPT, an AI assistant specialized in Estonian procurement data. 
        
        User asked: "{user_message}"
        
        Query results:
        {json.dumps(query_results, indent=2, default=str)}
        
        Generate a helpful, conversational response that:
        1. Directly answers the user's question
        2. Provides specific details from the results
        3. Includes relevant procurement information (titles, values, counties, etc.)
        4. Offers additional insights or suggestions
        5. Uses a friendly, professional tone
        
        If no results found, explain why and suggest alternative searches.
        Format the response in a clear, readable way with bullet points or numbered lists when appropriate.
        """
        
        response = self.llm.invoke([SystemMessage(content=response_prompt)])
        
        # Add AI response to messages
        state["messages"].append(AIMessage(content=response.content))
        
        return state
    
    def chat(self, user_message: str, chat_history: List = None) -> str:
        """Main chat interface"""
        if chat_history is None:
            chat_history = []
        
        # Add user message to history
        messages = chat_history + [HumanMessage(content=user_message)]
        
        # Create initial state
        initial_state = {
            "messages": messages,
            "query_results": None,
            "user_intent": None
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Return the AI response
        return final_state["messages"][-1].content
    
    def get_suggestions(self) -> List[str]:
        """Get sample questions users can ask"""
        return [
            "Show me all construction procurements in Tallinn",
            "What are the highest value procurements this month?",
            "Find IT procurements in Harjumaa",
            "Show me healthcare procurements over €100,000",
            "What procurements were published today?",
            "Compare construction vs IT procurement values",
            "Show me all procurements in Tartu",
            "Find energy and environment procurements",
            "What are the most common procurement categories?",
            "Show me recent procurements from universities"
        ]
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()

# Utility functions for the chat interface
def create_chat_agent():
    """Factory function to create a new chat agent"""
    return HangeGPTAgent()

def format_procurement_result(procurement: Dict) -> str:
    """Format a single procurement result for display"""
    title = procurement.get('title', 'Unknown Title')
    category = procurement.get('category', 'Unknown')
    county = procurement.get('county', 'Unknown')
    value = procurement.get('estimated_value')
    
    result = f"**{title}**\n"
    result += f"📂 Category: {category}\n"
    result += f"🗺️ County: {county}\n"
    
    if value:
        result += f"💰 Value: €{value:,.2f}\n"
    
    if procurement.get('link'):
        result += f"🔗 [View Details]({procurement['link']})\n"
    
    return result

def get_county_suggestions() -> List[str]:
    """Get list of Estonian counties for suggestions"""
    return list(ESTONIAN_COUNTIES.keys())

def get_category_suggestions() -> List[str]:
    """Get list of procurement categories for suggestions"""
    return [
        "Technology & IT",
        "Healthcare & Medical", 
        "Construction & Infrastructure",
        "Professional Services",
        "Education & Training",
        "Transportation",
        "Energy & Environment",
        "Security & Defense",
        "Food & Catering",
        "Office & Supplies",
        "Maintenance & Cleaning"
    ]

