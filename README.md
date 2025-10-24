# 🚀 AI Career & Skill Gap Analyzer

A comprehensive, **practical and deployable** career development platform powered by Google Gemini AI, built with Streamlit. Analyze resumes, explore job markets, and get personalized career guidance with seamless module integration.

## ✨ Enhanced Features

### 📄 Smart Resume Analysis
- **Multi-format Support**: Upload PDF and DOCX resumes
- **AI-Powered Analysis**: Gemini-powered resume evaluation with real feedback
- **Job Matching**: Compare resume against job descriptions with ATS scoring
- **Enhanced Summary Generator**: AI-generated professional resume summaries
- **Skill Extraction**: Automatic skill detection and categorization
- **LinkedIn Integration**: Direct job search with extracted skills
- **Module Integration**: Auto-feed skills to Career Assistant and Job Market Analysis

### 📊 Actionable Job Market Analysis
- **Real-time Insights**: 30,000+ job records with current market trends
- **Personalized Analysis**: Your Skills Analysis tab with career fit scoring
- **Salary Analysis**: Entry/Mid/Senior level salary expectations by region
- **Industry Trends**: Top hiring industries and growth sectors
- **Skill-Demand Graphs**: Visual analysis of in-demand skills
- **Geographic Opportunities**: High-demand regions and remote work trends
- **Certification Guidance**: Valuable credentials mapped to your skills

### 🤖 AI-Powered Career Assistant
- **Conversational Interface**: Interactive chat with memory and context retention
- **Career Fit Test**: Rate your skills vs trending roles with scoring
- **Learning Roadmap**: Generate detailed learning paths with resources
- **Portfolio Generator**: Suggest GitHub project ideas based on chosen roles
- **Personalized Guidance**: Context-aware responses based on your resume analysis
- **Module Integration**: Auto-load skills from Resume Analysis
- **Quick Actions**: Pre-built prompts for common career questions

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Google Gemini AI
- **Document Processing**: PyMuPDF, python-docx
- **NLP**: spaCy
- **Visualization**: Plotly
- **Language**: Python 3.8+

## 📁 Project Structure

```
5th_sem_project/
├── app/
│   ├── app.py                    # Main navigation page
│   └── pages/
│       ├── resume_analysis.py    # Enhanced resume analysis module
│       ├── job_market_analysis.py # Actionable job market analysis
│       └── career_assistant.py   # AI-powered career assistant
├── config/
│   └── gemini_config.py         # Gemini AI configuration
├── src/
│   ├── gemini_client.py         # Enhanced Gemini AI client
│   ├── resume_parser.py         # Resume parsing utilities
│   ├── job_market_analyzer.py   # Job market data analysis
│   └── shared_data.py           # Module integration and data sharing
├── data/                        # Analysis results and sample data
├── dataset/                     # Job market datasets (30,000+ records)
├── .streamlit/                  # Streamlit configuration
│   └── config.toml             # App configuration
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container deployment
├── docker-compose.yml          # Multi-service deployment
├── DEPLOYMENT.md               # Comprehensive deployment guide
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Set Up Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run the Application
```bash
streamlit run app/app.py
```

### 4. Access the Platform
Open your browser to `http://localhost:8501` and experience the integrated workflow:

1. **📄 Start with Resume Analysis**: Upload your resume to extract skills
2. **📊 Explore Job Market**: Use extracted skills for personalized market analysis
3. **🤖 Get Career Guidance**: Chat with AI assistant using your profile data

## 🐳 Docker Deployment

### Quick Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8501
```

### Production Deployment
```bash
# With reverse proxy
docker-compose --profile production up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment options.

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_MAX_TOKENS=8192
GEMINI_TEMPERATURE=0.7
```

### Dependencies
Key packages include:
- `streamlit` - Web application framework
- `google-generativeai` - Gemini AI integration
- `PyMuPDF` - PDF processing
- `python-docx` - DOCX processing
- `spacy` - Natural language processing
- `plotly` - Data visualization

## 📖 Enhanced Usage Guide

### 🔄 Integrated Workflow
The platform now features seamless module integration:

1. **📄 Resume Analysis** → Extract skills and get AI feedback
2. **📊 Job Market Analysis** → Auto-analyze your skills against market data
3. **🤖 Career Assistant** → Get personalized guidance with your profile

### 📄 Smart Resume Analysis
1. Upload your resume (PDF or DOCX)
2. Get instant AI-powered feedback and skill extraction
3. Generate enhanced professional summary
4. Compare against job descriptions with ATS scoring
5. **Auto-connect** to other modules with extracted data

### 📊 Actionable Job Market Analysis
1. **Your Skills Analysis** tab shows personalized insights
2. View career fit score and job opportunities for your skills
3. Get recommendations for high-demand skills to learn
4. Explore salary trends and geographic opportunities
5. Find relevant certifications for your skill set

### 🤖 AI-Powered Career Assistant
1. **Auto-load skills** from Resume Analysis
2. Take Career Fit Test for market readiness assessment
3. Get Learning Roadmap with specific resources
4. Generate Portfolio project ideas
5. Chat with context-aware AI coach

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation above
2. Review the error messages in the application
3. Ensure your Gemini API key is correctly set
4. Verify all dependencies are installed

## 🎯 What's New in This Version

### ✅ Phase 1: Core Improvements (Completed)
- **Module Integration**: Seamless data flow between all three modules
- **Enhanced Resume Analysis**: AI feedback, summary generation, ATS scoring
- **Actionable Job Market Analysis**: Personalized skills analysis, career fit scoring
- **AI-Powered Career Assistant**: Career fit test, learning roadmaps, portfolio suggestions
- **Shared Data Management**: Centralized data sharing and session management

### 🚀 Phase 2: Deployment Ready (Completed)
- **Docker Support**: Complete containerization with Dockerfile and docker-compose
- **Production Configuration**: Streamlit config, environment management
- **Deployment Guide**: Comprehensive deployment documentation
- **Environment Templates**: Easy setup with env.example

### 🔮 Future Roadmap
- [ ] User authentication and profiles
- [ ] Advanced job search integration (LinkedIn, Indeed APIs)
- [ ] Career progression tracking and analytics
- [ ] Multi-language support
- [ ] Mobile-responsive design improvements
- [ ] Export functionality for analysis results
- [ ] Real-time job alerts and notifications
- [ ] Advanced AI model fine-tuning

## 🏆 Key Achievements

- **30,000+ Job Records**: Real market data for accurate insights
- **AI Integration**: Full Gemini AI integration with error handling
- **Module Connectivity**: Skills flow seamlessly between modules
- **Production Ready**: Docker deployment with comprehensive documentation
- **User Experience**: Intuitive workflow with clear navigation

---

**Built with ❤️ using Google Gemini AI and Streamlit - Now Practical & Deployable!**