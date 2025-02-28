import time
import cv2
import numpy as np
import board
from PIL import Image
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from picamera2 import Picamera2
from git import Repo

# Hello my name is Terry

# Constants
THRESHOLD = 11  # Shake detection threshold
REPO_PATH = "/home/cubegeeks/cubegeeks"
FOLDER_PATH = "/cubesat"

# Initialize IMU and Camera
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)  # Accelerometer + Gyroscope
mag = LIS3MDL(i2c)        # Magnetometer
picam2 = Picamera2()

def git_push():
    """Stages, commits, and pushes new images to GitHub."""
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        origin.pull()
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo')
        origin.push()
        print("Image pushed to GitHub.")
    except Exception as e:
        print(f"GitHub upload failed: {e}")

def img_gen(name):
    """Generates a timestamped image filename."""
    timestamp = time.strftime("_%H%M%S")
    return f"{REPO_PATH}/{FOLDER_PATH}/{name}{timestamp}.jpg"

def detect_red_areas(image):
    """Finds red areas and their positions."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define red color range
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Create masks
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2

    # Get coordinates of red pixels
    y_coords, x_coords = np.where(red_mask > 0)

    return red_mask, x_coords, y_coords

def classify_red_areas(image_width, image_height, x_coords, y_coords):
    """Classifies red areas into 8U directions."""
    directions = {"N": 0, "NE": 0, "E": 0, "SE": 0, "S": 0, "SW": 0, "W": 0, "NW": 0}
    center_x, center_y = image_width // 2, image_height // 2

    for x, y in zip(x_coords, y_coords):
        dx, dy = x - center_x, center_y - y  

        angle = np.arctan2(dy, dx) * (180 / np.pi)

        if -22.5 <= angle < 22.5:
            directions["E"] += 1
        elif 22.5 <= angle < 67.5:
            directions["NE"] += 1
        elif 67.5 <= angle < 112.5:
            directions["N"] += 1
        elif 112.5 <= angle < 157.5:
            directions["NW"] += 1
        elif (157.5 <= angle <= 180) or (-180 <= angle < -157.5):
            directions["W"] += 1
        elif -157.5 <= angle < -112.5:
            directions["SW"] += 1
        elif -112.5 <= angle < -67.5:
            directions["S"] += 1
        elif -67.5 <= angle < -22.5:
            directions["SE"] += 1

    return directions

def take_photo():
    """Detects shake, captures & processes image, classifies red pixels in 8U."""
    while True:
        accel_x, accel_y, accel_z = accel_gyro.acceleration
        magnitude = (accel_x**2 + accel_y**2 + accel_z**2) ** 0.5

        if magnitude > THRESHOLD:
            print("Shake detected! Taking photo." + str(magnitude))

            picam2.configure(picam2.create_preview_configuration({"format": "RGB888"}))
            picam2.start()
            image = picam2.capture_image("main")
            picam2.stop()

            image_cv = np.array(image)
            image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)

            red_mask, x_coords, y_coords = detect_red_areas(image_cv)

            # Get image dimensions
            height, width = red_mask.shape

            # Classify red pixels into 8U directions
            red_directions = classify_red_areas(width, height, x_coords, y_coords)

            print("Red pixel distribution:", red_directions)

            filename = img_gen("Shake")
            cv2.imwrite(filename.replace(".jpg", "_red.jpg"), red_mask)

            print(f"Processed image saved: {filename}")
            git_push()
            return
def main():
    print("IMU Shake Detection")
    take_photo()

if __name__ == "__main__":
    main()