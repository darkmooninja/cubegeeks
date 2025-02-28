"""
The Python code you will write for this module should read
acceleration data from the IMU. When a reading comes in that surpasses
an acceleration threshold (indicating a shake), your Pi should pause,
trigger the camera to take a picture, then save the image with a
descriptive filename. You may use GitHub to upload your images automatically,
but for this activity it is not required.

The provided functions are only for reference, you do not need to use them. 
You will need to complete the take_photo() function and configure the VARIABLES section
"""

#AUTHOR: 
#DATE:


#import libraries
# Import libraries
import time
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2

# VARIABLES
THRESHOLD = 8  # Acceleration threshold for detecting a shake
REPO_PATH = "/home/cubegeeks/cubegeeks"  # Your GitHub repo path
FOLDER_PATH = "/cubesat"  # Folder path for storing images

# IMU and camera initialization
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)
picam2 = Picamera2()

def git_push():
    """
    Stages, commits, and pushes new images to GitHub.
    """
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        origin.pull()
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo')
        origin.push()
        print('Photo uploaded to GitHub.')
    except Exception as e:
        print(f'Git upload failed: {e}')

def img_gen(name):
    """
    Generates a unique image filename using the current timestamp.
    """
    timestamp = time.strftime("_%H%M%S")
    return f'{REPO_PATH}/{FOLDER_PATH}/{name}{timestamp}.jpg'

def take_photo():
    """
    Monitors IMU data for shakes and takes a photo when a shake is detected.
    """
    while True:
        accelx, accely, accelz = accel_gyro.acceleration
        magnitude = (accelx ** 2 + accely ** 2 + accelz ** 2) ** 0.5
        print(magnitude + "hello world!")
        if magnitude > THRESHOLD:
            print("SHAKE DETECTED! Capturing photo...")
            
            name = "Test"
            photo_name = img_gen(name)
            
            picam2.configure(picam2.create_still_configuration())
            picam2.start()
            time.sleep(1)  # Allow camera to adjust exposure
            image = picam2.capture_image()
            image.save(photo_name)
            picam2.stop()
            
            print(f"Photo saved: {photo_name}")
            git_push()
            
            time.sleep(2)  # Prevent multiple triggers in quick succession

def main():
    print("IMU Shake Detection Running...")
    take_photo()

if __name__ == "__main__":
    main()