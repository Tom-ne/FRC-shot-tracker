import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)
backSub = cv2.createBackgroundSubtractorMOG2()

shot_positions = []

# adjust these values based on your shot color
lower_color = np.array([5, 100, 100])
upper_color = np.array([15, 255, 255])

# get initial frame to determine dimensions
ret, frame = cap.read()
if ret:
    # calculate the center of the frame
    frame_height, frame_width = frame.shape[:2]
    frame_center_x = frame_width // 2
    frame_center_y = frame_height // 2

    # print frame center position once
    print(f"Frame center position: ({frame_center_x}, {frame_center_y})")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # convert frame to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # create mask for the specified color
    color_mask = cv2.inRange(hsv_frame, lower_color, upper_color)

    # apply background subtraction
    fgMask = backSub.apply(frame)

    # combine color mask with background mask
    combined_mask = cv2.bitwise_and(fgMask, color_mask)

    # threshold the mask to get a binary image
    _, thresh = cv2.threshold(combined_mask, 50, 255, cv2.THRESH_BINARY)

    # find contours of the shots
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) > 100:  # adjust the threshold as needed
            x, y, w, h = cv2.boundingRect(contour)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            center_x, center_y = x + w // 2, y + h // 2

            shot_positions.append((center_x, center_y))

            print(f"Shot detected at position: ({center_x}, {center_y})")

            time.sleep(0.5)

    cv2.circle(frame, (frame_center_x, frame_center_y), 5, (255, 0, 0), -1)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("Shot positions:", shot_positions)
