import os
import sys
import urllib.request
import torch
import torchxrayvision as xrv
from tqdm import tqdm
import requests

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True,
                           miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, 
                                 reporthook=lambda b, bsize, tsize: t.update_to(b, bsize, tsize))

def setup_models():
    """Download and set up all required model weights"""
    
    print("Setting up AI models for chest X-ray analysis...")
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Download TorchXRayVision weights
    print("\n1. Setting up TorchXRayVision model...")
    try:
        # This will automatically download and cache the weights
        model = xrv.models.DenseNet(weights="densenet121-res224-all")
        print("✓ TorchXRayVision model ready")
    except Exception as e:
        print(f"Error setting up TorchXRayVision model: {str(e)}")
        return False
    
    # Download MONAI pre-trained weights
    print("\n2. Setting up MONAI clinical model...")
    monai_weights_path = os.path.join(models_dir, "monai_chexnet.pth")
    if not os.path.exists(monai_weights_path):
        try:
            # Note: In a real application, you would download actual medical imaging weights
            # This is a placeholder URL - replace with actual pre-trained weights
            monai_url = "https://github.com/Project-MONAI/MONAI-extra-test-data/releases/download/0.8.1/chexnet_model.pth"
            print("Downloading MONAI weights...")
            download_url(monai_url, monai_weights_path)
            print("✓ MONAI weights downloaded")
        except Exception as e:
            print(f"Error downloading MONAI weights: {str(e)}")
            print("\nAlternative setup:")
            print("1. Download weights manually from the MONAI model zoo")
            print("2. Place the weights file in the 'models' directory as 'monai_chexnet.pth'")
            return False
    else:
        print("✓ MONAI weights already downloaded")
    
    print("\nAll models set up successfully!")
    return True

def verify_setup():
    """Verify that all required components are properly set up"""
    
    print("\nVerifying system setup...")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"\nPython version: {python_version}")
    
    # Check PyTorch
    try:
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version: {torch.version.cuda}")
    except Exception as e:
        print(f"Error checking PyTorch: {str(e)}")
    
    # Check TorchXRayVision
    try:
        print(f"TorchXRayVision version: {xrv.__version__}")
    except Exception as e:
        print(f"Error checking TorchXRayVision: {str(e)}")
    
    # Check model files
    models_dir = "models"
    if os.path.exists(models_dir):
        print("\nModel files:")
        for file in os.listdir(models_dir):
            print(f"✓ Found: {file}")
    else:
        print("\nModels directory not found")
    
    print("\nSetup verification complete!")

def main():
    print("Starting model setup...")
    if setup_models():
        verify_setup()
        print("\nSystem is ready to use!")
        print("\nTo analyze X-rays, run:")
        print("python advanced_radiology_ai.py <path_to_xray_image>")
    else:
        print("\nSetup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
