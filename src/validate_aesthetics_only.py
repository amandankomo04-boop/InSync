import os
import pickle
import torch
import numpy as np
from pathlib import Path
from torchvision import models, transforms
from PIL import Image
from sklearn.metrics import classification_report
from utils import calculate_cosine_similarity
from tqdm import tqdm

# 1. Setup Feature Extractor (Matches Training)
device = torch.device("cpu")
model = models.resnet50(pretrained=True)
model = torch.nn.Sequential(*(list(model.children())[:-1]))
model.to(device).eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_vector(img_path):
    try:
        img = Image.open(img_path).convert('RGB')
        img_t = transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            output = model(img_t)
        return output.squeeze().cpu().numpy()
    except:
        return None

# 2. Path Handling
root_path = Path(r"C:\Users\Amanda\Desktop\coursework")
dna_path = root_path / "models" / "system_dna.pkl"
# Target the test folder specifically
test_path = root_path / "data" / "images" / "aesthetics" / "test"

if __name__ == "__main__":
    if not dna_path.exists():
        print(f"❌ Error: system_dna.pkl not found at {dna_path}")
    elif not test_path.exists():
        print(f"❌ Error: Test folder not found at {test_path}")
    else:
        # Load the DNA
        with open(dna_path, "rb") as f:
            knowledge = pickle.load(f)
        
        centroids = knowledge.get("aesthetic_centroids", {})
        categories = list(centroids.keys())
        
        if not categories:
            print("❌ Error: No Aesthetic DNA found in the pickle file. Run training first.")
        else:
            y_true = []
            y_pred = []

            print(f"🚀 Validating Aesthetic Stream: {categories}")

            for category in categories:
                cat_dir = test_path / category
                if not cat_dir.exists():
                    print(f"⚠️ Skipping {category}: Folder not found in test set.")
                    continue
                    
                images = [f for f in os.listdir(cat_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
                
                for img_name in tqdm(images, desc=f"Testing {category}"):
                    img_path = cat_dir / img_name
                    vector = get_vector(img_path)
                    
                    if vector is not None:
                        # Find the best match among all aesthetic centroids
                        scores = {cat: calculate_cosine_similarity(vector, vec) for cat, vec in centroids.items()}
                        predicted_cat = max(scores, key=scores.get)
                        
                        y_true.append(category)
                        y_pred.append(predicted_cat)

            # 3. Final Report Generation
            print(f"\n--- Aesthetic Style Performance Report ---")
            print(classification_report(y_true, y_pred, target_names=categories, zero_division=0))