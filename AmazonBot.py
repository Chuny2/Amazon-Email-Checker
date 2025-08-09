"""
Entry point for the Amazon Email Checker application.
Launches the graphical user interface.
"""
import sys
from gui import setup_gui


if __name__ == "__main__":

    print("Starting GUI...")
    sys.exit(setup_gui())
