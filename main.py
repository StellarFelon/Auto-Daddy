"""
Auto Daddy - Main Script

This is the main entry point for the Auto Daddy application.
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from ui import AutoDaddyUI

def main():
    """Main entry point for the Auto Daddy application."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Start the application
    app = QApplication(sys.argv)
    window = AutoDaddyUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
