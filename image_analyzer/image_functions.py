import cv2
#from cv2 import cv2 # Visual Studio Code only, will be removed in final version
import numpy as np
from image_processing import colorThresholds, findTokens, getGameBoard, getMask, getProjection

# Handle all function calls in this file

# 1 complete process as in image_processing
def analyseImage() -> bytearray:
    # Create camera object and get a picture
    _camera = cv2.VideoCapture(0)
    picture : np.ndarray = _camera.read()
    _camera.release()

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
def detectHumanInteraction():
    # Take a picture
    _camera = cv2.VideoCapture(0)
    _referencePicture = _camera.read()

    # in a loop take new picture

    # compare the two, if more than ~20% change: interrupt