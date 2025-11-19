# Lawdit Web Interface Guide

## Overview

The Lawdit Web Interface provides a user-friendly Streamlit-based dashboard for managing legal due diligence workflows. Instead of using command-line tools, you can configure settings, index documents, run analyses, and view results through an interactive web browser.

## Features

### 🏠 Home Dashboard
- System status overview
- Quick access to all features
- Real-time progress tracking

### ⚙️ Configuration
- **API Keys Management**: Configure OpenAI and Tavily API keys
- **Google Drive Setup**: Upload credentials and set folder IDs
- **Processing Settings**: Adjust DPI, parallel processing, and rate limits
- **Model Selection**: Choose between different AI models

### 📥 Document Indexing
- Process Google Drive folders with progress tracking
- Real-time status updates during indexing
- View and manage existing indexes
- Advanced options for reprocessing

### 🔍 Legal Analysis
- Run comprehensive risk analysis on indexed documents
- Select focus areas (Contracts, Compliance, Litigation, Governance)
- Enable/disable web search for legal research
- Configure analysis depth and iterations
- Track analysis progress in real-time

### 📊 Results Visualization
- Interactive HTML dashboards
- Text-based analysis reports
- Statistical summaries with metrics
- Risk categorization and severity levels

### 📄 Reports Management
- Download Word reports (.docx)
- Download HTML dashboards
- View all generated files
- File management and organization

## Quick Start

### 1. Install Dependencies

```bash
# Make sure you're in the lawdit2 directory
cd lawdit2

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with Streamlit
pip install -e ".[dev]"

# Or update requirements
pip install -r requirements.txt
```

### 2. Launch the Web Interface

**Option A: Using the CLI command (recommended)**
```bash
lawdit-web
```

**Option B: Using the shell script**
```bash
./run_web.sh
```

**Option C: Using Make**
```bash
make web
```

**Option D: Direct Streamlit command**
```bash
streamlit run src/lawdit/web/app.py
```

### 3. Access the Interface

The web interface will automatically open in your browser at:
```
http://localhost:8501
```

If it doesn't open automatically, navigate to the URL manually.

## Configuration

### First-Time Setup

1. **Navigate to Configuration** (⚙️ Configuration page)

2. **Enter API Keys**:
   - OpenAI API Key (starts with `sk-`)
   - Tavily API Key (starts with `tvly-`)
   - Select your preferred models

3. **Configure Google Drive**:
   - Upload your `credentials.json` file
   - Enter your Google Drive Folder ID
   - Verify the credentials path

4. **Adjust Processing Settings** (optional):
   - PDF DPI (default: 200)
   - Max parallel processes (default: 4)
   - API rate limits

5. **Save Configuration**: Click the save buttons in each tab

### Finding Your Google Drive Folder ID

1. Open the folder in Google Drive
2. Look at the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
3. Copy the `FOLDER_ID_HERE` part
4. Paste it into the configuration

## Usage Workflow

### Complete Due Diligence Workflow

1. **Configure** (⚙️ Configuration)
   - Set up API keys and credentials
   - Verify configuration status shows ✅

2. **Index Documents** (📥 Index Documents)
   - Enter Google Drive Folder ID
   - Click "🚀 Start Indexing"
   - Wait for processing to complete
   - Index file will be saved automatically

3. **Run Analysis** (🔍 Analyze Documents)
   - Select the index file (auto-populated if just created)
   - Choose focus areas
   - Enable web search if desired
   - Click "🚀 Start Analysis"
   - Monitor progress in real-time

4. **View Results** (📊 View Results)
   - Browse interactive HTML dashboard
   - Read text analysis reports
   - Review statistical summaries

5. **Download Reports** (📄 Reports)
   - Download Word reports for sharing
   - Download HTML dashboards for presentations
   - Manage all output files

## Advanced Features

### Custom Model Selection

In Configuration → API Keys:
- **Vision Model**: Used for page-by-page analysis
  - `gpt-5-nano` (recommended, cost-effective)
  - `gpt-4-vision-preview`
  - `gpt-4o`

- **Analysis Model**: Used for legal risk analysis
  - `claude-sonnet-4-5-20250929` (recommended)
  - `claude-opus-4-5-20250514`
  - `gpt-4o`
  - `gpt-4-turbo`

### Processing Quality Settings

**PDF DPI Settings**:
- **72 DPI**: Lowest cost, basic quality
- **150 DPI**: Low cost, good quality ⭐
- **200 DPI**: Moderate cost, high quality ⭐ (recommended)
- **300 DPI**: High cost, very high quality
- **600 DPI**: Very high cost, maximum quality

