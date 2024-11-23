import hashlib
import os
import shutil
import random

# Helper function to compute the file hash (MD5 in this case)
def compute_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Move files if their hash doesn't match between source and destination
def move_files_if_not_moved(image_folder, annotation_folder, save_image_folder, save_annotation_folder, num_valid_files_to_keep):
    # Create source folders if they don't exist
    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(annotation_folder, exist_ok=True)

    # Check if the image folder is empty
    if not os.path.exists(image_folder) or not os.listdir(image_folder):
        print(f"Source folder {image_folder} is empty or does not exist.")
        return

    # List source files
    image_files = sorted(os.listdir(image_folder))
    num_files = len(image_files)
    
    if num_files <= num_valid_files_to_keep:
        print(f"Not enough files to move. There are only {num_files} files, which is less than or equal to the number to keep ({num_valid_files_to_keep}).")
        return

    # Determine how many files to move
    num_files_to_move = num_files - num_valid_files_to_keep

    # Randomly select files to move
    files_to_move = random.sample(image_files, num_files_to_move)

    # Create destination folders if they don't exist
    os.makedirs(save_image_folder, exist_ok=True)
    os.makedirs(save_annotation_folder, exist_ok=True)

    # Iterate over the images and check hashes
    for image_file in files_to_move:
        src_image_path = os.path.join(image_folder, image_file)
        dest_image_path = os.path.join(save_image_folder, image_file)

        # Compute hashes if file exists in both source and destination
        if os.path.exists(dest_image_path):
            src_hash = compute_file_hash(src_image_path)
            dest_hash = compute_file_hash(dest_image_path)
            if src_hash == dest_hash:
                print(f"File {image_file} already moved.")
                continue  # Skip moving if files are identical
        
        # Move the image file
        shutil.move(src_image_path, dest_image_path)

        # Move corresponding annotation file
        annotation_file = image_file.replace('.jpg', '.txt')  # Assuming .jpg images and .txt annotations
        src_annotation_path = os.path.join(annotation_folder, annotation_file)
        dest_annotation_path = os.path.join(save_annotation_folder, annotation_file)
        
        if os.path.exists(src_annotation_path):
            if os.path.exists(dest_annotation_path):
                src_annotation_hash = compute_file_hash(src_annotation_path)
                dest_annotation_hash = compute_file_hash(dest_annotation_path)
                if src_annotation_hash == dest_annotation_hash:
                    print(f"Annotation {annotation_file} already moved.")
                    continue
        
            shutil.move(src_annotation_path, dest_annotation_path)
        
        print(f"Moved {image_file} and {annotation_file}.")

# Example usage
move_files_if_not_moved(
    image_folder='dataset/Pieces/Pieces/images/valid',
    annotation_folder='dataset/Pieces/Pieces/labels/valid',
    save_image_folder='dataset/Pieces/Pieces/images/train',
    save_annotation_folder='dataset/Pieces/Pieces/labels/train',
    num_valid_files_to_keep=2
)
