from datetime import datetime
import os
import re
from typing import Dict, Union

from fastapi import HTTPException, logger
from sqlalchemy.orm import Session
import yaml
import shutil
from services.rotation_services import rotate_and_save_images_and_annotations
from database.piece.annotation import Annotation
from database.piece.piece import Piece
from database.piece.piece_image import PieceImage
from services.file_mover_with_hash_check import move_files_if_not_moved

# Virtual storage dictionary
virtual_storage: Dict[str, Dict] = {}

def get_images_of_piece(piece_label: str, db: Session):
    """Fetch all images of a piece that are not annotated yet."""
    # Fetch the piece from the database
    db_piece = db.query(Piece).filter(Piece.piece_label == piece_label).first()
    
    if db_piece:
        # Fetch images that are not annotated
        db_images = db.query(PieceImage).filter(
            PieceImage.piece_id == db_piece.id,
            PieceImage.is_annotated == False  # Exclude annotated images
        ).all()

        if not db_images:
            print("This piece has no unannotated images registered yet.")
            return []

        print("Piece images retrieved.")
        urlbase = "http://localhost:8000/images/"
        
        # Return the list of unannotated images with their URLs
        try:
            return [{"url": urlbase + image.url.replace("\\", "/"), "name": image.id} for image in db_images]
        except Exception as e:
            print(f"Error retrieving images: {e}")
            return []


    print("Piece doesn't exist.")
    return []

def get_img_non_annotated(db: Session):
    # Retrieve all pieces that are not annotated
    db_pieces = db.query(Piece).filter(Piece.is_annotated == False).all()
    result = []

    if not db_pieces:
        print("No non-annotated pieces found.")
        return result

    urlbase = "http://localhost:8000/images/"

    for piece in db_pieces:
        # Check for non-annotated images of the current piece
        non_annotated_images_count = db.query(PieceImage).filter(
            PieceImage.piece_id == piece.id,
            PieceImage.is_annotated == False
        ).count()

        print(f"Non-annotated images count for piece {piece.id}: {non_annotated_images_count}")

        # Get the first non-annotated image associated with the piece
        db_image = db.query(PieceImage).filter(
            PieceImage.piece_id == piece.id,
            PieceImage.is_annotated == False
        ).first()

        if db_image:
            # Construct the URL for the image and include the piece label
            image_info = {
                "piece_label": piece.piece_label,
                "url": urlbase + db_image.url.replace("\\", "/"),
                "name": db_image.id,
                "nbr_img": piece.nbre_img
            }
            result.append(image_info)
        else:
            print(f"No non-annotated images registered for piece {piece.piece_label}.")

    return result

def rotate_and_update_images(piece_label: str, db: Session):
    piece = db.query(Piece).filter(Piece.piece_label == piece_label).first()

    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found.")
    
    # Assuming PieceImage is a SQLAlchemy model and you have a piece_id or similar identifier
    piece_image = db.query(PieceImage).filter(PieceImage.piece_id == piece.id).first()
    
    # Validate piece_label format
    match = re.match(r'([A-Z]\d{3}\.\d{5})', piece_label)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid piece_label format.")
        
    group_label = match.group(1)
    
    image_folder = f'dataset_custom/images/valid/{piece_label}'
    annotation_folder = f'dataset_custom/labels/valid/{piece_label}'
    save_image_folder = f'dataset_custom/images/train/{piece_label}'
    save_annotation_folder = f'dataset_custom/labels/train/{piece_label}'


    # Rotate and save images and annotations (assuming you have this function defined)
    rotate_and_save_images_and_annotations(piece_label, rotation_angles=[45,90,135,180,270])
        # Call the move_files_if_not_moved function to handle the file movement with hash checking
    move_files_if_not_moved(image_folder, annotation_folder, save_image_folder, save_annotation_folder,2,db)

    image_folder_1 = f'dataset/Pieces/Pieces/images/valid/{group_label}/{piece_label}'
    annotation_folder_1 = f'dataset/Pieces/Pieces/labels/valid/{group_label}/{piece_label}'
    save_image_folder_1 = f'dataset/Pieces/Pieces/images/train/{group_label}/{piece_label}'
    save_annotation_folder_1 = f'dataset/Pieces/Pieces/labels/train/{group_label}/{piece_label}'

    # Rotate and save images and annotations (assuming you have this function defined)
    rotate_and_save_images_and_annotations(piece_label, rotation_angles=[45,90,135,180,270])
        # Call the move_files_if_not_moved function to handle the file movement with hash checking
    move_files_if_not_moved(image_folder_1, annotation_folder_1, save_image_folder_1, save_annotation_folder_1,2,db)

    # Update piece_image URL in the database after successful movement
    new_image_url = f'Pieces/Pieces/images/train/{group_label}/{piece_label}'
    
    if piece_image:
        piece_image.image_url = new_image_url
        db.commit()
        db.refresh(piece_image)
        print(f"Database updated: {piece_image.image_url}")
    else:
        raise HTTPException(status_code=404, detail="PieceImage not found.")
    
    print("Files moved and database updated successfully.")



