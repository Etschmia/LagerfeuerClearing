"""
Graphical user interface for Lagerfeuer Clearing.
"""

from lagerfeuer_clearing.gui.gui_app import main as main  # explicitly re-export

# Define what should be accessible when importing the package
__all__ = ["main"]
