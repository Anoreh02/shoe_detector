import os
from datetime import datetime
import cv2
from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "shoe_detections"
COLLECTION_NAME = "detections"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Directory to store detected shoe images
DETECTIONS_DIR = "database/images"

# Ensure the directory exists
if not os.path.exists(DETECTIONS_DIR):
    os.makedirs(DETECTIONS_DIR)

def save_detection(image, shoe_id):
    """
    Save the detection details to the local storage.

    Args:
        image (numpy.ndarray): The frame where the shoe was detected.
        shoe_id (int): Unique ID of the detected shoe.

    Returns:
        tuple: (file_path, date_time_str) of the saved image.
    """
    try:
        # Get the current date and time
        now = datetime.now()
        date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")

        # Create a unique filename for the shoe image
        filename = f"shoe_{shoe_id}_{date_time_str}.jpg"
        file_path = os.path.join(DETECTIONS_DIR, filename)

        # Save the image locally
        cv2.imwrite(file_path, image)

        # Log the detection to MongoDB
        detection_data = {
            "shoe_id": shoe_id,
            "timestamp": date_time_str,
            "image_path": file_path
        }
        collection.insert_one(detection_data)  # Save to MongoDB

        print(f"Detection saved to MongoDB and locally: {file_path}")

        return file_path, date_time_str
    
    except Exception as e:
        print(f"Error saving detection: {e}")
        return None, None
