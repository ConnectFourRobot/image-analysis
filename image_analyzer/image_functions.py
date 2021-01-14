import cv2
#from cv2 import cv2 # Visual Studio Code only, will be removed in final version
import numpy as np
from image_analyzer.image_processing import colorThresholds, findTokens, getGameBoard, getMask, getProjection

# Handle all function calls in this file

# 0 Check for open camera
def cameraCheck() -> int:
    for x in range(10):
        camera = cv2.VideoCapture(x, cv2.CAP_DSHOW)
        if camera is None or not camera.isOpened():
            continue
        elif camera.isOpened():
            return x
        else:
            return False


# 1 complete process as in image_processing
def analyseImage(cameraID : int) -> bytearray:
    # Create camera object and get a picture
    camera = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
    camera.open(cameraID)
    _, picture = camera.read()
    camera.release()

    # Return to main if picture is empty
    if picture is None:
        # Log for empty picture
        print('empty pictures')
        return False

    # Resize, colorshift, mask and project image
    picture : np.ndarray = cv2.resize(src = picture, dsize = (400,300))
    picture_hsv : np.ndarray = cv2.cvtColor(src = picture, code = cv2.COLOR_BGR2HSV)
    mask : np.ndarray = getMask(image = picture_hsv, color = "blue")

    if type(mask) == bool and not mask:
        # Log for mask error (color not found)
        print('no mask found')
        return False

    projection : np.ndarray = getProjection(image = picture, mask = mask)

    if type(projection) == bool and not projection:
        # Log for projection error
        print('Error in calculating the projection')
        return False

    # Calculate game tokens
    redTokens : list = findTokens(sourceImage = projection, tokenColor = "red")
    yellowTokens : list = findTokens(sourceImage = projection, tokenColor = "yellow")

    # Calculate game grid
    output : np.ndarray = getGameBoard(shape = projection.shape, redTokens = redTokens, yellowTokens = yellowTokens)

    return bytearray(output)


# 2 robot turn
def detectHumanInteraction(cameraID : int) -> bool:
    # Take a picture
    camera = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
    _, referencePicture = camera.read()
    referencePicture : np.ndarray = cv2.resize(src = referencePicture, dsize = (400,300))

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
