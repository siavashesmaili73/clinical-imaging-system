import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
                            QTextEdit, QProgressBar, QSplashScreen, QTabWidget,
                            QScrollArea, QFormLayout, QLineEdit, QTableWidget,
                            QTableWidgetItem, QHeaderView, QMenu, QMenuBar,
                            QStackedWidget, QComboBox, QFrame, QDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor, QAction
import time
from datetime import datetime
from ai.comprehensive_radiology_ai import ComprehensiveRadiologyAI
from ai.pathology_ai import PathologyAI

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

class ModernHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout()
        
        # Logo and title
        logo_layout = QHBoxLayout()
        logo = QLabel()
        logo_pixmap = QPixmap('assets/logo.png') if os.path.exists('assets/logo.png') else QPixmap(32, 32)
        logo.setPixmap(logo_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
        title = QLabel("Advanced Clinical Imaging System")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        logo_layout.addWidget(logo)
        logo_layout.addWidget(title)
        logo_layout.addStretch()
        
        # Navigation menu
        nav_menu = QHBoxLayout()
        for text in ["Dashboard", "Patients", "Studies", "Reports"]:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 8px 15px;
                    color: #2c3e50;
                    font-size: 14px;
                }
                QPushButton:hover {
                    color: #3498db;
                }
            """)
            nav_menu.addWidget(btn)
        
        # Add all components to main layout
        layout.addLayout(logo_layout)
        layout.addStretch()
        layout.addLayout(nav_menu)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            ModernHeader {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }
        """)

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

class ImageAnalysisTab(QWidget):
    def __init__(self, title, description, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title and description
        header = QWidget()
        header_layout = QVBoxLayout()
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("color: #7f8c8d;")
        desc_label.setWordWrap(True)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)
        header.setLayout(header_layout)
        
        # Image upload section
        upload_section = QWidget()
        upload_layout = QVBoxLayout()
        
        self.image_label = QLabel()
        self.image_label.setMinimumSize(500, 500)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("Drop image here\nor click Upload")
        
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
        
        upload_layout.addWidget(self.image_label)
        upload_layout.addLayout(button_layout)
        upload_section.setLayout(upload_layout)
        
        # Analysis results section
        results_section = QWidget()
        results_layout = QVBoxLayout()
        
        results_title = QLabel("Analysis Results")
        results_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        results_layout.addWidget(results_title)
        results_layout.addWidget(self.results_text)
        results_section.setLayout(results_layout)
        
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
        
        # Add all sections to main layout
        layout.addWidget(header)
        layout.addWidget(upload_section)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(results_section)
        
        self.setLayout(layout)
    
    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
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
            self.results_text.clear()
            self.status_label.setText("Image loaded")
    
    def analyze_image(self):
        """To be implemented by subclasses"""
        pass

