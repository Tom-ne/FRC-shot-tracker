import socket
import threading
import cv2
import numpy as np
import signal
import sys

def send_corners(client_socket, frame_width, frame_height):
    # Define the corners of the frame
    corners = [
        (0, 0),
        (frame_width, 0),
        (frame_width, frame_height),
        (0, frame_height)
    ]
    # Convert corners to a string format and send
    corners_str = ','.join(f"{x},{y}" for x, y in corners)
    client_socket.send(f"CORNERS:{corners_str}\n".encode('utf-8'))
    print(f"Sent corners to client: {corners_str}")

def detect_shots(client_socket):
    cap = cv2.VideoCapture(0)
    backSub = cv2.createBackgroundSubtractorMOG2()

    # Use the calibrated HSV values
    lower_color = np.array([5, 106, 70])
    upper_color = np.array([11, 255, 255])

    prev_center = None
    prev_velocity = None

    # Define a threshold for detecting significant velocity changes
    velocity_change_threshold = 20000.0  # Adjust this value as needed

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

        # Find contours of the shots
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        current_velocity = None
        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Adjust the threshold as needed
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
                        
                        # Compare velocity change to threshold
                        if velocity_change > velocity_change_threshold:
                            # Send the position to the client
                            response = f"{center_x},{center_y}\n"
                            client_socket.send(response.encode('utf-8'))
                            print(f"Sent position to client: ({center_x}, {center_y})")

                    # Update previous velocity
                    prev_velocity = velocity

                # Update previous center
                prev_center = (center_x, center_y)

        # Show the frame with drawn rectangles and circles
        cv2.imshow('Frame', frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def handle_client(client_socket):
    try:
        detect_shots(client_socket)
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Ensure client socket is closed
        client_socket.close()

def signal_handler(sig, frame):
    print("Keyboard interrupt received, shutting down.")
    sys.exit(0)

def start_server(host='127.0.0.1', port=8082):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server listening on {host}:{port}")

        # Handle keyboard interrupt to close server socket
        signal.signal(signal.SIGINT, signal_handler)

        try:
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr}")

                # Start a new thread to handle the client
                client_handler = threading.Thread(target=handle_client, args=(client_socket,))
                client_handler.start()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server_socket.close()
            print("Server socket closed.")

if __name__ == "__main__":
    start_server()
