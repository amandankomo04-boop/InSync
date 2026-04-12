import os
import shutil
import random
from pathlib import Path

def prepare_aesthetic_dataset(target_count=700, train_split=0.7):
    # Paths
    base = Path(r"C:\Users\Amanda\Desktop\coursework\data\images\aesthetics")
    output_train = base / "train"
    output_test = base / "test"

    # Create directories
    output_train.mkdir(parents=True, exist_ok=True)
    output_test.mkdir(parents=True, exist_ok=True)

    categories = [d for d in os.listdir(base) 
                  if os.path.isdir(base / d) and d not in ['train', 'test', 'temp']]

    print(f"--- Reorganising Aesthetic Folders: {categories} ---")

    for cat in categories:
        cat_path = base / cat
        
        # Find all images, including in subfolders
        all_images = []
        for root, dirs, files in os.walk(cat_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.jfif')):
                    all_images.append(Path(root) / file)
        
        # 1. Trim to 700
        if len(all_images) > target_count:
            selected_images = random.sample(all_images, target_count)
        else:
            selected_images = all_images
            print(f"⚠️ Warning: {cat} only has {len(selected_images)} images total.")
        
        random.shuffle(selected_images)
        
        # 2. Split (490 Train / 210 Test)
        split_idx = int(len(selected_images) * train_split)
        train_images = selected_images[:split_idx]
        test_images = selected_images[split_idx:]

        # 3. Create clean subfolders
        (output_train / cat).mkdir(exist_ok=True)
        (output_test / cat).mkdir(exist_ok=True)

        # 4. Copy Files (Flattening the structure)
        for i, img_path in enumerate(train_images):
            
            shutil.copy(img_path, output_train / cat / f"train_{i}_{img_path.name}")
            
        for i, img_path in enumerate(test_images):
            shutil.copy(img_path, output_test / cat / f"test_{i}_{img_path.name}")

        print(f"{cat}: {len(train_images)} to Train | {len(test_images)} to Test")

    print("\nAesthetic folders are now flattened and ready!")

if __name__ == "__main__":
    prepare_aesthetic_dataset()