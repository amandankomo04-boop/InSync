import joblib
import torch 
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import pickle
import os
from pathlib import Path

# 1. Load the model
current_file = Path(__file__).resolve()
root_path = current_file.parent.parent
model_path = root_path / "models" / "system_dna.pkl"
model = joblib.load(model_path)

# 2. Check the type of object
print(f"Model Type: {type(model)}")

# 3. Look for Class Labels
if hasattr(model, 'classes_'):
    print("Detected Classes:", model.classes_)

elif hasattr(model, 'dls'):
    print("FastAI Vocab:", model.dls.vocab)

elif isinstance(model, dict):
    print("Keys in the dictionary:", model.keys())