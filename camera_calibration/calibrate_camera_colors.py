import cv2
import numpy as np

def nothing(x):
    pass

def calibrate_color_ranges_on_image(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error loading image.")
        return
    
    # Create a window
    cv2.namedWindow('Calibration')

    # Create trackbars for color change
    cv2.createTrackbar('H Lower', 'Calibration', 0, 179, nothing)
    cv2.createTrackbar('S Lower', 'Calibration', 0, 255, nothing)
    cv2.createTrackbar('V Lower', 'Calibration', 0, 255, nothing)
    cv2.createTrackbar('H Upper', 'Calibration', 179, 179, nothing)
    cv2.createTrackbar('S Upper', 'Calibration', 255, 255, nothing)
    cv2.createTrackbar('V Upper', 'Calibration', 255, 255, nothing)

    # Set initial values
    cv2.setTrackbarPos('H Lower', 'Calibration', 5)
    cv2.setTrackbarPos('S Lower', 'Calibration', 100)
    cv2.setTrackbarPos('V Lower', 'Calibration', 100)
    cv2.setTrackbarPos('H Upper', 'Calibration', 15)
    cv2.setTrackbarPos('S Upper', 'Calibration', 255)
    cv2.setTrackbarPos('V Upper', 'Calibration', 255)

    while True:
        # Get the current positions of the trackbars
        h_lower = cv2.getTrackbarPos('H Lower', 'Calibration')
        s_lower = cv2.getTrackbarPos('S Lower', 'Calibration')
        v_lower = cv2.getTrackbarPos('V Lower', 'Calibration')
        h_upper = cv2.getTrackbarPos('H Upper', 'Calibration')
        s_upper = cv2.getTrackbarPos('S Upper', 'Calibration')
        v_upper = cv2.getTrackbarPos('V Upper', 'Calibration')

        # Convert image to HSV color space
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Create mask for the specified color
        lower_color = np.array([h_lower, s_lower, v_lower])
        upper_color = np.array([h_upper, s_upper, v_upper])
        color_mask = cv2.inRange(hsv_image, lower_color, upper_color)

        # Apply the mask to the image
        result = cv2.bitwise_and(image, image, mask=color_mask)

        # Show the original image and the masked result
        cv2.imshow('Original Image', image)
        cv2.imshow('Masked Result', result)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    calibrate_color_ranges_on_image('test_image.jpeg')
