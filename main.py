#!/usr/bin/env python3
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gui.healthcare_gui import main

if __name__ == '__main__':
    main()
