"""
Entry point for the Amazon Email Checker application.
Launches the graphical user interface.
"""
import sys
from gui import setup_gui
from amazon_auth import Amazon

if __name__ == "__main__":
    print("Initializing Amazon session...")
    Amazon.initialize_session()
    print("Amazon session ready! Starting GUI...")
    sys.exit(setup_gui())
