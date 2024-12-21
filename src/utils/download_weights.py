import torch
import torch.nn as nn
import torchvision.models as models
import urllib.request
import os

def download_chexnet_weights():
    # URL for the pre-trained CheXNet weights
    weights_url = "https://github.com/arnoweng/CheXNet/raw/master/model.pth.tar"
    weights_path = "chexnet_weights.pth"
    
    print("Downloading CheXNet weights...")
    
    try:
        # Download weights if they don't exist
        if not os.path.exists(weights_path):
            urllib.request.urlretrieve(weights_url, weights_path)
            print("Successfully downloaded weights to:", weights_path)
        else:
            print("Weights file already exists at:", weights_path)
            
    except Exception as e:
        print("Error downloading weights:", str(e))
        print("\nAlternative setup:")
        print("1. Download weights manually from:")
        print("   https://github.com/arnoweng/CheXNet/raw/master/model.pth.tar")
        print("2. Save the file as 'chexnet_weights.pth' in the same directory")
        print("3. Run medical_assistant.py again")

if __name__ == "__main__":
    download_chexnet_weights()
