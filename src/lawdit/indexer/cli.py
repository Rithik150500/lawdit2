"""
CLI for Data Room Indexing

Command-line interface for building data room indexes.
"""

import argparse
import os
import sys

from lawdit.indexer.data_room_indexer import DataRoomIndexer


def main():
    """Main entry point for the indexing CLI."""
    parser = argparse.ArgumentParser(
        description="Build a data room index from Google Drive documents"
    )

    parser.add_argument(
        "--credentials",
        "-c",
        required=True,
        help="Path to Google Cloud credentials JSON file",
    )

    parser.add_argument(
        "--folder-id", "-f", required=True, help="Google Drive folder ID to index"
    )

    parser.add_argument(
        "--output",
        "-o",
        default="./data_room_index.txt",
        help="Output path for the index file (default: ./data_room_index.txt)",
    )

    parser.add_argument(
        "--working-dir",
        "-w",
        default="./data_room_processing",
        help="Working directory for temporary files (default: ./data_room_processing)",
    )

    parser.add_argument(
        "--api-key",
        "-k",
        help="OpenAI API key (default: uses OPENAI_API_KEY env var)",
    )

    args = parser.parse_args()

    # Validate credentials file exists
    if not os.path.exists(args.credentials):
        print(f"Error: Credentials file not found: {args.credentials}")
        sys.exit(1)

    # Get API key from args or environment
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key not provided (use --api-key or OPENAI_API_KEY env var)")
        sys.exit(1)

    # Initialize and run the indexer
    try:
        indexer = DataRoomIndexer(
            google_credentials_path=args.credentials,
            openai_api_key=api_key,
            working_dir=args.working_dir,
        )

        index_text = indexer.build_data_room_index(
            folder_id=args.folder_id, output_path=args.output
        )

        print(f"\n{'='*70}")
        print("INDEX BUILT SUCCESSFULLY")
        print(f"{'='*70}")
        print(f"\nIndex saved to: {args.output}")
        print(f"Working files in: {args.working_dir}")

    except Exception as e:
        print(f"\nError building index: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