def save_annotation_in_memory(piece_label: str, image_id: int, annotation_data: dict):
    """Save the annotation in virtual storage instead of the database."""
    
    # Generate a unique key for the piece label
    if piece_label not in virtual_storage:
        virtual_storage[piece_label] = {'annotations': [], 'images': set()}
    
    # Validate the input data
    required_fields = ['type', 'x', 'y', 'width', 'height']
    missing_fields = [field for field in required_fields if field not in annotation_data]
    
    if missing_fields:
        raise ValueError(f"Missing fields in annotation data: {', '.join(missing_fields)}")
    
    # Add the annotation data to the virtual storage
    virtual_storage[piece_label]['annotations'].append({
        
        'type': str(annotation_data['type']),
        'x': float(annotation_data['x']),
        'y': float(annotation_data['y']),
        'width': float(annotation_data['width']),
        'height': float(annotation_data['height']),
        'image_id': int(image_id),

    })
    
    # Mark the image as annotated in virtual storage
    virtual_storage[piece_label]['images'].add(image_id)
   
    print(virtual_storage[piece_label]['annotations'])
  
    print(f"{annotation_data['x']} {annotation_data['y']} {annotation_data['width']} {annotation_data['height']}\n")

def save_annotations_to_db(db: Session, piece_label: str, save_folder: str):
    """Save all annotations from virtual storage to the database."""

    # Ensure the piece exists in the database
    piece = db.query(Piece).filter(Piece.piece_label == piece_label).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")

    print(f"Piece found: {piece}")

    # Check if the piece has any annotations in virtual storage
    if piece_label not in virtual_storage or not virtual_storage[piece_label]['annotations']:
        raise HTTPException(status_code=404, detail="No annotations to save for this piece")

    print(f"Annotations found for piece: {virtual_storage[piece_label]['annotations']}")

    # Collect unique class IDs and labels from annotations
    class_id_to_label = {}

    # Save each annotation from virtual storage to the database
    for annotation_data in virtual_storage[piece_label]['annotations']:
        print(f"Processing annotation: {annotation_data}")  # Debugging output to check the content

        # Validate required keys are present
        required_keys = ['type', 'x', 'y', 'width', 'height', 'image_id']
        missing_keys = [key for key in required_keys if key not in annotation_data]

        if missing_keys:
            print(f"Missing keys in annotation data: {missing_keys}")
            raise HTTPException(status_code=400, detail=f"Missing keys in annotation data: {', '.join(missing_keys)}")

        # Additional validation for key values
        for key in required_keys:
            if annotation_data[key] is None or annotation_data[key] == '':
                print(f"Invalid value for {key}: {annotation_data[key]}")
                raise HTTPException(status_code=400, detail=f"Invalid value for {key}: {annotation_data[key]}")

        # Fetch the image record for the current annotation
        piece_image = db.query(PieceImage).filter(PieceImage.id == annotation_data['image_id']).first()

        if not piece_image:
            print("Image not found for image_id:", annotation_data['image_id'])
            raise HTTPException(status_code=404, detail="Image not found")

        print(f"Piece image found: {piece_image}")

        # Convert from percentage to YOLO format
        width_normalized = annotation_data['width'] / 100
        height_normalized = annotation_data['height'] / 100
        x_center_normalized = (annotation_data['x'] + annotation_data['width'] / 2) / 100
        y_center_normalized = (annotation_data['y'] + annotation_data['height'] / 2) / 100

        # Generate the annotationTXT_name from the image name
        image_name_without_extension = os.path.splitext(piece_image.image_name)[0]
        annotationTXT_name = f"{image_name_without_extension}.txt"

        # Set the file path for saving the annotation
        file_path = os.path.join(save_folder, annotationTXT_name)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Prepare annotation in YOLO format
        annotationTXT = f"{piece.class_data_id} {x_center_normalized} {y_center_normalized} {width_normalized} {height_normalized}\n"

        # Save the annotation inside a text file
        with open(file_path, 'w') as file:
            file.write(annotationTXT)

        print(f"Annotation saved to text file: {file_path}")

        # Save the annotation in the database
        annotation = Annotation(
            annotationTXT_name=annotationTXT_name,
            type=annotation_data['type'],
            x=x_center_normalized,
            y=y_center_normalized,
            width=width_normalized,
            height=height_normalized,
            piece_image_id=annotation_data['image_id']
        )

        db.add(annotation)

        # Update the is_annotated field of the image
        piece_image.is_annotated = True
        class_id_to_label[piece.class_data_id] = piece.piece_label  # Collect unique class IDs and labels

    # Check if all images related to the piece are annotated
    all_images_annotated = db.query(PieceImage).filter(
        PieceImage.piece_id == piece.id,
        PieceImage.is_annotated == False
    ).count() == 0
    print ("all_images_annotated",all_images_annotated)
    all_images_annotatedTF = db.query(PieceImage).filter(
        PieceImage.piece_id == piece.id,
        PieceImage.is_annotated == False
    ).count()
    print ("all_images_annotatedTF",all_images_annotatedTF)
    # If all images are annotated, mark the piece as annotated
    if (all_images_annotatedTF-1)  == 0 :
        piece.is_annotated = True 
        print("All images annotated. Updating piece to annotated.")
        data_yaml_path = os.path.join("dataset_custom", "data.yaml")

        # Load existing data if it exists
        if os.path.exists(data_yaml_path):
            with open(data_yaml_path, 'r') as yaml_file:
                data_yaml = yaml.safe_load(yaml_file)
                print(f"Existing data_yaml loaded: {data_yaml}")
        else:
            data_yaml = {
                'names': {},
                'nc': 0,
                'val': os.path.join("C:\\Users\\hp\\Desktop\\Airbus\\detectionSystemAirbus", "backend", "dataset_custom","images","valid"),
                'train': os.path.join("C:\\Users\\hp\\Desktop\\Airbus\\detectionSystemAirbus", "backend", "dataset_custom", "images", "train")
                # C:\Users\hp\Desktop\Airbus\detectionSystemAirbus

            }
            print("No existing data_yaml found. Creating new.")

        # Update the data_yaml with new class data
        class_id_to_label[piece.class_data_id] = piece.piece_label
        data_yaml['names'].update(class_id_to_label)
        data_yaml['nc'] = len(data_yaml['names'])  # Update number of unique classes

        # Create directories if needed
        os.makedirs(os.path.dirname(data_yaml_path), exist_ok=True)

        # Write to data.yaml
        with open(data_yaml_path, 'w') as yaml_file:
            yaml.dump(data_yaml, yaml_file, default_flow_style=False)

        print(f"data.yaml file updated at: {data_yaml_path}")


    db.commit()
    db.refresh(annotation)
    db.refresh(piece)
    
    db.refresh(piece_image) 
          
    virtual_storage.pop(piece_label, None)
    print("Annotations saved successfully and virtual storage cleared.")
        # Call the stop camera endpoint
    try:
        # Assuming you're using the requests library to make an HTTP call
        import requests
        stop_camera_response = requests.post("http://127.0.0.1:8000/cameras/stop")

        if stop_camera_response.status_code != 200:
            print(f"Failed to stop camera: {stop_camera_response.json().get('detail')}")
        else:
            print("Camera stopped successfully.")
    except Exception as e:
        print(f"Error stopping camera: {str(e)}")

    return {"status": "Annotations saved successfully"}


