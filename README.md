# Advanced Clinical Imaging System

An AI-powered medical imaging analysis system that provides automated analysis for both radiology and pathology images. The system supports multiple modalities including chest X-rays, musculoskeletal imaging, and neurological studies.

## Features

- **Comprehensive Radiology Analysis**
  - Chest X-ray analysis
  - Musculoskeletal imaging
  - Neurological studies
  - Auto-detection of image types

- **Pathology Analysis**
  - Gross specimen analysis
  - H&E stain analysis

- **Modern GUI Interface**
  - Patient management
  - Image upload and analysis
  - Detailed reporting system

## Detailed Installation Guide

1. Clone the repository:
```bash
git clone https://github.com/siavashesmaili73/clinical-imaging-system.git
cd clinical-imaging-system
```

2. Set up a Python virtual environment (recommended):
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the setup script to organize project files:
```bash
python setup_project.py
```

5. Download model weights (will be done automatically on first run):
```bash
python src/utils/download_weights.py
```

## Usage

Run the application:
```bash
./main.py
```

## Project Structure

```
project_root/
├── main.py              # Main entry point
├── src/                 # Source code
│   ├── ai/             # AI models
│   ├── gui/            # GUI components
│   └── utils/          # Utilities
├── assets/             # Static assets
├── models/             # Model weights
├── tests/              # Test files
└── docs/               # Documentation
```

## Development Workflow

1. Create a new feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "Description of your changes"
```

3. Push your changes:
```bash
git push origin feature/your-feature-name
```

4. Create a Pull Request on GitHub

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TorchXRayVision for chest X-ray models
- PyQt6 for the GUI framework
