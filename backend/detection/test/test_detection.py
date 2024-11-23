import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
import os

# Load the trained YOLO model
model = YOLO('backend/detection/models/test/yolo8n_D532.31953.pt')

# Load the image
image_path = 'D:/Professional Vault/Internship/my work/DefectDetection/backend/dataset/D532.31953/D532.31953/images/train/D532.31953.010.10/D532.31953.010.10_1.jpg'
image = cv2.imread(image_path)

if image is None:
    print("Error: Image not found or unable to load.")
    exit()

# Define class names and colors
class_names = ['D532.31953.010.10', 'D532.31953.012.10']
colors = [(0, 255, 0), (255, 0, 0)]  # Green and Red colors for bounding boxes

# Set the confidence threshold
confidence_threshold = 0.5  # Adjust this value as needed

# Create directories for saving annotated images
output_dir = 'D:/Professional Vault/Internship/my work/DefectDetection/annotated_images'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
false_positive_dir = os.path.join(output_dir, 'false_positives')
true_positive_dir = os.path.join(output_dir, 'true_positives')
if not os.path.exists(false_positive_dir):
    os.makedirs(false_positive_dir)
if not os.path.exists(true_positive_dir):
    os.makedirs(true_positive_dir)

# Initialize metrics
true_positives = 0
false_positives = 0

# Placeholder for ground truth count
total_ground_truths = 1  # Replace with actual number of ground truths if available

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
        
        # Save the image with annotation for further inspection
        annotated_image_path = os.path.join(output_dir, f'{base_image_name}_annotated_{idx}.jpg')
        cv2.imwrite(annotated_image_path, image)
        
        # Save images of false positives and true positives
        if confidence < confidence_threshold:
            false_positive_image_path = os.path.join(false_positive_dir, f"false_positive_{base_image_name}_{idx}_{confidence:.2f}.jpg")
            cv2.imwrite(false_positive_image_path, image)
            false_positives += 1
        else:
            true_positive_image_path = os.path.join(true_positive_dir, f"true_positive_{base_image_name}_{idx}_{confidence:.2f}.jpg")
            cv2.imwrite(true_positive_image_path, image)
            true_positives += 1

# Calculate metrics
precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
recall = true_positives / total_ground_truths if total_ground_truths > 0 else 0
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

# Print metrics
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1 Score: {f1_score:.2f}")

# Convert BGR to RGB for displaying with Matplotlib
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Display the image with bounding boxes and labels
plt.imshow(image_rgb)
plt.axis('off')  # Hide the axes
plt.show()


print(f"False positives saved in {false_positive_dir}")
print(f"True positives saved in {true_positive_dir}")

# Visualization of problematic images
def visualize_images(image_paths, title="Problematic Images"):
    plt.figure(figsize=(12, 8))
    for i, path in enumerate(image_paths):
        img = cv2.imread(path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.subplot(1, len(image_paths), i + 1)
        plt.imshow(img_rgb)
        plt.axis('off')
        plt.title(f"Image {i+1}")
    plt.suptitle(title)
    plt.show()

# Example usage: visualizing false positives
false_positive_images = [os.path.join(false_positive_dir, f) for f in os.listdir(false_positive_dir)]
visualize_images(false_positive_images, title="False Positive Detections")
