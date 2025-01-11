import logging
import os
import re
import shutil
import cv2
from fastapi import HTTPException
import numpy as np

def rotate_and_save_images_and_annotations(piece_label: str, rotation_angles: list):
    """Rotate images and update annotations for the specified piece label."""

    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """Rotate the image by the given angle."""
        center = (image.shape[1] // 2, image.shape[0] // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_image = cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]), flags=cv2.INTER_LINEAR)
        return rotated_image

    # def rotate_annotation(annotation: list, angle: float, image_size: tuple) -> list:
    #     """Rotate the annotation based on the image rotation."""
    #     w, h = image_size
    #     x_center = annotation[1] * w
    #     y_center = annotation[2] * h
    #     width = annotation[3] * w
    #     height = annotation[4] * h

    #     # Calculate the four corners of the bounding box
    #     x1 = x_center - width / 2
    #     y1 = y_center - height / 2
    #     x2 = x_center + width / 2
    #     y2 = y_center - height / 2
    #     x3 = x_center + width / 2
    #     y3 = y_center + height / 2
    #     x4 = x_center - width / 2
    #     y4 = y_center + height / 2

    #     # Handle 90 and 270 degrees rotations separately
    #     if angle == 90:
    #         new_x_center = y_center / h
    #         new_y_center = 1 - (x_center / w)
    #         new_width = height / h
    #         new_height = width / w
    #     elif angle == 270:
    #         new_x_center = 1 - (y_center / h)
    #         new_y_center = x_center / w
    #         new_width = height / h
    #         new_height = width / w
    #     else:
    #         # Apply rotation to each corner for 0, 180 degrees
    #         angle_rad = np.radians(angle)
    #         cos_angle = np.cos(angle_rad)
    #         sin_angle = np.sin(angle_rad)
    #         cx, cy = w / 2, h / 2  # image center

    #         def rotate_point(x, y):
    #             x_new = cos_angle * (x - cx) - sin_angle * (y - cy) + cx
    #             y_new = sin_angle * (x - cx) + cos_angle * (y - cy) + cy
    #             return x_new, y_new

    #         x1_new, y1_new = rotate_point(x1, y1)
    #         x2_new, y2_new = rotate_point(x2, y2)
    #         x3_new, y3_new = rotate_point(x3, y3)
    #         x4_new, y4_new = rotate_point(x4, y4)

    #         # Find new bounding box
    #         new_x_min = min(x1_new, x2_new, x3_new, x4_new)
    #         new_y_min = min(y1_new, y2_new, y3_new, y4_new)
    #         new_x_max = max(x1_new, x2_new, x3_new, x4_new)
    #         new_y_max = max(y1_new, y2_new, y3_new, y4_new)

    #         # Compute the new bounding box center, width, and height
    #         new_x_center = (new_x_min + new_x_max) / 2
    #         new_y_center = (new_y_min + new_y_max) / 2
    #         new_width = new_x_max - new_x_min
    #         new_height = new_y_max - new_y_min

    #         # Normalize coordinates
    #         new_x_center /= w
    #         new_y_center /= h
    #         new_width /= w
    #         new_height /= h

    #     return [
    #         annotation[0],          # type
    #         new_x_center,           # normalized x_center
    #         new_y_center,           # normalized y_center
    #         new_width,              # normalized width
    #         new_height              # normalized height
    #     ]
    def flip_image(image: np.ndarray, flip_code: int) -> np.ndarray:
        """Flip the image: 1 for horizontal, 0 for vertical."""
        return cv2.flip(image, flip_code)
    
    def rotate_annotation(annotation: list, angle: float, image_size: tuple) -> list:
        w, h = image_size

        # Calculate the center and size of the bounding box
        x_center = annotation[1] * w  
        y_center = annotation[2] * h  
        width = annotation[3] * w     
        height = annotation[4] * h    

        print(f"Original Bounding Box Center: x_center = {x_center}, y_center = {y_center}")
        print(f"Original Bounding Box Size: width = {width}, height = {height}")
        print("*************")

        # Calculate the four corners of the bounding box in absolute pixel values
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center - height / 2
        x3 = x_center + width / 2
        y3 = y_center + height / 2
        x4 = x_center - width / 2
        y4 = y_center + height / 2

        print(f"Original Corners: \n"
            f"x1, y1 = ({x1:.2f}, {y1:.2f})\n"
            f"x2, y2 = ({x2:.2f}, {y2:.2f})\n"
            f"x3, y3 = ({x3:.2f}, {y3:.2f})\n"
            f"x4, y4 = ({x4:.2f}, {y4:.2f})\n")

        # Convert angle to radians
        angle_rad = np.radians(-angle)
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)

        # Set a tolerance level for small values
        tolerance = 1e-10

        # Treat values close to zero as zero
        if abs(cos_angle) < tolerance:
            cos_angle = 0.0
        if abs(sin_angle) < tolerance:
            sin_angle = 0.0

        # Define the center of the image
        cx, cy = w / 2, h / 2

        print(f"Image Center: cx = {cx}, cy = {cy}")
        print(f"Angle (in radians): {angle_rad}")
        print(f"cos(angle) = {cos_angle}, sin(angle) = {sin_angle}")

        # Rotate a point around the center of the image
        def rotate_point(x, y):
            x_new = cos_angle * (x - cx) - sin_angle * (y - cy) + cx
            y_new = sin_angle * (x - cx) + cos_angle * (y - cy) + cy
            return x_new, y_new

        # Rotate each corner of the bounding box
        x1_new, y1_new = rotate_point(x1, y1)
        x2_new, y2_new = rotate_point(x2, y2)
        x3_new, y3_new = rotate_point(x3, y3)
        x4_new, y4_new = rotate_point(x4, y4)

        # Print rotated corner points
        print(f"Rotated Points: \n"
            f"({x1_new:.2f}, {y1_new:.2f}), ({x2_new:.2f}, {y2_new:.2f}), "
            f"({x3_new:.2f}, {y3_new:.2f}), ({x4_new:.2f}, {y4_new:.2f})")

        # Calculate new bounding box from rotated corners
        new_x_min = min(x1_new, x2_new, x3_new, x4_new)
        new_y_min = min(y1_new, y2_new, y3_new, y4_new)
        new_x_max = max(x1_new, x2_new, x3_new, x4_new)
        new_y_max = max(y1_new, y2_new, y3_new, y4_new)

        print(f"New Bounding Box Coordinates:\n"
            f"Min: ({new_x_min:.2f}, {new_y_min:.2f}), Max: ({new_x_max:.2f}, {new_y_max:.2f})")

        # Compute new bounding box center, width, and height
        new_x_center = (new_x_min + new_x_max) / 2
        new_y_center = (new_y_min + new_y_max) / 2
        new_width = new_x_max - new_x_min
        new_height = new_y_max - new_y_min

        # Print new center and dimensions before normalization
        print(f"New Bounding Box Center: x_center = {new_x_center}, y_center = {new_y_center}")
        print(f"New Bounding Box Size: width = {new_width}, height = {new_height}")

        # Normalize for YOLO format
        new_x_center /= w
        new_y_center /= h
        new_width /= w
        new_height /= h

        # Print normalized values
        print(f"Normalized Center: ({new_x_center}, {new_y_center})")
        print(f"Normalized Size: width = {new_width}, height = {new_height}")

        return [
            annotation[0],          # class_id
            new_x_center,           # normalized x_center
            new_y_center,           # normalized y_center
            new_width,              # normalized width
            new_height              # normalized height
        ]
    def flip_annotation(annotation: list, flip_code: int, image_size: tuple) -> list:
        """Flip the annotation based on the image flip."""
        w, h = image_size
        
        if flip_code == 1:  # Horizontal flip
            new_x_center = 1 - annotation[1]  # Invert x_center
            return[
                annotation[0],  # class_id
                new_x_center,   # normalized x_center
                annotation[2],   # normalized y_center
                annotation[3],   # normalized width
                annotation[4]    # normalized height
            ]
        elif flip_code == 0:  # Vertical flip
            new_x_center = annotation[1]  # x_center remains the same
            new_y_center = 1 - annotation[2]  # Invert y_center
            return[
                annotation[0],  # class_id
                new_x_center,   # normalized x_center
                new_y_center,   # normalized y_center
                annotation[3],   # normalized width
                annotation[4]    # normalized height
            ]
        
        else:
            raise ValueError("Invalid flip code. Use 0 for vertical and 1 for horizontal.")
        
        
    def load_annotations(annotation_file: str) -> list:
        """Load annotations from a file."""
        annotations = []
        with open(annotation_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 5:
                    annotation = [
                        int(parts[0]),        # type
                        float(parts[1]),     # x
                        float(parts[2]),     # y
                        float(parts[3]),     # width
                        float(parts[4])      # height
                    ]
                    annotations.append(annotation)
        return annotations
    
    def save_annotations(annotation_file: str, annotations: list):
        """Save annotations to a file."""
        with open(annotation_file, 'w') as file:
            for annotation in annotations:
                line = f"{annotation[0]} {annotation[1]} {annotation[2]} {annotation[3]} {annotation[4]}\n"
                file.write(line)
    
    # Validate piece_label format
    match = re.match(r'([A-Z]\d{3}\.\d{5})', piece_label)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid piece_label format.")
        
    group_label = match.group(1)
    
    image_folder = f'dataset_custom/{piece_label}/images/valid'
    annotation_folder = f'dataset_custom/{piece_label}/labels/valid'
    save_image_folder = f'dataset_custom/{piece_label}/images/train'
    save_annotation_folder = f'dataset_custom/{piece_label}/labels/train'
    # image_folder = f'dataset/Pieces/Pieces/images/valid/{group_label}/{piece_label}'
    # annotation_folder = f'dataset/Pieces/Pieces/labels/valid/{group_label}/{piece_label}'
    # save_image_folder = f'dataset/Pieces/Pieces/images/train/{group_label}/{piece_label}'
    # save_annotation_folder = f'dataset/Pieces/Pieces/labels/train/{group_label}/{piece_label}'

    if not os.path.exists(save_image_folder):
        os.makedirs(save_image_folder)

    if not os.path.exists(save_annotation_folder):
        os.makedirs(save_annotation_folder)

    for image_file in os.listdir(image_folder):
        if image_file.endswith('.jpg') or image_file.endswith('.png'):
            image_path = os.path.join(image_folder, image_file)
            image = cv2.imread(image_path)

            # Load the original annotations
            annotation_file = os.path.join(annotation_folder, os.path.splitext(image_file)[0] + '.txt')
            annotations = load_annotations(annotation_file)

            for angle in rotation_angles:
                rotated_image = rotate_image(image, angle)
                rotated_image_name = f"{os.path.splitext(image_file)[0]}_rot{angle}.jpg"
                rotated_image_path = os.path.join(save_image_folder, rotated_image_name)
                cv2.imwrite(rotated_image_path, rotated_image)

                h, w = image.shape[:2]
                new_annotations = [rotate_annotation(annotation, angle, (w, h)) for annotation in annotations]
                annotation_file_rot = os.path.join(save_annotation_folder, os.path.splitext(rotated_image_name)[0] + '.txt')
                save_annotations(annotation_file_rot, new_annotations)
                      # Flip and save images/annotations
            for flip_code in [0, 1]:  # 0 for vertical, 1 for horizontal
                flipped_image = flip_image(image, flip_code)
                flipped_image_name = f"{os.path.splitext(image_file)[0]}_flip{flip_code}.jpg"
                flipped_image_path = os.path.join(save_image_folder, flipped_image_name)
                cv2.imwrite(flipped_image_path, flipped_image)

                h, w = image.shape[:2]
                flipped_annotations = [flip_annotation(annotation, flip_code, (w, h)) for annotation in annotations]
                annotation_file_flip = os.path.join(save_annotation_folder, os.path.splitext(flipped_image_name)[0] + '.txt')
                save_annotations(annotation_file_flip, flipped_annotations)

