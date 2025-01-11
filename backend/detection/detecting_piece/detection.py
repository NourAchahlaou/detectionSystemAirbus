import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
import os
import torch

# Check if CUDA is available and set device
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load the trained YOLO model and set to appropriate device
model = YOLO('backend/detection/models/yolo8x_model.pt').to(device)

# Load the image
image_path = 'C:\\Users\\hp\\Desktop\\Airbus\\detectionSystemAirbus\\backend\\dataset_custom\\G053.42874.105.03\\images\\train\\G053.42874.105.03_1_flip0.jpg'

image = cv2.imread(image_path)

if image is None:
    print("Error: Image not found or unable to load.")
    exit()

# Resize image to optimize processing (ensure compatibility with YOLO input size)


# Define class names and colors
class_names = ['G053.45622.103.03', 'G053.42874.105.03']
colors = [(0, 255, 0), (255, 255, 0)]  # Green and blue colors for bounding boxes

# Set the confidence threshold
confidence_threshold = 0.2  # Adjusted for better balance

# Run YOLO model on the image
results = model.predict(image, conf=confidence_threshold, device=device, imgsz=640)

# Create a base name for annotated images
base_image_name = os.path.basename(image_path).split('.')[0]

# Process the results
for result in results:
    for idx, box in enumerate(result.boxes):
        confidence = box.conf[0].item()

        # Check if the confidence is above the threshold
        if confidence < confidence_threshold:
            print(f"Skipping detection with low confidence: {confidence:.2f}")
            continue

        # Extract the bounding box coordinates
        xyxy = box.xyxy[0].cpu().numpy()  # Convert tensor to numpy array
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

# Optionally save the annotated image
output_path = f"C:/Users/hp/Desktop/Airbus/{base_image_name}_annotated.jpg"
cv2.imwrite(output_path, image)
print(f"Annotated image saved to: {output_path}")
