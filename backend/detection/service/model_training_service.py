import asyncio
import os
import logging
import torch
from fastapi import HTTPException
from requests import Session
from ultralytics import YOLO
import yaml
from collections import Counter
import matplotlib.pyplot as plt
from services.piece_service import get_piece_labels_by_group, rotate_and_update_images
from database.piece.piece import Piece

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler("training_logs.log", mode='a')])

logger = logging.getLogger(__name__)

# Global stop event
stop_event = asyncio.Event()
stop_sign = False

async def stop_training():
   
    stop_event.set()
    stop_sign == True 
    logger.info("Stop training signal sent.")

def select_device():
    """Select the best available device (GPU if available, else CPU)."""
    if torch.cuda.is_available():
        logger.info("GPU detected. Using CUDA.")
        return torch.device('cuda')
    else:
        logger.info("No GPU detected. Using CPU.")
        return torch.device('cpu')

def adjust_batch_size(device, base_batch_size=8):
    """Adjust batch size based on the available device."""
    if device.type == 'cuda':
        total_memory = torch.cuda.get_device_properties(0).total_memory
        if total_memory > 8 * 1024**3:  # If GPU has more than 8GB of memory
            return base_batch_size * 2
        elif total_memory > 4 * 1024**3:  # If GPU has more than 4GB of memory
            return base_batch_size
        else:
            return base_batch_size // 2
    else:
        return base_batch_size // 2

def analyze_class_distribution(data_yaml_path):
    """Analyze and plot class distribution in the dataset."""
    with open(data_yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    class_counts = Counter()
    train_labels_dir = data['train'].replace('images', 'labels')
    
    label_files = [os.path.join(train_labels_dir, f) for f in os.listdir(train_labels_dir) if f.endswith('.txt')]
    
    for label_file in label_files:
        with open(label_file, 'r') as lf:
            for line in lf:
                try:
                    class_idx = int(line.split()[0])
                    class_counts[class_idx] += 1
                except ValueError:
                    logger.error(f"Error parsing line in {label_file}: {line}")

    class_names = data['names']
    class_labels = [class_names[i] for i in sorted(class_counts.keys())]
    counts = [class_counts[i] for i in sorted(class_counts.keys())]

    plt.figure(figsize=(10, 6))
    plt.bar(class_labels, counts, color='skyblue')
    plt.xlabel('Class')
    plt.ylabel('Number of Samples')
    plt.title('Class Distribution')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("class_distribution.png")
    plt.show()

def train_model(group_label: str, db: Session):
    model = None
    try:
        # Set service directory
        service_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Service directory: {service_dir}")

        # Fetch pieces from database
        pieces = db.query(Piece).filter(Piece.piece_label.like(f'{group_label}%')).all()
        if not pieces:
            logger.error(f"No pieces found for group '{group_label}'.")
            return

        for piece in pieces:
            if not piece.is_annotated:
                logger.error(f"Piece with label '{piece.piece_label}' is not annotated. Training cannot proceed.")
                return

        logger.info(f"Found annotated pieces in group: {group_label}")

        # Resolve paths
        base_dir_data_yaml_path = os.path.abspath(os.path.join(service_dir, '..', '..', 'dataset','Pieces'))
        data_yaml_path = os.path.join(base_dir_data_yaml_path,'data.yaml')
        base_dir_model_save_path = os.path.abspath(os.path.join(service_dir, '..', '..', 'detection'))
        model_save_path = os.path.join(base_dir_model_save_path, 'models', 'yolo8n_model.pt')

        # Log paths for debugging
        logger.info(f"Resolved data.yaml path: {data_yaml_path}")
        logger.info(f"Model save path: {model_save_path}")

        # Check if the file exists
        if not os.path.isfile(data_yaml_path):
            logger.error(f"data.yaml file not found at {data_yaml_path}")
            return

        # Ensure the model directory exists
        os.makedirs(os.path.dirname(model_save_path), exist_ok=True)

        # Fetch piece labels and rotate images as before
        piece_labels = get_piece_labels_by_group(group_label, db)
        for piece_label in piece_labels:
            rotate_and_update_images(piece_label, db)

        # Initialize the model (load the previously trained model)
        device = select_device()
        if os.path.exists(model_save_path):
            logger.info(f"Loading existing model from {model_save_path}")
            model = YOLO(model_save_path)  # Load the pre-trained model for fine-tuning
        else:
            logger.info("No pre-existing model found. Starting training from scratch.")
            model = YOLO("yolov8n.pt")  # Load a base YOLO model

        model.to(device)
        batch_size = adjust_batch_size(device)

        logger.info(f"Starting fine-tuning for group: {group_label}")
        logger.info(f"Using device: {device}, Batch size: {batch_size}")

        # Fine-tuning loop with stop check
        for epoch in range(50):
              # Fine-tune for additional epochs
            if stop_event.is_set() or stop_sign == True:
                logger.info("Stop event detected. Ending training.")
                break

            # Perform one epoch of training
            model.train(data=data_yaml_path,
                        epochs=1,
                        imgsz=640,
                        batch=batch_size,
                        device=device)

            # Save model periodically (including fine-tuning progress)
            model.save(model_save_path)
            logger.info(f"Model saved to {model_save_path} after epoch {epoch + 1}")

        logger.info(f"Model fine-tuning complete. Final model saved to {model_save_path}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if model:
            try:
                model.save(model_save_path)
                logger.info(f"Model saved at {model_save_path} after encountering an error.")
            except Exception as save_error:
                logger.error(f"Failed to save model after error: {save_error}")
    finally:
        # Clear the stop event and release resources
        stop_event.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # Clear GPU cache to free memory
        logger.info("Fine-tuning process finished.")
