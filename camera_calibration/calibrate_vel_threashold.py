import cv2
import numpy as np

def calibrate_velocity_threshold():
    # Parameters
    lower_color = np.array([5, 106, 70])
    upper_color = np.array([11, 255, 255])
    velocity_change_threshold = 20000.0  # Initial threshold

    cap = cv2.VideoCapture(0)
    backSub = cv2.createBackgroundSubtractorMOG2()
    
    prev_center = None
    prev_velocity = None

    def update_threshold(val):
        nonlocal velocity_change_threshold
        velocity_change_threshold = val

    cv2.namedWindow('Calibration')
    cv2.createTrackbar('Threshold', 'Calibration', int(velocity_change_threshold), 50000, update_threshold)

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

        # Find contours of the detected objects
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        current_velocity = None
        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Adjust this value if needed
                x, y, w, h = cv2.boundingRect(contour)
                center_x, center_y = x + w // 2, y + h // 2

                # Draw a rectangle around the detected object
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Draw a circle at the center of the detected object
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

                # Calculate velocity
                if prev_center is not None:
                    dx = center_x - prev_center[0]
                    dy = center_y - prev_center[1]
                    velocity = np.sqrt(dx**2 + dy**2)

                    if prev_velocity is not None:
                        velocity_change = abs(velocity - prev_velocity)

                        # Display velocity change and threshold
                        cv2.putText(frame, f"Velocity Change: {velocity_change:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                        # Draw a line indicating the threshold
                        if velocity_change > velocity_change_threshold:
                            cv2.putText(frame, f"Threshold Exceeded", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.line(frame, (0, 90), (frame.shape[1], 90), (0, 255, 0), 2)

                # Update previous velocity and center
                prev_velocity = velocity
                prev_center = (center_x, center_y)

        # Display the frame
        cv2.imshow('Calibration', frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    calibrate_velocity_threshold()