def get_all_datasets(db: Session):
    """
    Fetch all datasets including pieces, images, and annotations from the database.
    """
    datasets = {}

    # Fetch all pieces
    pieces = db.query(Piece).all()

    for piece in pieces:
        piece_data = {
            "id": piece.id,
            "class_data_id" : piece.class_data_id,
            "label": piece.piece_label,
            "is_annotated": piece.is_annotated,
            "is_yolo_trained" : piece.is_yolo_trained,
            "nbre_img": piece.nbre_img,
            "images": []
        }

        # Fetch all images associated with the piece
        images = db.query(PieceImage).filter(PieceImage.piece_id == piece.id).all()

        for image in images:
            image_data = {
                "id": image.id,
                "url": f"http://localhost:8000/images/{image.url.replace('\\', '/')}",
                "is_annotated": image.is_annotated,
                "annotations": []
            }

            # Fetch all annotations associated with the image
            annotations = db.query(Annotation).filter(Annotation.piece_image_id == image.id).all()

            for annotation in annotations:
                annotation_data = {
                    "id": annotation.id,
                    "type": annotation.type,
                    "x": annotation.x,
                    "y": annotation.y,
                    "width": annotation.width,
                    "height": annotation.height
                }
                image_data["annotations"].append(annotation_data)

            piece_data["images"].append(image_data)

        datasets[piece.piece_label] = piece_data

    return datasets

