"""
Google Gemini AI Configuration
Contains API settings and prompt templates
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GeminiConfig:
    """Configuration for Gemini AI integration"""
    
    def __init__(self):
        """Initialize Gemini configuration"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '8192'))
        self.temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
        self.chunk_size = int(os.getenv('GEMINI_CHUNK_SIZE', '30000'))
        
        # Safety settings
        self.safety_settings = {
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
        }
    
    def get_resume_analysis_prompt(self) -> str:
        """Get the resume analysis prompt template"""
        return """
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
    
    def get_career_advice_prompt(self) -> str:
        """Get the career advice prompt template"""
        return """
You are an expert career coach. Provide personalized career advice based on:

Current Skills: {skills}
Career Goals: {goals}

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
    
    def get_skill_gap_analysis_prompt(self) -> str:
        """Get the skill gap analysis prompt template"""
        return """
You are a technical recruiter and career analyst. Analyze the skill gap between a candidate and job requirements.

CANDIDATE SKILLS: {candidate_skills}
JOB REQUIREMENTS: {job_requirements}

Provide analysis in this JSON format:
{{
    "gap_analysis": "Overall assessment of skill gaps",
    "strengths_match": ["Skill 1 that matches", "Skill 2 that matches"],
    "critical_gaps": ["Critical missing skill 1", "Critical missing skill 2"],
    "learning_priority": ["Priority 1 skill to learn", "Priority 2 skill to learn"],
    "readiness_score": 75,
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "interview_focus": ["Focus area 1", "Focus area 2"]
}}
"""
    
    def get_summary_prompt(self) -> str:
        """Get the resume summary prompt template"""
        return """
Summarize this resume in 500 words or less, focusing on:
- Key skills and technologies
- Work experience and roles
- Education and certifications
- Notable achievements

Resume text: {resume_text}
"""
    
    def get_resume_job_analysis_prompt(self) -> str:
        """Get the resume vs job analysis prompt template"""
        return """
You are an AI career analyst.

Compare this candidate's resume and the provided job description.
Evaluate:

1. Content Relevance — How well does the resume match the job requirements?
2. ATS Compatibility — Is the resume formatted for Applicant Tracking Systems?
3. Matching Skills — Skills found both in resume and job.
4. Missing Skills — Skills present in job but not resume.
5. Formatting Feedback — Suggestions to make it more readable and ATS-friendly.
6. Provide two numeric scores (0–1): relevance_score and ats_score.

Return JSON with:
{{
  "relevance_score": float,
  "ats_score": float,
  "key_matches": [skills],
  "missing_keywords": [skills],
  "formatting_feedback": str,
  "summary": str
}}

Resume Text:
{resume_text}

Job Description:
{job_description}
"""
    
    def get_job_market_analysis_prompt(self) -> str:
        """Get the job market analysis prompt template"""
        return """
You are an AI job market analyst with access to current market data and trends.

Given a job title or skill, provide comprehensive market analysis:

Job Title/Skill: {job_title_or_skill}

Please analyze and return structured JSON with:

{{
  "industries": [
    "Industry 1 with hiring demand",
    "Industry 2 with growth potential",
    "Industry 3 with emerging opportunities"
  ],
  "top_skills": [
    "Complementary skill 1",
    "Complementary skill 2", 
    "Complementary skill 3",
    "Emerging skill 4"
  ],
  "tools": [
    "Popular tool 1",
    "Popular tool 2",
    "Industry-standard tool 3"
  ],
  "salary_ranges": {{
    "entry_level": "X-Y range",
    "mid_level": "X-Y range",
    "senior_level": "X-Y range"
  }},
  "trends": [
    "Market trend 1",
    "Growth trend 2",
    "Technology trend 3"
  ],
  "certifications": [
    "Certification 1 with value",
    "Certification 2 for advancement",
    "Certification 3 for specialization"
  ],
  "regions": [
    "High-demand region 1",
    "Emerging market 2",
    "Remote-friendly area 3"
  ],
  "growth_outlook": "Overall market growth and future prospects",
  "key_insights": [
    "Insight 1 about market dynamics",
    "Insight 2 about skill demand",
    "Insight 3 about career progression"
  ]
}}

Focus on:
- Current market conditions and hiring trends
- Skills that complement the given role/skill
- Tools and technologies in high demand
- Realistic salary expectations by experience level
- Emerging trends and future outlook
- Valuable certifications and credentials
- Geographic regions with opportunities
- Actionable insights for career development

Be specific, data-driven, and provide actionable recommendations.
"""
    
    def get_career_assistant_prompt(self) -> str:
        """Get the career assistant prompt template"""
        return """
You are an AI Career Coach and mentor.

User Context:
- Skills: {user_skills}
- Experience Level: {experience_level}
- Career Goals: {career_goals}

User Query: {user_query}

Respond as a helpful career coach. Provide:

1. **Direct Answer**: Address their specific question
2. **Actionable Advice**: Concrete next steps they can take
3. **Resource Suggestions**: Specific learning resources, courses, or tools
4. **Career Insights**: Relevant market information or trends
5. **Motivation**: Encouraging and supportive tone

Keep responses:
- Concise but comprehensive
- Structured with bullet points when helpful
- Specific and actionable
- Motivating and supportive
- Based on their current skill level and goals

If they ask about:
- **Role recommendations**: Suggest specific roles with readiness assessment
- **Skill development**: Provide learning paths and resources
- **Interview prep**: Give targeted advice and practice suggestions
- **Portfolio projects**: Suggest relevant projects to build
- **Career roadmaps**: Create step-by-step progression plans
- **Salary negotiation**: Provide market-based guidance

Always be encouraging, specific, and focus on their growth potential.
"""
    
    def validate_config(self) -> bool:
        """Validate Gemini configuration"""
        if not self.api_key:
            print("❌ GEMINI_API_KEY environment variable is required")
            return False
        
        if not self.model_name:
            print("❌ GEMINI_MODEL environment variable is required")
            return False
        
        return True
    
    def get_connection_info(self) -> Dict[str, str]:
        """Get connection information for debugging"""
        return {
            'api_key_set': 'Yes' if self.api_key else 'No',
            'model': self.model_name,
            'max_tokens': str(self.max_tokens),
            'temperature': str(self.temperature),
            'chunk_size': str(self.chunk_size)
        }


# Environment variable examples
ENV_EXAMPLE = """
# Google Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MAX_TOKENS=8192
GEMINI_TEMPERATURE=0.7
GEMINI_CHUNK_SIZE=30000
"""


def get_gemini_config() -> GeminiConfig:
    """Get Gemini configuration instance"""
    return GeminiConfig()


if __name__ == "__main__":
    # Test configuration
    config = get_gemini_config()
    
    print("Google Gemini AI Configuration:")
    print("=" * 40)
    
    connection_info = config.get_connection_info()
    for key, value in connection_info.items():
        print(f"{key}: {value}")
    
    print(f"\nConfiguration valid: {config.validate_config()}")
    
    print("\nEnvironment Variables Example:")
    print(ENV_EXAMPLE)
