# Lawdit Usage Guide

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [First-Time Setup](#first-time-setup)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Detailed Workflows](#detailed-workflows)
  - [Workflow 1: Setting Up Your Environment](#workflow-1-setting-up-your-environment)
  - [Workflow 2: Indexing Your Data Room](#workflow-2-indexing-your-data-room)
  - [Workflow 3: Running Legal Analysis](#workflow-3-running-legal-analysis)
  - [Workflow 4: Understanding Your Results](#workflow-4-understanding-your-results)
- [Common Use Cases](#common-use-cases)
- [Best Practices](#best-practices)
- [Cost Optimization](#cost-optimization)
- [Troubleshooting](#troubleshooting)
- [Frequently Asked Questions](#frequently-asked-questions)

---

## Introduction

Lawdit is an AI-powered legal due diligence tool that helps you:
- **Analyze hundreds of legal documents** in minutes instead of days
- **Identify legal risks** across contracts, compliance, litigation, and governance
- **Generate professional reports** for stakeholders
- **Save time and money** on initial legal review

### When to Use Lawdit

✅ **Good Use Cases:**
- M&A due diligence data room analysis
- Contract portfolio risk assessment
- Regulatory compliance audits
- Corporate governance reviews
- Pre-investment legal screening

❌ **Not Suitable For:**
- Final legal opinions (always consult qualified attorneys)
- Court filings or legal briefs
- Real-time contract negotiations
- Documents requiring human judgment on complex legal matters

---

## Prerequisites

Before you start, ensure you have:

### Required Accounts
1. **OpenAI Account** with API access
   - Sign up at https://platform.openai.com/
   - Add billing information (required for API access)
   - Generate an API key

2. **Tavily Account** (for legal research)
   - Sign up at https://tavily.com/
   - Get your API key from the dashboard

3. **Google Cloud Project** (for Google Drive access)
   - Create a project at https://console.cloud.google.com/
   - Enable Google Drive API
   - Create a service account
   - Download credentials JSON file

### System Requirements
- **Python 3.10 or higher**
- **poppler-utils** (for PDF processing)
- **4GB RAM minimum** (8GB+ recommended)
- **Stable internet connection**

---

## First-Time Setup

### Step 1: Install Lawdit

```bash
# Clone the repository
git clone https://github.com/yourusername/lawdit.git
cd lawdit

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Step 2: Install poppler-utils

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
1. Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases)
2. Extract to `C:\Program Files\poppler`
3. Add `C:\Program Files\poppler\bin` to PATH

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

Add your credentials:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
TAVILY_API_KEY=tvly-your-tavily-api-key-here
GOOGLE_CREDENTIALS_PATH=./google-credentials.json
GOOGLE_DRIVE_FOLDER_ID=your-drive-folder-id
```

### Step 4: Set Up Google Drive

1. **Get Your Folder ID:**
   - Open the folder in Google Drive
   - Look at the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
   - Copy the `FOLDER_ID_HERE` part

2. **Share Folder with Service Account:**
   - Open your `google-credentials.json`
   - Find the `client_email` field (e.g., `lawdit@project.iam.gserviceaccount.com`)
   - In Google Drive, share the folder with this email address
   - Grant "Viewer" or "Editor" access

### Step 5: Verify Setup

```bash
# Test that everything is installed correctly
python -c "import lawdit; print('✓ Lawdit installed')"
python -c "import pdf2image; print('✓ PDF processing ready')"

# Check environment variables
python -c "from lawdit.config import get_settings; s = get_settings(); print(f'✓ Config loaded: OpenAI={bool(s.openai_api_key)}, Tavily={bool(s.tavily_api_key)}')"
```

---

## Quick Start (5 Minutes)

The fastest way to get results:

### Option 1: Web Interface (Recommended)

```bash
# Launch web interface
lawdit-web

# Navigate to http://localhost:8501
# Follow the on-screen instructions
```

### Option 2: Command Line

```bash
# 1. Index your documents (takes 5-15 minutes for ~50 documents)
lawdit-index \
  --credentials ./google-credentials.json \
  --folder-id YOUR_FOLDER_ID \
  --output ./data_room_index.txt

# 2. Run analysis (takes 10-30 minutes depending on complexity)
lawdit-analyze --index ./data_room_index.txt

# 3. View results
open ./outputs/legal_risk_analysis_report.docx  # macOS
xdg-open ./outputs/legal_risk_analysis_report.docx  # Linux
start ./outputs/legal_risk_analysis_report.docx  # Windows
```

---

## Detailed Workflows

### Workflow 1: Setting Up Your Environment

#### Using Web Interface

1. **Launch Lawdit:**
   ```bash
   lawdit-web
   ```

2. **Navigate to Configuration (⚙️):**
   - Click on "⚙️ Configuration" in the sidebar

3. **Configure API Keys:**
   - Enter your OpenAI API key
   - Enter your Tavily API key
   - Select models (defaults are recommended)
   - Click "Save API Configuration"

4. **Configure Google Drive:**
   - Upload your `google-credentials.json` file
   - Enter your Google Drive Folder ID
   - Click "Save Google Drive Configuration"

5. **Adjust Processing Settings (Optional):**
   - Set PDF DPI (200 recommended)
   - Set max parallel processes (4 recommended)
   - Adjust API rate limits if needed
   - Click "Save Processing Settings"

6. **Verify Configuration:**
   - Check that all status indicators show ✅
   - If any show ❌, review the error messages

#### Using Command Line

1. **Create Configuration File:**
   ```bash
   cp .env.example .env
   ```

2. **Edit Configuration:**
   ```bash
   nano .env
   ```

   Set required values:
   ```env
   OPENAI_API_KEY=sk-...
   TAVILY_API_KEY=tvly-...
   GOOGLE_CREDENTIALS_PATH=./google-credentials.json
   GOOGLE_DRIVE_FOLDER_ID=1abc...xyz
   ```

3. **Test Configuration:**
   ```bash
   python -c "from lawdit.config import get_settings; s = get_settings(); print('Configuration loaded successfully' if s.openai_api_key else 'Error: Missing API key')"
   ```

---

### Workflow 2: Indexing Your Data Room

Indexing processes all documents in your Google Drive folder and creates a searchable index with summaries.

#### Using Web Interface

1. **Navigate to Index Documents (📥):**
   - Click "📥 Index Documents" in the sidebar

2. **Enter Folder ID:**
   - Paste your Google Drive Folder ID
   - Or keep the default if configured

3. **Configure Options (Optional):**
   - Output path (default: `./data_room_index.txt`)
   - Working directory (default: `./data_room_processing`)

4. **Start Indexing:**
   - Click "🚀 Start Indexing"
   - Watch the progress bar
   - Monitor the status messages

5. **Wait for Completion:**
   - Small folders (10-20 docs): ~5 minutes
   - Medium folders (50-100 docs): ~15-30 minutes
   - Large folders (200+ docs): 1-2 hours

6. **Review Results:**
   - Index file location will be displayed
   - Preview the index in the UI
   - Download if needed

#### Using Command Line

1. **Run Indexer:**
   ```bash
   lawdit-index \
     --credentials ./google-credentials.json \
     --folder-id YOUR_FOLDER_ID \
     --output ./data_room_index.txt \
     --working-dir ./data_room_processing
   ```

2. **Monitor Progress:**
   ```
   Processing documents: [####------] 40% (20/50 docs)
   Current: analyzing_contract_agreement_2023.pdf
   Estimated time remaining: 8 minutes
   ```

3. **Verify Index:**
   ```bash
   # Check index file was created
   ls -lh ./data_room_index.txt

   # Preview first 50 lines
   head -50 ./data_room_index.txt
   ```

#### What Happens During Indexing?

1. **Download:** Fetches files from Google Drive
2. **Convert:** Exports Google Docs to PDF, converts PDF pages to images
3. **Analyze:** Uses AI vision to summarize each page
4. **Aggregate:** Combines page summaries into document summaries
5. **Categorize:** Classifies documents by type (contracts, regulatory, etc.)
6. **Index:** Creates structured searchable index

---

### Workflow 3: Running Legal Analysis

Analysis uses specialized AI agents to identify legal risks across your data room.

#### Using Web Interface

1. **Navigate to Analyze Documents (🔍):**
   - Click "🔍 Analyze Documents" in the sidebar

2. **Select Index File:**
   - Choose your previously created index
   - Or browse to select manually

3. **Configure Analysis:**
   - **Focus Areas:** Select risk categories to emphasize
     - ✅ Contracts (indemnification, liability, IP)
     - ✅ Compliance (GDPR, regulations, policies)
     - ✅ Litigation (lawsuits, disputes, claims)
     - ✅ Governance (board docs, corporate structure)

   - **Web Search:** Enable for legal precedent research

   - **Max Iterations:** Control analysis depth (default: 20)
     - Low (5-10): Quick overview
     - Medium (15-25): Standard analysis
     - High (30-50): Deep comprehensive review

4. **Start Analysis:**
   - Click "🚀 Start Analysis"
   - Monitor real-time progress
   - Watch for agent status updates

5. **Wait for Completion:**
   - Typical time: 10-30 minutes
   - Complex data rooms: 45-90 minutes

6. **Review Completion:**
   - Check summary statistics
   - Note output file locations

#### Using Command Line

1. **Basic Analysis:**
   ```bash
   lawdit-analyze --index ./data_room_index.txt
   ```

2. **Custom Analysis:**
   ```bash
   lawdit-analyze \
     --index ./data_room_index.txt \
     --focus contracts regulatory litigation \
     --enable-web-search \
     --max-iterations 25 \
     --output-dir ./outputs
   ```

3. **Monitor Progress:**
   ```
   [Main Agent] Analyzing data room index...
   [Main Agent] Identified 47 documents across 4 categories
   [Document Analyst] Retrieving contract documents...
   [Main Agent] Found 3 critical risks, 7 high-priority risks
   [Deliverable Creator] Generating Word report...
   [Deliverable Creator] Generating HTML dashboard...
   ✓ Analysis complete!
   ```

#### What Happens During Analysis?

1. **Coordination:** Main agent reviews index and creates analysis plan
2. **Document Retrieval:** Specialist agent fetches relevant documents
3. **Risk Identification:** Analyzes documents for legal risks
4. **Evidence Gathering:** Collects supporting evidence and citations
5. **Synthesis:** Main agent creates strategic risk assessment
6. **Report Generation:** Creates Word reports and HTML dashboards

---

### Workflow 4: Understanding Your Results

#### Output Files

After analysis completes, you'll find:

```
outputs/
├── legal_risk_analysis_report.docx    # Professional Word report
├── risk_dashboard.html                # Interactive HTML dashboard
├── analysis_summary.txt               # Text summary
└── agent_logs/                        # Detailed agent logs
```

#### Word Report Structure

1. **Cover Page**
   - Report title and date
   - Data room identifier

2. **Executive Summary**
   - High-level findings
   - Risk count by severity
   - Key recommendations

3. **Risk Sections** (by category)
   - Contractual Risks
   - Regulatory & Compliance Risks
   - Litigation Risks
   - Governance Risks

4. **Individual Risk Details**
   - Risk title and severity
   - Detailed description
   - Supporting evidence
   - Impact assessment
   - Recommendations

5. **Risk Matrix Table**
   - Complete list of all identified risks
   - Severity, category, affected documents

#### HTML Dashboard Features

1. **Risk Summary Cards**
   - Total risks by severity
   - Category breakdown
   - Visual severity distribution

2. **Interactive Risk List**
   - Filter by severity (Critical, High, Medium, Low)
   - Filter by category
   - Search by keyword
   - Expand/collapse details

3. **Visualizations**
   - Risk distribution pie chart
   - Category comparison bar chart
   - Severity heatmap

#### Interpreting Severity Levels

- **Critical:** Requires immediate legal attention
  - Unlimited liability exposure
  - Major compliance violations
  - Active lawsuits with high damages

- **High:** Address within 30-90 days
  - Significant contractual gaps
  - Regulatory compliance risks
  - Material governance issues

- **Medium:** Monitor and address in next review cycle
  - Minor contractual concerns
  - Documentation gaps
  - Process improvements needed

- **Low:** Informational, no immediate action
  - Best practice recommendations
  - Administrative updates
  - Minor policy improvements

#### Next Steps After Review

1. **Share with Legal Team**
   - Distribute Word report to counsel
   - Review critical and high-priority items first

2. **Create Action Plan**
   - Assign owners to each risk
   - Set deadlines for remediation
   - Track progress

3. **Follow-Up Analysis**
   - Re-run analysis after remediation
   - Compare before/after results
   - Document improvements

---

## Common Use Cases

### Use Case 1: M&A Due Diligence

**Scenario:** You're acquiring a company and need to review their data room.

**Workflow:**
1. Request access to target company's data room
2. Get shared folder ID from seller
3. Index the data room (usually 100-500 documents)
4. Run comprehensive analysis with all focus areas enabled
5. Generate report for investment committee
6. Create red flag summary for negotiation team

**Timeline:**
- Indexing: 1-3 hours
- Analysis: 45-90 minutes
- Review: 2-4 hours
- **Total: Same day results** (vs. 1-2 weeks manual review)

**Cost Estimate:**
- 200 documents × $0.10-0.30 per doc = $20-60 indexing
- Analysis: $30-50
- **Total: $50-110** (vs. $10,000-50,000 for attorney review)

---

### Use Case 2: Contract Portfolio Assessment

**Scenario:** Review all customer contracts for liability exposure.

**Workflow:**
1. Organize all contracts in single Google Drive folder
2. Index the contract folder
3. Run analysis with focus on "contracts" only
4. Filter results for indemnification and liability risks
5. Generate report for risk management

**Advanced Filtering:**
```bash
lawdit-analyze \
  --index ./contracts_index.txt \
  --focus contracts \
  --enable-web-search \
  --output-dir ./contract_review
```

---

### Use Case 3: Regulatory Compliance Audit

**Scenario:** Verify GDPR/CCPA compliance across policies and agreements.

**Workflow:**
1. Gather privacy policies, DPAs, and related documents
2. Index the compliance folder
3. Run analysis focused on "compliance"
4. Enable web search for latest regulations
5. Generate audit report

**Best Practice:**
- Include templates and executed agreements
- Add regulatory correspondence
- Include prior audit reports

---

### Use Case 4: Litigation Risk Assessment

**Scenario:** Assess litigation exposure before fundraising.

**Workflow:**
1. Collect all litigation files, demand letters, settlements
2. Index litigation folder
3. Run analysis focused on "litigation"
4. Review for materiality thresholds
5. Prepare disclosure schedules

---

### Use Case 5: Quarterly Governance Review

**Scenario:** Regular review of board minutes and corporate records.

**Workflow:**
1. Organize board minutes, resolutions, capitalization tables
2. Index governance folder
3. Run analysis focused on "governance"
4. Identify documentation gaps
5. Create remediation checklist

---

## Best Practices

### Document Organization

✅ **Do:**
- Organize documents in logical folders
- Use clear, descriptive filenames
- Remove duplicates before indexing
- Include version numbers in filenames
- Keep executed agreements separate from drafts

❌ **Don't:**
- Mix different document types in one folder
- Use generic names like "contract1.pdf"
- Include irrelevant files
- Upload password-protected files
- Include large image-only scans without OCR

### Configuration Optimization

#### For Cost Efficiency
```env
PDF_DPI=150                    # Lower quality, faster, cheaper
VISION_MODEL=gpt-5-nano        # Most cost-effective
MAX_PARALLEL_PROCESSES=4       # Balance speed vs. cost
```

#### For Best Quality
```env
PDF_DPI=300                    # High quality
VISION_MODEL=gpt-4o            # Best accuracy
MAX_PARALLEL_PROCESSES=8       # Faster processing
```

#### For Large Data Rooms (500+ docs)
```env
PDF_DPI=200                    # Balanced
VISION_MODEL=gpt-5-nano        # Cost control
MAX_PARALLEL_PROCESSES=16      # Maximum speed
OPENAI_MAX_REQUESTS_PER_MINUTE=100  # Higher throughput
```

### Analysis Strategy

**First Pass (Quick Review):**
- Use default settings
- Enable all focus areas
- Generate initial report
- Identify major red flags (30-60 minutes)

**Second Pass (Deep Dive):**
- Focus on specific risk categories
- Enable web search
- Increase max iterations to 40-50
- Review critical items in detail (2-3 hours)

**Ongoing Monitoring:**
- Re-index quarterly
- Compare results over time
- Track remediation progress
- Update configuration as needed

### Quality Assurance

1. **Verify Index Completeness**
   ```bash
   # Count documents in index
   grep -c "^### Document:" data_room_index.txt

   # Compare to folder
   # Should match number of files
   ```

2. **Spot Check Summaries**
   - Review 5-10 random document summaries
   - Verify accuracy against source documents
   - Adjust DPI if quality is poor

3. **Validate Analysis Results**
   - Have attorney review critical risks
   - Verify evidence citations
   - Check for false positives

---

## Cost Optimization

### Understanding Costs

Lawdit uses two types of API calls:
1. **Vision API** (indexing): $0.01-0.30 per page depending on DPI
2. **Language API** (analysis): $0.01-0.05 per 1K tokens

### Cost Breakdown Example

**Scenario:** 100 documents, 10 pages each = 1,000 pages

| DPI | Cost/Page | Total Indexing | Analysis | Total |
|-----|-----------|----------------|----------|-------|
| 150 | $0.05 | $50 | $30 | $80 |
| 200 | $0.10 | $100 | $30 | $130 |
| 300 | $0.20 | $200 | $30 | $230 |
| 600 | $0.30 | $300 | $30 | $330 |

### Reduction Strategies

1. **Lower DPI for Text-Heavy Documents**
   - Contracts, policies: 150-200 DPI sufficient
   - Charts, diagrams: 300 DPI recommended

2. **Batch Processing**
   - Process related documents together
   - Reuse indexes when possible

3. **Smart Caching**
   - Don't re-index unchanged documents
   - Save and reuse indexes

4. **Model Selection**
   - Use GPT-5-nano for indexing (10x cheaper than GPT-4)
   - Use premium models only for critical analysis

5. **Focused Analysis**
   - Start with specific focus areas
   - Expand scope only if needed

### Cost Monitoring

```bash
# Check OpenAI usage
# Visit: https://platform.openai.com/usage

# Estimate before processing
python -c "
from lawdit.config import get_settings
s = get_settings()
pages = 1000  # Your estimate
cost_per_page = 0.10  # Based on DPI
print(f'Estimated cost: ${pages * cost_per_page:.2f}')
"
```

---

## Troubleshooting

### Installation Issues

**Problem:** `pdf2image` import error
```
ImportError: Unable to find pdftoppm
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Verify installation
pdftoppm -v
```

---

**Problem:** Python version error
```
ERROR: This package requires Python 3.10 or higher
```

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.10+ and create new venv
python3.10 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

---

### Configuration Issues

**Problem:** `OPENAI_API_KEY` not found

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check contents
cat .env | grep OPENAI_API_KEY

# Ensure no spaces around =
# Correct:   OPENAI_API_KEY=sk-...
# Incorrect: OPENAI_API_KEY = sk-...
```

---

**Problem:** Google Drive authentication failed

**Solution:**
1. Verify credentials file exists:
   ```bash
   cat google-credentials.json
   ```

2. Check service account email:
   ```bash
   grep client_email google-credentials.json
   ```

3. Share folder with this email in Google Drive

4. Verify folder ID is correct:
   ```bash
   # URL format: https://drive.google.com/drive/folders/FOLDER_ID
   ```

---

### Indexing Issues

**Problem:** Indexing hangs or is very slow

**Solution:**
1. Check internet connection
2. Reduce parallel processes:
   ```env
   MAX_PARALLEL_PROCESSES=2
   ```
3. Check API rate limits:
   ```env
   OPENAI_MAX_REQUESTS_PER_MINUTE=30
   ```

---

**Problem:** Out of memory errors

**Solution:**
1. Reduce DPI:
   ```env
   PDF_DPI=150
   ```

2. Reduce parallel processes:
   ```env
   MAX_PARALLEL_PROCESSES=2
   ```

3. Process in smaller batches

---

**Problem:** Poor quality summaries

**Solution:**
1. Increase DPI:
   ```env
   PDF_DPI=300
   ```

2. Use better vision model:
   ```env
   VISION_MODEL=gpt-4o
   ```

3. Check source document quality
   - Scanned documents may need OCR
   - Low-resolution scans won't improve with higher DPI

---

### Analysis Issues

**Problem:** `Index file not found`

**Solution:**
```bash
# Verify index file path
ls -lh ./data_room_index.txt

# Use absolute path
lawdit-analyze --index /full/path/to/data_room_index.txt
```

---

**Problem:** Analysis produces generic results

**Solution:**
1. Enable web search:
   ```bash
   lawdit-analyze --index ./index.txt --enable-web-search
   ```

2. Increase iterations:
   ```bash
   lawdit-analyze --index ./index.txt --max-iterations 30
   ```

3. Be specific with focus areas:
   ```bash
   lawdit-analyze --index ./index.txt --focus contracts
   ```

---

**Problem:** OpenAI rate limit errors

**Solution:**
```env
# Reduce request rate in .env
OPENAI_MAX_REQUESTS_PER_MINUTE=30

# Or upgrade OpenAI tier
# Visit: https://platform.openai.com/account/billing
```

---

### Web Interface Issues

**Problem:** Web interface won't start

**Solution:**
```bash
# Install Streamlit
pip install streamlit>=1.28.0

# Try different port
streamlit run src/lawdit/web/app.py --server.port=8502
```

---

**Problem:** Configuration not saving

**Solution:**
1. Check file permissions:
   ```bash
   ls -la .env
   chmod 644 .env
   ```

2. Verify directory is writable:
   ```bash
   touch test.txt && rm test.txt
   ```

---

## Frequently Asked Questions

### General Questions

**Q: Is my data secure?**

A: Yes. Your documents are:
- Processed locally on your machine
- Only summaries sent to OpenAI API (not full documents)
- Stored in your local `data_room_processing` directory
- Not retained by OpenAI per their API terms
- Automatically gitignored to prevent accidental commits

**Q: Can I use Lawdit without Google Drive?**

A: Not currently. Lawdit requires Google Drive for document storage. Future versions may support local folders or other cloud storage.

**Q: How accurate are the results?**

A: Lawdit uses state-of-the-art AI models but:
- ✅ Excellent for initial risk screening
- ✅ Reliable for identifying obvious issues
- ❌ Not a substitute for attorney review
- ❌ May miss nuanced legal interpretations
- **Always have qualified attorneys review critical findings**

**Q: What languages are supported?**

A: Currently optimized for English documents. Other languages may work but accuracy is not guaranteed.

---

### Technical Questions

**Q: Can I process local PDF files instead of Google Drive?**

A: Not directly, but you can:
1. Upload PDFs to Google Drive
2. Index the folder
3. Process as normal

**Q: How do I reprocess a single document?**

A: You need to re-index the entire folder. Future versions will support incremental updates.

**Q: Can I export to formats other than Word/HTML?**

A: Currently no. You can:
- Convert Word report to PDF using Microsoft Word
- Print HTML dashboard to PDF from browser
- Future versions may add direct PDF export

**Q: Does Lawdit work offline?**

A: No. Lawdit requires internet connectivity for:
- Google Drive API access
- OpenAI API calls
- Tavily web search (if enabled)

---

### Cost Questions

**Q: How much does it cost to analyze 100 documents?**

A: Typical costs:
- Indexing: $50-100 (depends on DPI and page count)
- Analysis: $20-40
- **Total: $70-140**

Compare to manual attorney review: $10,000-50,000

**Q: Are there ongoing subscription costs?**

A: No. Lawdit is open source and free. You only pay for:
- OpenAI API usage (pay-as-you-go)
- Tavily API usage (free tier available)
- Google Cloud (usually free for API calls)

**Q: How can I reduce costs?**

A: See [Cost Optimization](#cost-optimization) section.

---

### Workflow Questions

**Q: How long does processing take?**

A: Typical timelines:
- Small (10-20 docs): 15-30 minutes total
- Medium (50-100 docs): 1-2 hours total
- Large (200-500 docs): 3-6 hours total
- Very large (1000+ docs): 12-24 hours total

**Q: Can I pause and resume processing?**

A: Not currently. If interrupted:
- Indexing: Must restart (cached results are saved)
- Analysis: Must restart

**Q: Can I process multiple data rooms in parallel?**

A: Yes! Run multiple instances:
```bash
# Terminal 1
lawdit-index --folder-id FOLDER_A --output index_a.txt

# Terminal 2
lawdit-index --folder-id FOLDER_B --output index_b.txt
```

Watch API rate limits to avoid throttling.

---

### Results Questions

**Q: What if Lawdit identifies something as "Critical" that isn't?**

A: This is a false positive. AI can be overly cautious. Always:
- Review with legal counsel
- Verify against source documents
- Use professional judgment

**Q: What if Lawdit misses a critical risk?**

A: This is a false negative. Lawdit is for initial screening, not final review. Always:
- Have attorneys conduct full review
- Don't rely solely on AI analysis
- Use Lawdit to prioritize manual review

**Q: Can I customize risk severity thresholds?**

A: Not currently. Future versions may allow custom risk scoring.

---

### Support Questions

**Q: Where can I get help?**

A:
1. Check this guide and README.md
2. Review troubleshooting section
3. Search existing GitHub issues
4. Create new GitHub issue with details

**Q: Can I request new features?**

A: Yes! Create a GitHub issue with:
- Feature description
- Use case
- Expected behavior

**Q: Is commercial use allowed?**

A: Yes! Lawdit is MIT licensed. You can:
- Use commercially
- Modify the code
- Redistribute
- **Must retain copyright notice**

---

## Additional Resources

### Documentation
- [README.md](README.md) - Technical documentation
- [WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md) - Web interface details
- [.env.example](.env.example) - Configuration reference

### Code Examples
- [examples/run_analysis_example.py](examples/run_analysis_example.py) - Python API example
- [examples/generate_deliverables_example.py](examples/generate_deliverables_example.py) - Report generation

### External Resources
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Tavily API Docs](https://docs.tavily.com)
- [Google Drive API](https://developers.google.com/drive)

---

## Contributing

We welcome contributions! See our contribution guidelines in the README.

---

## License

MIT License - See LICENSE file for details.

---

**Ready to start?** Jump to [Quick Start](#quick-start-5-minutes) or launch the web interface with `lawdit-web`!
