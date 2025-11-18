"""
CLI for Legal Analysis Agents

Command-line interface for running legal risk analysis.
"""

import argparse
import os
import sys
from pathlib import Path

from lawdit.agents import create_legal_risk_agent, run_analysis
from lawdit.tools import initialize_document_store


def main():
    """Main entry point for the analysis CLI."""
    parser = argparse.ArgumentParser(
        description="Run legal risk analysis on a data room index",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full analysis
  lawdit-analyze --index ./data_room_index.txt

  # Focus on specific areas
  lawdit-analyze --index ./index.txt --focus contracts regulatory

  # Specify custom output directory
  lawdit-analyze --index ./index.txt --output-dir ./my-reports

  # Specify working directory
  lawdit-analyze --index ./index.txt --working-dir ./data_room
        """,
    )

    parser.add_argument(
        "--index",
        "-i",
        required=True,
        help="Path to the data room index file",
    )

    parser.add_argument(
        "--working-dir",
        "-w",
        default="./data_room_processing",
        help="Working directory containing processed documents (default: ./data_room_processing)",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        default="./outputs",
        help="Output directory for deliverables (default: ./outputs)",
    )

    parser.add_argument(
        "--focus",
        "-f",
        nargs="+",
        choices=["contracts", "regulatory", "litigation", "governance", "all"],
        default=["all"],
        help="Areas to focus analysis on (default: all)",
    )

    parser.add_argument(
        "--no-deep-agents",
        action="store_true",
        help="Use simplified agent system (if Deep Agents not available)",
    )

    args = parser.parse_args()

    # Validate index file exists
    if not os.path.exists(args.index):
        print(f"Error: Index file not found: {args.index}")
        print("Please run the indexer first: lawdit-index --credentials ... --folder-id ...")
        return 1

    # Validate working directory exists
    if not os.path.exists(args.working_dir):
        print(f"Warning: Working directory not found: {args.working_dir}")
        print("Analysis may be limited to index summaries only.")

    # Ensure output directory exists
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("LAWDIT LEGAL RISK ANALYSIS")
    print("=" * 70)
    print(f"\nIndex file: {args.index}")
    print(f"Working directory: {args.working_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Focus areas: {', '.join(args.focus)}")
    print()

    try:
        # Step 1: Initialize document store
        print("Step 1: Initializing document store...")
        initialize_document_store(args.index, args.working_dir)
        print("✓ Document store initialized\n")

        # Step 2: Load data room index
        print("Step 2: Loading data room index...")
        with open(args.index, "r") as f:
            data_room_index = f.read()
        print(f"✓ Loaded index ({len(data_room_index)} characters)\n")

        # Step 3: Create agent system
        print("Step 3: Creating legal risk analysis agent...")
        use_deep_agents = not args.no_deep_agents
        try:
            agent = create_legal_risk_agent(use_deep_agents=use_deep_agents)
            print(f"✓ Agent system created ({'Deep Agents' if use_deep_agents else 'Simple'})\n")
        except ImportError as e:
            print(f"\nWarning: {e}")
            print("Deep Agents framework not available.")
            print("Install it with: pip install deepagents")
            print("\nFalling back to simplified analysis...")
            return 1

        # Step 4: Run analysis
        print("Step 4: Running legal risk analysis...")
        print("This may take several minutes depending on the size of the data room...")
        print("-" * 70)

        focus_areas = args.focus if "all" not in args.focus else None

        result = run_analysis(
            agent=agent,
            data_room_index=data_room_index,
            focus_areas=focus_areas,
            output_dir=args.output_dir,
        )

        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print("\nCheck the output directory for deliverables:")
        print(f"  - Word Report: {args.output_dir}/legal_risk_analysis_report.docx")
        print(f"  - HTML Dashboard: {args.output_dir}/risk_dashboard.html")
        print()

        return 0

    except FileNotFoundError as e:
        print(f"\nError: File not found - {e}")
        return 1
    except ImportError as e:
        print(f"\nError: Missing dependency - {e}")
        print("Please install required packages: pip install -e '.[dev]'")
        return 1
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
