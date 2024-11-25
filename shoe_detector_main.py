from shoe_detector_detection import track_shoes
from shoe_detector_notification import show_notification
from shoe_detector_control_panel import ControlPanel
from shoe_detector_database import save_detection
import cv2
import time
import threading

def shoe_detection_thread(control_panel):
    cap = cv2.VideoCapture(0)  # Open webcam
    notified_shoes = set()  # Set to track notified shoe IDs
    tracked_shoes = []  # To keep track of the current shoes in the frame

    while not control_panel.exit_flag:
        ret, frame = cap.read()
        if not ret:
            break

        # Track shoes in the current frame
        tracked_shoes = track_shoes(frame)

        # Check and handle notifications
        for shoe in tracked_shoes:
            shoe_id = shoe.id

            # Notify if shoe is not in the notified set
            if shoe_id not in notified_shoes:
                # Retrieve the duration set in the control panel (e.g., slider or user input)
                durationNotification = control_panel.duration_slider.get() / 2  # Assuming you're using a slider for duration
                durationAlarm = control_panel.alarm_duration_slider.get()

                # Show notification for new shoe ID with the user-defined duration (only if enabled)
                if control_panel.popup_enabled:
                    show_notification(durationNotification)
                
                if control_panel.alarm_enabled:
                    control_panel.play_alarm_sound(durationAlarm)

                    
                x1, y1, x2, y2 = shoe.bbox
                detected_shoe_image = frame[y1:y2, x1:x2]
                save_detection(detected_shoe_image, shoe_id)
                

                
                # Add the shoe ID to the notified set
                notified_shoes.add(shoe_id)

        # Check for shoes that are no longer in the frame and remove them from notified_shoes
        current_ids = {shoe.id for shoe in tracked_shoes}
        for notified_id in list(notified_shoes):
            if notified_id not in current_ids:
                notified_shoes.remove(notified_id)  # Remove ID if it goes out of frame

        # Display tracked results
        for shoe in tracked_shoes:
            x1, y1, x2, y2 = shoe.bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {shoe.id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Show the frame
        cv2.imshow("Shoe Detection and Tracking", frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    control_panel = ControlPanel()
    detection_thread = threading.Thread(target=shoe_detection_thread, args=(control_panel,))
    detection_thread.start()
    control_panel.ctk.mainloop()
    detection_thread.join()

if __name__ == "__main__":
    main()
