# Lawdit - Legal Due Diligence Intelligence Tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered legal risk analysis system for comprehensive due diligence. Lawdit automates the processing and analysis of legal documents from Google Drive, providing intelligent insights for legal professionals.

## Features

- **Automated Document Indexing**: Process entire Google Drive folders of legal documents
- **Vision-Based Analysis**: Extract information from PDFs using advanced vision AI
- **Hierarchical Summarization**: Page-level, document-level, and index-level summaries
- **Multi-Agent Analysis**: Specialized AI agents for different legal domains
- **Professional Deliverables**: Generate Word reports and interactive dashboards
- **Cost-Optimized**: Smart model selection to minimize API costs

## Architecture

Lawdit consists of two main components:

### 1. Data Room Indexer
Processes raw documents from Google Drive into structured indexes:
- Downloads PDFs and exports Google Docs/Sheets/Slides
- Converts pages to images for vision analysis
- Generates hierarchical summaries (page → document → index)
- Categorizes documents by type (contracts, regulatory, financial, etc.)

### 2. Legal Analysis Agents
Multi-agent system for comprehensive risk analysis:
- **Main Agent**: Coordinates analysis and synthesizes findings
- **Document Analyst**: Retrieves and analyzes specific documents
- **Deliverable Creator**: Generates professional reports and dashboards

## Installation

### Prerequisites

- Python 3.10 or higher
- [poppler-utils](https://poppler.freedesktop.org/) for PDF processing
- Google Cloud credentials with Drive API access
- OpenAI API key

### Install poppler-utils

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

**Windows:**
Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases)

### Install Lawdit

**From source (recommended for development):**
```bash
# Clone the repository
git clone https://github.com/yourusername/lawdit.git
cd lawdit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
make install-dev

# Or manually:
pip install -e ".[dev]"
```

**Quick install:**
```bash
pip install -e .
```

## Quick Start

### 1. Configure Environment

Create a `.env` file from the template:
```bash
make setup-env
# Or manually:
cp .env.example .env
```

Edit `.env` with your credentials:
```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CREDENTIALS_PATH=path/to/google-credentials.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
```

### 2. Build a Data Room Index

```bash
# Using the CLI
lawdit-index \
  --credentials ./google-credentials.json \
  --folder-id YOUR_FOLDER_ID \
  --output ./data_room_index.txt

# Or using Make
make index
```

### 3. Run Legal Analysis

```bash
# Using the CLI
lawdit-analyze --index ./data_room_index.txt

# Or using Make
make analyze
```

## Usage Examples

### Python API

```python
from lawdit import DataRoomIndexer

# Initialize the indexer
indexer = DataRoomIndexer(
    google_credentials_path="./google-credentials.json",
    openai_api_key="your-api-key",
    working_dir="./data_room_processing"
)

# Build the index
index_text = indexer.build_data_room_index(
    folder_id="YOUR_FOLDER_ID",
    output_path="./data_room_index.txt"
)

print("Index created successfully!")
```

### Command Line

```bash
# Index a data room
lawdit-index \
  --credentials ./credentials.json \
  --folder-id 1abc...xyz \
  --output ./index.txt \
  --working-dir ./processing

# Analyze with specific focus
lawdit-analyze \
  --index ./index.txt \
  --focus contracts regulatory \
  --output-dir ./outputs
```

## Project Structure

```
lawdit/
├── src/lawdit/           # Main package
│   ├── indexer/          # Data room indexing
│   │   ├── google_drive_client.py
│   │   ├── pdf_processor.py
│   │   ├── vision_summarizer.py
│   │   ├── data_room_indexer.py
│   │   └── cli.py
│   ├── agents/           # Analysis agents
│   │   └── cli.py
│   ├── tools/            # Custom tools
│   ├── utils/            # Utilities
│   └── config.py         # Configuration
├── tests/                # Test suite
├── data_room_processing/ # Working directory (gitignored)
├── outputs/              # Analysis outputs (gitignored)
├── Makefile              # Build automation
├── pyproject.toml        # Package configuration
└── README.md             # This file
```

## Development

### Setup Development Environment

```bash
make setup
```

This will:
- Install development dependencies
- Create `.env` from template
- Set up pre-commit hooks (if configured)

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests without coverage (faster)
make test-fast
```

### Code Quality

```bash
# Format code
make format

# Check formatting
make format-check

# Run linters
make lint

# Run all CI checks
make ci
```

### Available Make Commands

```bash
make help  # Show all available commands
```

## Docker Support

### Build Image

```bash
make docker-build
```

### Run Container

```bash
make docker-run
```

Or manually:
```bash
docker run -it --rm \
  -v $(pwd)/data_room_processing:/app/data_room_processing \
  -v $(pwd)/outputs:/app/outputs \
  --env-file .env \
  lawdit:latest
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options:

- `OPENAI_API_KEY`: OpenAI API key (required)
- `GOOGLE_CREDENTIALS_PATH`: Path to Google credentials
- `GOOGLE_DRIVE_FOLDER_ID`: Folder ID to process
- `PDF_DPI`: Image quality (72-600, default: 200)
- `VISION_MODEL`: Model for vision tasks
- `ANALYSIS_MODEL`: Model for analysis tasks

### Advanced Configuration

Edit `src/lawdit/config.py` for programmatic configuration or use the Settings class:

```python
from lawdit.config import get_settings

settings = get_settings()
settings.pdf_dpi = 300  # Higher quality
settings.max_parallel_processes = 8  # More parallelism
```

## Cost Optimization

- **DPI Settings**: Lower DPI (150-200) reduces costs significantly
- **Model Selection**: Use GPT-4-Vision for indexing, reserve premium models for analysis
- **Parallel Processing**: Process multiple pages concurrently
- **Caching**: Enable smart caching to avoid reprocessing unchanged documents

## Architecture Details

### Indexing Pipeline

1. **Download**: Fetch files from Google Drive
2. **Convert**: Export Google Docs to PDF, convert PDFs to images
3. **Analyze**: Use vision AI to summarize each page
4. **Aggregate**: Combine page summaries into document summaries
5. **Index**: Categorize and format the complete index

### Analysis Pipeline

1. **Coordinate**: Main agent reviews index and delegates tasks
2. **Retrieve**: Document analyst fetches specific documents
3. **Analyze**: Identify legal risks and compliance issues
4. **Synthesize**: Main agent creates strategic assessment
5. **Deliver**: Generate Word reports and interactive dashboards

## Troubleshooting

### Common Issues

**Import Error: pdf2image**
```bash
# Install poppler-utils (see Prerequisites)
```

**Google Auth Error**
```bash
# Ensure credentials file path is correct
# Verify service account has Drive API access
```

**OpenAI Rate Limits**
```bash
# Adjust rate limits in .env:
OPENAI_MAX_REQUESTS_PER_MINUTE=30
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters (`make ci`)
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [OpenAI GPT-4](https://openai.com/)
- Uses [LangChain](https://github.com/langchain-ai/langchain) and [LangGraph](https://github.com/langchain-ai/langgraph)
- PDF processing by [pdf2image](https://github.com/Belval/pdf2image)
- Document generation with [python-docx](https://python-docx.readthedocs.io/)

## Roadmap

- [ ] Multi-language support
- [ ] OCR for scanned documents
- [ ] Advanced risk scoring algorithms
- [ ] Integration with legal databases
- [ ] Real-time collaboration features
- [ ] Enhanced dashboard visualizations

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting guide

---

**Note**: This tool is designed to assist legal professionals but should not replace human judgment in legal matters. Always have qualified attorneys review AI-generated analyses.
