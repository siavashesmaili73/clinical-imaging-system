import os
import shutil

def setup_project_structure():
    # Define the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Define directory structure
    directories = {
        'src': [
            'ai',      # AI models and related code
            'gui',     # GUI-related code
            'utils'    # Utility functions and helpers
        ],
        'assets': [
            'images',  # For logos, icons, etc.
            'styles'   # CSS/styling files
        ],
        'models': [
            'weights'  # Pre-trained model weights
        ],
        'tests': [],  # For test files
        'docs': []    # For documentation
    }
    
    # Create directories
    for main_dir, subdirs in directories.items():
        main_path = os.path.join(project_root, main_dir)
        os.makedirs(main_path, exist_ok=True)
        for subdir in subdirs:
            os.makedirs(os.path.join(main_path, subdir), exist_ok=True)
    
    # Define file mappings (source -> destination)
    file_mappings = {
        'comprehensive_radiology_ai.py': 'src/ai/comprehensive_radiology_ai.py',
        'pathology_ai.py': 'src/ai/pathology_ai.py',
        'healthcare_gui.py': 'src/gui/healthcare_gui.py',
        'create_splash.py': 'src/utils/create_splash.py',
        'download_weights.py': 'src/utils/download_weights.py',
        'setup_models.py': 'src/utils/setup_models.py'
    }
    
    # Move files to their new locations
    for src, dest in file_mappings.items():
        src_path = os.path.join(project_root, src)
        dest_path = os.path.join(project_root, dest)
        if os.path.exists(src_path):
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.move(src_path, dest_path)
            print(f"Moved {src} to {dest}")
    
    # Create __init__.py files for Python packages
    python_dirs = [
        'src/ai',
        'src/gui',
        'src/utils'
    ]
    
    for dir_path in python_dirs:
        init_file = os.path.join(project_root, dir_path, '__init__.py')
        if not os.path.exists(init_file):
            open(init_file, 'a').close()
            print(f"Created {init_file}")
    
    # Create a main.py file at the project root
    main_content = '''#!/usr/bin/env python3
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gui.healthcare_gui import main

if __name__ == '__main__':
    main()
'''
    
    with open(os.path.join(project_root, 'main.py'), 'w') as f:
        f.write(main_content)
    
    # Make main.py executable
    os.chmod(os.path.join(project_root, 'main.py'), 0o755)
    
    print("\nProject structure set up successfully!")
    print("\nTo run the application:")
    print("1. Make sure you're in the project root directory")
    print("2. Run: ./main.py")
    print("\nDirectory structure:")
    print("project_root/")
    print("├── main.py")
    print("├── src/")
    print("│   ├── ai/")
    print("│   ├── gui/")
    print("│   └── utils/")
    print("├── assets/")
    print("│   ├── images/")
    print("│   └── styles/")
    print("├── models/")
    print("│   └── weights/")
    print("├── tests/")
    print("└── docs/")

if __name__ == '__main__':
    setup_project_structure()
