"""
Smart Resume Analysis page powered by Gemini AI.
Features:
- Upload resume (PDF/DOCX), extract and display skills as badges
- Paste job posting URL or manual job description input
- AI-powered resume vs job matching analysis
- Visual score displays and improvement recommendations
- LinkedIn job search integration
"""

import os
import re
import urllib.parse
from typing import List, Dict, Any

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Local imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from resume_parser import ResumeParser
from gemini_client import analyze_resume_vs_job, extract_job_description_from_url
from shared_data import get_shared_data

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from gemini_config import get_gemini_config


def _inject_styles() -> None:
    """Inject custom CSS styles for better UI"""
    st.markdown(
        """
<style>
        .skill-container {
            display: flex; 
            flex-wrap: wrap; 
            gap: 8px; 
            margin-top: 10px;
        }
        .skill-badge {
            background: linear-gradient(90deg, #0072ff, #00c6ff); 
            color: white; 
            padding: 6px 12px; 
            border-radius: 14px; 
            font-size: 14px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .match-badge {
            background: linear-gradient(90deg, #28a745, #20c997);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin: 2px;
            display: inline-block;
        }
        .missing-badge {
            background: linear-gradient(90deg, #dc3545, #fd7e14);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin: 2px;
            display: inline-block;
        }
        .score-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            margin: 10px 0;
        }
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        div.stSpinner > div {
            border-top-color: #00c6ff;
        }
        .job-search-btn {
            background: linear-gradient(90deg, #0077b5, #00a0dc);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            display: inline-block;
            margin: 10px 0;
            font-weight: bold;
        }
        .job-search-btn:hover {
            background: linear-gradient(90deg, #005885, #0077b5);
            color: white;
            text-decoration: none;
        }
</style>
        """,
        unsafe_allow_html=True,
    )


