# 🏛️ Hange AI - Estonian Procurement Intelligence Platform

AI-powered procurement search platform for the Estonian market with intelligent document processing, email notifications, and automated form filling capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 18+ (for UI components)
- Git

## 📦 Installation & Deployment

### 1. Streamlit Application (Main Platform)

#### Local Development

```bash
# Clone the repository
git clone https://github.com/kaljuvee/hange.git
cd hange

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key:
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_MODEL=gpt-4.1-mini

# Run the application
streamlit run Home.py
```

The application will be available at `http://localhost:8501`

#### Production Deployment

##### Option 1: Render.com (Recommended)

1. **Connect Repository**:
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Select "Web Service"

2. **Configuration**:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run Home.py --server.port $PORT --server.address 0.0.0.0
   Environment: Python 3
   ```

3. **Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4.1-mini
   ```

##### Option 2: Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set main file path: `Home.py`
4. Add secrets in Streamlit Cloud dashboard:
   ```toml
   [secrets]
   OPENAI_API_KEY = "your_openai_api_key_here"
   OPENAI_MODEL = "gpt-4.1-mini"
   ```

##### Option 3: Heroku

```bash
# Install Heroku CLI and login
heroku create your-app-name

# Create Procfile
echo "web: streamlit run Home.py --server.port \$PORT --server.address 0.0.0.0" > Procfile

# Set environment variables
heroku config:set OPENAI_API_KEY=your_openai_api_key_here
heroku config:set OPENAI_MODEL=gpt-4.1-mini

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

##### Option 4: Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

```bash
# Build and run
docker build -t hange-ai .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key hange-ai
```

### 2. Next.js Landing Page (UI)

**Framework**: Next.js 15 + TypeScript + Tailwind CSS  
**Location**: `ui/web-ui/`

#### Local Development

```bash
# Navigate to UI directory
cd ui/web-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

The landing page will be available at `http://localhost:3000`

#### Production Deployment

##### Option 1: Deploy to Vercel (Recommended)

1. **Visit vercel.com**
2. **Connect your GitHub account**
3. **Import the repository**
4. **Set the Root Directory to `ui/web-ui`**
5. **Deploy automatically**

**Custom Domain (Optional)**:
- Add your custom domain in Vercel dashboard
- Update DNS settings as instructed

##### Option 2: Deploy to Netlify

1. **Build the application**:
   ```bash
   cd web-ui
   npm install
   npm run build
   ```

2. **Deploy to Netlify**:
   - Visit netlify.com
   - Drag and drop the `web-ui/out` folder (after running `npm run build`)
   - **Or connect your GitHub repository**:
     - Set **Base directory** to `web-ui`
     - Set **Build command** to `npm run build`
     - Set **Publish directory** to `web-ui/out`

##### Option 3: Render.com (Static Site)

```bash
# Connect GitHub repository
# Service type: Static Site
# Root Directory: web-ui
# Build command: npm run build
# Publish directory: out
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini

# Optional: Database Configuration (uses SQLite by default)
DATABASE_URL=sqlite:///./procurement.db

# Optional: Email Configuration (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#3b82f6"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
textColor = "#1f2937"
```

## 🏗️ Project Structure

```
hange/
├── 📁 pages/                    # Streamlit pages
│   ├── 1_🔍_Search_Browse.py   # Advanced search & filtering
│   ├── 2_📄_Documents.py       # AI document processing
│   └── 3_📧_Email_Notifications.py # Email subscription system
├── 📁 tests/                   # Test suite
│   ├── test_enhanced_extraction.py
│   └── test_document_extraction.py
├── 📁 test-data/              # Sample data for testing
│   ├── sample_procurement_data.json
│   ├── extracted_fields_sample.csv
│   └── enhanced_test_results_*.json
├── 📁 web-ui/                 # Next.js Landing Page (Production Ready)
│   ├── src/app/               # Next.js app directory
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── DEPLOYMENT_INSTRUCTIONS.md # Deployment guide
├── 📄 Home.py                 # Main Streamlit application
├── 📄 enhanced_document_processor.py # AI document processing
├── 📄 requirements.txt        # Python dependencies
├── 📄 .env                    # Environment variables
└── 📄 README.md              # This file
```

## 🚀 Features

### Streamlit Application
- **🔍 Intelligent Search**: AI-powered procurement discovery with real-time RSS feed
- **📄 Document Processing**: OpenAI-powered form field extraction (90% confidence)
- **📧 Email Notifications**: Personalized alerts with sector-based filtering
- **📊 Analytics Dashboard**: Interactive charts and procurement statistics
- **🎯 AI Classification**: Automatic categorization of procurement types

### UI Components
- **🌐 Bilingual Support**: Estonian (default) and English versions
- **📱 Responsive Design**: Mobile and desktop optimized
- **🎨 Modern UI**: Professional design with Tailwind CSS
- **⚡ Fast Performance**: Optimized builds with Vite/Next.js

## 🔧 Troubleshooting

### Common Deployment Issues

#### 1. SQLite3 Error
```
ERROR: No matching distribution found for sqlite3
```
**Solution**: Remove `sqlite3` from `requirements.txt` (it's built into Python)

#### 2. OpenAI API Key Issues
```
openai.AuthenticationError: Incorrect API key provided
```
**Solution**: 
- Verify your OpenAI API key in environment variables
- Ensure the key has sufficient credits
- Check the model name is correct (`gpt-4.1-mini`)

#### 3. Streamlit Port Issues
```
Port 8501 is already in use
```
**Solution**: 
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or use a different port
streamlit run Home.py --server.port 8502
```

#### 4. Memory Issues on Render/Heroku
**Solution**: Add to your deployment configuration:
```bash
# For Render: increase instance size
# For Heroku: upgrade dyno type or add swap
```

#### 5. Build Timeout Issues
**Solution**: 
- Remove large files from repository
- Use `.gitignore` to exclude `node_modules/`, `__pycache__/`, etc.
- Optimize Docker builds with multi-stage builds

### Performance Optimization

#### Streamlit Caching
```python
# Use Streamlit caching for expensive operations
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_procurement_data():
    # Expensive data loading
    pass
```

#### UI Optimization
```bash
# Optimize bundle size
npm run build -- --analyze

# Use environment-specific builds
NODE_ENV=production npm run build
```

## 📚 API Documentation

### Document Processing API

```python
from enhanced_document_processor import EnhancedDocumentProcessor

# Initialize processor
processor = EnhancedDocumentProcessor()

# Process document
analysis = processor.process_document("path/to/document.docx")

# Access results
print(f"Confidence: {analysis.confidence_score:.2%}")
print(f"Fields extracted: {len(analysis.form_fields)}")
```

### Procurement Data API

```python
import feedparser

# Load Estonian procurement RSS feed
feed = feedparser.parse('https://riigihanked.riik.ee/rhr/api/public/v1/rss')

# Process entries
for entry in feed.entries:
    print(f"Title: {entry.title}")
    print(f"Link: {entry.link}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/kaljuvee/hange/issues)
- **Documentation**: This README and inline code comments
- **Email**: Contact repository maintainers

## 🔄 Updates

### Latest Version Features
- ✅ Enhanced document processing with 90% confidence scores
- ✅ Production-ready caching system (10x performance improvement)
- ✅ Quality assurance with validation rules
- ✅ Professional UI with gradient design
- ✅ Comprehensive testing framework
- ✅ Multi-deployment options (Render, Streamlit Cloud, Heroku, Docker)

---

**🏛️ Hange AI** - Revolutionizing Estonian Public Procurement with AI

*Last updated: September 4, 2025*

