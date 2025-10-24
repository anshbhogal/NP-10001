"""
Google Gemini AI Client for Resume Analysis
Handles API calls, prompt engineering, and response parsing
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google AI API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        logger.info("✅ Gemini client initialized successfully")
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyze resume using Gemini AI
        
        Args:
            resume_text: Full resume text to analyze
            
        Returns:
            Dictionary with structured analysis results
        """
        try:
            # Check text length and chunk if necessary
            if len(resume_text) > 30000:  # Approximate token limit
                return self._analyze_large_resume(resume_text)
            else:
                return self._analyze_resume_direct(resume_text)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing resume: {e}")
            return self._get_fallback_response()
    
    def _analyze_resume_direct(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume directly (for smaller texts)"""
        prompt = self._create_resume_analysis_prompt(resume_text)
        
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            
            return self._parse_analysis_response(response.text)
            
        except Exception as e:
            logger.error(f"❌ Error in direct analysis: {e}")
            return self._get_fallback_response()
    
    def _analyze_large_resume(self, resume_text: str) -> Dict[str, Any]:
        """Analyze large resume by chunking"""
        try:
            # First, get a summary
            summary_prompt = f"""
            Summarize this resume in 500 words or less, focusing on:
            - Key skills and technologies
            - Work experience and roles
            - Education and certifications
            - Notable achievements
            
            Resume text: {resume_text[:15000]}  # First 15k chars
            """
            
            summary_response = self.model.generate_content(
                summary_prompt,
                safety_settings=self.safety_settings
            )
            
            # Then analyze the summary
            analysis_prompt = self._create_resume_analysis_prompt(summary_response.text)
            
            analysis_response = self.model.generate_content(
                analysis_prompt,
                safety_settings=self.safety_settings
            )
            
            return self._parse_analysis_response(analysis_response.text)
            
        except Exception as e:
            logger.error(f"❌ Error in chunked analysis: {e}")
            return self._get_fallback_response()
    
    def _create_resume_analysis_prompt(self, resume_text: str) -> str:
        """Create the prompt for resume analysis"""
        return f"""
You are an expert career coach and AI analyst. Analyze the following resume and provide a structured assessment.

RESUME TEXT:
{resume_text}

Please provide your analysis in the following JSON format:

{{
    "candidate_summary": "Brief 2-3 sentence summary of the candidate",
    "key_strengths": [
        "Strength 1 with specific examples",
        "Strength 2 with specific examples", 
        "Strength 3 with specific examples"
    ],
    "skill_gaps": [
        "Missing skill 1 with explanation",
        "Missing skill 2 with explanation",
        "Missing skill 3 with explanation"
    ],
    "suitable_roles": [
        "Role 1 with readiness level (Entry/Mid/Senior)",
        "Role 2 with readiness level",
        "Role 3 with readiness level"
    ],
    "career_level": "Entry/Mid/Senior/Lead",
    "experience_quality": "Assessment of experience depth and relevance",
    "learning_recommendations": [
        "Specific skill to learn with resource suggestion",
        "Another skill with resource suggestion",
        "Third skill with resource suggestion"
    ],
    "salary_estimate": {{
        "entry_level": "X-Y range",
        "mid_level": "X-Y range", 
        "senior_level": "X-Y range"
    }},
    "interview_readiness": "Assessment of readiness for technical interviews",
    "portfolio_suggestions": [
        "Project idea 1",
        "Project idea 2",
        "Project idea 3"
    ]
}}

Focus on:
- Technical skills and their depth
- Industry experience and relevance
- Leadership and soft skills
- Career progression and trajectory
- Market demand for their skills
- Specific, actionable recommendations

Be constructive and specific in your analysis.
"""
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured data"""
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                # Fallback: create structured response from text
                return self._parse_text_response(response_text)
            
            # Parse JSON
            analysis = json.loads(json_text)
            
            # Validate and clean the response
            return self._validate_analysis_response(analysis)
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON parsing failed: {e}")
            return self._parse_text_response(response_text)
        except Exception as e:
            logger.error(f"❌ Error parsing response: {e}")
            return self._get_fallback_response()
    
    def _parse_text_response(self, response_text: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        return {
            "candidate_summary": "AI analysis completed",
            "key_strengths": ["Analysis completed - see full response"],
            "skill_gaps": ["Analysis completed - see full response"],
            "suitable_roles": ["Analysis completed - see full response"],
            "career_level": "Mid",
            "experience_quality": "Analysis completed",
            "learning_recommendations": ["Analysis completed - see full response"],
            "salary_estimate": {"entry_level": "N/A", "mid_level": "N/A", "senior_level": "N/A"},
            "interview_readiness": "Analysis completed",
            "portfolio_suggestions": ["Analysis completed - see full response"],
            "raw_response": response_text
        }
    
    def _validate_analysis_response(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean analysis response"""
        required_fields = [
            "candidate_summary", "key_strengths", "skill_gaps", 
            "suitable_roles", "career_level", "learning_recommendations"
        ]
        
        for field in required_fields:
            if field not in analysis:
                analysis[field] = "Not specified"
        
        # Ensure lists are properly formatted
        list_fields = ["key_strengths", "skill_gaps", "suitable_roles", "learning_recommendations", "portfolio_suggestions"]
        for field in list_fields:
            if field in analysis and not isinstance(analysis[field], list):
                analysis[field] = [str(analysis[field])]
        
        return analysis
    
    def _get_fallback_response(self) -> Dict[str, Any]:
        """Get fallback response when analysis fails"""
        return {
            "candidate_summary": "Resume analysis could not be completed due to technical issues",
            "key_strengths": ["Analysis unavailable"],
            "skill_gaps": ["Analysis unavailable"],
            "suitable_roles": ["Analysis unavailable"],
            "career_level": "Unknown",
            "experience_quality": "Analysis unavailable",
            "learning_recommendations": ["Please try again or contact support"],
            "salary_estimate": {"entry_level": "N/A", "mid_level": "N/A", "senior_level": "N/A"},
            "interview_readiness": "Analysis unavailable",
            "portfolio_suggestions": ["Analysis unavailable"],
            "error": "Analysis failed"
        }
    
    def get_career_advice(self, user_skills: List[str], career_goals: str = None) -> Dict[str, Any]:
        """
        Get personalized career advice based on skills and goals
        
        Args:
            user_skills: List of user's current skills
            career_goals: Optional career goals description
            
        Returns:
            Dictionary with career advice
        """
        try:
            skills_text = ", ".join(user_skills)
            goals_text = career_goals or "General career advancement"
            
            prompt = f"""
            You are an expert career coach. Provide personalized career advice based on:
            
            Current Skills: {skills_text}
            Career Goals: {goals_text}
            
            Please provide advice in this JSON format:
            {{
                "career_path": "Recommended career progression path",
                "next_skills": ["Skill 1 to learn", "Skill 2 to learn", "Skill 3 to learn"],
                "target_roles": ["Role 1", "Role 2", "Role 3"],
                "learning_plan": "Step-by-step learning plan",
                "timeline": "Estimated timeline for career advancement",
                "salary_progression": "Expected salary progression",
                "networking_tips": ["Tip 1", "Tip 2", "Tip 3"]
            }}
            """
            
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            
            return self._parse_analysis_response(response.text)
            
        except Exception as e:
            logger.error(f"❌ Error getting career advice: {e}")
            return self._get_fallback_response()
    
    def test_connection(self) -> bool:
        """Test Gemini API connection"""
        try:
            test_prompt = "Say 'Hello, I am working correctly!' in exactly those words."
            response = self.model.generate_content(test_prompt)
            return "Hello, I am working correctly!" in response.text
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


def get_gemini_client() -> GeminiClient:
    """Get Gemini client instance (singleton pattern)"""
    if not hasattr(get_gemini_client, 'instance'):
        get_gemini_client.instance = GeminiClient()
    return get_gemini_client.instance


# === Lightweight helper functions for resume evaluation and ATS comparison ===
def analyze_resume_content(resume_text: str) -> str:
    """Return concise bullet-point analysis of resume content and ATS formatting."""
    try:
        client = get_gemini_client()
        prompt = f"""
    You are an expert resume reviewer and ATS specialist.
    Evaluate the following resume for:
    1. Content and keyword relevance to job markets.
    2. Formatting, section clarity, and ATS compatibility.

    Return your analysis as 5 concise bullet points.
    Resume text:
    {resume_text[:2500]}
    """
        response = client.model.generate_content(prompt)
        return (response.text or "").strip()
    except Exception as e:
        logger.error(f"❌ analyze_resume_content failed: {e}")
        return "- Unable to analyze resume right now. Please try again later."


def compare_resume_to_job(resume_text: str, job_description: str) -> str:
    """Return ATS match score and improvement tips comparing resume to job."""
    try:
        client = get_gemini_client()
        prompt = f"""
    Compare this resume and job description for ATS match.
    Provide:
    1. ATS match score (0–100)
    2. 3 improvement suggestions.

    Resume:
    {resume_text[:1500]}

    Job Description:
    {job_description[:1000]}
    """
        result = client.model.generate_content(prompt)
        return (result.text or "").strip()
    except Exception as e:
        logger.error(f"❌ compare_resume_to_job failed: {e}")
        return "- Unable to compute ATS match right now. Please try again later."


def analyze_resume_vs_job(resume_text: str, job_description: str) -> dict:
    """
    Analyze resume against job description using Gemini AI
    
    Args:
        resume_text: Full resume text
        job_description: Job description text
        
    Returns:
        Dictionary with structured analysis results
    """
    try:
        client = get_gemini_client()
        
        # Import config to get the prompt template
        import sys
        import os
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config')
        if config_path not in sys.path:
            sys.path.append(config_path)
        from gemini_config import get_gemini_config
        
        config = get_gemini_config()
        prompt_template = config.get_resume_job_analysis_prompt()
        
        # Format the prompt with actual data
        prompt = prompt_template.format(
            resume_text=resume_text[:8000],  # Limit text length
            job_description=job_description[:4000]
        )
        
        response = client.model.generate_content(
            prompt,
            safety_settings=client.safety_settings
        )
        
        return _parse_job_analysis_response(response.text)
        
    except Exception as e:
        logger.error(f"❌ analyze_resume_vs_job failed: {e}")
        return _get_fallback_job_analysis()


def _parse_job_analysis_response(response_text: str) -> dict:
    """Parse Gemini response for job analysis into structured data"""
    try:
        # Try to extract JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "{" in response_text and "}" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_text = response_text[json_start:json_end]
        else:
            # Fallback: create structured response from text
            return _parse_text_job_response(response_text)
        
        # Parse JSON
        analysis = json.loads(json_text)
        
        # Validate and clean the response
        return _validate_job_analysis_response(analysis)
        
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ JSON parsing failed for job analysis: {e}")
        return _parse_text_job_response(response_text)
    except Exception as e:
        logger.error(f"❌ Error parsing job analysis response: {e}")
        return _get_fallback_job_analysis()


def _parse_text_job_response(response_text: str) -> dict:
    """Parse text response when JSON parsing fails for job analysis"""
    return {
        "relevance_score": 0.5,
        "ats_score": 0.5,
        "key_matches": ["Analysis completed - see full response"],
        "missing_keywords": ["Analysis completed - see full response"],
        "formatting_feedback": "Analysis completed - see full response",
        "summary": "Analysis completed - see full response",
        "raw_response": response_text
    }


def _validate_job_analysis_response(analysis: dict) -> dict:
    """Validate and clean job analysis response"""
    required_fields = [
        "relevance_score", "ats_score", "key_matches", 
        "missing_keywords", "formatting_feedback", "summary"
    ]
    
    for field in required_fields:
        if field not in analysis:
            if field in ["relevance_score", "ats_score"]:
                analysis[field] = 0.5
            elif field in ["key_matches", "missing_keywords"]:
                analysis[field] = []
            else:
                analysis[field] = "Not specified"
    
    # Ensure scores are floats between 0 and 1
    if "relevance_score" in analysis:
        analysis["relevance_score"] = max(0.0, min(1.0, float(analysis["relevance_score"])))
    if "ats_score" in analysis:
        analysis["ats_score"] = max(0.0, min(1.0, float(analysis["ats_score"])))
    
    # Ensure lists are properly formatted
    list_fields = ["key_matches", "missing_keywords"]
    for field in list_fields:
        if field in analysis and not isinstance(analysis[field], list):
            analysis[field] = [str(analysis[field])]
    
    return analysis


def _get_fallback_job_analysis() -> dict:
    """Get fallback response when job analysis fails"""
    return {
        "relevance_score": 0.0,
        "ats_score": 0.0,
        "key_matches": ["Analysis unavailable"],
        "missing_keywords": ["Analysis unavailable"],
        "formatting_feedback": "Analysis could not be completed due to technical issues",
        "summary": "Analysis unavailable - please try again",
        "error": "Analysis failed"
    }


def extract_job_description_from_url(url: str) -> str:
    """
    Extract job description from a URL using Gemini AI
    
    Args:
        url: Job posting URL
        
    Returns:
        Extracted job description text
    """
    try:
        client = get_gemini_client()
        
        prompt = f"""
        You are a web scraping assistant. I need you to extract the job description from this URL.
        
        URL: {url}
        
        Please:
        1. Access the URL and read the page content
        2. Extract the main job description text
        3. Focus on job requirements, responsibilities, and qualifications
        4. Remove any navigation, ads, or irrelevant content
        5. Return only the clean job description text
        
        If you cannot access the URL, please return "Unable to access URL. Please try a different link or paste the job description manually."
        """
        
        response = client.model.generate_content(
            prompt,
            safety_settings=client.safety_settings
        )
        
        return response.text.strip() if response.text else "Unable to extract job description from URL."
        
    except Exception as e:
        logger.error(f"❌ extract_job_description_from_url failed: {e}")
        return "Unable to extract job description from URL. Please paste the job description manually."


def analyze_job_market(job_title_or_skill: str) -> dict:
    """
    Analyze job market trends and opportunities for a given job title or skill
    
    Args:
        job_title_or_skill: Job title or skill to analyze
        
    Returns:
        Dictionary with market analysis results
    """
    try:
        client = get_gemini_client()
        
        # Import config to get the prompt template
        import sys
        import os
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config')
        if config_path not in sys.path:
            sys.path.append(config_path)
        from gemini_config import get_gemini_config
        
        config = get_gemini_config()
        prompt_template = config.get_job_market_analysis_prompt()
        
        # Format the prompt with actual data
        prompt = prompt_template.format(job_title_or_skill=job_title_or_skill)
        
        response = client.model.generate_content(
            prompt,
            safety_settings=client.safety_settings
        )
        
        return _parse_job_market_response(response.text)
        
    except Exception as e:
        logger.error(f"❌ analyze_job_market failed: {e}")
        return _get_fallback_job_market_analysis()


def get_career_advice(user_skills: List[str], user_query: str, experience_level: str = "Mid", career_goals: str = "Career advancement") -> str:
    """
    Get personalized career advice using Gemini AI
    
    Args:
        user_skills: List of user's skills
        user_query: User's question or request
        experience_level: User's experience level (Entry/Mid/Senior)
        career_goals: User's career goals
        
    Returns:
        Career advice response
    """
    try:
        client = get_gemini_client()
        
        # Import config to get the prompt template
        import sys
        import os
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config')
        if config_path not in sys.path:
            sys.path.append(config_path)
        from gemini_config import get_gemini_config
        
        config = get_gemini_config()
        prompt_template = config.get_career_assistant_prompt()
        
        # Format the prompt with actual data
        skills_text = ", ".join(user_skills) if user_skills else "Not specified"
        prompt = prompt_template.format(
            user_skills=skills_text,
            experience_level=experience_level,
            career_goals=career_goals,
            user_query=user_query
        )
        
        response = client.model.generate_content(
            prompt,
            safety_settings=client.safety_settings
        )
        
        return response.text.strip() if response.text else "Unable to provide career advice at this time."
        
    except Exception as e:
        logger.error(f"❌ get_career_advice failed: {e}")
        return "I'm sorry, I'm having trouble providing career advice right now. Please try again later."


def _parse_job_market_response(response_text: str) -> dict:
    """Parse Gemini response for job market analysis into structured data"""
    try:
        # Try to extract JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "{" in response_text and "}" in response_text:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            json_text = response_text[json_start:json_end]
        else:
            # Fallback: create structured response from text
            return _parse_text_job_market_response(response_text)
        
        # Parse JSON
        analysis = json.loads(json_text)
        
        # Validate and clean the response
        return _validate_job_market_response(analysis)
        
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ JSON parsing failed for job market analysis: {e}")
        return _parse_text_job_market_response(response_text)
    except Exception as e:
        logger.error(f"❌ Error parsing job market response: {e}")
        return _get_fallback_job_market_analysis()


def _parse_text_job_market_response(response_text: str) -> dict:
    """Parse text response when JSON parsing fails for job market analysis"""
    return {
        "industries": ["Analysis completed - see full response"],
        "top_skills": ["Analysis completed - see full response"],
        "tools": ["Analysis completed - see full response"],
        "salary_ranges": {"entry_level": "N/A", "mid_level": "N/A", "senior_level": "N/A"},
        "trends": ["Analysis completed - see full response"],
        "certifications": ["Analysis completed - see full response"],
        "regions": ["Analysis completed - see full response"],
        "growth_outlook": "Analysis completed - see full response",
        "key_insights": ["Analysis completed - see full response"],
        "raw_response": response_text
    }


def _validate_job_market_response(analysis: dict) -> dict:
    """Validate and clean job market analysis response"""
    required_fields = [
        "industries", "top_skills", "tools", "salary_ranges", 
        "trends", "certifications", "regions", "growth_outlook", "key_insights"
    ]
    
    for field in required_fields:
        if field not in analysis:
            if field == "salary_ranges":
                analysis[field] = {"entry_level": "N/A", "mid_level": "N/A", "senior_level": "N/A"}
            elif field in ["industries", "top_skills", "tools", "trends", "certifications", "regions", "key_insights"]:
                analysis[field] = ["Not specified"]
            else:
                analysis[field] = "Not specified"
    
    # Ensure lists are properly formatted
    list_fields = ["industries", "top_skills", "tools", "trends", "certifications", "regions", "key_insights"]
    for field in list_fields:
        if field in analysis and not isinstance(analysis[field], list):
            analysis[field] = [str(analysis[field])]
    
    return analysis


def _get_fallback_job_market_analysis() -> dict:
    """Get fallback response when job market analysis fails"""
    return {
        "industries": ["Analysis unavailable"],
        "top_skills": ["Analysis unavailable"],
        "tools": ["Analysis unavailable"],
        "salary_ranges": {"entry_level": "N/A", "mid_level": "N/A", "senior_level": "N/A"},
        "trends": ["Analysis unavailable"],
        "certifications": ["Analysis unavailable"],
        "regions": ["Analysis unavailable"],
        "growth_outlook": "Analysis unavailable - please try again",
        "key_insights": ["Analysis unavailable"],
        "error": "Analysis failed"
    }


if __name__ == "__main__":
    # Test the Gemini client
    try:
        client = GeminiClient()
        print("✅ Gemini client initialized successfully")
        
        # Test connection
        if client.test_connection():
            print("✅ Gemini API connection successful")
        else:
            print("❌ Gemini API connection failed")
            
    except Exception as e:
        print(f"❌ Gemini client test failed: {e}")
        print("Make sure to set GEMINI_API_KEY environment variable")
