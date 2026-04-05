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
# If it's a Scikit-Learn model, it usually has a .classes_ attribute
if hasattr(model, 'classes_'):
    print("Detected Classes:", model.classes_)

# If it's a PyTorch/FastAI model, look for 'dls.vocab' or 'model.meta'
elif hasattr(model, 'dls'):
    print("FastAI Vocab:", model.dls.vocab)

# 4. If it's a dictionary (common for PyTorch state_dicts)
elif isinstance(model, dict):
    print("Keys in the dictionary:", model.keys())