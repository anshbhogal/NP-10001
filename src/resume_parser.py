"""
Resume Parser Module (simplified)
Now focuses solely on extracting skills from resume PDFs using PyMuPDF and spaCy.
"""

import fitz  # PyMuPDF
import spacy
import re
from spacy.matcher import PhraseMatcher
from typing import List
import os
import sys

# For DOCX support
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Add src directory to path for imports
sys.path.append(os.path.dirname(__file__))
from gemini_client import get_gemini_client  # kept for backward compatibility if imported elsewhere


class ResumeParser:
    def __init__(self, skill_list: List[str] = None):
        """Initialize the resume parser with a skill dictionary (skills only)."""
        self.skill_list = skill_list or self._get_default_skills()
        self.nlp = None
        self.matcher = None
        self._load_spacy_model()
        self._setup_matcher()
    
    def _get_default_skills(self) -> List[str]:
        """Default skill dictionary for matching"""
        return [
            "Python", "Java", "JavaScript", "C++", "C#", "R", "SQL", "HTML", "CSS",
            "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Matplotlib",
            "Machine Learning", "Deep Learning", "Data Analysis", "Data Science",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "Linux",
            "React", "Node.js", "Django", "Flask", "Spring Boot", "Express.js",
            "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch",
            "Excel", "Tableau", "Power BI", "Jupyter", "Apache Spark",
            "NLP", "Computer Vision", "Statistics", "A/B Testing", "Agile", "Scrum"
        ]
    
    def _load_spacy_model(self):
        """Load spaCy model for NLP processing"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("WARNING: spaCy model 'en_core_web_sm' not found. Please install it with:")
            print("python -m spacy download en_core_web_sm")
            # Fallback to basic model
            self.nlp = spacy.blank("en")
    
    def _setup_matcher(self):
        """Setup phrase matcher for skill extraction"""
        if self.nlp and hasattr(self.nlp, 'vocab'):
            self.matcher = PhraseMatcher(self.nlp.vocab)
            patterns = [self.nlp.make_doc(skill) for skill in self.skill_list]
            self.matcher.add("SKILLS", patterns)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"ERROR: Error extracting text from {pdf_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """
        Extract text from DOCX file
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            Extracted text as string
        """
        if not DOCX_AVAILABLE:
            print("ERROR: python-docx not installed. Install with: pip install python-docx")
            return ""
        
        try:
            doc = Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"ERROR: Error extracting text from {docx_path}: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from PDF or DOCX file based on file extension
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text as string
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            return self.extract_text_from_docx(file_path)
        else:
            print(f"ERROR: Unsupported file format: {file_ext}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text by removing extra whitespace and formatting."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        return text.strip()
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract and normalize unique skills from text using phrase matching."""
        if not self.nlp or not self.matcher:
            return []
        try:
            doc = self.nlp(text)
            matches = self.matcher(doc)
            found = [doc[start:end].text.strip().lower() for _mid, start, end in matches]
            # Normalize: lowercase, strip, deduplicate while preserving order
            seen = set()
            unique_ordered: List[str] = []
            for skill in found:
                if not skill:
                    continue
                if skill not in seen:
                    seen.add(skill)
                    unique_ordered.append(skill)
            return unique_ordered
        except Exception as e:
            print(f"ERROR: Error extracting skills: {e}")
            return []
    
    # Removed education extraction; parser now focuses only on skills
    
    # Removed experience extraction; parser now focuses only on skills
    
    def parse_resume(self, file_path: str) -> List[str]:
        """Extract and return unique normalized skills from a PDF or DOCX resume."""
        if not os.path.exists(file_path):
            return []
        raw_text = self.extract_text_from_file(file_path)
        if not raw_text:
            return []
        cleaned_text = self.clean_text(raw_text)
        return self.extract_skills(cleaned_text)
    
    def parse_resume_detailed(self, file_path: str) -> dict:
        """Parse resume and return detailed analysis in the old format for backward compatibility."""
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        try:
            # Extract text and skills
            raw_text = self.extract_text_from_file(file_path)
            if not raw_text:
                return {"error": "Could not extract text from file"}
            
            cleaned_text = self.clean_text(raw_text)
            skills = self.extract_skills(cleaned_text)
            
            # Basic analysis
            text_length = len(cleaned_text)
            skill_count = len(skills)
            
            # Simple experience detection (basic regex)
            import re
            exp_patterns = [
                r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
                r'experience\s*:?\s*(\d+)\+?\s*years?',
                r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?field'
            ]
            
            experience_years = None
            for pattern in exp_patterns:
                match = re.search(pattern, cleaned_text, re.IGNORECASE)
                if match:
                    try:
                        experience_years = int(match.group(1))
                        break
                    except (ValueError, IndexError):
                        continue
            
            # Try to get AI analysis if Gemini is available
            ai_analysis = None
            try:
                from gemini_client import get_gemini_client
                client = get_gemini_client()
                if client:
                    ai_analysis = client.analyze_resume(cleaned_text)
            except Exception as e:
                print(f"AI analysis not available: {e}")
            
            return {
                "skills": skills,
                "skill_count": skill_count,
                "text_length": text_length,
                "experience_years": experience_years,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "ai_analysis": ai_analysis
            }
            
        except Exception as e:
            return {"error": f"Parsing failed: {str(e)}"}


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Standalone function for simple text extraction from PDF
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    parser = ResumeParser()
    return parser.extract_text_from_pdf(pdf_path)


def extract_text_from_file(file_path: str) -> str:
    """
    Standalone function for simple text extraction from PDF or DOCX
    
    Args:
        file_path: Path to file
        
    Returns:
        Extracted text as string
    """
    parser = ResumeParser()
    return parser.extract_text_from_file(file_path)


def extract_skills(text: str, skill_list: List[str] = None) -> List[str]:
    """
    Standalone function for skill extraction
    
    Args:
        text: Text to extract skills from
        skill_list: Custom skill list (optional)
        
    Returns:
        List of found skills
    """
    parser = ResumeParser(skill_list)
    return parser.extract_skills(text)


if __name__ == "__main__":
    # Test the parser
    parser = ResumeParser()
    print("Resume Parser initialized successfully")
    print(f"Default skills dictionary: {len(parser.skill_list)} skills")
