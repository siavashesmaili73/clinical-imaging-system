import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
                            QTextEdit, QProgressBar, QSplashScreen)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon
import time
from advanced_radiology_ai import AdvancedRadiologyAI

class AnalysisWorker(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, ai_system, image_path):
        super().__init__()
        self.ai_system = ai_system
        self.image_path = image_path
    
    def run(self):
        self.progress.emit("Loading models...")
        time.sleep(1)  # Give UI time to update
        
        self.progress.emit("Preprocessing image...")
        time.sleep(1)
        
        self.progress.emit("Analyzing with multiple AI models...")
        analysis = self.ai_system.analyze_image(self.image_path)
        
        self.progress.emit("Generating report...")
        time.sleep(1)
        
        self.finished.emit(analysis)

class RadiologyGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ai_system = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Advanced Radiology AI Assistant')
        self.setMinimumSize(1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel for image
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setMinimumSize(500, 500)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 5px;
                background-color: #f5f5f5;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("Drop X-ray image here\nor click Upload")
        
        # Upload button
        upload_btn = QPushButton("Upload X-Ray Image")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 15px;
                font-size: 16px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        upload_btn.clicked.connect(self.upload_image)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        self.progress_bar.hide()
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.status_label)
        
        # Right panel for analysis
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Analysis title
        analysis_title = QLabel("Analysis Results")
        analysis_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # Analysis text area
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        # Analyze button
        self.analyze_btn = QPushButton("Analyze Image")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 15px;
                font-size: 16px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_image)
        self.analyze_btn.setEnabled(False)
        
        right_layout.addWidget(analysis_title)
        right_layout.addWidget(self.analysis_text)
        right_layout.addWidget(self.analyze_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add panels to main layout
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        # Initialize AI system
        self.initialize_ai_system()
    
    def initialize_ai_system(self):
        """Initialize the AI system in the background"""
        self.status_label.setText("Initializing AI system...")
        self.ai_system = AdvancedRadiologyAI()
        self.status_label.setText("System ready")
    
    def upload_image(self):
        """Handle image upload"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select X-Ray Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if file_name:
            pixmap = QPixmap(file_name)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.current_image_path = file_name
            self.analyze_btn.setEnabled(True)
            self.analysis_text.clear()
            self.status_label.setText("Image loaded")
    
    def analyze_image(self):
        """Handle image analysis"""
        if not hasattr(self, 'current_image_path'):
            return
        
        # Disable UI elements
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        self.progress_bar.show()
        
        # Create and start worker thread
        self.worker = AnalysisWorker(self.ai_system, self.current_image_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_complete)
        self.worker.start()
    
    def update_progress(self, message):
        """Update progress status"""
        self.status_label.setText(message)
    
    def analysis_complete(self, analysis):
        """Handle completed analysis"""
        self.progress_bar.hide()
        self.analyze_btn.setEnabled(True)
        
        if analysis.get('success', False):
            # Format and display results
            report = "RADIOLOGY AI ANALYSIS REPORT\n"
            report += "=" * 50 + "\n\n"
            
            report += f"Analysis Time: {analysis['analysis_time']:.2f} seconds\n"
            report += f"Urgency Level: {analysis['urgency_level']}\n\n"
            
            report += "KEY FINDINGS:\n"
            report += "-" * 20 + "\n"
            for finding in analysis['findings']:
                report += f"\n• {finding['condition']}:\n"
                report += f"  - Confidence: {finding['confidence']:.1f}%\n"
                report += f"  - Description: {finding['description']['definition']}\n"
                report += "  - Recommendations:\n"
                for rec in finding['recommendations']:
                    report += f"    * {rec['action']} ({rec['urgency']})\n"
            
            if analysis['action_plan']['immediate_actions']:
                report += "\nIMMEDIATE ACTIONS REQUIRED:\n"
                report += "-" * 20 + "\n"
                for action in analysis['action_plan']['immediate_actions']:
                    report += f"• {action['action']}\n"
            
            report += "\nDIFFERENTIAL DIAGNOSES:\n"
            report += "-" * 20 + "\n"
            for diff in analysis['differential_diagnoses']:
                report += f"\n• {diff['diagnosis']}:\n"
                report += f"  - Likelihood: {diff['likelihood']}\n"
                report += f"  - Supporting Findings: {', '.join(diff['supporting_findings'])}\n"
                report += f"  - Next Steps: {', '.join(diff['next_steps'])}\n"
            
            report += "\nMONITORING PLAN:\n"
            report += "-" * 20 + "\n"
            for plan in analysis['action_plan']['monitoring_plan']:
                report += f"\n• {plan['parameter']}:\n"
                report += f"  - Frequency: {plan['frequency']}\n"
                report += f"  - Duration: {plan['duration']}\n"
                report += f"  - Measures: {', '.join(plan['specific_measures'])}\n"
            
            report += "\nDISCLAIMER: This analysis is generated by an AI system and should be "
            report += "verified by a qualified radiologist. Clinical correlation is recommended."
            
            self.analysis_text.setText(report)
            self.status_label.setText("Analysis complete")
        else:
            self.analysis_text.setText(f"Error during analysis: {analysis.get('error', 'Unknown error')}")
            self.status_label.setText("Analysis failed")

def main():
    app = QApplication(sys.argv)
    
    # Show splash screen while loading
    splash_pix = QPixmap('splash.png') if os.path.exists('splash.png') else QPixmap(400, 200)
    splash = QSplashScreen(splash_pix)
    splash.show()
    
    # Create and show main window
    window = RadiologyGUI()
    window.show()
    
    # Close splash screen
    splash.finish(window)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
