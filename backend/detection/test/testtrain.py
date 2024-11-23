import logging
import torch
from ultralytics import YOLO

def train_model(piece_label: str):
    model = YOLO("yolov8n.pt")
    model_save_path = f"backend/api/models/yolov8n_{piece_label}.pt"

    # Determine whether to use GPU or CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    try:
        # Dynamically adjust batch size based on available memory
        batch_size = 8 if device.type == 'cpu' else 16  # Adjust based on your GPU memory

        # Train the model with the specified dataset, epochs, image size, and batch size
        model.train(data=f"backend/dataset/{piece_label}/data.yaml", 
                    epochs=50, 
                    imgsz=640, 
                    batch=batch_size, 
                    device=device)

        # Save the trained model
        model.save(model_save_path)     
    except Exception as e:
        # Log any errors that occur during training
        logging.error(f"Training interrupted: {e}")

        # Save the model even if an error occurs, to retain the progress
        model.save(model_save_path)

    logging.info(f"Model training complete. Saved to {model_save_path}")