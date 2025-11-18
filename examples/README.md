# Lawdit Examples

This directory contains example scripts demonstrating how to use the Lawdit legal risk analysis system.

## Prerequisites

1. Complete the setup from the main README
2. Generate a data room index using `lawdit-index`
3. Ensure you have the required dependencies installed

## Examples

### 1. Run Full Analysis (`run_analysis_example.py`)

Demonstrates the complete end-to-end workflow:
- Initialize document store
- Load data room index
- Create multi-agent system
- Run comprehensive legal risk analysis
- Generate deliverables

**Usage:**
```bash
python examples/run_analysis_example.py
```

**Requirements:**
- Data room index file at `./data_room_index.txt`
- Processed documents in `./data_room_processing/`
- Deep Agents framework installed

### 2. Generate Sample Deliverables (`generate_deliverables_example.py`)

Shows how to use the document generation utilities directly without running a full analysis. Useful for:
- Testing deliverable generation
- Understanding the output format
- Customizing report templates

**Usage:**
```bash
python examples/generate_deliverables_example.py
```

**Outputs:**
- `./outputs/sample_legal_risk_report.docx` - Sample Word report
- `./outputs/sample_risk_dashboard.html` - Sample interactive dashboard

## Expected Outputs

### Word Document Report

Professional legal risk analysis report with:
- Cover page
- Executive summary
- Table of contents
- Risk findings organized by category
- Severity ratings with color coding
- Supporting evidence and recommendations

### HTML Dashboard

Interactive web dashboard featuring:
- Summary statistics cards
- Filtering by category and severity
- Search functionality
- Risk cards with detailed information
- Responsive design

## Customization

You can customize the examples by:

1. **Modifying Risk Categories**: Edit the category lists in the agents or generators
2. **Changing Output Formats**: Extend the document generators with custom styles
3. **Adding New Focus Areas**: Extend the analysis focus beyond contracts, regulatory, litigation, governance
4. **Custom Prompts**: Modify the agent prompts in `src/lawdit/agents/prompts.py`

## Troubleshooting

**Error: "Document store not initialized"**
- Ensure you've run the indexer to create the data room index
- Check that the index path is correct

**Error: "Deep Agents framework not available"**
- Install Deep Agents: `pip install deepagents`
- Or use `--no-deep-agents` flag for simplified mode

**Error: "Index file not found"**
- Run the indexer first: `lawdit-index --credentials ... --folder-id ...`
- Verify the path in the example script

## Next Steps

After running these examples:

1. Review the generated deliverables
2. Customize the prompts and templates for your needs
3. Integrate with your existing workflows
4. Scale to larger data rooms

## Support

For issues or questions:
- Check the main README troubleshooting section
- Review the inline code documentation
- Submit an issue on GitHub
