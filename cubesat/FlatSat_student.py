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
import time
import board
from PIL import Image
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2, Preview


#VARIABLES
THRESHOLD = 8      #Any desired value from the accelerometer
REPO_PATH = "/home/pi/cubegeeks"     #Your github repo path: ex. /home/pi/FlatSatChallenge
FOLDER_PATH = "/cubesat"  #Your image folder path in your GitHub repo: ex. /Images

#imu and camera initialization
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)
picam2 = Picamera2()


def git_push():
    """
    This function is complete. Stages, commits, and pushes new images to your GitHub repo.
    """
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        print('added remote')
        origin.pull()
        print('pulled changes')
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo')
        print('made the commit')
        origin.push()
        print('pushed changes')
    except:
        print('Couldn\'t upload to git')


def img_gen(name):
    """
    This function is complete. Generates a new image name.

    Parameters:
        name (str): your name ex. MasonM
    """
    t = time.strftime("_%H%M%S")
    imgname = (f'{REPO_PATH}/{FOLDER_PATH}/{name}{t}.jpg')
    return imgname


def take_photo():
    """
    This function is NOT complete. Takes a photo when the FlatSat is shaken.
    Replace psuedocode with your own code.
    """


    while True:
        accelx, accely, accelz = accel_gyro.acceleration
        acceleration = accelx ** 2 + accely ** 2 + accelz ** 2
        magnitude = acceleration ** (1/2)
        

        if magnitude > THRESHOLD:
            print("SHAKE")
            picam2.configure(picam2.create_preview_configuration({"format": "RGB888"}))
            min_exp, max_exp, default_exp = picam2.camera_controls["AfPause"]

            name = "Test"
            photo_name = img_gen(name)
            
            picam2.start()

            image = picam2.capture_image("main")
            arr = picam2.capture_array("main")
            image.save(photo_name)
            git_push()
            print("picture done")
            picam2.stop()
            return arr
            
            
            

            

        

        #CHECKS IF READINGS ARE ABOVE THRESHOLD
            #PAUSE
            #name = ""     #First Name, Last Initial  ex. MasonM
            #TAKE PHOTO
            #PUSH PHOTO TO GITHUB
        
        #PAUSE
def process_image(image):
    d = dict()
    d["Area1"] = 0
    d["Area2"] = 0
    d["Area3"] = 0
    d["Area4"] = 0

    #White: (256, 256, 256), #black: (0, 0, 0)
    for i in range(len(image)):
        for j in range(len(image[0])):
            #area 1
            temp = sum(image[i][j])
            if i <= 239:
                if j <= 319:
                    #Area1
                    if temp >= 175:
                        d["Area1"] += 1
                else:
                    #Area3
                    if temp >= 175:
                        d["Area3"] += 1
            else:
                if j <= 319:
                    #Area2
                    if temp >= 175:
                        d["Area2"] += 1
                else:
                    #Area4
                    if temp >= 175:
                        d["Area4"] += 1    
    return d
def detect_difference(before, after):
    arr = [False] * 4
    for i in range(len(before)):
        if before[i] - after[i] > 10000:
            arr[i] = True

    return arr

def detect_difference_one(Onephoto):
    arr = [False] * 4
    for i in range(len(Onephoto)):
        if Onephoto[i] > 10000:
            arr[i] = True
    return arr


def compare(before, after):

    d = dict()
    d["Area1"] = 0
    d["Area2"] = 0
    d["Area3"] = 0
    d["Area4"] = 0

    for i in range(len(before)):
        for j in range(len(before[0])):

            cell_before = sum(before[i][j])
            cell_after = sum(after[i][j])

            if i <= 239:
                if j <= 319:
                    #Area1
                    if cell_before - cell_after >= 150:
                        d["Area1"] += 1
                else:
                    #Area3
                    if cell_before - cell_after >= 150:
                        d["Area3"] += 1
            else:
                if j <= 319:
                    #Area2
                    if cell_before - cell_after >= 150:
                        d["Area2"] += 1
                else:
                    #Area4
                    if cell_before - cell_after >= 150:
                        d["Area4"] += 1
    
    lst = list(d.values())
    result = [False] * 4
    for i in range(len(lst)):
        if lst[i] >= 15000:
            result[i] = True
    return result

def main():
    Stop = 0
    while True:
        if Stop == 3:
            break
        image_1 = take_photo()

        processed_1 = process_image(image_1)

        print(processed_1)

        arr_1 = list(processed_1.values())

        image_1_black = detect_difference_one(arr_1)

        print(image_1_black)

        Stop+=1
        time.sleep(1)

        
    # image_2 = take_photo()

    # processed_2 = process_image(image_2)

    # print(processed_2)

    # arr_2 = list(processed_2.values())

    # image_2_black = detect_difference_one(arr_2)

    # print("Image 1: " + image_1_black)

    

if __name__ == '__main__':
    # print("Hello World!")
    main()
