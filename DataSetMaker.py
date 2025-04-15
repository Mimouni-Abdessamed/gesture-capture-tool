import cv2
import os
import time

# === Configuration ===
gesture_name = input("Enter the gesture name: ").upper()
capture_interval = 0.5  # seconds
images_per_hand = 100
target_size = (224, 224)  # Resize target

# === Paths ===
base_path = os.path.join("dataset", gesture_name)
left_path = os.path.join(base_path, "left")
right_path = os.path.join(base_path, "right")

# Create directories if they don't exist
os.makedirs(left_path, exist_ok=True)
os.makedirs(right_path, exist_ok=True)

# === Camera Setup ===
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

    frame = cv2.flip(frame, 1)  # Flip for mirror view

    # Crop to right half (you can adjust if needed)
    height, width, _ = frame.shape
    frame = frame[:, width // 2:]  # Use right half of the frame (X axis)

    # Frame to show instructions
    display_frame = frame.copy()

    # Display instructions
    if not capturing:
        instruction = f"Press 's' to start capturing {hand} hand ({gesture_name})"
    elif paused:
        instruction = "Paused. Press 'a' to resume/pause."
    else:
        instruction = f"Capturing {hand} hand: {image_count}/{images_per_hand} ({gesture_name})"

    control_instructions = "Press 'a' to pause/resume | Press 'q' to quit"
    cv2.putText(display_frame, instruction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(display_frame, control_instructions, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Capture and save frame
    if capturing and not paused:
        if time.time() - last_capture_time >= capture_interval:
            save_folder = left_path if hand == "left" else right_path
            filename = f"{gesture_name}_{hand}_{image_count:03}.jpg"
            save_path = os.path.join(save_folder, filename)

            resized_frame = cv2.resize(frame, target_size)
            cv2.imwrite(save_path, resized_frame)
            print(f"Saved: {save_path}")
            image_count += 1
            last_capture_time = time.time()

        if image_count >= images_per_hand:
            capturing = False
            image_count = 0
            if hand == "left":
                print(f"✅ Finished LEFT hand. Press 's' to start RIGHT hand for gesture '{gesture_name}'.")
                hand = "right"
            else:
                print("✅ Finished RIGHT hand. All done! Exiting now...")
                break  # Auto-quit after both hands

    # Show frame
    cv2.imshow("Hand Data Capture", display_frame)

    # Keyboard controls
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
        print("⏸️ Paused." if paused else "▶️ Resumed.")

cap.release()
cv2.destroyAllWindows()
