import os
import shutil
import random
from pathlib import Path
from tqdm import tqdm

def flatten_and_trim_niches(train_limit=3000):
    # Paths
    base_path = Path(r"C:\Users\Amanda\Desktop\coursework\data\images\niche\split\train")
    
    if not base_path.exists():
        print(f"ERROR: Cannot find path: {base_path}")
        return

    # Get categories 
    niches = [d for d in os.listdir(base_path) if os.path.isdir(base_path / d)]
    print(f"Processing Niches: {niches}")

    for niche in niches:
        niche_dir = base_path / niche
        print(f"Dissolving subfolders in: {niche}")
        
        # 1. Recursive search for ALL images in ANY subfolder
        all_found_images = []
        for root, dirs, files in os.walk(niche_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif')):
                    all_found_images.append(Path(root) / file)
        
        if not all_found_images:
            print(f"No images found in {niche}. Skipping.")
            continue

        # 2. Select 3,000 images
        if len(all_found_images) > train_limit:
            selected_images = random.sample(all_found_images, train_limit)
        else:
            selected_images = all_found_images
            print(f"{niche} only has {len(all_found_images)} images. Using all.")

        # 3. Create a temporary "Holding Area" outside the niche folder
        temp_holding = base_path / f"temp_holding_{niche}"
        temp_holding.mkdir(exist_ok=True)

        # 4. Copy selected images to holding area
        for i, img_path in enumerate(tqdm(selected_images, desc=f"  Extracting {niche}", leave=False)):
            new_name = f"{niche}_{i}{img_path.suffix}"
            shutil.copy(img_path, temp_holding / new_name)

        # 5. Clear original niche folder
        shutil.rmtree(niche_dir)
        
        # 6. Move the holding area back to be the niche folder
        shutil.move(str(temp_holding), str(niche_dir))
        
        print(f"{niche} is now flat with {len(selected_images)} images.")

    print("\nDone! Your niche folders are now clean and flattened.")

if __name__ == "__main__":
    flatten_and_trim_niches()