def get_piece_labels_by_group(group_label: str, db: Session):
    try:
        # Query the database for pieces with piece_label starting with group_label
        pieces = db.query(Piece).filter(Piece.piece_label.like(f'{group_label}%')).all()
        
        # Extract piece labels
        piece_labels = [piece.piece_label for piece in pieces]
        
        if not piece_labels:
            logger.info(f"No pieces found for group '{group_label}'.")
        
        return piece_labels

    except Exception as e:
        logger.error(f"An error occurred while fetching piece labels: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching piece labels: {e}")
    

# ****************

# this will handle the deletion 
def delete_directory(directory_path: str):
    """Recursively delete a directory and its contents."""
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        print(f"Deleted directory: {directory_path}")
    else:
        print(f"Directory not found: {directory_path}")


def delete_piece_by_label(piece_label: str, db: Session):
    """Delete a piece, its images, annotations, and related folders."""
    # Fetch the piece from the database
    piece = db.query(Piece).filter(Piece.piece_label == piece_label).first()
    if not piece:
        raise HTTPException(status_code=404, detail="Piece not found")

    # Fetch all images related to the piece
    images = db.query(PieceImage).filter(PieceImage.piece_id == piece.id).all()
    
    # Delete all annotations related to each image
    for image in images:
        annotations = db.query(Annotation).filter(Annotation.piece_image_id == image.id).all()
        for annotation in annotations:
            db.delete(annotation)
    
    # Delete all images
    for image in images:
        db.delete(image)
    
    # Delete the piece
    db.delete(piece)
    db.commit()

    # Extract label for folder paths
    match = re.match(r'([A-Z]\d{3}\.\d{5})', piece_label)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid piece_label format.")
    
    extracted_label = match.group(1)
    
   
    folder_path_annotations_valid = os.path.join("dataset",'Pieces','Pieces','labels','valid',extracted_label,piece_label)
    folder_path_images_valid = os.path.join("dataset",'Pieces','Pieces','images','valid',extracted_label,piece_label)
    folder_path_annotations_train = os.path.join("dataset",'Pieces','Pieces','labels','train',extracted_label,piece_label)
    folder_path_images_train = os.path.join("dataset",'Pieces','Pieces','images','train',extracted_label,piece_label)
    
    # Delete the folders
    delete_directory(folder_path_annotations_valid)
    delete_directory(folder_path_images_valid)
    delete_directory(folder_path_annotations_train)
    delete_directory(folder_path_images_train)
    
    return {"status": "Piece and associated data deleted successfully"}

def delete_all_pieces(db: Session):
    """Delete all pieces, their images, annotations, and associated folders."""
    
    # Fetch all pieces
    pieces = db.query(Piece).all()
    
    if not pieces:
        raise HTTPException(status_code=404, detail="No pieces found to delete")

    for piece in pieces:
        # Fetch all images associated with the piece
        images = db.query(PieceImage).filter(PieceImage.piece_id == piece.id).all()

        # Delete annotations and images
        for image in images:
            # Fetch and delete annotations
            annotations = db.query(Annotation).filter(Annotation.piece_image_id == image.id).all()
            for annotation in annotations:
                db.delete(annotation)
            
            # Delete image record
            db.delete(image)
        
        # Delete the piece record
        db.delete(piece)
        
        # Determine the path of the folder to delete
        match = re.match(r'([A-Z]\d{3}\.\d{5})', piece.piece_label)
        if match:
            extracted_label = match.group(1)
            folder_path = os.path.join("dataset","Pieces")
            
            # Remove the folder and all its contents
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"Folder {folder_path} deleted successfully.")
            else:
                print(f"Folder {folder_path} does not exist.")

    # Commit the changes
    db.commit()
    
    return {"status": "All pieces and associated data deleted successfully"}
