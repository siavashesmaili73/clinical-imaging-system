import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
                            QTextEdit, QProgressBar, QSplashScreen, QTabWidget,
                            QScrollArea, QFormLayout, QLineEdit, QTableWidget,
                            QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor
import time
from datetime import datetime
from advanced_radiology_ai import AdvancedRadiologyAI

# Sample patient data
SAMPLE_PATIENTS = [
    {
        'id': 'P001',
        'name': 'John Smith',
        'age': '45',
        'gender': 'Male',
        'dob': '1979-05-15',
        'history': 'HTN, T2DM',
        'allergies': 'Penicillin',
        'last_visit': '2024-01-10',
        'studies': [
            {'date': '2024-01-10', 'type': 'Chest X-Ray', 'reason': 'Annual checkup'},
            {'date': '2023-06-15', 'type': 'CT Chest', 'reason': 'Persistent cough'}
        ]
    },
    {
        'id': 'P002',
        'name': 'Sarah Johnson',
        'age': '62',
        'gender': 'Female',
        'dob': '1962-08-23',
        'history': 'CAD, COPD',
        'allergies': 'None',
        'last_visit': '2024-02-01',
        'studies': [
            {'date': '2024-02-01', 'type': 'Chest X-Ray', 'reason': 'SOB workup'},
            {'date': '2023-11-20', 'type': 'Chest X-Ray', 'reason': 'COPD exacerbation'}
        ]
    },
    {
        'id': 'P003',
        'name': 'Michael Chen',
        'age': '35',
        'gender': 'Male',
        'dob': '1989-11-30',
        'history': 'Asthma',
        'allergies': 'Sulfa',
        'last_visit': '2024-01-25',
        'studies': [
            {'date': '2024-01-25', 'type': 'Chest X-Ray', 'reason': 'Pneumonia follow-up'}
        ]
    }
]

class PatientTab(QWidget):
    def __init__(self, patient_data):
        super().__init__()
        self.patient_data = patient_data
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Patient info section
        info_group = QWidget()
        info_layout = QFormLayout()
        
        # Style for labels
        label_style = """
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                min-width: 100px;
            }
        """
        
        # Style for text fields
        field_style = """
            QLineEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background: #f8f9fa;
                min-width: 200px;
            }
            QLineEdit:disabled {
                background: #f5f6f7;
                color: #2c3e50;
            }
        """
        
        # Create and style fields
        fields = [
            ('Patient ID:', self.patient_data['id']),
            ('Name:', self.patient_data['name']),
            ('Age:', self.patient_data['age']),
            ('Gender:', self.patient_data['gender']),
            ('DOB:', self.patient_data['dob']),
            ('Medical History:', self.patient_data['history']),
            ('Allergies:', self.patient_data['allergies'])
        ]
        
        for label_text, value in fields:
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            field = QLineEdit(value)
            field.setReadOnly(True)
            field.setStyleSheet(field_style)
            info_layout.addRow(label, field)
        
        info_group.setLayout(info_layout)
        
        # Studies section
        studies_label = QLabel("Imaging Studies")
        studies_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 15px;
                margin-bottom: 5px;
            }
        """)
        
        studies_table = QTableWidget()
        studies_table.setColumnCount(3)
        studies_table.setHorizontalHeaderLabels(['Date', 'Type', 'Reason'])
        studies_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        studies_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #bdc3c7;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        
        # Add studies to table
        studies_table.setRowCount(len(self.patient_data['studies']))
        for i, study in enumerate(self.patient_data['studies']):
            studies_table.setItem(i, 0, QTableWidgetItem(study['date']))
            studies_table.setItem(i, 1, QTableWidgetItem(study['type']))
            studies_table.setItem(i, 2, QTableWidgetItem(study['reason']))
        
        # Add all components to main layout
        layout.addWidget(info_group)
        layout.addWidget(studies_label)
        layout.addWidget(studies_table)
        layout.addStretch()
        
        self.setLayout(layout)

class ClinicalGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ai_system = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Clinical Imaging System')
        self.setMinimumSize(1400, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left panel with tabs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                border: 1px solid #bdc3c7;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
            }
        """)
        
        # Add patient tabs
        for patient in SAMPLE_PATIENTS:
            tab = PatientTab(patient)
            tabs.addTab(tab, f"{patient['name']} ({patient['id']})")
        
        left_layout.addWidget(tabs)
        
        # Right panel for image and analysis
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Image section
        image_section = QWidget()
        image_layout = QVBoxLayout(image_section)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setMinimumSize(600, 600)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("Drop X-ray image here\nor click Upload")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        upload_btn = QPushButton("Upload Image")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        upload_btn.clicked.connect(self.upload_image)
        
        analyze_btn = QPushButton("Analyze Image")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_image)
        self.analyze_btn = analyze_btn
        self.analyze_btn.setEnabled(False)
        
        button_layout.addWidget(upload_btn)
        button_layout.addWidget(analyze_btn)
        
        image_layout.addWidget(self.image_label)
        image_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 5px;
            }
        """)
        self.progress_bar.hide()
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #7f8c8d;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Analysis results
        analysis_section = QWidget()
        analysis_layout = QVBoxLayout(analysis_section)
        
        analysis_title = QLabel("Analysis Results")
        analysis_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        analysis_layout.addWidget(analysis_title)
        analysis_layout.addWidget(self.analysis_text)
        
        # Add all sections to right panel
        right_layout.addWidget(image_section)
        right_layout.addWidget(self.progress_bar)
        right_layout.addWidget(self.status_label)
        right_layout.addWidget(analysis_section)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)
        
        # Initialize AI system
        self.initialize_ai_system()
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
        """)
    
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
        self.progress_bar.setMaximum(0)
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

class AnalysisWorker(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, ai_system, image_path):
        super().__init__()
        self.ai_system = ai_system
        self.image_path = image_path
    
    def run(self):
        self.progress.emit("Loading models...")
        time.sleep(1)
        
        self.progress.emit("Preprocessing image...")
        time.sleep(1)
        
        self.progress.emit("Analyzing with multiple AI models...")
        analysis = self.ai_system.analyze_image(self.image_path)
        
        self.progress.emit("Generating report...")
        time.sleep(1)
        
        self.finished.emit(analysis)

def main():
    app = QApplication(sys.argv)
    
    # Show splash screen while loading
    splash_pix = QPixmap('splash.png') if os.path.exists('splash.png') else QPixmap(400, 200)
    splash = QSplashScreen(splash_pix)
    splash.show()
    
    # Create and show main window
    window = ClinicalGUI()
    window.show()
    
    # Close splash screen
    splash.finish(window)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
