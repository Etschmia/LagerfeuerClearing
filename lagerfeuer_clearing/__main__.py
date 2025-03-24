#!/usr/bin/env python3
"""
Main entry point when package is run directly with python -m lagerfeuer_clearing
"""
import sys
from lagerfeuer_clearing.gui import main as gui_main
from lagerfeuer_clearing.cli import main as cli_main


def main():
    """Parse args and run the appropriate interface."""
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # Run CLI version if --cli flag is provided
        cli_main()
    else:
        # Default to GUI version
        gui_main()


if __name__ == "__main__":
    main() 