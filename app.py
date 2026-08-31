import os
import streamlit as st
import importlib

# 1. Page Configuration (Must be first)
st.set_page_config(
    page_title="MedInsight AI — Clinical Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom Ultra-Premium CSS Theme
def inject_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "css", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

inject_custom_css()

# 3. Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Dashboard'
if 'selected_report_id' not in st.session_state:
    st.session_state['selected_report_id'] = None

# Lazy view loader
def get_view_module(module_name):
    return importlib.import_module(f"views.{module_name}")

def main():
    if not st.session_state['logged_in']:
        login_view = get_view_module('login_page')
        login_view.render_login_page()
        return

    # User Profile Sidebar Branding
    user = st.session_state['user']
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <div style="display: inline-block; padding: 12px; background: rgba(99, 102, 241, 0.2); border-radius: 50%; border: 1px solid rgba(99, 102, 241, 0.4); box-shadow: 0 0 25px rgba(99, 102, 241, 0.5); margin-bottom: 10px;">
                <img src="https://img.icons8.com/fluency/96/caduceus.png" width="55" style="filter: drop-shadow(0 0 8px rgba(255,255,255,0.4));"/>
            </div>
            <h2 style="margin: 0; font-size: 1.45rem; color: #ffffff !important; font-weight: 800; font-family: 'Outfit', sans-serif; letter-spacing: 0.05em; text-shadow: 0 2px 10px rgba(0,0,0,0.5);">MedInsight AI</h2>
            <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #a5b4fc !important; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">Clinical Intelligence</p>
        </div>
        <div style="background: rgba(255, 255, 255, 0.06); border-radius: 16px; padding: 16px; border: 1px solid rgba(255, 255, 255, 0.12); margin-bottom: 22px; box-shadow: 0 8px 20px rgba(0,0,0,0.3);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <p style="margin: 0; font-size: 0.75rem; color: #94a3b8 !important; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Active Profile</p>
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981;"></div>
            </div>
            <h4 style="margin: 0 0 4px 0; color: #ffffff !important; font-size: 1.15rem; font-family: 'Outfit', sans-serif; font-weight: 700; text-transform: capitalize;">{user.get('full_name', 'Patient')}</h4>
            <div style="display: flex; gap: 8px; margin-top: 10px;">
                <span style="background: rgba(16, 185, 129, 0.2); color: #34d399 !important; font-size: 0.75rem; padding: 4px 10px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3);">{user.get('age', 40)} YRS</span>
                <span style="background: rgba(59, 130, 246, 0.2); color: #60a5fa !important; font-size: 0.75rem; padding: 4px 10px; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-weight: 700; border: 1px solid rgba(59, 130, 246, 0.3);">{user.get('gender', 'Male').upper()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    pages = [
        "Dashboard",
        "Upload Report",
        "Health Score",
        "Predictions & Risks",
        "Chatbot & Assistant",
        "Report Comparison",
        "Analytics & Trends",
        "Patient History",
        "My Profile",
        "Logout"
    ]

    icons = {
        "Dashboard": "📊",
        "Upload Report": "📤",
        "Health Score": "🧬",
        "Predictions & Risks": "⚠️",
        "Chatbot & Assistant": "💬",
        "Report Comparison": "⚖️",
        "Analytics & Trends": "📈",
        "Patient History": "📁",
        "My Profile": "👤",
        "Logout": "🚪"
    }

    selection = st.sidebar.radio(
        "Navigation",
        pages,
        format_func=lambda x: f"{icons.get(x, '•')}  {x}",
        index=pages.index(st.session_state['current_page']) if st.session_state['current_page'] in pages else 0
    )

    if selection == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.session_state['current_page'] = 'Dashboard'
        st.session_state['last_analysis'] = None
        st.rerun()

    st.session_state['current_page'] = selection

    # Routing
    view_map = {
        "Dashboard": "dashboard_page",
        "Upload Report": "upload_page",
        "Health Score": "health_score_page",
        "Predictions & Risks": "prediction_page",
        "Chatbot & Assistant": "chatbot_page",
        "Report Comparison": "comparison_page",
        "Analytics & Trends": "analytics_page",
        "Patient History": "history_page",
        "My Profile": "profile_page"
    }

    if selection in view_map:
        get_view_module(view_map[selection]).render()

if __name__ == "__main__":
    main()
