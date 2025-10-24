"""
AI Career Assistant page with conversational interface.
Features:
- Interactive chatbot for career guidance
- Context-aware responses based on user skills
- Role recommendations and learning paths
- Interview preparation and portfolio suggestions
"""

import os
import sys
from typing import List, Dict, Any
from datetime import datetime

import streamlit as st

# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from gemini_client import get_career_advice
from shared_data import get_shared_data, sync_resume_skills_to_career_assistant, get_career_fit_score

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from gemini_config import get_gemini_config


def _inject_styles() -> None:
    """Inject custom CSS styles for better UI"""
    st.markdown(
        """
        <style>
        /* Main container styling */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header styling */
        .header-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        /* Chat container */
        .chat-container {
            background: white;
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            border: 1px solid #e0e0e0;
        }
        
        /* Message styling */
        .user-message {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 20px;
            border-radius: 20px 20px 5px 20px;
            margin: 10px 0;
            max-width: 85%;
            margin-left: auto;
            box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
        }
        
        .assistant-message {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 15px 20px;
            border-radius: 20px 20px 20px 5px;
            margin: 10px 0;
            max-width: 85%;
            box-shadow: 0 3px 10px rgba(40, 167, 69, 0.3);
        }
        
        /* Profile section */
        .profile-section {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            border: 1px solid #dee2e6;
        }
        
        /* Quick actions grid */
        .quick-actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .quick-action-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .quick-action-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .quick-action-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .quick-action-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .quick-action-desc {
            color: #666;
            font-size: 0.9em;
        }
        
        /* Skill badges */
        .skill-badge {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px;
            display: inline-block;
            font-size: 0.9em;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        /* Metrics styling */
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            margin: 10px 0;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9em;
        }
        
        /* Sidebar styling */
        .sidebar-content {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 20px;
            border-radius: 15px;
            margin: 10px 0;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* Input styling */
        .stTextArea > div > div > textarea {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }
        
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }
        
        /* Chat input styling */
        .stChatInput > div > div > div > div {
            border-radius: 25px;
            border: 2px solid #e0e0e0;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5a6fd8, #6a4190);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state():
    """Initialize session state for chat"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "user_skills" not in st.session_state:
        st.session_state.user_skills = []
    
    if "experience_level" not in st.session_state:
        st.session_state.experience_level = "Mid"
    
    if "career_goals" not in st.session_state:
        st.session_state.career_goals = "Career advancement"


def load_skills_from_resume():
    """Load skills from resume analysis if available"""
    shared_data = get_shared_data()
    return shared_data.get_resume_skills()


def display_chat_interface():
    """Display the chat interface"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="color: #333; margin: 0;">💬 Chat with Your AI Career Coach</h3>
        <p style="color: #666; margin: 5px 0 0 0; font-size: 0.9em;">Ask questions and get personalized career guidance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display chat messages with custom styling
    if st.session_state.messages:
        for message_data in st.session_state.messages:
            if message_data["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong><br>
                    {message_data["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 Career Coach:</strong><br>
                    {message_data["content"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        # Personalized welcome based on resume data
        if has_resume_data:
            top_skills = user_profile.get("skills", [])[:3]
            skills_text = ", ".join(top_skills) if top_skills else "your skills"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 40px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 15px; margin: 20px 0; border: 1px solid #dee2e6;">
                <h4 style="color: #333; margin: 0 0 10px 0;">👋 Welcome back!</h4>
                <p style="color: #666; margin: 0 0 15px 0;">I see you have experience with <strong>{skills_text}</strong>.</p>
                <p style="color: #666; margin: 0; font-size: 0.9em;">Would you like me to suggest top AI career paths or learning plans based on your profile?</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Personalized quick suggestions
            st.markdown("**💡 Suggested Questions for You:**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎯 What roles fit my skills?", use_container_width=True, key="suggested_roles"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": f"Based on my skills ({skills_text}), what roles would be good for me?"
                    })
                    st.rerun()
            
            with col2:
                if st.button("📈 How can I advance my career?", use_container_width=True, key="suggested_advancement"):
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": "How can I advance my career with my current skill set?"
                    })
                    st.rerun()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 40px; background: #f8f9fa; border-radius: 15px; margin: 20px 0;">
                <h4 style="color: #666; margin: 0 0 10px 0;">👋 Welcome to Your AI Career Coach!</h4>
                <p style="color: #999; margin: 0;">Start by asking a question or using one of the quick actions below.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input with custom styling
    if prompt := st.chat_input("Ask me anything about your career...", key="chat_input"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong><br>
            {prompt}
        </div>
        """, unsafe_allow_html=True)
        
        # Get AI response
        with st.spinner("🤖 Your AI career coach is thinking..."):
            try:
                response = get_career_advice(
                    user_skills=st.session_state.user_skills,
                    user_query=prompt,
                    experience_level=st.session_state.experience_level,
                    career_goals=st.session_state.career_goals
                )
                
                # Display assistant response
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 Career Coach:</strong><br>
                    {response}
                </div>
                """, unsafe_allow_html=True)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"I'm sorry, I'm having trouble responding right now. Please try again later. Error: {e}"
                st.markdown(f"""
                <div class="assistant-message" style="background: linear-gradient(135deg, #dc3545, #c82333);">
                    <strong>🤖 Career Coach:</strong><br>
                    {error_msg}
                </div>
                """, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


def display_quick_actions():
    """Display quick action buttons for common questions"""
    st.markdown("""
    <div style="text-align: center; margin: 30px 0;">
        <h2 style="color: #333; margin-bottom: 20px;">🚀 Quick Actions</h2>
        <p style="color: #666; margin-bottom: 30px;">Choose a topic to get started with your AI career coach</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions Grid
    st.markdown('<div class="quick-actions-grid">', unsafe_allow_html=True)
    
    # Row 1: Basic Career Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Role Recommendations", use_container_width=True, key="role_rec"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "What roles would be good for someone with my skills?"
            })
            st.rerun()
    
    with col2:
        if st.button("📚 Learning Path", use_container_width=True, key="learning_path"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "What should I learn next to advance my career?"
            })
            st.rerun()
    
    with col3:
        if st.button("💼 Interview Prep", use_container_width=True, key="interview_prep"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "How should I prepare for technical interviews?"
            })
            st.rerun()
    
    # Row 2: Advanced Career Actions
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🚀 Portfolio Ideas", use_container_width=True, key="portfolio_ideas"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "What projects should I build for my portfolio?"
            })
            st.rerun()
    
    with col5:
        if st.button("💰 Salary Negotiation", use_container_width=True, key="salary_negotiation"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "How should I approach salary negotiations?"
            })
            st.rerun()
    
    with col6:
        if st.button("🗺️ Career Roadmap", use_container_width=True, key="career_roadmap"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Create a career roadmap for me"
            })
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI-Powered Features Section
    st.markdown("""
    <div style="text-align: center; margin: 40px 0 20px 0;">
        <h3 style="color: #333; margin-bottom: 20px;">🧠 AI-Powered Features</h3>
        <p style="color: #666; margin-bottom: 30px;">Advanced AI tools for career development</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Features Grid
    st.markdown('<div class="quick-actions-grid">', unsafe_allow_html=True)
    
    col7, col8, col9 = st.columns(3)
    
    with col7:
        if st.button("🧠 Career Fit Test", use_container_width=True, key="career_fit_test"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Rate my skills against trending roles and give me a career fit score"
            })
            st.rerun()
    
    with col8:
        if st.button("🧭 Learning Roadmap", use_container_width=True, key="learning_roadmap"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Generate a detailed learning roadmap with courses and resources"
            })
            st.rerun()
    
    with col9:
        if st.button("📑 Portfolio Generator", use_container_width=True, key="portfolio_generator"):
            st.session_state.messages.append({
                "role": "user", 
                "content": "Suggest specific GitHub project ideas based on my chosen role"
            })
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_user_profile():
    """Display and allow editing of user profile"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 style="color: #333; margin: 0;">👤 Your Profile</h3>
        <p style="color: #666; margin: 5px 0 0 0; font-size: 0.9em;">Manage your skills and career information</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Skills section
    st.markdown("**🎯 Your Skills:**")
    skills_input = st.text_area(
        "Enter your skills (comma-separated)",
        value=", ".join(st.session_state.user_skills),
        height=80,
        help="List your technical and soft skills",
        key="skills_input"
    )
    
    if skills_input:
        st.session_state.user_skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
    
    # Display current skills as badges
    if st.session_state.user_skills:
        st.markdown("**Current Skills:**")
        skills_html = "".join([f'<span class="skill-badge">{skill}</span>' for skill in st.session_state.user_skills[:10]])
        st.markdown(f'<div style="margin: 10px 0;">{skills_html}</div>', unsafe_allow_html=True)
        if len(st.session_state.user_skills) > 10:
            st.caption(f"... and {len(st.session_state.user_skills) - 10} more skills")
    
    # Experience level
    st.markdown("**📊 Experience Level:**")
    st.session_state.experience_level = st.selectbox(
        "Select your experience level",
        ["Entry", "Mid", "Senior", "Lead"],
        index=["Entry", "Mid", "Senior", "Lead"].index(st.session_state.experience_level),
        key="exp_level"
    )
    
    # Career goals
    st.markdown("**🎯 Career Goals:**")
    st.session_state.career_goals = st.text_area(
        "Describe your career aspirations",
        value=st.session_state.career_goals,
        height=80,
        help="Describe your career aspirations and goals",
        key="career_goals"
    )
    
    # Action buttons
    st.markdown("**⚡ Quick Actions:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Load skills from resume button
        if st.button("📄 Load from Resume", use_container_width=True, key="load_resume"):
            loaded_skills = load_skills_from_resume()
            if loaded_skills:
                st.session_state.user_skills = loaded_skills
                st.success(f"✅ Loaded {len(loaded_skills)} skills!")
                sync_resume_skills_to_career_assistant()
                st.rerun()
            else:
                st.info("No resume analysis found. Please analyze your resume first.")
    
    with col2:
        # Career Fit Test
        if st.button("🧠 Career Fit Test", use_container_width=True, key="fit_test"):
            if st.session_state.user_skills:
                fit_data = get_career_fit_score(st.session_state.user_skills)
                
                st.markdown("### 🎯 Your Career Fit Results")
                
                # Metrics in a nice layout
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{fit_data['score']:.0f}/100</div>
                        <div class="metric-label">Career Fit Score</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{fit_data['level']}</div>
                        <div class="metric-label">Skill Level</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{fit_data['matched_skills']}/{fit_data['total_high_demand']}</div>
                        <div class="metric-label">High-Demand Skills</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### 💡 Recommendations")
                for i, rec in enumerate(fit_data['recommendations'], 1):
                    st.markdown(f"**{i}.** {rec}")
            else:
                st.warning("Please add your skills first to take the career fit test.")


def display_conversation_history():
    """Display conversation history with export option"""
    if st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0 15px 0;">
            <h4 style="color: #333; margin: 0;">📝 Conversation History</h4>
            <p style="color: #666; margin: 5px 0 0 0; font-size: 0.9em;">Manage your chat history</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show message count
        message_count = len(st.session_state.messages)
        st.markdown(f"**Messages:** {message_count}")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear History", use_container_width=True, key="clear_history"):
                st.session_state.messages = []
                st.success("Chat history cleared!")
                st.rerun()
        
        with col2:
            if st.button("💾 Export Chat", use_container_width=True, key="export_chat"):
                # Create exportable format
                chat_export = f"Career Assistant Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                chat_export += "=" * 50 + "\n\n"
                
                for msg in st.session_state.messages:
                    role = "You" if msg["role"] == "user" else "Career Coach"
                    chat_export += f"{role}: {msg['content']}\n\n"
                
                st.download_button(
                    label="📥 Download Chat",
                    data=chat_export,
                    file_name=f"career_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    else:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <h4 style="color: #666; margin: 0;">📝 No Conversation Yet</h4>
            <p style="color: #999; margin: 5px 0 0 0; font-size: 0.9em;">Start chatting to see your history here</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="AI Career Assistant", 
        page_icon="🤖", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    _inject_styles()

    # Check for resume profile data
    user_profile = st.session_state.get("user_profile", {})
    has_resume_data = user_profile.get("resume_analyzed", False)
    
    # Dynamic header based on resume data
    if has_resume_data:
        skills_count = len(user_profile.get("skills", []))
        st.markdown(f"""
        <div class="header-section">
            <h1 style="margin: 0; font-size: 2.5em;">🤖 AI Career Assistant</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">
                Step 2: Your personal career coach powered by Gemini AI
            </p>
            <p style="margin: 5px 0 0 0; opacity: 0.8;">
                👋 Welcome! I've loaded your profile with {skills_count} detected skills from your enhanced resume summary.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-load skills from resume
        if user_profile.get("skills"):
            st.session_state.user_skills = user_profile["skills"]
            st.session_state.experience_level = user_profile.get("experience_level", "Mid")
            st.session_state.career_goals = "Career advancement based on resume analysis"
    else:
        st.markdown("""
        <div class="header-section">
            <h1 style="margin: 0; font-size: 2.5em;">🤖 AI Career Assistant</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">
                Your personal career coach powered by Gemini AI
            </p>
            <p style="margin: 5px 0 0 0; opacity: 0.8;">
                Get personalized advice, role recommendations, and career guidance!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show info about resume analysis
        st.info("💡 **Tip**: Upload your resume in the Enhanced Resume Summary module first for personalized career guidance based on your actual skills and experience!")

    # Initialize session state
    initialize_session_state()

    # Main layout with improved structure
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat interface in a styled container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        display_chat_interface()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick actions with new grid layout
        if not st.session_state.messages:
            display_quick_actions()
    
    with col2:
        # Sidebar content
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # User profile
        display_user_profile()
        
        # Conversation history
        display_conversation_history()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer with tips and navigation
    st.markdown("---")
    
    if has_resume_data:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 15px; margin-top: 20px;">
            <h4 style="color: #333; margin-bottom: 10px;">💡 Pro Tips</h4>
            <p style="color: #666; margin: 0 0 15px 0;">
                Ask specific questions like <strong>"What skills should I learn for data science?"</strong> 
                or <strong>"How do I transition from software development to machine learning?"</strong> for the best advice!
            </p>
            <p style="color: #999; margin: 0; font-size: 0.9em;">
                Your resume analysis is loaded and ready for personalized guidance
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 15px; margin-top: 20px;">
            <h4 style="color: #333; margin-bottom: 10px;">💡 Pro Tips</h4>
            <p style="color: #666; margin: 0 0 15px 0;">
                Ask specific questions like <strong>"What skills should I learn for data science?"</strong> 
                or <strong>"How do I transition from software development to machine learning?"</strong> for the best advice!
            </p>
            <p style="color: #999; margin: 0; font-size: 0.9em;">
                For personalized guidance, start with the Enhanced Resume Summary module first
            </p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
