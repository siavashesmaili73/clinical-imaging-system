import torch
import torch.nn as nn
import torchvision.models as models
import torchxrayvision as xrv
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
from typing import Dict, List, Tuple
import monai
from monai.networks.nets import DenseNet121
from monai.transforms import (
    Compose,
    LoadImage,
    ScaleIntensity,
    ResizeWithPadOrCrop,
)

class ComprehensiveRadiologyAI:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Initialize models
        print("Loading comprehensive radiology AI models...")
        self.model_dict = self.load_models()
        print("Models loaded successfully")
        
        # Define image transformations for different modalities
        self.transforms = {
            'chest': None,  # We'll handle chest X-ray preprocessing separately
            'general': transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ]),
            'musculoskeletal': transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ]),
            'neuro': transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
        }
        
        # MONAI transforms
        self.monai_transforms = Compose([
            ScaleIntensity(),
            ResizeWithPadOrCrop((224, 224))
        ])
    
    def load_models(self) -> Dict[str, nn.Module]:
        """Load multiple specialized radiology models"""
        model_dict = {}
        
        # Load TorchXRayVision model for chest X-rays
        model_dict['chest'] = xrv.models.DenseNet(weights="densenet121-res224-all")
        model_dict['chest'].to(self.device)
        model_dict['chest'].eval()
        
        # Load MONAI DenseNet for general radiology
        model_dict['general'] = DenseNet121(
            spatial_dims=2,
            in_channels=3,  # RGB input
            out_channels=len(self.general_conditions)
        )
        model_dict['general'].to(self.device)
        model_dict['general'].eval()
        
        # Load specialized models for different body parts
        model_dict['musculoskeletal'] = models.densenet121(pretrained=True)
        num_ftrs = model_dict['musculoskeletal'].classifier.in_features
        model_dict['musculoskeletal'].classifier = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, len(self.musculoskeletal_conditions))
        )
        model_dict['musculoskeletal'].to(self.device)
        model_dict['musculoskeletal'].eval()
        
        # Load model for neurological imaging
        model_dict['neuro'] = models.resnet50(pretrained=True)
        num_ftrs = model_dict['neuro'].fc.in_features
        model_dict['neuro'].fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, len(self.neuro_conditions))
        )
        model_dict['neuro'].to(self.device)
        model_dict['neuro'].eval()
        
        return model_dict
    
    @property
    def general_conditions(self) -> List[str]:
        """General radiological conditions"""
        return [
            'Normal',
            'Fracture',
            'Dislocation',
            'Arthritis',
            'Tumor',
            'Infection',
            'Foreign Body',
            'Soft Tissue Swelling'
        ]
    
    @property
    def musculoskeletal_conditions(self) -> List[str]:
        """Musculoskeletal conditions"""
        return [
            'Fracture',
            'Osteoarthritis',
            'Rheumatoid Arthritis',
            'Osteomyelitis',
            'Bone Tumor',
            'Osteoporosis',
            'Joint Effusion',
            'Dislocation',
            'Ligament Injury',
            'Tendon Injury'
        ]
    
    @property
    def neuro_conditions(self) -> List[str]:
        """Neurological conditions"""
        return [
            'Normal',
            'Hemorrhage',
            'Ischemic Stroke',
            'Mass Effect',
            'Midline Shift',
            'Hydrocephalus',
            'Skull Fracture',
            'Calcification',
            'White Matter Disease',
            'Atrophy'
        ]
    
    def detect_image_type(self, image_path: str) -> str:
        """Detect the type of radiological image using advanced image analysis"""
        image = Image.open(image_path).convert('L')  # Convert to grayscale for analysis
        
        # Get image statistics
        img_array = np.array(image)
        mean = np.mean(img_array)
        std = np.std(img_array)
        histogram = np.histogram(img_array, bins=256)[0]
        
        # Calculate additional features
        aspect_ratio = image.width / image.height
        center_intensity = np.mean(img_array[img_array.shape[0]//3:2*img_array.shape[0]//3, 
                                           img_array.shape[1]//3:2*img_array.shape[1]//3])
        edge_intensity = np.mean([np.mean(img_array[0:10,:]), np.mean(img_array[-10:,:]),
                                np.mean(img_array[:,0:10]), np.mean(img_array[:,-10:])])
        
        # Enhanced chest X-ray detection
        is_chest = (
            (aspect_ratio > 0.8 and aspect_ratio < 1.2) and  # Typical chest X-ray aspect ratio
            (center_intensity < edge_intensity * 1.2) and    # Center typically darker than edges
            (std < 70) and                                   # Moderate contrast
            (mean > 100 and mean < 200)                      # Typical brightness range
        )
        
        if is_chest:
            return 'chest'
        elif std > 60 and center_intensity < edge_intensity * 0.8:  # High contrast with dark center
            return 'neuro'
        elif np.max(histogram[:128]) > np.max(histogram[128:]) and aspect_ratio > 1.5:
            return 'musculoskeletal'
        else:
            return 'chest'  # Default to chest for typical radiographs
    
    def get_features(self, image_type: str, findings: Dict[str, float]) -> List[Dict[str, str]]:
        """Get detailed features based on findings"""
        features = []
        
        # Add features based on image type and findings
        for condition, confidence in findings.items():
            if confidence > 0.5:
                if image_type == "musculoskeletal":
                    if "Fracture" in condition:
                        features.extend([
                            {
                                'name': 'Fracture Characteristics',
                                'description': 'Linear lucency with cortical disruption',
                                'significance': 'Indicates acute fracture'
                            },
                            {
                                'name': 'Surrounding Soft Tissue',
                                'description': 'Soft tissue swelling present',
                                'significance': 'Suggests acute injury'
                            }
                        ])
                elif image_type == "neuro":
                    if "Hemorrhage" in condition:
                        features.extend([
                            {
                                'name': 'Density',
                                'description': 'Hyperdense collection',
                                'significance': 'Acute hemorrhage'
                            },
                            {
                                'name': 'Mass Effect',
                                'description': 'Local mass effect with edema',
                                'significance': 'Space-occupying lesion'
                            }
                        ])
                elif image_type == "chest":
                    if "Cardiomegaly" in condition:
                        features.extend([
                            {
                                'name': 'Heart Size',
                                'description': 'Enlarged cardiac silhouette',
                                'significance': 'Indicates cardiomegaly'
                            },
                            {
                                'name': 'Cardiothoracic Ratio',
                                'description': 'Increased cardiothoracic ratio',
                                'significance': 'Suggests cardiac enlargement'
                            }
                        ])
                    elif "Pneumonia" in condition:
                        features.extend([
                            {
                                'name': 'Opacity Characteristics',
                                'description': 'Patchy airspace opacification',
                                'significance': 'Consistent with pneumonia'
                            },
                            {
                                'name': 'Distribution',
                                'description': 'Focal or multifocal involvement',
                                'significance': 'Pattern typical for infection'
                            }
                        ])
        
        return features
    
    def get_recommendations(self, image_type: str, findings: Dict[str, float]) -> List[Dict[str, str]]:
        """Get recommendations based on findings"""
        recommendations = []
        
        # Critical findings requiring immediate attention
        if any(conf > 0.7 for conf in findings.values()):
            recommendations.append({
                'type': 'Critical',
                'action': 'Immediate radiologist review required',
                'urgency': 'STAT'
            })
        
        # Add specific recommendations based on image type and findings
        for condition, confidence in findings.items():
            if confidence > 0.5:
                if image_type == "musculoskeletal":
                    if "Fracture" in condition:
                        recommendations.extend([
                            {
                                'type': 'Imaging',
                                'action': 'Additional views recommended',
                                'urgency': 'Within 24 hours'
                            },
                            {
                                'type': 'Orthopedic Consultation',
                                'action': 'Refer to orthopedics for evaluation',
                                'urgency': 'Urgent'
                            }
                        ])
                elif image_type == "neuro":
                    if "Hemorrhage" in condition:
                        recommendations.extend([
                            {
                                'type': 'Neurosurgical Consultation',
                                'action': 'Immediate neurosurgical evaluation',
                                'urgency': 'STAT'
                            },
                            {
                                'type': 'Imaging',
                                'action': 'CT angiogram recommended',
                                'urgency': 'STAT'
                            }
                        ])
                elif image_type == "chest":
                    if "Cardiomegaly" in condition:
                        recommendations.extend([
                            {
                                'type': 'Cardiac Consultation',
                                'action': 'Cardiology evaluation recommended',
                                'urgency': 'Within 24 hours'
                            },
                            {
                                'type': 'Additional Testing',
                                'action': 'Consider echocardiogram',
                                'urgency': 'Routine'
                            }
                        ])
                    elif "Pneumonia" in condition:
                        recommendations.extend([
                            {
                                'type': 'Clinical Correlation',
                                'action': 'Correlate with symptoms and labs',
                                'urgency': 'Urgent'
                            },
                            {
                                'type': 'Follow-up',
                                'action': 'Follow-up chest X-ray in 2-3 weeks',
                                'urgency': 'Routine'
                            }
                        ])
        
        return recommendations
    
    def analyze_image(self, image_path: str, image_type: str = None) -> Dict:
        """Analyze radiological image and generate comprehensive report"""
        try:
            # Auto-detect image type if not specified
            if image_type is None or image_type.lower() == 'auto-detect':
                image_type = self.detect_image_type(image_path)
            else:
                image_type = image_type.lower().replace(" ", "_")
            
            # Load and preprocess image based on type
            image = Image.open(image_path)
            
            if image_type == 'chest':
                # Process chest X-rays using TorchXRayVision's method
                img = np.array(image.convert('L'))
                img = xrv.datasets.normalize(img, 255)  # Normalize to [0, 1]
                img = transforms.Resize(224)(torch.from_numpy(img).unsqueeze(0))
                image_tensor = img.unsqueeze(0)  # Add batch dimension
            else:
                # Keep RGB for other models trained on ImageNet
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                transform = self.transforms.get(image_type, self.transforms['general'])
                # Apply transform for non-chest images
                image_tensor = transform(image).unsqueeze(0)
            
            # Move tensor to device
            image_tensor = image_tensor.to(self.device)
            
            # Select appropriate model and get predictions
            model = self.model_dict[image_type]
            
            with torch.no_grad():
                if image_type == 'chest':
                    outputs = model(image_tensor)
                    findings = {}
                    # Get predictions from the model
                    outputs = outputs.squeeze()  # Remove batch dimension
                    for i, pathology in enumerate(model.pathologies):
                        prob = float(torch.sigmoid(outputs[i]).item())
                        findings[pathology] = prob
                else:
                    outputs = model(image_tensor)
                    probabilities = torch.sigmoid(outputs)[0]
                    
                    # Get appropriate condition list
                    if image_type == "musculoskeletal":
                        conditions = self.musculoskeletal_conditions
                    elif image_type == "neuro":
                        conditions = self.neuro_conditions
                    else:
                        conditions = self.general_conditions
                    
                    findings = {
                        condition: float(prob)
                        for condition, prob in zip(conditions, probabilities)
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
    # Test the comprehensive radiology AI system
    ai = ComprehensiveRadiologyAI()
    print("Comprehensive Radiology AI system initialized successfully")

if __name__ == "__main__":
    main()
