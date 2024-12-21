import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
                            QTextEdit, QScrollArea, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import densenet121
from PIL import Image
import numpy as np

# Define the conditions this model can detect
CONDITIONS = [
    'Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema', 'Effusion',
    'Emphysema', 'Fibrosis', 'Hernia', 'Infiltration', 'Mass', 'Nodule',
    'Pleural_Thickening', 'Pneumonia', 'Pneumothorax'
]

class CheXNet(nn.Module):
    def __init__(self, num_classes=14):
        super(CheXNet, self).__init__()
        self.model = densenet121(pretrained=True)
        num_features = self.model.classifier.in_features
        self.model.classifier = nn.Sequential(
            nn.Linear(num_features, num_classes),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

class MedicalAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical X-Ray Assistant")
        self.setMinimumSize(1200, 800)
        
        # Initialize model
        self.model = self.load_model()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])
        
        # Setup UI
        self.setup_ui()
        
        # Store current image path
        self.current_image_path = None

    def load_model(self):
        model = CheXNet()
        # In a real application, you would load pre-trained weights here
        # model.load_state_dict(torch.load('chexnet_weights.pth'))
        model.eval()
        return model

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for image
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(500, 500)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 5px;
                background-color: #f5f5f5;
            }
        """)
        self.image_label.setText("Drop X-ray image here\nor click Upload button")
        self.image_label.setWordWrap(True)
        
        # Upload button
        upload_btn = QPushButton("Upload X-Ray Image")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        upload_btn.clicked.connect(self.upload_image)
        
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Right panel for analysis
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Analysis title
        analysis_title = QLabel("Medical Analysis")
        analysis_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # Progress bars for conditions
        self.condition_bars = {}
        conditions_widget = QWidget()
        conditions_layout = QVBoxLayout(conditions_widget)
        
        for condition in CONDITIONS:
            condition_widget = QWidget()
            condition_layout = QHBoxLayout(condition_widget)
            
            label = QLabel(condition)
            label.setMinimumWidth(150)
            progress = QProgressBar()
            progress.setMaximum(100)
            progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 5px;
                }
            """)
            
            condition_layout.addWidget(label)
            condition_layout.addWidget(progress)
            
            self.condition_bars[condition] = progress
            conditions_layout.addWidget(condition_widget)
        
        # Scrollable area for conditions
        scroll = QScrollArea()
        scroll.setWidget(conditions_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
        """)
        
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
        analyze_btn = QPushButton("Analyze X-Ray")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_image)
        
        right_layout.addWidget(analysis_title)
        right_layout.addWidget(scroll)
        right_layout.addWidget(self.analysis_text)
        right_layout.addWidget(analyze_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
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
            "Select X-Ray Image",
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
            # Reset progress bars
            for bar in self.condition_bars.values():
                bar.setValue(0)

    def analyze_image(self):
        if not self.current_image_path:
            self.analysis_text.setText("Please upload an X-ray image first.")
            return
        
        try:
            # Load and preprocess image
            image = Image.open(self.current_image_path).convert('RGB')
            input_tensor = self.transform(image)
            input_batch = input_tensor.unsqueeze(0)
            
            # Analyze image
            with torch.no_grad():
                output = self.model(input_batch)
            
            # Update progress bars with predictions
            predictions = output[0].numpy() * 100
            for condition, prob in zip(CONDITIONS, predictions):
                self.condition_bars[condition].setValue(int(prob))
            
            # Generate analysis text
            analysis = self.generate_analysis(predictions)
            self.analysis_text.setText(analysis)
            
        except Exception as e:
            self.analysis_text.setText(f"Error analyzing image: {str(e)}")

    def generate_analysis(self, predictions):
        # Sort conditions by probability
        condition_probs = list(zip(CONDITIONS, predictions))
        condition_probs.sort(key=lambda x: x[1], reverse=True)
        
        analysis = "X-Ray Analysis Report\n\n"
        
        # Add image properties
        image = Image.open(self.current_image_path)
        analysis += "Image Properties:\n"
        analysis += f"- Dimensions: {image.size[0]}x{image.size[1]} pixels\n"
        analysis += f"- Format: {image.format}\n\n"
        
        # Add findings
        analysis += "Primary Findings:\n"
        for condition, prob in condition_probs:
            if prob > 50:  # Only include significant findings
                analysis += f"- {condition}: {prob:.1f}% probability\n"
        
        # Generate recommendations based on findings
        analysis += "\nRecommended Actions:\n"
        for condition, prob in condition_probs:
            if prob > 70:
                analysis += self.get_recommendation(condition)
        
        # Add follow-up recommendations
        analysis += "\nFollow-up Plan:\n"
        high_risk = any(prob > 80 for _, prob in condition_probs)
        if high_risk:
            analysis += "- Urgent follow-up recommended within 24-48 hours\n"
            analysis += "- Consider additional imaging studies\n"
            analysis += "- Specialist consultation advised\n"
        else:
            analysis += "- Routine follow-up as clinically indicated\n"
            analysis += "- Monitor for symptom changes\n"
        
        analysis += "\nNote: This is an AI-assisted analysis. "
        analysis += "Please verify all findings clinically. "
        analysis += "Consultation with a radiologist is recommended "
        analysis += "for final diagnosis."
        
        return analysis

    def get_recommendation(self, condition):
        recommendations = {
            'Pneumonia': "- Start empiric antibiotics based on local guidelines\n"
                        "- Consider blood cultures if severe\n"
                        "- Monitor oxygen saturation\n",
            
            'Pneumothorax': "- Evaluate for chest tube placement if large\n"
                           "- Monitor respiratory status\n"
                           "- Consider pulmonology consultation\n",
            
            'Cardiomegaly': "- Evaluate cardiac function with echocardiogram\n"
                           "- Consider cardiology consultation\n"
                           "- Monitor fluid status\n",
            
            'Edema': "- Evaluate fluid status and cardiac function\n"
                    "- Consider diuretic therapy\n"
                    "- Monitor renal function\n",
            
            'Effusion': "- Consider thoracentesis if large\n"
                       "- Evaluate for underlying cause\n"
                       "- Monitor respiratory status\n",
            
            'Mass': "- Urgent CT chest with contrast\n"
                   "- Pulmonology/Oncology consultation\n"
                   "- Consider biopsy\n",
            
            'Nodule': "- Follow Fleischner Society guidelines\n"
                     "- Schedule follow-up imaging\n"
                     "- Consider CT chest\n",
            
            'Atelectasis': "- Encourage deep breathing exercises\n"
                          "- Consider chest physiotherapy\n"
                          "- Monitor oxygen saturation\n",
            
            'Consolidation': "- Evaluate for infectious vs. non-infectious cause\n"
                           "- Consider antibiotics if indicated\n"
                           "- Monitor clinical response\n",
            
            'Emphysema': "- Pulmonary function testing\n"
                        "- Smoking cessation counseling\n"
                        "- Consider inhaler therapy\n",
            
            'Fibrosis': "- Pulmonology consultation\n"
                        "- Consider high-resolution CT\n"
                        "- Evaluate for underlying cause\n",
            
            'Hernia': "- Surgical consultation\n"
                      "- Monitor for complications\n"
                      "- Consider CT for better characterization\n",
            
            'Infiltration': "- Monitor for progression\n"
                           "- Consider underlying cause\n"
                           "- Follow-up imaging as indicated\n",
            
            'Pleural_Thickening': "- Evaluate for asbestos exposure\n"
                                 "- Consider CT chest\n"
                                 "- Monitor for progression\n"
        }
        
        return recommendations.get(condition, "- Follow-up as clinically indicated\n")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = MedicalAssistant()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
