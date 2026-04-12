import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import pickle
import os
from pathlib import Path
from tqdm import tqdm

# 1. Setup Feature Extractor
device = torch.device("cpu")
print(f"🖥️ Using CPU for Aesthetic Style Extraction")

resnet = models.resnet50(pretrained=True)
feature_extractor = torch.nn.Sequential(*(list(resnet.children())[:-1]))
feature_extractor.to(device).eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_vector(img_path):
    try:
        img = Image.open(img_path).convert('RGB')
        tensor = preprocess(img).unsqueeze(0).to(device)
        with torch.no_grad():
            return feature_extractor(tensor).flatten().numpy()
    except:
        return None

# 2. Paths 
root = Path(r"C:\Users\Amanda\Desktop\coursework")
aesthetic_base = root / "data" / "images" / "aesthetics" / "train"

if not aesthetic_base.exists():
    print(f"Warning: 'train' folder not found. Checking main aesthetic folder...")
    aesthetic_base = root / "data" / "images" / "aesthetics"

# 3. Training Logic
if __name__ == "__main__":
    print(f"Targeted Aesthetic Training Started at: {aesthetic_base}")
    
    # Get Style Folders 
    categories = [d for d in os.listdir(aesthetic_base) 
                 if os.path.isdir(aesthetic_base / d) and d not in ['train', 'test', 'temp']]
    
    aesthetic_dna = {}

    for cat in categories:
        print(f"\nExtracting Style DNA: {cat}")
        cat_dir = aesthetic_base / cat
        images = [f for f in os.listdir(cat_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
        
        vectors = []
        for img_name in tqdm(images[:500], desc=f"Analyzing {cat}"):
            vec = get_vector(cat_dir / img_name)
            if vec is not None:
                vectors.append(vec)
        
        if vectors:
            aesthetic_dna[cat] = np.mean(vectors, axis=0)
            print(f"Created Centroid for {cat}")

    # 4. Merging with system_dna.pkl
    dna_path = root / "models" / "system_dna.pkl"
    
    if dna_path.exists():
        with open(dna_path, "rb") as f:
            existing_data = pickle.load(f)
        
        # Update only the aesthetic part
        existing_data["aesthetic_centroids"] = aesthetic_dna
        
        with open(dna_path, "wb") as f:
            pickle.dump(existing_data, f)
        print(f"\nSUCCESS: Aesthetic DNA merged into system_dna.pkl")
    else:
        # If the file didn't exist for some reason, create a new one
        with open(dna_path, "wb") as f:
            pickle.dump({"niche_centroids": {}, "aesthetic_centroids": aesthetic_dna}, f)
        print(f"\nCreated NEW system_dna.pkl with Aesthetic data only.")