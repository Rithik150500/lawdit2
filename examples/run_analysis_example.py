"""
Example: Running Legal Risk Analysis

This example demonstrates how to use the Lawdit system to analyze a data room.
"""

import os
from pathlib import Path

from lawdit.agents import create_legal_risk_agent, run_analysis
from lawdit.tools import initialize_document_store


def main():
    """Run a complete legal risk analysis example."""

    # Configuration
    INDEX_PATH = "./data_room_index.txt"
    WORKING_DIR = "./data_room_processing"
    OUTPUT_DIR = "./outputs"

    # Ensure directories exist
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Step 1: Initialize the document store
    print("Step 1: Initializing document store...")
    initialize_document_store(INDEX_PATH, WORKING_DIR)
    print("✓ Document store initialized\n")

    # Step 2: Load the data room index
    print("Step 2: Loading data room index...")
    if not Path(INDEX_PATH).exists():
        print(f"Error: Index file not found at {INDEX_PATH}")
        print("Please run the indexer first: lawdit-index --credentials ... --folder-id ...")
        return

    with open(INDEX_PATH, "r") as f:
        data_room_index = f.read()

    print(f"✓ Loaded index ({len(data_room_index)} characters)\n")

    # Step 3: Create the legal risk analysis agent
    print("Step 3: Creating legal risk analysis agent...")
    try:
        agent = create_legal_risk_agent(use_deep_agents=True)
        print("✓ Agent system created\n")
    except ImportError as e:
        print(f"Error: {e}")
        print("Deep Agents framework not available. Please install it.")
        return

    # Step 4: Run the analysis
    print("Step 4: Running legal risk analysis...")
    print("This may take several minutes depending on the size of the data room...")
    print("-" * 70)

    focus_areas = ["contracts", "regulatory", "litigation", "governance"]

    try:
        result = run_analysis(
            agent=agent,
            data_room_index=data_room_index,
            focus_areas=focus_areas,
            output_dir=OUTPUT_DIR,
        )

        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print("\nResults:")
        print(result)

    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback

        traceback.print_exc()

    print("\nCheck the output directory for deliverables:")
    print(f"  - Word Report: {OUTPUT_DIR}/legal_risk_analysis_report.docx")
    print(f"  - HTML Dashboard: {OUTPUT_DIR}/risk_dashboard.html")


if __name__ == "__main__":
    main()
