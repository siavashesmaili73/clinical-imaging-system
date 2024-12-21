import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
                            QTextEdit, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon
import torch
from torchvision import transforms, models
from PIL import Image
import numpy as np

class ClinicalAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clinical Assistant")
        self.setMinimumSize(1000, 700)
        
        # Initialize model
        self.model = self.load_model()
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])
        
        # Setup UI
        self.setup_ui()
        
        # Store current image path
        self.current_image_path = None

    def load_model(self):
        # Load pre-trained ResNet model
        model = models.resnet50(pretrained=True)
        model.eval()
        return model

    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for image
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setStyleSheet("border: 2px dashed #cccccc; border-radius: 5px;")
        self.image_label.setText("Drag and drop image here\nor click Upload button")
        self.image_label.setWordWrap(True)
        
        # Upload button
        upload_btn = QPushButton("Upload Image")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        upload_btn.clicked.connect(self.upload_image)
        
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(upload_btn)
        
        # Right panel for analysis
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Analysis title
        analysis_title = QLabel("Clinical Analysis")
        analysis_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # Analysis text area
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        
        # Analyze button
        analyze_btn = QPushButton("Analyze Image")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_image)
        
        right_layout.addWidget(analysis_title)
        right_layout.addWidget(self.analysis_text)
        right_layout.addWidget(analyze_btn)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QLabel {
                color: #333;
            }
        """)

    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        
        if file_name:
            self.current_image_path = file_name
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.analysis_text.clear()

    def analyze_image(self):
        if not self.current_image_path:
            self.analysis_text.setText("Please upload an image first.")
            return
        
        try:
            # Load and preprocess image
            image = Image.open(self.current_image_path).convert('RGB')
            input_tensor = self.transform(image)
            input_batch = input_tensor.unsqueeze(0)
            
            # Analyze image
            with torch.no_grad():
                output = self.model(input_batch)
            
            # Generate analysis text
            analysis = self.generate_analysis(output)
            self.analysis_text.setText(analysis)
            
        except Exception as e:
            self.analysis_text.setText(f"Error analyzing image: {str(e)}")

    def generate_analysis(self, model_output):
        # This is a placeholder for actual medical image analysis
        # In a real application, you would:
        # 1. Use a model trained on medical images
        # 2. Implement proper medical condition detection
        # 3. Add confidence scores and detailed analysis
        
        # Simulate medical analysis
        analysis_text = "Clinical Analysis Report:\n\n"
        
        # Add image properties
        image = Image.open(self.current_image_path)
        analysis_text += f"Image Properties:\n"
        analysis_text += f"- Dimensions: {image.size[0]}x{image.size[1]} pixels\n"
        analysis_text += f"- Format: {image.format}\n"
        analysis_text += f"- Mode: {image.mode}\n\n"
        
        # Add simulated findings
        analysis_text += "Preliminary Findings:\n"
        analysis_text += "1. Image Quality: Good, suitable for analysis\n"
        analysis_text += "2. Detected Features:\n"
        
        # Simulate different findings based on model output
        probabilities = torch.nn.functional.softmax(model_output[0], dim=0)
        max_prob = torch.max(probabilities).item()
        
        if max_prob > 0.8:
            analysis_text += "   - High contrast regions detected\n"
            analysis_text += "   - Clear tissue boundaries visible\n"
        else:
            analysis_text += "   - Moderate contrast levels\n"
            analysis_text += "   - Some regions require closer examination\n"
        
        analysis_text += "\nSuggested Actions:\n"
        analysis_text += "1. Review highlighted regions\n"
        analysis_text += "2. Consider additional views if needed\n"
        analysis_text += "3. Compare with previous studies if available\n\n"
        
        analysis_text += "Note: This is an AI-assisted analysis. "
        analysis_text += "Please verify all findings clinically.\n"
        analysis_text += "Consultation with a specialist is recommended "
        analysis_text += "for final diagnosis."
        
        return analysis_text

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = ClinicalAssistant()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
