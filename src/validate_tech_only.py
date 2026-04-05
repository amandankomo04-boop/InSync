import os
import pickle
import torch
import numpy as np
from pathlib import Path
from torchvision import models, transforms
from PIL import Image
from utils import calculate_cosine_similarity
from tqdm import tqdm
from sklearn.metrics import classification_report

# 1. Setup
device = torch.device("cpu")
model = models.resnet50(pretrained=True)
model = torch.nn.Sequential(*(list(model.children())[:-1]))
model.to(device).eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# 2. Paths
root_path = Path(r"C:\Users\Amanda\Desktop\coursework")
dna_path = root_path / "models" / "system_dna.pkl"
tech_test_path = root_path / "data" / "images" / "niche" / "test" / "tech"

if not tech_test_path.exists():
    print(f"❌ Folder missing: {tech_test_path}")
else:
    with open(dna_path, "rb") as f:
        knowledge = pickle.load(f)
    
    centroids = knowledge["niche_centroids"]
    
    # Handle naming case sensitivity
    if "tech" in centroids:
        tech_vector = centroids["tech"]
    elif "Tech" in centroids:
        tech_vector = centroids["Tech"]
    else:
        tech_vector = None

    if tech_vector is None:
        print("❌ 'Tech' DNA not found in system_dna.pkl.")
    else:
        images = [f for f in os.listdir(tech_test_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        print(f"🚀 Found {len(images)} images. Validating...")

        y_true = []
        y_pred = []

        for img_name in tqdm(images):
            try:
                img = Image.open(tech_test_path / img_name).convert('RGB')
                img_t = transform(img).unsqueeze(0).to(device)
                with torch.no_grad():
                    feat = model(img_t).squeeze().cpu().numpy()
                
                score = calculate_cosine_similarity(feat, tech_vector)
                
                y_true.append("tech")
                # If similarity is high, we count it as a correct 'tech' prediction
                if score > 0.5:
                    y_pred.append("tech")
                else:
                    y_pred.append("other")
            except:
                continue

        # 3. Final Report Generation
        print(f"\n--- Formal Tech Performance Report ---")
        # We use labels=["tech", "other"] so the table knows what to show
        print(classification_report(y_true, y_pred, labels=["tech", "other"], zero_division=0))