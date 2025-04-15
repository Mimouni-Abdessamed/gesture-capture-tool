import cv2
import os
import time

# === Configuration ===
gesture_name = input("Enter the gesture name: ").upper()
capture_interval = 0.5  # seconds
images_per_hand = 100
target_size = (224, 224)  # Resize target

# Paths
base_path = os.path.join("dataset", gesture_name)
combined_path = os.path.join(base_path, "left_right")
os.makedirs(combined_path, exist_ok=True)

# Initialize camera
cap = cv2.VideoCapture(0)
hand = "left"
image_count = 0
capturing = False
paused = False
last_capture_time = time.time()

print(f"Press 's' to start capturing images for the LEFT hand of gesture '{gesture_name}'.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip horizontally

    # Crop to right half (X-axis)
    height, width, _ = frame.shape
    frame = frame[:, width // 2:]  # Keep right half of the frame only

    # Copy frame to display instructions on it (not affecting saved image)
    display_frame = frame.copy()

    # Display instructions
    if not capturing:
        instruction = f"Press 's' to start capturing {hand} hand ({gesture_name})"
    elif paused:
        instruction = "Paused. Press 'a' to resume or 'a' to pause."
    else:
        instruction = f"Capturing {hand} hand: {image_count}/{images_per_hand} ({gesture_name})"

    control_instructions = "Press 'a' to pause/resume | Press 'q' to quit"
    cv2.putText(display_frame, instruction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(display_frame, control_instructions, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Save resized frame
    if capturing and not paused:
        if time.time() - last_capture_time >= capture_interval:
            save_path = os.path.join(combined_path, f"{gesture_name}_{hand}_{image_count:03}.jpg")
            resized_frame = cv2.resize(frame, target_size)
            cv2.imwrite(save_path, resized_frame)
            print(f"Saved: {save_path}")
            image_count += 1
            last_capture_time = time.time()

        if image_count >= images_per_hand:
            capturing = False
            if hand == "left":
                print(f"✅ Finished LEFT hand. Press 's' to start RIGHT hand for gesture '{gesture_name}'.")
                hand = "right"
            else:
                print("✅ Finished RIGHT hand. Press 'q' to quit or run again for another gesture.")
            image_count = 0

    # Show frame with instructions
    cv2.imshow("Hand Data Capture", display_frame)

    # Handle key input
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        capturing = True
        paused = False
        last_capture_time = time.time()
        print(f"🟢 Started capturing {hand} hand for gesture '{gesture_name}'.")
    elif key == ord('q'):
        break
    elif key == ord('a'):
        paused = not paused
        print("⏸️ Capturing paused." if paused else "▶️ Capturing resumed.")

cap.release()
cv2.destroyAllWindows()
