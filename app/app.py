"""
AI Career & Skill Gap Analyzer - Main Navigation
Streamlit application with navigation to different career analysis modules
"""

import streamlit as st
import os
import sys

# Add src and config directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from gemini_client import get_gemini_client


def _inject_styles() -> None:
    """Inject custom CSS styles for better UI"""
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .module-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .module-card:hover {
            transform: translateY(-5px);
        }
        .feature-list {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-online {
            background-color: #28a745;
        }
        .status-offline {
            background-color: #dc3545;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def check_gemini_status() -> bool:
    """Check if Gemini API is available"""
    try:
        client = get_gemini_client()
        return client.test_connection()
    except Exception:
        return False


def main():
    """Main Streamlit application with navigation"""
    
    # Page configuration
    st.set_page_config(
        page_title="AI Career & Skill Gap Analyzer",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    _inject_styles()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 AI Career & Skill Gap Analyzer</h1>', unsafe_allow_html=True)
    
    # Status check
    gemini_status = check_gemini_status()
    status_color = "🟢" if gemini_status else "🔴"
    status_text = "Online" if gemini_status else "Offline"
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="status-indicator {'status-online' if gemini_status else 'status-offline'}"></span>
        <strong>Gemini AI Status: {status_text}</strong>
        {"" if gemini_status else "<br><small>Some features may be limited without Gemini API access</small>"}
    </div>
    """, unsafe_allow_html=True)
    
    # Main description with simplified flow
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; font-size: 1.2rem; color: #666;">
        Your comprehensive career development platform powered by AI.<br>
        <strong>Upload Resume → Get Enhanced Summary → Career Guidance</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Flow indicator
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="display: inline-flex; align-items: center; background: white; padding: 15px 30px; border-radius: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <div style="background: #667eea; color: white; padding: 8px 15px; border-radius: 20px; margin-right: 10px; font-weight: bold;">Step 1</div>
            <span style="color: #333; margin-right: 10px;">📄 Enhanced Resume Summary</span>
            <span style="color: #999; margin: 0 10px;">→</span>
            <div style="background: #28a745; color: white; padding: 8px 15px; border-radius: 20px; margin-right: 10px; font-weight: bold;">Step 2</div>
            <span style="color: #333; margin-right: 10px;">🤖 AI Career Assistant</span>
            <span style="color: #999; margin: 0 10px;">→</span>
            <div style="background: #ffc107; color: #333; padding: 8px 15px; border-radius: 20px; font-weight: bold;">Step 3</div>
            <span style="color: #333;">📊 Job Market Analysis</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Module cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="module-card">
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="background: #667eea; color: white; padding: 5px 15px; border-radius: 15px; display: inline-block; font-weight: bold; margin-bottom: 10px;">Step 1</div>
                <h2 style="margin: 0;">📄 Enhanced Resume Summary</h2>
            </div>
            <p>Upload your resume and get an AI-powered enhanced summary with personalized career insights.</p>
            <div class="feature-list">
                <strong>Start Here:</strong>
                <ul>
                    <li>📄 PDF & DOCX support</li>
                    <li>🎯 Skill extraction</li>
                    <li>✨ AI-enhanced summary</li>
                    <li>📊 ATS compatibility scoring</li>
                    <li>➡️ Auto-feed to Career Assistant</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📄 Get Enhanced Resume Summary", use_container_width=True, type="primary"):
            st.switch_page("pages/resume_analysis.py")
    
    with col2:
        st.markdown("""
        <div class="module-card">
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="background: #28a745; color: white; padding: 5px 15px; border-radius: 15px; display: inline-block; font-weight: bold; margin-bottom: 10px;">Step 2</div>
                <h2 style="margin: 0;">🤖 AI Career Assistant</h2>
            </div>
            <p>Get personalized career guidance powered by your resume analysis and AI insights.</p>
            <div class="feature-list">
                <strong>Personalized Guidance:</strong>
                <ul>
                    <li>💬 AI-powered chat coaching</li>
                    <li>🎯 Career fit testing</li>
                    <li>📚 Learning roadmap generation</li>
                    <li>🚀 Portfolio project suggestions</li>
                    <li>📈 Role recommendations</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🤖 Go to Career Assistant", use_container_width=True, type="primary"):
            st.switch_page("pages/career_assistant.py")
    
    with col3:
        st.markdown("""
        <div class="module-card">
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="background: #ffc107; color: #333; padding: 5px 15px; border-radius: 15px; display: inline-block; font-weight: bold; margin-bottom: 10px;">Step 3</div>
                <h2 style="margin: 0;">📊 Job Market Analysis</h2>
            </div>
            <p>Explore real-time market trends and opportunities based on your skills and profile.</p>
            <div class="feature-list">
                <strong>Market Insights:</strong>
                <ul>
                    <li>📈 Skill-demand analysis</li>
                    <li>💰 Salary expectations</li>
                    <li>🏢 Industry insights</li>
                    <li>🌍 Geographic opportunities</li>
                    <li>🎓 Certification recommendations</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Go to Job Market Analysis", use_container_width=True, type="primary"):
            st.switch_page("pages/job_market_analysis.py")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p><strong>🚀 AI Career & Skill Gap Analyzer</strong></p>
        <p>Powered by Google Gemini AI • Built with Streamlit</p>
        <p><small>Navigate to any module above to get started with your career development journey!</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()