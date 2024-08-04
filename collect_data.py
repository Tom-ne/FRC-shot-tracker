import cv2
import numpy as np
import time

def main():
    cap = cv2.VideoCapture(0)
    backSub = cv2.createBackgroundSubtractorMOG2()

    shot_positions = []

    # Adjust these values based on your shot color
    lower_color = np.array([5, 100, 100])
    upper_color = np.array([15, 255, 255])

    # Get initial frame to determine dimensions
    ret, frame = cap.read()
    if ret:
        frame_height, frame_width = frame.shape[:2]
        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2

        # Print frame center position once
        print(f"Frame center position: ({frame_center_x}, {frame_center_y})")
    else:
        print("Failed to capture initial frame.")
        cap.release()
        cv2.destroyAllWindows()
        return

    prev_center = None
    prev_velocity = None

    # Define a threshold for detecting significant velocity changes
    velocity_change_threshold = 10.0  # Adjust this value as needed

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to HSV color space
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create mask for the specified color
        color_mask = cv2.inRange(hsv_frame, lower_color, upper_color)

        # Apply background subtraction
        fgMask = backSub.apply(frame)

        # Combine color mask with background mask
        combined_mask = cv2.bitwise_and(fgMask, color_mask)

        # Threshold the mask to get a binary image
        _, thresh = cv2.threshold(combined_mask, 50, 255, cv2.THRESH_BINARY)

        # Find contours of the detected shots
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Adjust the threshold as needed
                x, y, w, h = cv2.boundingRect(contour)
                center_x, center_y = x + w // 2, y + h // 2

                # Draw rectangle around detected object
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Draw circle at the center of detected object
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

                # Calculate velocity
                if prev_center is not None:
                    dx = center_x - prev_center[0]
                    dy = center_y - prev_center[1]
                    velocity = np.sqrt(dx**2 + dy**2)

                    # Calculate and print velocity change
                    if prev_velocity is not None:
                        velocity_change = abs(velocity - prev_velocity)
                        
                        # Check if velocity change exceeds threshold
                        if velocity_change > velocity_change_threshold:
                            print(f"Significant speed difference detected: {velocity_change:.2f} at ({center_x}, {center_y})")
                            shot_positions.append((center_x, center_x))

                    prev_velocity = velocity
                # Pause briefly to avoid overwhelming the console with too many messages
                time.sleep(0.5)

        # Draw the center of the frame
        cv2.circle(frame, (frame_center_x, frame_center_y), 5, (255, 0, 0), -1)

        # Display the frame
        cv2.imshow('Frame', frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("Shot positions:", shot_positions)

if __name__ == "__main__":
    main()
