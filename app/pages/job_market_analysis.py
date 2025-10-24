"""
Enhanced Job Market Analysis page powered by real CSV datasets and Gemini AI.
Features:
- Real-time market insights from 30,000+ job records
- Industry trends and salary analysis
- Skills demand and growth outlook
- Certification recommendations
- Geographic opportunities
- Interactive visualizations
"""

import os
import sys
from typing import List, Dict, Any

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from gemini_client import analyze_job_market
from job_market_analyzer import JobMarketAnalyzer

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
from gemini_config import get_gemini_config


def _inject_styles() -> None:
    """Inject custom CSS styles for better UI"""
    st.markdown(
        """
        <style>
        .market-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .insight-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        .skill-badge {
            background: linear-gradient(90deg, #28a745, #20c997);
            color: white;
            padding: 6px 12px;
            border-radius: 14px;
            font-size: 14px;
            margin: 4px;
            display: inline-block;
        }
        .industry-badge {
            background: linear-gradient(90deg, #0072ff, #00c6ff);
            color: white;
            padding: 6px 12px;
            border-radius: 14px;
            font-size: 14px;
            margin: 4px;
            display: inline-block;
        }
        .trend-badge {
            background: linear-gradient(90deg, #ff6b6b, #ffa500);
            color: white;
            padding: 6px 12px;
            border-radius: 14px;
            font-size: 14px;
            margin: 4px;
            display: inline-block;
        }
        .salary-highlight {
            background: linear-gradient(90deg, #28a745, #20c997);
            color: white;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }
        .growth-positive {
            color: #28a745;
            font-weight: bold;
        }
        .growth-negative {
            color: #dc3545;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_salary_chart(salary_ranges: Dict[str, str]) -> go.Figure:
    """Create a salary range visualization"""
    if not salary_ranges or all(v == "N/A" for v in salary_ranges.values()):
        return None
    
    # Extract numeric values from salary ranges
    levels = []
    salaries = []
    
    for level, range_str in salary_ranges.items():
        if range_str != "N/A":
            # Try to extract numbers from range like "50-70k" or "$60,000-$80,000"
            import re
            numbers = re.findall(r'[\d,]+', range_str.replace('k', '000'))
            if len(numbers) >= 2:
                try:
                    avg_salary = (int(numbers[0].replace(',', '')) + int(numbers[1].replace(',', ''))) / 2
                    levels.append(level.replace('_', ' ').title())
                    salaries.append(avg_salary)
                except ValueError:
                    continue
    
    if not salaries:
        return None
    
    fig = go.Figure(data=[
        go.Bar(
            x=levels,
            y=salaries,
            marker_color=['#28a745', '#007bff', '#ffc107'],
            text=[f"${int(s):,}" for s in salaries],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Salary Ranges by Experience Level",
        xaxis_title="Experience Level",
        yaxis_title="Average Salary ($)",
        showlegend=False,
        height=400
    )
    
    return fig


@st.cache_data
def load_analyzer():
    """Load the job market analyzer with caching"""
    return JobMarketAnalyzer()

def display_dataset_overview(analyzer: JobMarketAnalyzer) -> None:
    """Display dataset overview and summary statistics"""
    st.subheader("📊 Dataset Overview")
    
    summary = analyzer.get_summary_insights()
    if "error" in summary:
        st.error(summary["error"])
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", f"{summary['total_jobs']:,}")
    
    with col2:
        st.metric("Average Salary", f"${summary['average_salary']:,.0f}")
    
    with col3:
        st.metric("Top Industry", summary['top_industry'])
    
    with col4:
        st.metric("Remote Jobs", f"{summary['remote_percentage']:.1f}%")
    
    # Experience level distribution
    st.subheader("👥 Experience Level Distribution")
    exp_dist = summary['experience_distribution']
    if exp_dist:
        exp_df = pd.DataFrame(list(exp_dist.items()), columns=['Level', 'Count'])
        fig = px.pie(exp_df, values='Count', names='Level', title="Jobs by Experience Level")
        st.plotly_chart(fig, use_container_width=True)

def display_salary_analysis(analyzer: JobMarketAnalyzer, filters: Dict[str, Any]) -> None:
    """Display comprehensive salary analysis"""
    st.subheader("💰 Salary Analysis")
    
    # Get salary analysis
    salary_data = analyzer.get_salary_analysis(
        experience_level=filters.get('experience_level'),
        industry=filters.get('industry')
    )
    
    if "error" in salary_data:
        st.error(salary_data["error"])
        return
    
    # Display statistics
    stats = salary_data['stats']
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Salary", f"${stats['mean']:,.0f}")
    
    with col2:
        st.metric("Median Salary", f"${stats['median']:,.0f}")
    
    with col3:
        st.metric("Min Salary", f"${stats['min']:,.0f}")
    
    with col4:
        st.metric("Max Salary", f"${stats['max']:,.0f}")
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Salary by experience level
        salary_chart = analyzer.create_salary_visualization(salary_data)
        if salary_chart:
            st.plotly_chart(salary_chart, use_container_width=True)
    
    with col2:
        # Top paying industries
        if salary_data['by_industry']:
            industries = list(salary_data['by_industry'].keys())[:10]
            salaries = list(salary_data['by_industry'].values())[:10]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=industries,
                    y=salaries,
                    marker_color='#28a745',
                    text=[f"${int(s):,}" for s in salaries],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Top Paying Industries",
                xaxis_title="Industry",
                yaxis_title="Average Salary (USD)",
                height=400,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)

def display_skill_analysis(analyzer: JobMarketAnalyzer) -> None:
    """Display skill demand analysis"""
    st.subheader("🎯 Skills Demand Analysis")
    
    skill_data = analyzer.get_skill_demand_analysis()
    
    # Top skills chart
    skill_chart = analyzer.create_skill_demand_chart(skill_data)
    if skill_chart:
        st.plotly_chart(skill_chart, use_container_width=True)
    
    # Skills by experience level
    st.subheader("Skills by Experience Level")
    skills_by_exp = skill_data.get('by_experience', {})
    
    if skills_by_exp:
        tabs = st.tabs(list(skills_by_exp.keys()))
        for i, (exp_level, skills) in enumerate(skills_by_exp.items()):
            with tabs[i]:
                if skills:
                    skills_df = pd.DataFrame(skills, columns=['Skill', 'Count'])
                    fig = px.bar(skills_df.head(10), x='Count', y='Skill', 
                               orientation='h', title=f"Top Skills for {exp_level}")
                    st.plotly_chart(fig, use_container_width=True)

def display_industry_analysis(analyzer: JobMarketAnalyzer) -> None:
    """Display industry trends analysis"""
    st.subheader("🏢 Industry Trends")
    
    industry_data = analyzer.get_industry_trends()
    
    # Industry job counts
    industry_chart = analyzer.create_industry_trends_chart(industry_data)
    if industry_chart:
        st.plotly_chart(industry_chart, use_container_width=True)
    
    # Remote work trends
    st.subheader("Remote Work by Industry")
    remote_trends = industry_data.get('remote_trends', {})
    if remote_trends:
        remote_df = pd.DataFrame(list(remote_trends.items()), columns=['Industry', 'Remote Ratio'])
        remote_df = remote_df.head(10)
        
        fig = px.bar(remote_df, x='Industry', y='Remote Ratio', 
                    title="Remote Work Percentage by Industry")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def display_geographic_analysis(analyzer: JobMarketAnalyzer) -> None:
    """Display geographic opportunities analysis"""
    st.subheader("🌍 Geographic Opportunities")
    
    geo_data = analyzer.get_geographic_analysis()
    
    # Salary by country
    geo_chart = analyzer.create_geographic_chart(geo_data)
    if geo_chart:
        st.plotly_chart(geo_chart, use_container_width=True)
    
    # Job counts by country
    st.subheader("Job Distribution by Country")
    job_counts = geo_data.get('job_counts', {})
    if job_counts:
        countries = list(job_counts.keys())[:10]
        counts = list(job_counts.values())[:10]
        
        fig = go.Figure(data=[
            go.Bar(
                x=countries,
                y=counts,
                marker_color='#007bff',
                text=counts,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Top Countries by Job Count",
            xaxis_title="Country",
            yaxis_title="Number of Jobs",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_job_title_analysis(analyzer: JobMarketAnalyzer, search_term: str) -> None:
    """Display analysis for specific job titles"""
    st.subheader(f"🔍 Analysis for: {search_term}")
    
    job_data = analyzer.get_job_title_analysis(search_term)
    
    if "error" in job_data:
        st.error(job_data["error"])
        return
    
    # Job title statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Jobs Found", job_data['total_jobs'])
    
    with col2:
        if job_data['salary_analysis']:
            avg_salary = sum(item['mean'] for item in job_data['salary_analysis'][:5]) / min(5, len(job_data['salary_analysis']))
            st.metric("Average Salary", f"${avg_salary:,.0f}")
    
    with col3:
        if job_data['experience_distribution']:
            most_common_exp = max(job_data['experience_distribution'], key=job_data['experience_distribution'].get)
            st.metric("Most Common Level", most_common_exp)
    
    # Top skills for this job
    st.subheader("Top Skills for This Role")
    top_skills = job_data.get('top_skills', [])
    if top_skills:
        skills_df = pd.DataFrame(top_skills, columns=['Skill', 'Count'])
        fig = px.bar(skills_df.head(10), x='Count', y='Skill', 
                    orientation='h', title=f"Most Required Skills for {search_term}")
        st.plotly_chart(fig, use_container_width=True)
    
    # Salary analysis for job titles
    if job_data['salary_analysis']:
        st.subheader("Salary by Job Title")
        salary_df = pd.DataFrame(job_data['salary_analysis'][:10])
        fig = px.bar(salary_df, x='job_title', y='mean', 
                    title="Average Salary by Job Title")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def display_certification_recommendations(analyzer: JobMarketAnalyzer, skills: List[str]) -> None:
    """Display certification recommendations based on skills"""
    st.subheader("🎓 Certification Recommendations")
    
    recommendations = analyzer.get_certification_recommendations(skills)
    
    if recommendations:
        for skill, certs in recommendations.items():
            st.markdown(f"**For {skill}:**")
            for cert in certs:
                st.markdown(f"• {cert}")
            st.markdown("---")
    else:
        st.info("No specific certifications found for the selected skills")

def display_market_analysis(analysis: Dict[str, Any]) -> None:
    """Display the legacy market analysis results (for Gemini AI insights)"""
    
    # Header with growth outlook
    st.subheader("🤖 AI-Powered Market Insights")
    growth_outlook = analysis.get("growth_outlook", "Analysis unavailable")
    st.info(f"**Growth Outlook:** {growth_outlook}")
    
    # Key insights
    key_insights = analysis.get("key_insights", [])
    if key_insights and key_insights != ["Analysis unavailable"]:
        st.subheader("💡 AI-Generated Insights")
        for insight in key_insights:
            st.markdown(f"• {insight}")
    
    # Create columns for different sections
    col1, col2 = st.columns(2)
    
    with col1:
        # Industries
        st.subheader("🏢 AI-Identified Industries")
        industries = analysis.get("industries", [])
        if industries and industries != ["Analysis unavailable"]:
            industries_html = "".join([f'<span class="industry-badge">{industry}</span>' for industry in industries])
            st.markdown(f'<div style="margin: 10px 0;">{industries_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Industry data not available")
        
        # Skills
        st.subheader("🎯 AI-Identified Skills")
        top_skills = analysis.get("top_skills", [])
        if top_skills and top_skills != ["Analysis unavailable"]:
            skills_html = "".join([f'<span class="skill-badge">{skill}</span>' for skill in top_skills])
            st.markdown(f'<div style="margin: 10px 0;">{skills_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Skills data not available")
    
    with col2:
        # Tools
        st.subheader("🛠️ AI-Identified Tools")
        tools = analysis.get("tools", [])
        if tools and tools != ["Analysis unavailable"]:
            tools_html = "".join([f'<span class="skill-badge">{tool}</span>' for tool in tools])
            st.markdown(f'<div style="margin: 10px 0;">{tools_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Tools data not available")
        
        # Regions
        st.subheader("🌍 AI-Identified Regions")
        regions = analysis.get("regions", [])
        if regions and regions != ["Analysis unavailable"]:
            regions_html = "".join([f'<span class="industry-badge">{region}</span>' for region in regions])
            st.markdown(f'<div style="margin: 10px 0;">{regions_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Regional data not available")
    
    # Salary ranges
    st.subheader("💰 AI Salary Expectations")
    salary_ranges = analysis.get("salary_ranges", {})
    if salary_ranges and not all(v == "N/A" for v in salary_ranges.values()):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Entry Level", salary_ranges.get("entry_level", "N/A"))
        with col2:
            st.metric("Mid Level", salary_ranges.get("mid_level", "N/A"))
        with col3:
            st.metric("Senior Level", salary_ranges.get("senior_level", "N/A"))
        
        # Create salary chart if possible
        salary_chart = create_salary_chart(salary_ranges)
        if salary_chart:
            st.plotly_chart(salary_chart, use_container_width=True)
    else:
        st.info("Salary data not available")
    
    # Trends
    st.subheader("📈 AI Market Trends")
    trends = analysis.get("trends", [])
    if trends and trends != ["Analysis unavailable"]:
        for trend in trends:
            st.markdown(f"• {trend}")
    else:
        st.info("Trend data not available")
    
    # Certifications
    st.subheader("🎓 AI Certification Recommendations")
    certifications = analysis.get("certifications", [])
    if certifications and certifications != ["Analysis unavailable"]:
        for cert in certifications:
            st.markdown(f"• {cert}")
    else:
        st.info("Certification data not available")


def main():
    st.set_page_config(
        page_title="Enhanced Job Market Analysis", 
        page_icon="📊", 
        layout="wide"
    )
    _inject_styles()

    st.title("📊 Enhanced Job Market Analysis")
    st.caption("Powered by 30,000+ real job records and AI insights! Get comprehensive market trends, salary analysis, and career guidance.")

    # Load the analyzer
    analyzer = load_analyzer()
    
    # Check for skills from enhanced resume summary
    resume_skills = st.session_state.get("extracted_skills", [])
    if resume_skills:
        st.success(f"🎯 Found {len(resume_skills)} skills from your enhanced resume summary! Use them for personalized insights below.")
    
    # Sidebar for filters
    st.sidebar.header("🔧 Filters")
    
    # Experience level filter
    experience_levels = ["All", "EN", "MI", "SE", "EX"]
    selected_exp = st.sidebar.selectbox("Experience Level", experience_levels)
    
    # Industry filter
    if not analyzer.df.empty:
        industries = ["All"] + sorted(analyzer.df['industry'].unique().tolist())
        selected_industry = st.sidebar.selectbox("Industry", industries)
    else:
        selected_industry = "All"
    
    # Create filters dict
    filters = {}
    if selected_exp != "All":
        filters['experience_level'] = selected_exp
    if selected_industry != "All":
        filters['industry'] = selected_industry
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", "💰 Salary Analysis", "🎯 Skills", 
        "🏢 Industries", "🌍 Geography", "🔍 Job Search", "🎯 Your Skills Analysis"
    ])
    
    with tab1:
        st.header("📊 Dataset Overview")
        display_dataset_overview(analyzer)
    
    with tab2:
        st.header("💰 Salary Analysis")
        display_salary_analysis(analyzer, filters)
    
    with tab3:
        st.header("🎯 Skills Demand Analysis")
        display_skill_analysis(analyzer)
    
    with tab4:
        st.header("🏢 Industry Trends")
        display_industry_analysis(analyzer)
    
    with tab5:
        st.header("🌍 Geographic Opportunities")
        display_geographic_analysis(analyzer)
    
    with tab6:
        st.header("🔍 Job Title Analysis")
        
        # Job search section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            job_input = st.text_input(
                "Search for specific job titles",
                placeholder="e.g., 'Data Scientist', 'AI Engineer', 'Machine Learning Engineer'",
                help="Enter a job title to get detailed analysis"
            )
        
        with col2:
            search_button = st.button("🔍 Search Jobs", type="primary", use_container_width=True)
        
        if search_button and job_input:
            display_job_title_analysis(analyzer, job_input)
            
            # Get top skills for certification recommendations
            job_data = analyzer.get_job_title_analysis(job_input)
            if "error" not in job_data and job_data.get('top_skills'):
                top_skills = [skill for skill, count in job_data['top_skills'][:5]]
                display_certification_recommendations(analyzer, top_skills)
        
        elif not job_input:
            st.info("👆 Enter a job title to search and analyze")
    
    with tab7:
        st.header("🎯 Your Skills Analysis")
        
        if resume_skills:
            st.subheader("📈 Skill-Demand Analysis for Your Skills")
            
            # Analyze each skill from resume
            skill_analysis_results = []
            for skill in resume_skills[:10]:  # Limit to top 10 skills
                job_data = analyzer.get_job_title_analysis(skill)
                if "error" not in job_data:
                    skill_analysis_results.append({
                        'skill': skill,
                        'job_count': job_data['total_jobs'],
                        'avg_salary': sum(item['mean'] for item in job_data['salary_analysis'][:3]) / min(3, len(job_data['salary_analysis'])) if job_data['salary_analysis'] else 0
                    })
            
            if skill_analysis_results:
                # Create skill demand chart
                skills_df = pd.DataFrame(skill_analysis_results)
                fig = px.bar(skills_df, x='skill', y='job_count', 
                           title="Job Demand for Your Skills",
                           labels={'job_count': 'Number of Jobs', 'skill': 'Your Skills'})
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Top 3 recommended skills to learn
                st.subheader("🚀 Recommended Skills to Learn")
                all_skills_data = analyzer.get_skill_demand_analysis()
                top_skills = [skill for skill, count in all_skills_data['top_skills'][:20]]
                
                # Find skills not in user's resume
                missing_skills = [skill for skill in top_skills if skill.lower() not in [s.lower() for s in resume_skills]]
                
                if missing_skills:
                    st.write("**Top skills you should consider learning:**")
                    for i, skill in enumerate(missing_skills[:5], 1):
                        st.write(f"{i}. **{skill}** - High demand in the market")
                else:
                    st.success("🎉 You already have most of the top in-demand skills!")
            
            # Career fit score
            st.subheader("🎯 Career Fit Score")
            if skill_analysis_results:
                total_jobs = sum(result['job_count'] for result in skill_analysis_results)
                avg_salary = sum(result['avg_salary'] for result in skill_analysis_results) / len(skill_analysis_results)
                
                # Simple scoring algorithm
                fit_score = min(100, (total_jobs / 100) + (avg_salary / 1000))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Career Fit Score", f"{fit_score:.0f}/100")
                with col2:
                    st.metric("Total Job Opportunities", f"{total_jobs:,}")
                with col3:
                    st.metric("Average Salary Potential", f"${avg_salary:,.0f}")
                
                # Recommendations based on fit score
                if fit_score >= 80:
                    st.success("🌟 Excellent! Your skills are highly in demand.")
                elif fit_score >= 60:
                    st.info("👍 Good! Your skills have solid market demand.")
                else:
                    st.warning("💡 Consider learning additional in-demand skills to improve your market fit.")
        else:
            st.info("👆 Upload your resume in the Enhanced Resume Summary module to get personalized skill insights here!")
            
            # Manual skill input option
            st.subheader("🔍 Analyze Specific Skills")
            manual_skills = st.text_input(
                "Enter skills to analyze (comma-separated)",
                placeholder="e.g., Python, Machine Learning, AWS"
            )
            
            if manual_skills and st.button("Analyze Skills"):
                skills_list = [skill.strip() for skill in manual_skills.split(",")]
                st.session_state["extracted_skills"] = skills_list
                st.rerun()
    
    # AI Insights section
    st.markdown("---")
    st.header("🤖 AI-Powered Insights")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ai_job_input = st.text_input(
            "Get AI insights for any role",
            placeholder="e.g., 'Python Developer', 'Data Analyst', 'AI Researcher'",
            help="Get AI-generated insights and recommendations"
        )
    
    with col2:
        ai_analyze_button = st.button("🚀 Get AI Insights", type="secondary", use_container_width=True)
    
    # AI Analysis section
    if ai_analyze_button and ai_job_input:
        with st.spinner("Generating AI insights with Gemini..."):
            try:
                analysis_results = analyze_job_market(ai_job_input)
                st.session_state["ai_market_analysis"] = analysis_results
                st.session_state["ai_analyzed_job"] = ai_job_input
                st.success("✅ AI analysis completed!")
            except Exception as e:
                st.error(f"AI analysis failed: {e}")
    
    # Display AI results if available
    if st.session_state.get("ai_market_analysis"):
        st.markdown("---")
        display_market_analysis(st.session_state["ai_market_analysis"])
        
        # Additional AI insights section
        st.subheader("💡 AI Actionable Insights")
        st.info(
            f"Based on AI analysis of '{st.session_state.get('ai_analyzed_job', 'your search')}', "
            "consider focusing on the trending skills and tools mentioned above to stay competitive in the market."
        )
    
    # Footer with tips
    st.markdown("---")
    st.markdown(
        """
        💡 **Tips**: 
        - Use the filters in the sidebar to narrow down your analysis
        - Try different job titles in the Job Search tab to compare opportunities
        - Check the AI insights for additional market intelligence
        - Explore certification recommendations based on in-demand skills
        """
    )


if __name__ == "__main__":
    main()
