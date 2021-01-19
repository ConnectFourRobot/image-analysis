import cv2
#from cv2 import cv2 # Visual Studio Code only, will be removed in final version
import numpy as np
from image_analyzer.image_processing import colorThresholds, findTokens, getGameBoard, getMask, getProjection
import os

# Handle all function calls in this file

# 0 Check for open camera
def cameraCheck() -> int:
    path = "/dev/"
    files = os.listdir(path)
    cameraIdx = []

    for file in files:
        if file.startswith("video"):
            cameraIdx.append(int(file.lstrip("video")))
    
    for cam in cameraIdx:
        camera = cv2.VideoCapture(cam, cv2.CAP_DSHOW)
        camera.open(cam)

        for _ in range(10):
            payload : bytearray = analyseImage(cameraID = cam)
            if type(payload) == bool and not payload:
                continue
            else:
                return cam
    
    # No camera found that can find a board
    return False
    

# 1 Get picture
def getPicture(cameraID : int) -> np.ndarray:
    camera = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
    camera.open(cameraID)
    _, picture = camera.read()
    camera.release()

    return picture

# 2 complete process as in image_processing
def analyseImage(cameraID : int) -> bytearray:
    # Get picture
    picture = getPicture(cameraID = cameraID)

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


# 3 robot turn
def detectHumanInteraction(referencePicture : np.ndarray, cameraID : int) -> bool:
    # Resize referencePicture
    referencePicture : np.ndarray = cv2.resize(src = referencePicture, dsize = (400,300))

    # Take new picture
    newPicture = getPicture(cameraID = cameraID)
    newPicture : np.ndarray = cv2.resize(src = newPicture, dsize = (400, 300))
    newPicture = newPicture[0:150, 0:400]

    # Comparison
    # Convert color scale to HSV
    hsvim = cv2.cvtColor(newPicture, cv2.COLOR_BGR2HSV)

    # Color boundaries for skin-tone
    lower = np.array([0, 48, 80], dtype = "uint8")
    upper = np.array([20, 255, 255], dtype = "uint8")

    # Apply mask
    skinRegionHSV = cv2.inRange(hsvim, lower, upper)
    blurred = cv2.blur(skinRegionHSV, (2,2))
    _, thresh = cv2.threshold(blurred,0,255,cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = max(contours, key=lambda x: cv2.contourArea(x))

    if (cv2.contourArea(contours) > 500):
        # send messageType: UnexpectedInterference
        return True
