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
    _, picture = camera.read()
    camera.release()

    # Return to main if picture is empty
    if picture is None:
        # Log for empty picture
        return False

    # Resize, colorshift, mask and project image
    picture : np.ndarray = cv2.resize(src = picture, dsize = (400,300))
    picture_hsv : np.ndarray = cv2.cvtColor(src = picture, code = cv2.COLOR_BGR2HSV)
    mask : np.ndarray = getMask(image = picture_hsv, color = "blue")

    if type(mask) == bool and not mask:
        # Log for mask error (color not found)
        return False

    projection : np.ndarray = getProjection(image = picture, mask = mask)

    if type(projection) == bool and not projection:
        # Log for projection error
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

    # Comparison
    averageValuesRef = np.average(np.array([np.average(referencePicture[0]), np.average(referencePicture[1]), np.average(referencePicture[2])]))
    averageValueNew = np.average(np.array([np.average(newPicture[0]), np.average(newPicture[1]), np.average(newPicture[2])]))
    if (np.abs(averageValueNew - averageValuesRef) > 10):
            # send messageType: UnexpectedInterference
            camera.release()
            return True
    camera.release()