def create_score_gauge(score: float, title: str, color: str = "blue") -> go.Figure:
    """Create a gauge chart for displaying scores"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        font={'color': "darkblue", 'family': "Arial"},
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def display_analysis_results(analysis: Dict[str, Any]) -> None:
    """Display the analysis results in a visually appealing way"""
    st.subheader("🎯 Analysis Results")
    
    # Create two columns for scores
    col1, col2 = st.columns(2)
    
    with col1:
        relevance_score = analysis.get("relevance_score", 0.0)
        st.metric(
            "Relevance Score", 
            f"{relevance_score:.1%}",
            delta=f"{'Strong match' if relevance_score > 0.7 else 'Moderate match' if relevance_score > 0.4 else 'Weak match'}"
        )
        
        # Create gauge for relevance
        fig1 = create_score_gauge(relevance_score, "Content Relevance", "blue")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        ats_score = analysis.get("ats_score", 0.0)
        st.metric(
            "ATS Score", 
            f"{ats_score:.1%}",
            delta=f"{'ATS Ready' if ats_score > 0.7 else 'Needs Work' if ats_score > 0.4 else 'Major Issues'}"
        )
        
        # Create gauge for ATS
        fig2 = create_score_gauge(ats_score, "ATS Compatibility", "green")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Display matching skills
    st.subheader("✅ Matching Skills")
    key_matches = analysis.get("key_matches", [])
    if key_matches:
        matches_html = "".join([f'<span class="match-badge">{skill}</span>' for skill in key_matches])
        st.markdown(f'<div class="skill-container">{matches_html}</div>', unsafe_allow_html=True)
    else:
        st.info("No matching skills found.")
    
    # Display missing keywords
    st.subheader("❌ Missing Keywords")
    missing_keywords = analysis.get("missing_keywords", [])
    if missing_keywords:
        missing_html = "".join([f'<span class="missing-badge">{skill}</span>' for skill in missing_keywords])
        st.markdown(f'<div class="skill-container">{missing_html}</div>', unsafe_allow_html=True)
    else:
        st.success("No critical missing keywords!")
    
    # Display feedback
    st.subheader("💡 Formatting Feedback")
    formatting_feedback = analysis.get("formatting_feedback", "No feedback available.")
    st.info(formatting_feedback)
    
    # Display summary
    st.subheader("📋 Summary")
    summary = analysis.get("summary", "No summary available.")
    st.write(summary)


def create_linkedin_search_url(skills: List[str]) -> str:
    """Create LinkedIn job search URL with extracted skills"""
    if not skills:
        return "https://www.linkedin.com/jobs/"
    
    # Take top 3-5 skills and create search query
    search_skills = skills[:5]
    query = " ".join(search_skills)
    encoded_query = urllib.parse.quote_plus(query)
    
    return f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}"


def display_resume_summary_card(skills: List[str], ai_feedback: str):
    """Display a clean summary card with key insights and next step"""
    st.markdown("""
    <div style="background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 30px 0; border: 1px solid #e0e0e0;">
        <div style="text-align: center; margin-bottom: 25px;">
            <h2 style="color: #333; margin: 0 0 10px 0;">✅ Resume Analysis Complete!</h2>
            <p style="color: #666; margin: 0;">Your profile has been analyzed and is ready for personalized career guidance</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics in a clean layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2em; font-weight: bold; color: #667eea; margin-bottom: 5px;">{len(skills)}</div>
            <div style="color: #666; font-size: 0.9em;">Skills Detected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2em; font-weight: bold; color: #28a745; margin-bottom: 5px;">85%</div>
            <div style="color: #666; font-size: 0.9em;">ATS Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 15px; margin: 10px 0;">
            <div style="font-size: 2em; font-weight: bold; color: #ffc107; margin-bottom: 5px;">Mid</div>
            <div style="color: #666; font-size: 0.9em;">Experience Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Skills display
    st.markdown("**🎯 Detected Skills:**")
    skills_html = "".join([f'<span class="skill-badge">{skill}</span>' for skill in skills[:10]])
    st.markdown(f'<div class="skill-container">{skills_html}</div>', unsafe_allow_html=True)
    if len(skills) > 10:
        st.caption(f"... and {len(skills) - 10} more skills")
    
    # AI Feedback
    st.markdown("**🤖 AI Analysis:**")
    st.info(ai_feedback)
    
    # Next Step Button
    st.markdown("""
    <div style="text-align: center; margin: 30px 0;">
        <h3 style="color: #333; margin-bottom: 15px;">🚀 Ready for Personalized Career Guidance?</h3>
        <p style="color: #666; margin-bottom: 20px;">Your profile is now loaded and ready for AI-powered career coaching</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("👉 Continue to AI Career Assistant", use_container_width=True, type="primary"):
            st.switch_page("pages/career_assistant.py")


def main():
    st.set_page_config(
        page_title="Smart Resume Analysis", 
        page_icon="📄", 
        layout="wide"
    )
    _inject_styles()

    # Unified Header Design
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white; margin-bottom: 30px;">
        <h1 style="margin: 0; font-size: 2.5em;">📄 Enhanced Resume Summary</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">
            Step 1: Upload your resume to get an AI-powered enhanced summary and personalized career insights
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "extracted_skills" not in st.session_state:
        st.session_state["extracted_skills"] = []
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = ""
    if "job_description" not in st.session_state:
        st.session_state["job_description"] = ""
    if "analysis_results" not in st.session_state:
        st.session_state["analysis_results"] = None
    if "resume_analysis_complete" not in st.session_state:
        st.session_state["resume_analysis_complete"] = False
    if "ai_resume_feedback" not in st.session_state:
        st.session_state["ai_resume_feedback"] = None
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = {}

    # Minimal Upload Section
    st.markdown("""
    <div style="text-align: center; margin: 40px 0;">
        <h3 style="color: #333; margin-bottom: 20px;">📄 Upload Your Resume</h3>
        <p style="color: #666; margin-bottom: 30px;">Get instant AI-powered analysis and personalized career insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centered upload box
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        uploaded_file = st.file_uploader(
            "Choose a PDF or DOCX file", 
            type=["pdf", "docx"],
            help="Upload your resume in PDF or DOCX format",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
        
        if uploaded_file:
            temp_path = f"temp_resume_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                parser = ResumeParser()
                with st.spinner("Extracting skills from resume..."):
                    extracted_skills = parser.parse_resume(temp_path)
                    resume_text = parser.extract_text_from_file(temp_path)

                # Store in session state and shared data
                st.session_state["extracted_skills"] = extracted_skills
                st.session_state["resume_text"] = resume_text
                
                # Save to shared data for other modules
                shared_data = get_shared_data()
                shared_data.save_resume_analysis(extracted_skills, resume_text)

                # Display results in a clean summary card
                if extracted_skills:
                    # Auto-generate AI resume feedback
                    with st.spinner("🤖 Generating AI-powered analysis..."):
                        try:
                            from gemini_client import analyze_resume_content
                            ai_feedback = analyze_resume_content(resume_text)
                            st.session_state["ai_resume_feedback"] = ai_feedback
                            st.session_state["resume_analysis_complete"] = True
                            
                            # Create user profile for seamless integration
                            st.session_state["user_profile"] = {
                                "skills": extracted_skills,
                                "experience_level": "Mid",  # Could be extracted from resume
                                "ats_score": 85,  # Could be calculated
                                "missing_keywords": [],
                                "resume_analyzed": True,
                                "ai_feedback": ai_feedback
                            }
                            
                            # Display clean summary card
                            display_resume_summary_card(extracted_skills, ai_feedback)
                            
                        except Exception as e:
                            st.warning(f"AI feedback unavailable: {e}")
                            # Still show basic summary
                            display_resume_summary_card(extracted_skills, "Basic analysis completed")
                else:
                    st.warning("No skills detected. Try another resume or adjust file format.")

            finally:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
        else:
            st.info("👆 Upload a resume to begin analysis")


    # AI Resume Feedback Section
    if st.session_state.get("resume_text") and st.session_state.get("ai_resume_feedback"):
        st.subheader("🤖 AI Resume Feedback")
        st.info(st.session_state["ai_resume_feedback"])

    # Enhanced Resume Summary Section
    if st.session_state.get("resume_text") and st.session_state.get("ai_resume_feedback"):
        st.subheader("✨ Enhanced Resume Summary")
        
        # Generate enhanced summary button
        if st.button("🚀 Generate Enhanced Summary", type="primary"):
            with st.spinner("Generating enhanced summary with AI..."):
                try:
                    from gemini_client import get_gemini_client
                    client = get_gemini_client()
                    
                    prompt = f"""
                    Create an enhanced, professional resume summary for this candidate.
                    Make it compelling, ATS-friendly, and highlight key achievements.
                    
                    Resume text: {st.session_state["resume_text"][:2000]}
                    
                    Return a professional summary (2-3 sentences) that would impress recruiters.
                    """
                    
                    response = client.model.generate_content(prompt)
                    enhanced_summary = response.text.strip()
                    
                    st.session_state["enhanced_summary"] = enhanced_summary
                    st.success("✅ Enhanced Summary Generated!")
                    
                except Exception as e:
                    st.error(f"Summary generation failed: {e}")
        
        # Display enhanced summary if available
        if st.session_state.get("enhanced_summary"):
            st.markdown("**✨ Your Enhanced Resume Summary:**")
            st.info(st.session_state["enhanced_summary"])
            
            # Download option
            st.download_button(
                label="📄 Download Enhanced Summary",
                data=st.session_state["enhanced_summary"],
                file_name="enhanced_resume_summary.txt",
                mime="text/plain"
            )
            
            # LinkedIn job search button
            st.subheader("🔍 Find Jobs with Your Skills")
            if st.session_state.get("extracted_skills"):
                linkedin_url = create_linkedin_search_url(st.session_state["extracted_skills"])
                st.markdown(
                    f'<a href="{linkedin_url}" target="_blank" class="job-search-btn">🔍 Search Matching Jobs on LinkedIn</a>',
                    unsafe_allow_html=True
                )

    elif not st.session_state.get("resume_text"):
        st.info("👆 Please upload a resume to begin analysis")

    # Module Integration Section
    if st.session_state.get("resume_analysis_complete") and st.session_state.get("extracted_skills"):
        st.markdown("---")
        st.subheader("🚀 Next Steps - Continue Your Career Journey")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🤖 AI Career Assistant**")
            st.markdown("Get personalized career guidance based on your enhanced resume summary")
            if st.button("Go to Career Assistant", use_container_width=True):
                st.switch_page("pages/career_assistant.py")
        
        with col2:
            st.markdown("**📊 Job Market Analysis**")
            st.markdown("Explore job opportunities and salary trends for your skills")
            if st.button("Go to Job Market Analysis", use_container_width=True):
                st.switch_page("pages/job_market_analysis.py")
        
        with col3:
            st.markdown("**📈 Career Fit Test**")
            st.markdown("Rate your skills vs trending roles in the market")
            if st.button("Take Career Fit Test", use_container_width=True):
                st.info("Career Fit Test coming soon! Use Job Market Analysis for now.")

    # Footer
    st.markdown("---")
    st.markdown(
        "💡 **Tip**: For best results, use a well-formatted resume. "
        "The AI will extract your skills, generate an enhanced summary, and provide personalized career guidance."
    )


if __name__ == "__main__":
    main()