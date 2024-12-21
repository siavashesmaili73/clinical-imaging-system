import os
import sys
import time
import torch
import numpy as np
import pandas as pd
from PIL import Image
import torchxrayvision as xrv
from datetime import datetime
from tqdm import tqdm

class AdvancedRadiologyAI:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize model
        print("Loading AI models...")
        self.model = self.load_model()
        self.model = self.model.to(self.device)
        print("Model loaded successfully")
        
        # Define standard image size
        self.image_size = (224, 224)

    def load_model(self):
        """Load pre-trained model"""
        print("Loading TorchXRayVision model...")
        model = xrv.models.DenseNet(weights="densenet121-res224-all")
        model.eval()
        return model

    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        print("\nPreprocessing image...")
        try:
            # Load image
            image = Image.open(image_path).convert('L')  # Convert directly to grayscale
            
            # Resize to model's expected size
            image = image.resize(self.image_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            image_np = np.array(image)
            
            # Apply TorchXRayVision preprocessing
            img = xrv.datasets.normalize(image_np, 255)
            
            # Add batch and channel dimensions
            img = torch.from_numpy(img).unsqueeze(0).unsqueeze(0)
            
            # Move to device
            img = img.to(self.device)
            
            return img
            
        except Exception as e:
            print(f"Error in preprocessing: {str(e)}")
            raise

    def analyze_image(self, image_path):
        """Perform thorough image analysis"""
        try:
            start_time = time.time()
            
            # Process image
            img = self.preprocess_image(image_path)
            
            print("\nAnalyzing image...")
            with torch.no_grad():
                output = self.model(img)
            
            # Get predictions and pathology names
            predictions = {
                name: float(pred) for name, pred in 
                zip(self.model.pathologies, output[0].cpu())
            }
            
            # Generate comprehensive report
            analysis = self.generate_comprehensive_report(predictions)
            
            # Add analysis time
            analysis_time = time.time() - start_time
            analysis['analysis_time'] = analysis_time
            analysis['success'] = True
            
            return analysis
            
        except Exception as e:
            return {
                'error': f"Error analyzing image: {str(e)}",
                'success': False
            }

    def generate_comprehensive_report(self, predictions):
        """Generate detailed clinical report"""
        report = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'findings': [],
            'recommendations': [],
            'urgency_level': 'ROUTINE',
            'confidence_scores': {},
            'detailed_analysis': {}
        }
        
        # Process predictions
        for condition, probability in predictions.items():
            confidence = probability * 100
            if confidence > 20:  # Include findings with >20% confidence
                finding = {
                    'condition': condition,
                    'confidence': confidence,
                    'description': self.get_condition_description(condition),
                    'recommendations': self.get_recommendations(condition, confidence)
                }
                report['findings'].append(finding)
                report['confidence_scores'][condition] = confidence
        
        # Sort findings by confidence
        report['findings'].sort(key=lambda x: x['confidence'], reverse=True)
        
        # Determine urgency level
        report['urgency_level'] = self.determine_urgency(report['findings'])
        
        # Generate action plan
        report['action_plan'] = self.generate_action_plan(report['findings'])
        
        # Add differential diagnoses
        report['differential_diagnoses'] = self.generate_differential_diagnoses(report['findings'])
        
        return report

    def get_condition_description(self, condition):
        """Get detailed description of radiological findings"""
        descriptions = {
            'Cardiomegaly': {
                'definition': 'Enlargement of the heart',
                'appearance': 'Increased cardiothoracic ratio >0.5',
                'clinical_significance': 'May indicate underlying heart disease',
                'common_causes': [
                    'Hypertension',
                    'Coronary artery disease',
                    'Valvular heart disease',
                    'Cardiomyopathy'
                ]
            },
            'Edema': {
                'definition': 'Fluid accumulation in lung tissues',
                'appearance': 'Bilateral opacities, often with peripheral distribution',
                'clinical_significance': 'Indicates fluid overload or heart failure',
                'common_causes': [
                    'Congestive heart failure',
                    'Renal failure',
                    'Fluid overload',
                    'Hypoalbuminemia'
                ]
            },
            'Pneumonia': {
                'definition': 'Infection/inflammation of lung tissue',
                'appearance': 'Focal or diffuse opacities, often with air bronchograms',
                'clinical_significance': 'Requires prompt antibiotic treatment',
                'common_causes': [
                    'Bacterial infection',
                    'Viral infection',
                    'Aspiration',
                    'Hospital-acquired infection'
                ]
            },
            'Atelectasis': {
                'definition': 'Collapse of lung tissue',
                'appearance': 'Volume loss with shift of fissures/mediastinum',
                'clinical_significance': 'May impair oxygenation',
                'common_causes': [
                    'Post-operative',
                    'Bronchial obstruction',
                    'Poor inspiratory effort',
                    'Pleural effusion'
                ]
            },
            'Pleural Effusion': {
                'definition': 'Fluid in pleural space',
                'appearance': 'Blunting of costophrenic angles, fluid levels',
                'clinical_significance': 'May indicate underlying disease',
                'common_causes': [
                    'Heart failure',
                    'Malignancy',
                    'Infection',
                    'Pulmonary embolism'
                ]
            }
        }
        
        return descriptions.get(condition, {
            'definition': 'Radiological finding',
            'appearance': 'Varies',
            'clinical_significance': 'Requires clinical correlation',
            'common_causes': ['Multiple possible etiologies']
        })

    def get_recommendations(self, condition, confidence):
        """Get detailed clinical recommendations based on findings"""
        if confidence < 50:
            return [{
                'type': 'Clinical',
                'action': 'Correlate with clinical findings',
                'urgency': 'Routine'
            }]
        
        recommendations = {
            'Cardiomegaly': [
                {
                    'type': 'Imaging',
                    'action': 'Obtain echocardiogram',
                    'urgency': 'Within 1 week'
                },
                {
                    'type': 'Consultation',
                    'action': 'Cardiology referral',
                    'urgency': 'Within 1 week'
                },
                {
                    'type': 'Laboratory',
                    'action': 'BNP, troponin, basic metabolic panel',
                    'urgency': 'Within 24 hours'
                }
            ],
            'Pneumonia': [
                {
                    'type': 'Treatment',
                    'action': 'Start empiric antibiotics',
                    'urgency': 'Immediate'
                },
                {
                    'type': 'Laboratory',
                    'action': 'Blood cultures, CBC, CRP',
                    'urgency': 'Immediate'
                },
                {
                    'type': 'Monitoring',
                    'action': 'Pulse oximetry monitoring',
                    'urgency': 'Continuous'
                }
            ],
            'Pleural Effusion': [
                {
                    'type': 'Imaging',
                    'action': 'Consider chest ultrasound',
                    'urgency': 'Within 24 hours'
                },
                {
                    'type': 'Procedure',
                    'action': 'Consider thoracentesis if large',
                    'urgency': 'Within 24-48 hours'
                },
                {
                    'type': 'Laboratory',
                    'action': 'Basic metabolic panel, LDH, protein',
                    'urgency': 'Within 24 hours'
                }
            ]
        }
        
        return recommendations.get(condition, [{
            'type': 'Clinical',
            'action': 'Clinical correlation recommended',
            'urgency': 'As needed'
        }])

    def determine_urgency(self, findings):
        """Determine overall urgency level based on findings"""
        urgent_conditions = {
            'Pneumothorax': 90,
            'Pneumonia': 80,
            'Pulmonary Edema': 85,
            'Mass': 75
        }
        
        for finding in findings:
            condition = finding['condition']
            confidence = finding['confidence']
            
            if condition in urgent_conditions and confidence > urgent_conditions[condition]:
                return 'STAT'
            elif confidence > 70:
                return 'URGENT'
        
        return 'ROUTINE'

    def generate_action_plan(self, findings):
        """Generate structured action plan based on findings"""
        plan = {
            'immediate_actions': [],
            'short_term_actions': [],
            'long_term_actions': [],
            'monitoring_plan': []
        }
        
        for finding in findings:
            if finding['confidence'] > 70:
                plan['immediate_actions'].extend([
                    rec for rec in finding['recommendations'] 
                    if rec['urgency'] == 'Immediate'
                ])
            elif finding['confidence'] > 50:
                plan['short_term_actions'].extend([
                    rec for rec in finding['recommendations']
                    if 'within' in rec['urgency'].lower()
                ])
            else:
                plan['long_term_actions'].extend([
                    rec for rec in finding['recommendations']
                    if rec['urgency'] == 'Routine'
                ])
        
        # Add monitoring plan based on findings
        plan['monitoring_plan'] = self.generate_monitoring_plan(findings)
        
        return plan

    def generate_monitoring_plan(self, findings):
        """Generate monitoring plan based on findings"""
        monitoring_plan = []
        
        for finding in findings:
            if finding['confidence'] > 50:
                if 'Pneumonia' in finding['condition']:
                    monitoring_plan.append({
                        'parameter': 'Respiratory status',
                        'frequency': 'Every 4 hours',
                        'duration': '48-72 hours',
                        'specific_measures': [
                            'Oxygen saturation',
                            'Respiratory rate',
                            'Work of breathing'
                        ]
                    })
                elif 'Cardiomegaly' in finding['condition']:
                    monitoring_plan.append({
                        'parameter': 'Cardiovascular status',
                        'frequency': 'Every shift',
                        'duration': 'Until stable',
                        'specific_measures': [
                            'Blood pressure',
                            'Heart rate',
                            'Daily weights',
                            'Fluid balance'
                        ]
                    })
        
        return monitoring_plan

    def generate_differential_diagnoses(self, findings):
        """Generate differential diagnoses based on findings"""
        differentials = []
        
        # Group related findings
        related_findings = {}
        for finding in findings:
            if finding['confidence'] > 30:
                system = self.get_body_system(finding['condition'])
                if system not in related_findings:
                    related_findings[system] = []
                related_findings[system].append(finding)
        
        # Generate differentials for each system
        for system, system_findings in related_findings.items():
            differentials.extend(
                self.get_system_differential_diagnoses(system, system_findings)
            )
        
        return differentials

    def get_body_system(self, condition):
        """Map condition to body system"""
        system_mapping = {
            'Cardiomegaly': 'Cardiovascular',
            'Edema': 'Cardiovascular',
            'Pneumonia': 'Respiratory',
            'Atelectasis': 'Respiratory',
            'Pleural Effusion': 'Respiratory',
            'Mass': 'Neoplastic',
            'Nodule': 'Neoplastic'
        }
        return system_mapping.get(condition, 'Other')

    def get_system_differential_diagnoses(self, system, findings):
        """Generate system-specific differential diagnoses"""
        differentials = []
        
        if system == 'Cardiovascular':
            if any('Cardiomegaly' in f['condition'] for f in findings):
                differentials.extend([
                    {
                        'diagnosis': 'Hypertensive Heart Disease',
                        'likelihood': 'High',
                        'supporting_findings': ['Cardiomegaly'],
                        'next_steps': ['Check blood pressure', 'Echocardiogram']
                    },
                    {
                        'diagnosis': 'Dilated Cardiomyopathy',
                        'likelihood': 'Medium',
                        'supporting_findings': ['Cardiomegaly', 'Possible edema'],
                        'next_steps': ['BNP', 'Echocardiogram']
                    }
                ])
        
        elif system == 'Respiratory':
            if any('Pneumonia' in f['condition'] for f in findings):
                differentials.extend([
                    {
                        'diagnosis': 'Community Acquired Pneumonia',
                        'likelihood': 'High',
                        'supporting_findings': ['Consolidation', 'Possible effusion'],
                        'next_steps': ['Sputum culture', 'Blood cultures']
                    },
                    {
                        'diagnosis': 'Viral Pneumonia',
                        'likelihood': 'Medium',
                        'supporting_findings': ['Ground glass opacities'],
                        'next_steps': ['Viral panel', 'O2 saturation monitoring']
                    }
                ])
        
        return differentials

