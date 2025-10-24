"""
Shared Data Module for AI Career & Skill Gap Analyzer
Handles data sharing between different modules and session management
"""

import streamlit as st
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime


class SharedDataManager:
    """Manages shared data between modules"""
    
    def __init__(self):
        self.session_key = "career_analyzer_data"
    
    def save_resume_analysis(self, skills: List[str], resume_text: str, analysis_results: Dict[str, Any] = None):
        """Save resume analysis results to shared storage"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {}
        
        st.session_state[self.session_key].update({
            "extracted_skills": skills,
            "resume_text": resume_text,
            "resume_analysis_results": analysis_results,
            "resume_analysis_timestamp": datetime.now().isoformat(),
            "resume_analysis_complete": True
        })
    
    def get_resume_skills(self) -> List[str]:
        """Get extracted skills from resume analysis"""
        if self.session_key in st.session_state:
            return st.session_state[self.session_key].get("extracted_skills", [])
        return []
    
    def get_resume_text(self) -> str:
        """Get resume text from analysis"""
        if self.session_key in st.session_state:
            return st.session_state[self.session_key].get("resume_text", "")
        return ""
    
    def is_resume_analyzed(self) -> bool:
        """Check if resume has been analyzed"""
        if self.session_key in st.session_state:
            return st.session_state[self.session_key].get("resume_analysis_complete", False)
        return False
    
    def save_career_goals(self, goals: str, experience_level: str, skills: List[str]):
        """Save career goals and profile data"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {}
        
        st.session_state[self.session_key].update({
            "career_goals": goals,
            "experience_level": experience_level,
            "user_skills": skills,
            "profile_timestamp": datetime.now().isoformat()
        })
    
    def get_career_profile(self) -> Dict[str, Any]:
        """Get complete career profile"""
        if self.session_key in st.session_state:
            return {
                "skills": st.session_state[self.session_key].get("extracted_skills", []),
                "career_goals": st.session_state[self.session_key].get("career_goals", ""),
                "experience_level": st.session_state[self.session_key].get("experience_level", "Mid"),
                "resume_analyzed": st.session_state[self.session_key].get("resume_analysis_complete", False)
            }
        return {
            "skills": [],
            "career_goals": "",
            "experience_level": "Mid",
            "resume_analyzed": False
        }
    
    def save_job_market_insights(self, job_title: str, insights: Dict[str, Any]):
        """Save job market analysis insights"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {}
        
        if "job_market_insights" not in st.session_state[self.session_key]:
            st.session_state[self.session_key]["job_market_insights"] = {}
        
        st.session_state[self.session_key]["job_market_insights"][job_title] = {
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_job_market_insights(self, job_title: str) -> Optional[Dict[str, Any]]:
        """Get job market insights for a specific job title"""
        if (self.session_key in st.session_state and 
            "job_market_insights" in st.session_state[self.session_key] and
            job_title in st.session_state[self.session_key]["job_market_insights"]):
            return st.session_state[self.session_key]["job_market_insights"][job_title]["insights"]
        return None
    
    def get_learning_recommendations(self) -> List[str]:
        """Get personalized learning recommendations based on all available data"""
        profile = self.get_career_profile()
        skills = profile["skills"]
        
        # Basic recommendations based on common skill gaps
        recommendations = []
        
        if not any("python" in skill.lower() for skill in skills):
            recommendations.append("Learn Python programming fundamentals")
        
        if not any("machine learning" in skill.lower() or "ml" in skill.lower() for skill in skills):
            recommendations.append("Explore Machine Learning concepts and tools")
        
        if not any("cloud" in skill.lower() or "aws" in skill.lower() or "azure" in skill.lower() for skill in skills):
            recommendations.append("Get familiar with cloud platforms (AWS, Azure, GCP)")
        
        if not any("data" in skill.lower() for skill in skills):
            recommendations.append("Develop data analysis and visualization skills")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def export_profile_data(self) -> str:
        """Export complete profile data as JSON"""
        if self.session_key in st.session_state:
            return json.dumps(st.session_state[self.session_key], indent=2, default=str)
        return "{}"
    
    def clear_all_data(self):
        """Clear all shared data"""
        if self.session_key in st.session_state:
            del st.session_state[self.session_key]


# Global instance
shared_data = SharedDataManager()


def get_shared_data() -> SharedDataManager:
    """Get the global shared data manager instance"""
    return shared_data


def sync_resume_skills_to_career_assistant():
    """Sync resume skills to career assistant session state"""
    skills = shared_data.get_resume_skills()
    if skills:
        st.session_state["user_skills"] = skills
        st.session_state["resume_skills_loaded"] = True


def get_career_fit_score(skills: List[str]) -> Dict[str, Any]:
    """Calculate career fit score based on skills"""
    # This would integrate with the job market analyzer
    # For now, return a basic score
    if not skills:
        return {"score": 0, "level": "No skills", "recommendations": ["Start by learning basic programming skills"]}
    
    # Simple scoring based on common in-demand skills
    high_demand_skills = ["python", "javascript", "java", "sql", "aws", "docker", "kubernetes", "machine learning", "data analysis"]
    skill_matches = sum(1 for skill in skills if any(high_skill in skill.lower() for high_skill in high_demand_skills))
    
    score = min(100, (skill_matches / len(high_demand_skills)) * 100)
    
    if score >= 80:
        level = "Excellent"
        recommendations = ["Your skills are highly in demand!", "Consider specializing in emerging technologies"]
    elif score >= 60:
        level = "Good"
        recommendations = ["Your skills have solid market demand", "Consider learning cloud technologies"]
    elif score >= 40:
        level = "Fair"
        recommendations = ["Consider learning more in-demand skills", "Focus on Python, cloud platforms, or data analysis"]
    else:
        level = "Needs Improvement"
        recommendations = ["Start with Python programming", "Learn basic data analysis", "Explore cloud platforms"]
    
    return {
        "score": score,
        "level": level,
        "recommendations": recommendations,
        "matched_skills": skill_matches,
        "total_high_demand": len(high_demand_skills)
    }


if __name__ == "__main__":
    # Test the shared data manager
    print("Shared Data Manager initialized successfully")
    print(f"Available methods: {[method for method in dir(SharedDataManager) if not method.startswith('_')]}")
