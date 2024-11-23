import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import os

# Load the trained YOLO model
model = YOLO('backend/detection/model/yolo8n_D532.31953.pt')

# Load the image
image_path = 'D:/Professional Vault/Internship/my work/DefectDetection/backend/dataset/D532.31953/D532.31953/images/train/D532.31953.012.10/D532.31953.012.10_1.jpg'
image = cv2.imread(image_path)

if image is None:
    print("Error: Image not found or unable to load.")
    exit()

# Define class names and colors
class_names = ['D532.31953.010.10', 'D532.31953.012.10']
colors = [(0, 255, 0), (255, 0, 0)]  # Green and blue colors for bounding boxes

# Set the confidence threshold
confidence_threshold = 0.5  # Adjust this value as needed

# Run YOLO model on the image
results = model.predict(image)

# Create a base name for annotated images
base_image_name = os.path.basename(image_path).split('.')[0]

# Process the results
for result in results:
    for idx, box in enumerate(result.boxes):
        confidence = box.conf[0].item()
        
        # Check if the confidence is above the threshold
        if confidence < confidence_threshold:
            print(f"Skipping detection with low confidence: {confidence:.2f}")
            continue  # Skip this detection
        
        # Extract the bounding box coordinates
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, xyxy)
        
        # Extract the class ID
        class_id = int(box.cls[0].item())
        
        # Draw the bounding box with class-specific color
        cv2.rectangle(image, (x1, y1), (x2, y2), colors[class_id % len(colors)], 2)
        
        # Add the class name and confidence score above the bounding box
        label = f"{class_names[class_id]}: {confidence:.2f}"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[class_id % len(colors)], 2)
        



# Convert BGR to RGB for displaying with Matplotlib
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Display the image with bounding boxes and labels
plt.imshow(image_rgb)
plt.axis('off')  # Hide the axes
plt.show()