def main():
    if len(sys.argv) != 2:
        print("Usage: python advanced_radiology_ai.py <path_to_image>")
        return
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return
    
    # Initialize AI system
    print("\nInitializing Advanced Radiology AI System...")
    ai_system = AdvancedRadiologyAI()
    
    # Analyze image
    print(f"\nAnalyzing image: {image_path}")
    analysis = ai_system.analyze_image(image_path)
    
    if analysis.get('success', False):
        # Print analysis results
        print("\n" + "="*50)
        print("RADIOLOGY AI ANALYSIS REPORT")
        print("="*50)
        print(f"\nAnalysis completed in {analysis['analysis_time']:.2f} seconds")
        print(f"Urgency Level: {analysis['urgency_level']}")
        
        print("\nKEY FINDINGS:")
        for finding in analysis['findings']:
            print(f"\n• {finding['condition']}:")
            print(f"  - Confidence: {finding['confidence']:.1f}%")
            print(f"  - Description: {finding['description']['definition']}")
            print("  - Recommendations:")
            for rec in finding['recommendations']:
                print(f"    * {rec['action']} ({rec['urgency']})")
        
        print("\nACTION PLAN:")
        if analysis['action_plan']['immediate_actions']:
            print("\nImmediate Actions Required:")
            for action in analysis['action_plan']['immediate_actions']:
                print(f"• {action['action']}")
        
        print("\nDIFFERENTIAL DIAGNOSES:")
        for diff in analysis['differential_diagnoses']:
            print(f"\n• {diff['diagnosis']}:")
            print(f"  - Likelihood: {diff['likelihood']}")
            print(f"  - Supporting Findings: {', '.join(diff['supporting_findings'])}")
            print(f"  - Next Steps: {', '.join(diff['next_steps'])}")
        
        print("\nMONITORING PLAN:")
        for plan in analysis['action_plan']['monitoring_plan']:
            print(f"\n• {plan['parameter']}:")
            print(f"  - Frequency: {plan['frequency']}")
            print(f"  - Duration: {plan['duration']}")
            print(f"  - Measures: {', '.join(plan['specific_measures'])}")
        
        print("\nDISCLAIMER: This analysis is generated by an AI system and should be")
        print("verified by a qualified radiologist. Clinical correlation is recommended.")
        
    else:
        print("\nError during analysis:", analysis.get('error', 'Unknown error'))

if __name__ == "__main__":
    main()
