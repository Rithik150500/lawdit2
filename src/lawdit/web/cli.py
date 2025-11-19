"""CLI entry point for Lawdit web interface."""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Launch the Streamlit web interface."""
    # Get the path to the app.py file
    app_path = Path(__file__).parent / "app.py"

    if not app_path.exists():
        print(f"Error: Web app not found at {app_path}", file=sys.stderr)
        sys.exit(1)

    # Launch Streamlit
    print("🚀 Starting Lawdit Web Interface...")
    print("📍 URL will open in your browser automatically")
    print("⏹️  Press Ctrl+C to stop the server\n")

    try:
        subprocess.run(
            [
                "streamlit",
                "run",
                str(app_path),
                "--server.port=8501",
                "--server.address=localhost",
                "--browser.gatherUsageStats=false",
            ],
            check=True,
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Lawdit Web Interface...")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(
            "Error: Streamlit not found. Please install it with: pip install streamlit",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
