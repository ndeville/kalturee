# VERSION 1 - DELETE DUPLICATE IMAGES BY HASH, ie IDENTICAL IMAGES AT THE BYTE LEVEL

# import os
# import hashlib
# from PIL import Image
# from pathlib import Path

# def hash_image(image_path):
#     try:
#         with Image.open(image_path) as img:
#             img = img.convert('RGB')
#             return hashlib.md5(img.tobytes()).hexdigest()
#     except Exception:
#         return None

# def delete_duplicate_images(folder_path):
#     seen_hashes = {}
#     folder = Path(folder_path)

#     for ext in ('*.jpg', '*.jpeg', '*.png'):
#         for image_path in folder.rglob(ext):
#             img_hash = hash_image(image_path)
#             if not img_hash:
#                 continue
#             if img_hash in seen_hashes:
#                 os.remove(image_path)
#             else:
#                 seen_hashes[img_hash] = image_path



# VERSION 2 - DELETE DUPLICATE IMAGES BY PERCEPTUAL HASH, ie SIMILAR IMAGES

import os
from pathlib import Path
from PIL import Image
import imagehash

def perceptual_hash(image_path):
    try:
        with Image.open(image_path) as img:
            return imagehash.phash(img)
    except Exception:
        return None

def delete_duplicate_images(folder_path, threshold=5):
    seen_hashes = {}
    folder = Path(folder_path)

    for ext in ('*.jpg', '*.jpeg', '*.png'):
        for image_path in folder.rglob(ext):
            img_hash = perceptual_hash(image_path)
            if img_hash is None:
                continue

            duplicate_found = False
            for existing_hash in seen_hashes:
                if abs(img_hash - existing_hash) <= threshold:
                    os.remove(image_path)
                    duplicate_found = True
                    break

            if not duplicate_found:
                seen_hashes[img_hash] = image_path



if __name__ == "__main__":

    # folder_path = input("\nEnter the folder path: ")
    folder_path = "/Users/nic/demo/test"

    delete_duplicate_images(folder_path)