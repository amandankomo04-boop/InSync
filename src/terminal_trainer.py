import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import pickle
import os
from pathlib import Path
from tqdm import tqdm

# 1. Initialize the ResNet-50 Feature Extractor
# Running on CPU for the Dell Latitude 7390
device = torch.device("cpu") 
print(f"🖥️ System using: {device}")

# Load Pre-trained ResNet-50 and remove the final classification layer
resnet = models.resnet50(pretrained=True)
feature_extractor = torch.nn.Sequential(*(list(resnet.children())[:-1]))
feature_extractor.to(device)
feature_extractor.eval()

# Standard Image Pre-processing for ResNet
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_vector(img_path):
    """Converts a single image into a 2048-dimensional feature vector."""
    try:
        img = Image.open(img_path).convert('RGB')
        tensor = preprocess(img).unsqueeze(0).to(device)
        with torch.no_grad():
            # Extract features and flatten to 1D array
            vector = feature_extractor(tensor).flatten().numpy()
        return vector
    except Exception as e:
        # Silently skip corrupted images
        return None

# 2. Process Niche DNA (Using the flattened 'train' folder)
def process_niche_split(base_path):
    niche_knowledge = {}
    train_path = Path(base_path) / "train"
    
    if not train_path.exists():
        print(f"❌ Error: Niche train path not found at {train_path}")
        return {}

    categories = [d for d in os.listdir(train_path) if os.path.isdir(train_path / d)]
    
    for cat in categories:
        print(f"\n🧬 Learning Niche DNA: {cat}...")
        cat_dir = train_path / cat
        # Using all 3,000 images in your flattened folder
        images = [f for f in os.listdir(cat_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
        
        vectors = []
        for img_name in tqdm(images, desc=f"Extracting {cat}"):
            vec = get_vector(cat_dir / img_name)
            if vec is not None: 
                vectors.append(vec)
        
        # Calculate the mathematical average (Centroid) for this Niche
        if vectors:
            niche_knowledge[cat] = np.mean(vectors, axis=0)
        
    return niche_knowledge

# 3. Process Aesthetic DNA (Using the flattened 'train' folder)
def process_aesthetic(base_path):
    aesthetic_knowledge = {}
    train_path = Path(base_path) / "train"
    
    if not train_path.exists():
        print(f"❌ Error: Aesthetic train path not found at {train_path}")
        return {}

    categories = [d for d in os.listdir(train_path) if os.path.isdir(train_path / d)]
    
    for cat in categories:
        print(f"\n🎨 Extracting Aesthetic Style: {cat}...")
        cat_dir = train_path / cat
        # Using the 490 images from your 70/30 split
        images = [f for f in os.listdir(cat_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif'))]
        
        vectors = []
        for img_name in tqdm(images, desc=f"Extracting {cat}"):
            vec = get_vector(cat_dir / img_name)
            if vec is not None: 
                vectors.append(vec)
            
        if vectors:
            aesthetic_knowledge[cat] = np.mean(vectors, axis=0)
        
    return aesthetic_knowledge

# --- EXECUTION PHASE ---
if __name__ == "__main__":
    print("🚀 --- Starting System DNA Extraction --- 🚀")

    # Define Absolute Paths for stability on Windows
    root = Path(r"C:\Users\Amanda\Desktop\coursework")
    n_path = root / "data" / "images" / "niche"
    a_path = root / "data" / "images" / "aesthetic"
    m_path = root / "models"

    # Run the extraction
    niche_dna = process_niche_split(n_path)
    aesthetic_dna = process_aesthetic(a_path)

    # Save the Knowledge Base
    m_path.mkdir(exist_ok=True)
    save_file = m_path / "system_dna.pkl"

    with open(save_file, "wb") as f:
        pickle.dump({
            "niche_centroids": niche_dna, 
            "aesthetic_centroids": aesthetic_dna
        }, f)

    print(f"\n✅ SUCCESS: Serialized DNA saved to {save_file}")
    print("Next step: Run 'py src/validate_system.py' to generate your BSc report metrics.")