**Performance Settings**:
- **Max Parallel Processes**: 1-16 (default: 4)
  - Higher = Faster but more memory usage
- **API Rate Limits**: Adjust based on your OpenAI tier

### Analysis Options

- **Focus Areas**: Select specific risk categories to emphasize
- **Web Search**: Enable legal precedent and regulation research
- **Max Iterations**: Control analysis depth (5-50, default: 20)
- **Deliverable Generation**: Choose Word reports and/or HTML dashboards

## Troubleshooting

### Web Interface Won't Start

**Error: "Streamlit not found"**
```bash
pip install streamlit>=1.28.0
```

**Error: "Port 8501 already in use"**
```bash
# Find and kill the process
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run src/lawdit/web/app.py --server.port=8502
```

### Configuration Issues

**"Configuration incomplete" warning**
- Check that all required fields are filled in Configuration
- Verify API keys are valid
- Ensure Google credentials file exists at specified path

**Google Auth Error**
- Verify credentials.json is valid
- Ensure service account has Google Drive API enabled
- Check folder ID is correct and accessible

### Indexing Issues

**"Failed to initialize indexer"**
- Verify Google credentials are correct
- Check internet connection
- Ensure folder ID is valid

**Processing is slow**
- Reduce PDF DPI in Configuration
- Check API rate limits
- Verify internet connection speed

### Analysis Issues

**"Index file not found"**
- Run indexing first
- Verify index file path is correct
- Check file permissions

**Analysis fails or hangs**
- Check API keys are valid and have credits
- Reduce max iterations
- Try with fewer focus areas
- Check internet connection

## Development

### Running in Development Mode

```bash
make web-dev
```

This enables auto-reload when you modify the code.

### Project Structure

```
src/lawdit/web/
├── app.py                    # Main Streamlit application
├── cli.py                    # CLI entry point
├── __init__.py
└── pages/
    ├── __init__.py
    ├── configuration.py      # Settings page
    ├── indexer.py           # Document indexing page
    ├── analyzer.py          # Analysis execution page
    ├── results.py           # Results visualization page
    └── reports.py           # Reports management page
```

### Customization

You can customize the web interface by editing:
- **Styling**: Modify CSS in `app.py`
- **Pages**: Edit individual page files in `pages/`
- **Configuration**: Extend `configuration.py`
- **Visualizations**: Enhance `results.py`

## Production Deployment

### Docker Deployment

```bash
# Build image with web interface
docker build -t lawdit-web:latest .

# Run with web interface exposed
docker run -p 8501:8501 \
  -v $(pwd)/data_room_processing:/app/data_room_processing \
  -v $(pwd)/outputs:/app/outputs \
  --env-file .env \
  lawdit-web:latest \
  lawdit-web
```

### Cloud Deployment

The Streamlit app can be deployed to:
- **Streamlit Cloud**: Free hosting for Streamlit apps
- **Heroku**: With Docker container
- **AWS ECS/Fargate**: Production container hosting
- **Google Cloud Run**: Serverless container hosting
- **Azure Container Instances**: Cloud container hosting

## Security Considerations

- **API Keys**: Never commit `.env` to version control
- **Credentials**: Store Google credentials securely
- **Access Control**: Run on localhost or use authentication
- **HTTPS**: Use reverse proxy (nginx) for production
- **Rate Limiting**: Configure appropriate API limits

## Support

For issues with the web interface:
1. Check this guide first
2. Review the main README.md
3. Check logs in the browser console (F12)
4. Create an issue on GitHub

## Tips and Best Practices

1. **Start Small**: Index a small folder first to test the setup
2. **Monitor Costs**: Watch API usage in your OpenAI dashboard
3. **Save Configurations**: Download your `.env` as backup
4. **Regular Backups**: Export reports regularly
5. **Use Appropriate DPI**: Don't use 600 DPI unless necessary
6. **Enable Web Search**: For better legal context and precedents
7. **Review Results**: Always have legal professionals review AI analysis

## Keyboard Shortcuts

- **Ctrl+C**: Stop the web server (in terminal)
- **Ctrl+R** or **F5**: Refresh the page
- **Ctrl+Shift+R**: Rerun the Streamlit app
- **F12**: Open browser developer tools

## What's Next?

- [ ] User authentication and multi-user support
- [ ] Database integration for result storage
- [ ] Real-time collaboration features
- [ ] Advanced visualization with Chart.js/D3.js
- [ ] Export to additional formats (PDF, Excel)
- [ ] Scheduled analysis jobs
- [ ] Email notifications
- [ ] API endpoint exposure for integrations

---

**Ready to get started?** Run `lawdit-web` and navigate to http://localhost:8501!
