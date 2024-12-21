import os
import sys

def check_dependencies():
    try:
        import torch
        import torchvision
        import PyQt6
        import PIL
        print("All required dependencies are installed.")
        return True
    except ImportError as e:
        print(f"Missing dependency: {str(e)}")
        print("\nPlease install required packages:")
        print("python3 -m pip install PyQt6 torch torchvision Pillow")
        return False

def main():
    if not check_dependencies():
        return
    
    # Check for weights file
    if not os.path.exists("chexnet_weights.pth"):
        print("\nDownloading required model weights...")
        import download_weights
        download_weights.download_chexnet_weights()
    
    print("\nStarting Medical Assistant...")
    import medical_assistant
    medical_assistant.main()

if __name__ == "__main__":
    main()
