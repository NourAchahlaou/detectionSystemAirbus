import os
from ultralytics import YOLO


 #tthis is the final correct laod model 
def load_model(piece_label: str):
    # Get the directory of the script being executed
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Adjust the model directory path
    model_dir = os.path.join(script_dir, '..', 'models')
    model_path = os.path.join(model_dir, f'yolo8x_{piece_label}.pt')

    print(f"Script directory: {script_dir}")
    print(f"Model directory: {model_dir}")
    print(f"Model path: {model_path}")

    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")


    my_path_model = YOLO(model_path)

    print("Models loaded successfully.")
    return my_path_model

# # Example usage
# try:
#     load_model("D532.31953")
# except Exception as e:
#     print(e)


 #tthis is the final correct laod model 
def load_my_model():
    # Get the directory of the script being executed
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Adjust the model directory path
    model_dir = os.path.join(script_dir, '..', 'models')
    model_path = os.path.join(model_dir, 'yolo8x_model.pt')

    print(f"Script directory: {script_dir}")
    print(f"Model directory: {model_dir}")
    print(f"Model path: {model_path}")

    # Check if the model file exists
    if not os.path.isfile(model_path):
        print(f"Model file not found at: {model_path}")
        return None  # Return None or an appropriate placeholder if model is not found

    # Load the model if the file exists
    my_path_model = YOLO(model_path)

    print("Model loaded successfully.")
    return my_path_model