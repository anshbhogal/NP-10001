# AI Career & Skill Gap Analyzer - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Gemini API Key
- Docker (optional, for containerized deployment)

### 1. Local Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd 5th_sem_project

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Set up environment variables
cp env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the application
streamlit run app/app.py
```

### 2. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t career-analyzer .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key_here career-analyzer
```

### 3. Production Deployment

#### Option A: Cloud Platforms (Heroku, Railway, etc.)

1. **Heroku Deployment:**
```bash
# Install Heroku CLI
# Create Procfile
echo "web: streamlit run app/app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_key_here
git push heroku main
```

2. **Railway Deployment:**
```bash
# Connect your GitHub repo to Railway
# Set environment variables in Railway dashboard
# Deploy automatically on push
```

#### Option B: VPS/Server Deployment

```bash
# On your server
git clone <your-repo-url>
cd 5th_sem_project

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Set up systemd service
sudo nano /etc/systemd/system/career-analyzer.service
```

**Service file content:**
```ini
[Unit]
Description=AI Career Analyzer
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/5th_sem_project
Environment=PATH=/path/to/5th_sem_project/venv/bin
ExecStart=/path/to/5th_sem_project/venv/bin/streamlit run app/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable career-analyzer
sudo systemctl start career-analyzer
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | - |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.5-flash` |
| `GEMINI_MAX_TOKENS` | Maximum tokens per request | `8192` |
| `GEMINI_TEMPERATURE` | AI response creativity | `0.7` |
| `DEBUG` | Enable debug mode | `false` |

### Streamlit Configuration

The app uses `.streamlit/config.toml` for configuration:
- Theme colors and fonts
- Server settings
- Logging levels

## 📊 Data Management

### Dataset Files
- `dataset/ai_job_dataset.csv` - Main job market data
- `dataset/ai_job_dataset1.csv` - Additional job data
- `data/analysis_results.db` - SQLite database for results

### File Uploads
- Resume files are processed temporarily and not stored
- All analysis results are stored in session state

## 🔒 Security Considerations

1. **API Keys:** Never commit API keys to version control
2. **File Uploads:** Resume files are processed in memory only
3. **CORS:** Configured for local development
4. **Rate Limiting:** Consider implementing for production

## 🐛 Troubleshooting

### Common Issues

1. **spaCy Model Not Found:**
```bash
python -m spacy download en_core_web_sm
```

2. **Gemini API Errors:**
- Check API key validity
- Verify API quotas
- Check network connectivity

3. **Port Already in Use:**
```bash
# Find process using port 8501
lsof -i :8501
# Kill process or use different port
streamlit run app/app.py --server.port=8502
```

4. **Memory Issues:**
- Reduce dataset size for testing
- Increase Docker memory limits
- Use smaller spaCy model

### Logs and Debugging

```bash
# Enable debug mode
export DEBUG=true
streamlit run app/app.py

# Check logs
tail -f ~/.streamlit/logs/streamlit.log
```

## 📈 Performance Optimization

### For Production:

1. **Caching:**
   - Streamlit's `@st.cache_data` is used for expensive operations
   - Consider Redis for distributed caching

2. **Database:**
   - Current SQLite is fine for small deployments
   - Consider PostgreSQL for larger scale

3. **CDN:**
   - Use CloudFlare or similar for static assets
   - Enable gzip compression

4. **Monitoring:**
   - Add health check endpoints
   - Monitor API usage and costs
   - Set up error tracking (Sentry)

## 🔄 Updates and Maintenance

### Updating the Application:
```bash
git pull origin main
pip install -r requirements.txt
# Restart service
sudo systemctl restart career-analyzer
```

### Backup Strategy:
- Regular database backups
- Environment variable backups
- Code repository backups

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Create an issue in the repository
4. Contact the development team

## 🎯 Next Steps

After successful deployment:
1. Set up monitoring and alerts
2. Configure custom domain (if needed)
3. Set up SSL certificates
4. Implement user authentication (if required)
5. Add analytics and usage tracking
