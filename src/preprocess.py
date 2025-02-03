"""
preprocess.py

This script processes Pokémon images to generate grayscale silhouettes.

1. OpenCV Method:
   - Supports images with transparency (RGBA).
   - Extracts transparency (alpha) and applies thresholding.
   - Resizes and centers the silhouette on a 256x256 white background.

Dependencies:
- cv2 (OpenCV)
- numpy
"""

from pathlib import Path
import cv2
import numpy as np

def create_silhouette_opencv(input_folder, output_folder, threshold=1, target_size=(256, 256), scale_factor=0.75):
    input_path = Path(input_folder)
    output_path = Path(output_folder) / "BulbapediaGrayscaleImages"
    output_path.mkdir(parents=True, exist_ok=True)

    for file in input_path.iterdir():
        if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            try:
                # Read the image with the alpha channel (supports transparency)
                img = cv2.imread(str(file), cv2.IMREAD_UNCHANGED)

                if img is None:
                    print(f"Skipping file {file.name}: Unable to read")
                    continue

                original_h, original_w = img.shape[:2]

                # Check if image has 4 channels (RGBA)
                if img.shape[2] == 4:
                    # Extract the alpha channel for transparency handling
                    alpha = img[:, :, 3]

                    # Create a binary mask based on transparency
                    _, mask = cv2.threshold(alpha, threshold, 255, cv2.THRESH_BINARY)

                else:
                    # If no alpha channel, assume a white background
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

                # Invert mask to make Pokémon black
                silhouette = cv2.bitwise_not(mask)

                # Compute new dimensions while keeping aspect ratio
                scale = min((target_size[0] * scale_factor) / original_w, (target_size[1] * scale_factor) / original_h)
                new_w, new_h = int(original_w * scale), int(original_h * scale)

                # Resize Pokémon silhouette while maintaining aspect ratio
                resized_silhouette = cv2.resize(silhouette, (new_w, new_h), interpolation=cv2.INTER_AREA)

                # Create a blank 256x256 white background
                final_image = np.ones(target_size, dtype=np.uint8) * 255  # White background

                # Compute centering coordinates
                x_offset = (target_size[0] - new_w) // 2
                y_offset = (target_size[1] - new_h) // 2

                # Place resized silhouette at the center of the blank background
                final_image[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized_silhouette

                # Save the silhouette
                output_file = output_path / f"{file.stem}_silhouette{file.suffix}"
                cv2.imwrite(str(output_file), final_image)
                print(f"Processed and saved: {file.name}")

            except Exception as e:
                print(f"Error processing {file.name}: {e}")






