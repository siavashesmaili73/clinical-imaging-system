import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from typing import Dict, List, Tuple

class PathologyAI:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize models
        print("Loading pathology AI models...")
        self.model_dict = self.load_models()
        print("Models loaded successfully")
        
        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def load_models(self) -> Dict[str, nn.Module]:
        """Load pre-trained models for different types of pathology analysis"""
        model_dict = {}
        
        # Load DenseNet for H&E analysis
        model_dict['he'] = models.densenet121(pretrained=True)
        num_ftrs = model_dict['he'].classifier.in_features
        model_dict['he'].classifier = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, len(self.he_classes))
        )
        model_dict['he'].to(self.device)
        model_dict['he'].eval()
        
        # Load ResNet for gross specimen analysis
        model_dict['gross'] = models.resnet50(pretrained=True)
        num_ftrs = model_dict['gross'].fc.in_features
        model_dict['gross'].fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, len(self.gross_classes))
        )
        model_dict['gross'].to(self.device)
        model_dict['gross'].eval()
        
        return model_dict
    
    @property
    def he_classes(self) -> List[str]:
        """H&E stain classification categories"""
        return [
            'Normal',
            'Adenocarcinoma',
            'Squamous Cell Carcinoma',
            'Small Cell Carcinoma',
            'Chronic Inflammation',
            'Acute Inflammation',
            'Organizing Pneumonia',
            'Fibrosis',
            'Metastatic Disease',
            'Lymphoma'
        ]
    
    @property
    def gross_classes(self) -> List[str]:
        """Gross specimen classification categories"""
        return [
            'Normal Lung',
            'Consolidation',
            'Mass/Nodule',
            'Emphysema',
            'Hemorrhage',
            'Necrosis',
            'Pleural Effusion',
            'Abscess',
            'Granuloma',
            'Infarct'
        ]
    
    def get_features(self, image_type: str, findings: Dict[str, float]) -> List[Dict[str, str]]:
        """Get detailed features based on findings"""
        features = []
        
        if image_type == "H&E Stain":
            if findings.get('Adenocarcinoma', 0) > 0.5:
                features.extend([
                    {
                        'name': 'Glandular Formation',
                        'description': 'Presence of abnormal glandular structures',
                        'significance': 'Characteristic of adenocarcinoma'
                    },
                    {
                        'name': 'Nuclear Atypia',
                        'description': 'Enlarged, hyperchromatic nuclei with prominent nucleoli',
                        'significance': 'Indicates malignant transformation'
                    },
                    {
                        'name': 'Invasion Pattern',
                        'description': 'Lepidic, acinar, papillary, or solid growth patterns',
                        'significance': 'Helps determine tumor grade and subtype'
                    }
                ])
            
            if findings.get('Organizing Pneumonia', 0) > 0.5:
                features.extend([
                    {
                        'name': 'Masson Bodies',
                        'description': 'Fibroblastic plugs within alveolar spaces',
                        'significance': 'Characteristic of organizing pneumonia'
                    },
                    {
                        'name': 'Inflammatory Infiltrate',
                        'description': 'Mixed inflammatory cells in alveolar walls',
                        'significance': 'Indicates active inflammatory process'
                    }
                ])
        
        elif image_type == "Gross Specimen":
            if findings.get('Mass/Nodule', 0) > 0.5:
                features.extend([
                    {
                        'name': 'Mass Characteristics',
                        'description': 'Solid, well-circumscribed lesion',
                        'significance': 'Suggests neoplastic process'
                    },
                    {
                        'name': 'Cut Surface',
                        'description': 'Tan-white with areas of necrosis',
                        'significance': 'Common in malignant tumors'
                    }
                ])
            
            if findings.get('Consolidation', 0) > 0.5:
                features.extend([
                    {
                        'name': 'Texture',
                        'description': 'Firm, hepatized appearance',
                        'significance': 'Indicates airspace filling'
                    },
                    {
                        'name': 'Distribution',
                        'description': 'Patchy or lobar involvement',
                        'significance': 'Helps determine underlying process'
                    }
                ])
        
        return features
    
    def get_recommendations(self, image_type: str, findings: Dict[str, float]) -> List[Dict[str, str]]:
        """Get recommendations based on findings"""
        recommendations = []
        
        # High confidence threshold for critical findings
        if any(conf > 0.7 for conf in findings.values()):
            recommendations.append({
                'type': 'Critical',
                'action': 'Immediate pathologist review required',
                'urgency': 'STAT'
            })
        
        if image_type == "H&E Stain":
            if findings.get('Adenocarcinoma', 0) > 0.5:
                recommendations.extend([
                    {
                        'type': 'Additional Stains',
                        'action': 'Perform TTF-1 and Napsin-A immunostains',
                        'urgency': 'Within 24 hours'
                    },
                    {
                        'type': 'Molecular Testing',
                        'action': 'Order EGFR, ALK, ROS1, and PD-L1 testing',
                        'urgency': 'Within 48 hours'
                    }
                ])
            
            if findings.get('Lymphoma', 0) > 0.5:
                recommendations.extend([
                    {
                        'type': 'Flow Cytometry',
                        'action': 'Submit fresh tissue for flow cytometric analysis',
                        'urgency': 'STAT'
                    },
                    {
                        'type': 'Immunohistochemistry',
                        'action': 'Perform lymphoma panel (CD20, CD3, CD5, CD10, etc.)',
                        'urgency': 'Within 24 hours'
                    }
                ])
        
        elif image_type == "Gross Specimen":
            if findings.get('Mass/Nodule', 0) > 0.5:
                recommendations.extend([
                    {
                        'type': 'Sampling',
                        'action': 'Submit multiple sections including margins',
                        'urgency': 'Routine'
                    },
                    {
                        'type': 'Photography',
                        'action': 'Document gross findings with photographs',
                        'urgency': 'Before sectioning'
                    }
                ])
            
            if findings.get('Necrosis', 0) > 0.5:
                recommendations.extend([
                    {
                        'type': 'Cultures',
                        'action': 'Submit tissue for microbiological studies',
                        'urgency': 'STAT'
                    }
                ])
        
        return recommendations
    
    def analyze_image(self, image_path: str, image_type: str) -> Dict:
        """Analyze pathology image and generate comprehensive report"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Select appropriate model
            if image_type == "H&E Stain":
                model = self.model_dict['he']
                classes = self.he_classes
            else:  # Gross Specimen
                model = self.model_dict['gross']
                classes = self.gross_classes
            
            # Get predictions
            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.sigmoid(outputs)[0]
            
            # Convert to dictionary
            findings = {
                class_name: float(prob)
                for class_name, prob in zip(classes, probabilities)
            }
            
            # Filter findings by confidence
            significant_findings = {
                k: v for k, v in findings.items() if v > 0.2
            }
            
            # Get detailed features and recommendations
            features = self.get_features(image_type, significant_findings)
            recommendations = self.get_recommendations(image_type, significant_findings)
            
            # Determine urgency level
            urgency = 'STAT' if any(conf > 0.7 for conf in findings.values()) else 'ROUTINE'
            
            return {
                'success': True,
                'image_type': image_type,
                'findings': significant_findings,
                'features': features,
                'recommendations': recommendations,
                'urgency_level': urgency
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def main():
    # Test the pathology AI system
    ai = PathologyAI()
    print("Pathology AI system initialized successfully")

if __name__ == "__main__":
    main()
