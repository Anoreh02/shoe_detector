from ultralytics import YOLO
import time

# Load the trained YOLO model
model = YOLO("model.pt")

    
class TrackedShoe:
    def __init__(self, bbox, id, timestamp):
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.id = id
        self.last_seen = timestamp

    def update(self, bbox, timestamp):
        self.bbox = bbox
        self.last_seen = timestamp

class ShoeTracker:
    def __init__(self):
        self.tracked_shoes = []
        self.next_id = 0  # Unique ID counter
        self.cooldown_time = 3.0  # Cooldown time in seconds

    def track(self, detections, current_time):
        new_tracks = []
        unmatched_detections = detections[:]
        
        # Match new detections with existing tracks
        for shoe in self.tracked_shoes:
            best_match = None
            best_iou = 0
            for detection in unmatched_detections:
                iou = calculate_iou(shoe.bbox, detection)
                if iou > 0.5 and iou > best_iou:
                    best_match = detection
                    best_iou = iou
            
            if best_match:
                # Update tracked shoe
                shoe.update(best_match, current_time)
                new_tracks.append(shoe)
                unmatched_detections.remove(best_match)
        
        # Add new detections as new tracks
        for detection in unmatched_detections:
            new_shoe = TrackedShoe(detection, self.next_id, current_time)
            new_tracks.append(new_shoe)
            self.next_id += 1
        
        # Filter out expired tracks
        self.tracked_shoes = [
            shoe for shoe in new_tracks
            if (current_time - shoe.last_seen) < self.cooldown_time
        ]

        return self.tracked_shoes  # Return updated list of tracked shoes
def calculate_iou(box1, box2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Args:
        box1 (tuple): Bounding box 1 in (x1, y1, x2, y2) format.
        box2 (tuple): Bounding box 2 in (x1, y1, x2, y2) format.

    Returns:
        float: IoU value, ranging from 0 to 1.
    """
    # Unpack box coordinates
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    # Calculate intersection coordinates
    inter_x1 = max(x1_1, x1_2)
    inter_y1 = max(y1_1, y1_2)
    inter_x2 = min(x2_1, x2_2)
    inter_y2 = min(y2_1, y2_2)

    # Compute intersection area
    inter_width = max(0, inter_x2 - inter_x1)
    inter_height = max(0, inter_y2 - inter_y1)
    intersection = inter_width * inter_height

    # Compute union area
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection

    # Handle division by zero
    if union == 0:
        return 0.0

    # Calculate IoU
    iou = intersection / union
    return iou

def track_shoes(frame):
    """
    Detect and track shoes in the given frame.

    Args:
        frame (numpy.ndarray): Input image frame.

    Returns:
        list: List of tracked shoes with stable IDs.
    """
    # Perform detection
    results = model(frame, conf=0.65)
    
    # Extract bounding boxes from results
    detections = []
    if results[0].boxes is not None:  # Check if any boxes are detected
        detections = [
            (
                int(box[0]),  # x1
                int(box[1]),  # y1
                int(box[2]),  # x2
                int(box[3])   # y2
            )
            for box in results[0].boxes.xyxy.cpu().numpy()  # Convert to NumPy array
        ]

    # Use ShoeTracker to assign stable IDs
    current_time = time.time()
    tracker = ShoeTracker()  # Ensure you use the same tracker instance across calls
    tracked_shoes = tracker.track(detections, current_time)

    return tracked_shoes
