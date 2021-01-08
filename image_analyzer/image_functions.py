import cv2
#from cv2 import cv2 # Visual Studio Code only, will be removed in final version
import numpy as np
from image_analyzer.image_processing import colorThresholds, findTokens, getGameBoard, getMask, getProjection

# Handle all function calls in this file

# 1 complete process as in image_processing
def analyseImage() -> bytearray:
    # Create camera object and get a picture
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    _, picture = camera.read()
    camera.release()

    # Resize, colorshift, mask and project image
    picture : np.ndarray = cv2.resize(src = picture, dsize = (400,300)) #make this dynamic, depending on camera resolution
    picture_hsv : np.ndarray = cv2.cvtColor(src = picture, code = cv2.COLOR_BGR2HSV)
    mask : np.ndarray = getMask(image = picture_hsv, color = "blue")
    projection : np.ndarray = getProjection(image = picture, mask = mask)
    
    # Calculate game tokens
    redTokens : list = findTokens(sourceImage = projection, tokenColor = "red")
    yellowTokens : list = findTokens(sourceImage = projection, tokenColor = "yellow")

    # Calculate game grid
    output : np.ndarray = getGameBoard(shape = projection.shape, redTokens = redTokens, yellowTokens = yellowTokens)

    return bytearray(output)


# 2 robot turn
def detectHumanInteraction() -> bool:
    # Take a picture
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    _, referencePicture = camera.read()
    referencePicture : np.ndarray = cv2.resize(src = referencePicture, dsize = (400,300)) #make this dynamic, depending on camera resolution

    # Take new picture and compare it
    while(True):
        # if messageType: StopAnalysis -> break
        _, newPicture = camera.read()
        newPicture : np.ndarray = cv2.resize(src = newPicture, dsize = (400, 300))

        totalPixels : np.uint16 = 400 * 300
        unequal : np.uint16 = 0

        # Compare first value of each pixel to speed up process of comparison
        # TO DO: threshhold value that is overwritten instead of just difference
        for x in range(0, 300):
            for y in range(0, 400):
                if (referencePicture[x][y][0] != newPicture[x][y][0]):
                    unequal = unequal + 1
        
        # If more than 30% of the pixels are changed: send UnexpectedInterference message
        # TO DO: Get some example pictures of moving robot and adjust 30% threshhold of changed pixels
        if (((unequal / totalPixels) * 100) > 30):
            # send messageType: UnexpectedInterference
            camera.release()
            return True
    camera.release()
