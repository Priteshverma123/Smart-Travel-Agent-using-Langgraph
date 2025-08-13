import streamlit as st
import datetime
import os
from agents.agent import TravelAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="✈️ Smart Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .search-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .result-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .sidebar-info {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .email-section {
        background: #f0f8f0;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #4caf50;
        margin-top: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Header
st.markdown("""
<div class="main-header">
    <h1>✈️ Smart Travel Assistant</h1>
    <p>Your AI-powered companion for finding the best flights and hotels</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔧 Configuration")
    
    # Email settings
    st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
    st.markdown("**📧 Email Features**")
    enable_email = st.checkbox("Enable Email Functionality", value=False)
    
    if enable_email:
        recipient_email = st.text_input("📧 Recipient Email", placeholder="your-email@example.com")
        
        # Check for email configuration
        has_sendgrid = bool(os.environ.get('SENDGRID_API_KEY'))
        has_smtp = all([
            os.environ.get('SMTP_SERVER'),
            os.environ.get('SMTP_USERNAME'),
            os.environ.get('SMTP_PASSWORD')
        ])
        
        if has_sendgrid:
            st.success("✅ SendGrid configured")
        elif has_smtp:
            st.success("✅ SMTP configured")
        else:
            st.info("📁 Email will be saved as HTML file")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API Status
    st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
    st.markdown("**🔑 API Status**")
    
    apis_status = {
        "OpenAI": bool(os.environ.get('OPENAI_API_KEY')),
        "SerpAPI": bool(os.environ.get('SERPAPI_API_KEY')),
    }
    
    for api, status in apis_status.items():
        if status:
            st.success(f"✅ {api}")
        else:
            st.error(f"❌ {api} - Please add to .env file")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search History
    if st.session_state.search_history:
        st.markdown("### 📋 Recent Searches")
        for i, search in enumerate(st.session_state.search_history[-5:]):
            with st.expander(f"Search {len(st.session_state.search_history) - i}"):
                st.write(search[:100] + "..." if len(search) > 100 else search)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 Travel Search")
    
    # Quick search examples
    st.markdown("**💡 Try these example searches:**")
    
    examples = [
        "Find flights from New York to Paris from December 15-22, 2024",
        "I want to travel to Tokyo from London, 3 adults, January 5-12, 2025",
        "Find 4-star hotels in Barcelona for March 10-15, 2025, 2 adults, 1 child",
        "Round trip flights from Miami to Rome, 2 adults, February 14-21, 2025"
    ]
    
    example_cols = st.columns(2)
    for i, example in enumerate(examples):
        with example_cols[i % 2]:
            if st.button(f"📝 Example {i+1}", key=f"example_{i}", help=example):
                st.session_state.search_query = example
    
    # Search input
    search_query = st.text_area(
        "✍️ Describe your travel needs:",
        placeholder="e.g., I want to travel from New York to London from December 1-10, 2024. Find me flights and 4-star hotels.",
        height=120,
        value=st.session_state.get('search_query', '')
    )
    
    # Search parameters
    col_params1, col_params2 = st.columns(2)
    with col_params1:
        search_flights = st.checkbox("✈️ Search Flights", value=True)
        search_hotels = st.checkbox("🏨 Search Hotels", value=True)
    
    with col_params2:
        if enable_email:
            send_email_results = st.checkbox("📧 Email Results", value=False)
        else:
            send_email_results = False
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 🌟 Features")
    
    features = [
        ("🔍", "Smart Search", "AI-powered flight and hotel search"),
        ("⚡", "Real-time", "Live availability and pricing"),
        ("🌍", "Global Coverage", "Worldwide destinations"),
    ]
    
    for icon, title, desc in features:
        st.markdown(f"""
        <div class="feature-card">
            <h3>{icon} {title}</h3>
            <p style="margin: 0; color: #666;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# Search button
if st.button("🚀 Search Travel Options", type="primary", use_container_width=True):
    if not search_query.strip():
        st.error("Please enter your travel requirements")
    elif not (search_flights or search_hotels):
        st.error("Please select at least one search option (Flights or Hotels)")
    elif enable_email and send_email_results and not recipient_email:
        st.error("Please enter recipient email address")
    else:
        # Add to search history
        st.session_state.search_history.append(search_query)
        
        with st.spinner("🔍 Searching for the best travel options..."):
            try:
                # Initialize agent
                agent = TravelAgent(enable_email=enable_email)
                
                # Perform search
                result = agent.search_travel(
                    query=search_query,
                    send_email=send_email_results,
                    recipient_email=recipient_email if enable_email else None
                )
                
                st.session_state.search_results = result
                
            except Exception as e:
                st.error(f"An error occurred during search: {str(e)}")
                st.error("Please check your API keys and internet connection")

# Display results
if st.session_state.search_results:
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown("### 📋 Search Results")
    
    # Display the main response
    st.markdown(st.session_state.search_results['response'])
    
    # Email section
    if st.session_state.search_results.get('email_content'):
        st.markdown('<div class="email-section">', unsafe_allow_html=True)
        st.markdown("### 📧 Email Content")
        
        if st.session_state.search_results.get('email_sent'):
            st.success("✅ Email sent successfully!")
        else:
            st.info("📁 Email content prepared (saved as HTML file)")
        
        # Option to download email content
        if st.button("💾 Download Email HTML"):
            st.download_button(
                label="📧 Download Email HTML",
                data=st.session_state.search_results['email_content'],
                file_name=f"travel_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
        
        # Preview email content
        with st.expander("👀 Preview Email Content"):
            st.components.v1.html(st.session_state.search_results['email_content'], height=400, scrolling=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>🤖 Powered by AI | 🔒 Your data is secure | 📞 Need help? Check the sidebar for API status</p>
    <p>Built with ❤️ using Streamlit, LangChain, and OpenAI</p>
</div>
""", unsafe_allow_html=True)