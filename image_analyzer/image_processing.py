import cv2
#from cv2 import cv2 # Visual Studio Code only, will be removed in final version
import numpy as np
from image_analyzer.ia_logging.ia_logger import loggingIt

colorThresholds : dict = {
                "blue" : [np.array([93, 90, 33]), np.array([141, 255, 222])],
                "red" : [np.array([0, 73, 147]), np.array([9, 255, 253])],
                "yellow" : [np.array([17, 58, 63]), np.array([40, 242, 255])]
                }

def getMask(image : np.ndarray, color : str) -> np.ndarray:
    if color in colorThresholds.keys():
        return cv2.inRange(src = image, lowerb = colorThresholds[color][0], upperb = colorThresholds[color][1])
    else:
        return False

def getProjection(image : np.ndarray, mask : np.ndarray) -> np.ndarray:
    # Get contours
    contours, _ = cv2.findContours(image = mask, mode = cv2.RETR_TREE, method = cv2.CHAIN_APPROX_SIMPLE)    # check if RETR_LIST is better or other methods
                                                                                                            # check if grayscale is better than mask

    if not contours:
        # Log for no contours found
        loggingIt("No contours were found.")
        return False

    # Calculate biggest contour
    maxContourArea : np.uint16 = 0
    maxContourIndex : np.uint8 = 0
    for idx, cont in enumerate(contours):
        _, _, width, height = cv2.boundingRect(array = cont)
        area = width * height
        if area > maxContourArea:
            maxContourArea = area
            maxContourIndex = idx
    
    # Check if contour is big enough to be the board
    height, width = mask.shape
    percentage = maxContourArea / (width * height) * 100
    if percentage < 20:
        # Log for board not found
        loggingIt("Contour is too small to be the board.")
        return False
    
    # Get a blank image with only the contours
    contourImage = np.zeros_like(a = mask, dtype = np.uint8)
    cv2.drawContours(image = contourImage, contours = contours, contourIdx = maxContourIndex, color = (255))

    # Get lines through HoughTransformation
    lines = cv2.HoughLines(image = contourImage, rho = 1, theta = np.pi / 180, threshold = 60)

    if lines.size == 0:
        # Log for no HoughLines found
        loggingIt("No HoughLines were found.")
        return False

    # Calculate the coordinates of the found lines and append to list
    detectedLines : list = []
    for line in lines:
        (rho, theta) = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        _, (x1, y1), (x2, y2) = cv2.clipLine(imgRect = (0, 0, width, height), pt1 = (x1, y1), pt2 = (x2, y2))
        detectedLines.append(np.array([x1, y1, x2, y2]))

    # Call to calculateBorderFromLines, just below
    corners = getCorners(lines = detectedLines)

    if not corners:
        # Log not enough corners found
        loggingIt("No corners were found.")
        return False

    cornersPicture = np.array([
                                (0, 0), 
                                (width, 0), 
                                (0, height), 
                                (width, height)
                            ])
    
    cornersPicture = np.float32(cornersPicture[:,np.newaxis,:]) # New dimension needed for opencv2 functions

    transform = cv2.getPerspectiveTransform(src = np.float32(corners), dst = cornersPicture)
    dst = cv2.warpPerspective(src = image, M = transform, dsize = (width, height))

    return dst

def getIntersection(line_1 : tuple, line_2 : tuple):# -> tuple:
    # Get start and end points of each line
    x_1, y_1, x_2, y_2 = line_1
    x_3, y_3, x_4, y_4 = line_2

    denominator = ((x_1 - x_2) * (y_3 - y_4) - (y_1 - y_2) * (x_3 - x_4))

    if -0.1 < denominator < 0.1:
        return False
    else:
        # Calculate coordinates of intersection, for formula check Line-line intersection
        p_x = ((x_1*y_2 - y_1 * x_2) * (x_3 - x_4) - (x_1 - x_2) * (x_3 * y_4 - y_3 * x_4)) / denominator
        p_y = ((x_1*y_2 - y_1 * x_2) * (y_3 - y_4) - (y_1 - y_2) * (x_3 * y_4 - y_3 * x_4)) / denominator

        return (p_x, p_y)