class RadiologyTab(ImageAnalysisTab):
    def __init__(self, parent=None):
        super().__init__(
            "Comprehensive Radiology Analysis",
            "Upload any radiological image for automated analysis. Supports multiple modalities including chest X-rays, musculoskeletal imaging, and neurological studies.",
            parent
        )
        self.ai_system = ComprehensiveRadiologyAI()
        self.initializeRadiologyUI()
    
    def initializeRadiologyUI(self):
        # Add radiology-specific controls
        self.image_type = QComboBox()
        self.image_type.addItems([
            "Chest X-Ray",  # Make chest X-ray the default
            "Auto-detect",
            "Musculoskeletal",
            "Neurological",
            "General Radiology"
        ])
        self.image_type.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(assets/dropdown.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        # Insert combobox after the image label
        layout = self.layout()
        layout.insertWidget(2, self.image_type)
    
    def analyze_image(self):
        if not hasattr(self, 'current_image_path'):
            return
        
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.show()
        
        # Get selected image type
        selected_type = self.image_type.currentText()
        
        # Convert selected type to the format expected by the AI system
        if selected_type == "Auto-detect" or selected_type == "Chest X-Ray":
            image_type = "chest"  # Always use "chest" for chest X-rays
        else:
            image_type = selected_type.lower().replace(" ", "_")
        
        # Create and start worker thread
        self.worker = RadiologyAnalysisWorker(
            self.ai_system, 
            self.current_image_path,
            image_type
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_complete)
        self.worker.start()
    
    def update_progress(self, message):
        self.status_label.setText(message)
    
    def analysis_complete(self, analysis):
        self.progress_bar.hide()
        self.analyze_btn.setEnabled(True)
        
        if analysis.get('success', False):
            report = "RADIOLOGY ANALYSIS REPORT\n"
            report += "=" * 50 + "\n\n"
            
            # Get primary diagnosis (highest confidence finding)
            primary_diagnosis = max(analysis['findings'].items(), key=lambda x: x[1], default=('No significant findings', 0))
            
            # Primary Diagnosis and Treatment
            report += "PRIMARY DIAGNOSIS:\n"
            report += "-" * 20 + "\n"
            report += f"• {primary_diagnosis[0]} ({primary_diagnosis[1]*100:.1f}% confidence)\n\n"
            
            report += "RECOMMENDED ACTIONS:\n"
            report += "-" * 20 + "\n"
            if analysis['recommendations']:
                critical_recs = [r for r in analysis['recommendations'] if r['urgency'] == 'STAT']
                if critical_recs:
                    for rec in critical_recs:
                        report += f"• {rec['action']} - {rec['urgency']}\n"
                else:
                    report += f"• {analysis['recommendations'][0]['action']} - {analysis['recommendations'][0]['urgency']}\n"
            else:
                report += "• Routine radiologist review\n"
            report += "\n"
            
            # Image Info
            report += f"Image Type: {analysis['image_type'].replace('_', ' ').title()}\n"
            report += f"Urgency Level: {analysis['urgency_level']}\n\n"
            
            # Detailed Findings
            report += "DETAILED FINDINGS:\n"
            report += "-" * 20 + "\n"
            for condition, confidence in analysis['findings'].items():
                if condition != primary_diagnosis[0]:  # Skip primary diagnosis as it's shown above
                    report += f"• {condition}: {confidence*100:.1f}% confidence\n"
            
            # Features
            if analysis['features']:
                report += "\nDETAILED FEATURES:\n"
                report += "-" * 20 + "\n"
                for feature in analysis['features']:
                    report += f"• {feature['name']}:\n"
                    report += f"  - Description: {feature['description']}\n"
                    report += f"  - Significance: {feature['significance']}\n"
            
            # Recommendations
            if analysis['recommendations']:
                report += "\nRECOMMENDATIONS:\n"
                report += "-" * 20 + "\n"
                for rec in analysis['recommendations']:
                    report += f"• [{rec['type']}] {rec['action']} ({rec['urgency']})\n"
            
            report += "\nDISCLAIMER: This analysis is generated by an AI system and should be "
            report += "verified by a qualified radiologist. Clinical correlation is recommended."
            
            self.results_text.setText(report)
            self.status_label.setText("Analysis complete")
        else:
            self.results_text.setText(f"Error during analysis: {analysis.get('error', 'Unknown error')}")
            self.status_label.setText("Analysis failed")

class RadiologyAnalysisWorker(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, ai_system, image_path, image_type):
        super().__init__()
        self.ai_system = ai_system
        self.image_path = image_path
        self.image_type = image_type
    
    def run(self):
        self.progress.emit("Loading models...")
        time.sleep(1)
        
        self.progress.emit("Preprocessing image...")
        time.sleep(1)
        
        self.progress.emit("Analyzing with AI models...")
        analysis = self.ai_system.analyze_image(self.image_path, self.image_type)
        
        self.progress.emit("Generating report...")
        time.sleep(1)
        
        self.finished.emit(analysis)

class PathologyTab(ImageAnalysisTab):
    def __init__(self, parent=None):
        super().__init__(
            "Pathology Analysis",
            "Upload pathology images (gross specimens or histological slides) for automated analysis and classification.",
            parent
        )
        self.initializePathologyUI()
        self.ai_system = PathologyAI()
    
    def initializePathologyUI(self):
        # Add pathology-specific controls
        self.image_type = QComboBox()
        self.image_type.addItems(["Gross Specimen", "H&E Stain"])
        self.image_type.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(assets/dropdown.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        # Insert combobox after the image label
        layout = self.layout()
        layout.insertWidget(2, self.image_type)
    
    def analyze_image(self):
        if not hasattr(self, 'current_image_path'):
            return
        
        self.analyze_btn.setEnabled(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.show()
        
        # Create and start worker thread
        self.worker = PathologyAnalysisWorker(
            self.ai_system, 
            self.current_image_path,
            self.image_type.currentText()
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.analysis_complete)
        self.worker.start()
    
    def update_progress(self, message):
        self.status_label.setText(message)
    
    def analysis_complete(self, analysis):
        self.progress_bar.hide()
        self.analyze_btn.setEnabled(True)
        
        if analysis.get('success', False):
            report = "PATHOLOGY ANALYSIS REPORT\n"
            report += "=" * 50 + "\n\n"
            
            report += f"Image Type: {analysis['image_type']}\n"
            report += f"Urgency Level: {analysis['urgency_level']}\n\n"
            
            # Findings
            report += "FINDINGS:\n"
            report += "-" * 20 + "\n"
            for condition, confidence in analysis['findings'].items():
                report += f"• {condition}: {confidence*100:.1f}% confidence\n"
            
            # Features
            if analysis['features']:
                report += "\nDETAILED FEATURES:\n"
                report += "-" * 20 + "\n"
                for feature in analysis['features']:
                    report += f"• {feature['name']}:\n"
                    report += f"  - Description: {feature['description']}\n"
                    report += f"  - Significance: {feature['significance']}\n"
            
            # Recommendations
            if analysis['recommendations']:
                report += "\nRECOMMENDATIONS:\n"
                report += "-" * 20 + "\n"
                for rec in analysis['recommendations']:
                    report += f"• [{rec['type']}] {rec['action']} ({rec['urgency']})\n"
            
            report += "\nDISCLAIMER: This analysis is generated by an AI system and should be "
            report += "verified by a qualified pathologist. Clinical correlation is recommended."
            
            self.results_text.setText(report)
            self.status_label.setText("Analysis complete")
        else:
            self.results_text.setText(f"Error during analysis: {analysis.get('error', 'Unknown error')}")
            self.status_label.setText("Analysis failed")

class PathologyAnalysisWorker(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, ai_system, image_path, image_type):
        super().__init__()
        self.ai_system = ai_system
        self.image_path = image_path
        self.image_type = image_type
    
    def run(self):
        self.progress.emit("Loading models...")
        time.sleep(1)
        
        self.progress.emit("Preprocessing image...")
        time.sleep(1)
        
        self.progress.emit("Analyzing with AI models...")
        analysis = self.ai_system.analyze_image(self.image_path, self.image_type)
        
        self.progress.emit("Generating report...")
        time.sleep(1)
        
        self.finished.emit(analysis)

class HealthcareGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Advanced Clinical Imaging System')
        self.setMinimumSize(1400, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Add modern header
        header = ModernHeader()
        main_layout.addWidget(header)
        
        # Create content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        
        # Left panel with patient tabs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Patient tabs
        patient_tabs = QTabWidget()
        patient_tabs.setStyleSheet("""
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
        
        for patient in SAMPLE_PATIENTS:
            tab = PatientTab(patient)
            patient_tabs.addTab(tab, f"{patient['name']} ({patient['id']})")
        
        left_layout.addWidget(patient_tabs)
        
        # Right panel with analysis tabs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        analysis_tabs = QTabWidget()
        analysis_tabs.setStyleSheet("""
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
        
        radiology_tab = RadiologyTab()
        pathology_tab = PathologyTab()
        
        analysis_tabs.addTab(radiology_tab, "Radiology")
        analysis_tabs.addTab(pathology_tab, "Pathology")
        
        right_layout.addWidget(analysis_tabs)
        
        # Add panels to content layout
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 2)
        
        # Add content to main layout
        main_layout.addWidget(content)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QWidget {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }
        """)

def main():
    app = QApplication(sys.argv)
    
    # Show splash screen while loading
    splash_pix = QPixmap('splash.png') if os.path.exists('splash.png') else QPixmap(400, 200)
    splash = QSplashScreen(splash_pix)
    splash.show()
    
    # Create and show main window
    window = HealthcareGUI()
    window.show()
    
    # Close splash screen
    splash.finish(window)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