# angle = acos(v1•v2)
def validTheta(line1, line2) -> bool:
    theta = np.arccos(np.around(np.dot(normalizeVector(np.array((line1[2] - line1[0], line1[3] - line1[1]), dtype=np.int16)), normalizeVector(np.array((line2[2] - line2[0], line2[3] - line2[1]), dtype=np.int16))), decimals=2))
    return (np.pi/3 < theta < (3*np.pi)/4) or (5*np.pi/4 < theta < 5*np.pi/3)

def normalizeVector(v):
    return v/np.linalg.norm(v)

def validPoint(point : tuple) -> bool:
    return ((0 <= point[0] <= 400) and (0 <= point[1] <= 300))

def getAveragePoint(points) -> tuple:
    x = 0
    y = 0
    for point in points:
        x = x + float(point[0])
        y = y + float(point[1])
    x = int(x / len(points))
    y = int(y / len(points))
    return (x, y)

def getCorners(lines):
    # Get all intersection points
    intersectionPoints = []
    for i in range(0, len(lines)):
        for j in range(i+1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            if validTheta(line1, line2): 
                point = getIntersection(line_1 = line1, line_2 = line2)
                # detect if out of bounds
                if (point and validPoint(point)):
                    intersectionPoints.append(point)
    if not intersectionPoints:
        # Log for no intersections found
        loggingIt("No intersections were found.")
        return False

    # Get average point in between all intersections
    averagePoint = getAveragePoint(points = intersectionPoints)

    # Corner Points
    topLeftPoints = []
    topRightPoints = []
    bottomLeftPoints = []
    bottomRightPoints = []

    # Append points to respective array
    for point in intersectionPoints:
        if point[0] < averagePoint[0]:
            if point[1] < averagePoint[1]:
                topLeftPoints.append(point)
            else:
                bottomLeftPoints.append(point)
        else:
            if point[1] < averagePoint[1]:
                topRightPoints.append(point)
            else:
                bottomRightPoints.append(point)
    
    # Check if enough corners are found
    if ((not topLeftPoints) or (not topRightPoints) or (not bottomLeftPoints) or (not bottomRightPoints)):
        # Log not enough corners found
        loggingIt("Not enough points in one of the corners.")
        return False

    # Distribute points to each respective corner
    topLeftPoints = list(topLeftPoints)
    topRightPoints = list(topRightPoints)
    bottomLeftPoints = list(bottomLeftPoints)
    bottomRightPoints = list(bottomRightPoints)

    # Get average point in each corner
    corners = [
                getAveragePoint(points = topLeftPoints), 
                getAveragePoint(points = topRightPoints), 
                getAveragePoint(points = bottomLeftPoints), 
                getAveragePoint(points = bottomRightPoints)
            ]

    return corners

def findTokens(sourceImage : np.ndarray, tokenColor : str) -> list:
    # First convert to HSV colorspace
    sourceImageHSV : np.ndarray = cv2.cvtColor(src = sourceImage, code = cv2.COLOR_BGR2HSV)

    # Create a mask of the respective color
    mask : np.ndarray = getMask(image = sourceImageHSV, color = tokenColor)

    # Find contours and look for circles
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    minCircles : list = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if (area > 200):
            (centerX, centerY), radius = cv2.minEnclosingCircle(contour)
            minCircles.append((centerX, centerY, radius))
    return minCircles

def getGameBoard(shape : tuple, redTokens : list, yellowTokens : list):
    # Split game board into equal blocks
    boardHeight, boardWidth, _ = shape
    blockWidth = boardWidth / 7
    blockHeight = boardHeight / 6

    # Generate empty grid and then check if insert token of respective color
    grid : np.ndarray = np.zeros(shape = (6, 7), dtype = np.int8)
    for row in range(0, 6):
        for column in range(0, 7):
            point : tuple = (column * blockWidth + blockWidth / 2, (6 - row - 1) * blockHeight + blockHeight / 2)
            for token in redTokens:
                if np.power((point[0] - token[0]), 2) + np.power((point[1] - token[1]), 2) <= np.power(token[2], 2):
                    grid[5 - row][column] = 2
                    break
            for token in yellowTokens:
                if np.power((point[0] - token[0]), 2) + np.power((point[1] - token[1]), 2) <= np.power(token[2], 2):
                    grid[5 - row][column] = 1
                    break

    return grid
