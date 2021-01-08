import cv2
#from cv2 import cv2 # Visual Studio Code only, will be removed in final version
import numpy as np

def polar2cart(rho, theta) -> tuple:
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return (x, y)

colorThresholds : dict = {
                "blue" : [np.array([111, 50, 147]), np.array([132, 205, 255])],
                "red" : [np.array([131, 39, 145]), np.array([179, 170, 255])],
                "yellow" : [np.array([17, 58, 63]), np.array([40, 242, 253])]
                }

def getMask(image : np.ndarray, color : str) -> np.ndarray:
    if color in colorThresholds.keys():
        return cv2.inRange(src = image, lowerb = colorThresholds[color][0], upperb = colorThresholds[color][1])
    else:
        print("Fail")
        return np.zeros_like(image) # discuss this corner case

def getProjection(image : np.ndarray, mask : np.ndarray) -> np.ndarray:
    # Get contours
    contours, _ = cv2.findContours(image = mask, mode = cv2.RETR_TREE, method = cv2.CHAIN_APPROX_SIMPLE)    # check if RETR_LIST is better or other methods
                                                                                                            # check if grayscale is better than mask

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
    if percentage < 20:                             #needs to be tested "better"
        print("Too small to be the board")
    
    # Get a blank image with only the contours
    contourImage = np.zeros_like(a = mask, dtype = np.uint8)
    cv2.drawContours(image = contourImage, contours = contours, contourIdx = maxContourIndex, color = (255))

    # Get lines through HoughTransformation
    lines = cv2.HoughLines(image = contourImage, rho = 1, theta = np.pi / 180, threshold = 60)
    print("Number of Hough Lines: ", str(len(lines)))

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

        cv2.clipLine(imgRect = (0, 0, width, height), pt1 = (x1, y1), pt2 = (x2, y2))
        detectedLines.append(np.array([x1, y1, x2, y2]))
    
    print("There are: " + str(len(detectedLines)) + " detected Lines!")

    # Call to calculateBorderFromLines, just below
    corners = getCorners(lines = detectedLines)
    cornersPicture = np.array([
                                (0, 0), 
                                (width, 0), 
                                (0, height), 
                                (width, height)
                            ])
    
    cornersPicture = np.float32(cornersPicture[:,np.newaxis,:]) # new dimension needed for opencv2 functions

    transform = cv2.getPerspectiveTransform(src = np.float32(corners), dst = cornersPicture)
    dst = cv2.warpPerspective(src = picture, M = transform, dsize = (width, height))

    return dst

def getIntersection(line_1 : tuple, line_2 : tuple) -> tuple:
    # Get start and end points of each line
    x_1, y_1, x_2, y_2 = line_1
    x_3, y_3, x_4, y_4 = line_2

    # Calculate coordinates of intersection, for formula check Line-line intersection
    p_x = ((x_1*y_2 - y_1 * x_2) * (x_3 - x_4) - (x_1 - x_2) * (x_3 * y_4 - y_3 * x_4)) / ((x_1 - x_2) * (y_3 - y_4) - (y_1 - y_2) * (x_3 - x_4))
    p_y = ((x_1*y_2 - y_1 * x_2) * (y_3 - y_4) - (y_1 - y_2) * (x_3 * y_4 - y_3 * x_4)) / ((x_1 - x_2) * (y_3 - y_4) - (y_1 - y_2) * (x_3 - x_4))

    return (p_x, p_y)

def validPoint(point : tuple) -> bool:
    return ((point[0] > 0) and (point[0] < 400)) and ((point[1] > 0) and (point[1] < 300))

def getAveragePoint(points) -> tuple:
    x = 0
    y = 0
    for point in points:
        x = x + float(point[0])
        y = y + float(point[1])
    x = x / len(points)
    y = y / len(points)
    return (x, y)

def getCorners(lines):
    # Get all intersection points
    intersectionPoints = []
    for i in range(0, len(lines)):
        for j in range(i+1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            point = getIntersection(line_1 = line1, line_2 = line2)
            # detect if out of bounds
            if validPoint(point):
                intersectionPoints.append(point)
    print("Intersections detected: " + str(len(intersectionPoints)))

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
        print("Could not identify the corners of the board.")
        # Send error

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
    cv2.imshow("token"+tokenColor, mask)

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
    grid : np.ndarray = np.zeros(shape = (6, 7))
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

# # Load picture, resize it, convert to HSV colorspace, get mask of color blue and finally transform to only the board
# #picture : np.ndarray = cv2.imread(filename = "./pictures/test_1.jpg")
# cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# _, picture = cam.read()
# picture : np.ndarray = cv2.resize(src = picture, dsize = (400, 300))            #should be dynamic in case of other ratio
# imag_hsv : np.ndarray = cv2.cvtColor(src = picture, code = cv2.COLOR_BGR2HSV)
# mask : np.ndarray = getMask(image = imag_hsv, color = "blue")
# projection : np.ndarray = getProjection(image = picture, mask = mask)

# # Showing images
# cv2.imshow(winname = 'picture', mat = picture)
# cv2.imshow(winname = 'imag_hsv', mat = imag_hsv)
# cv2.imshow(winname = 'mask', mat = mask)
# cv2.imshow(winname = 'projection', mat = projection)

# # Get red circles
# redTokens : list = findTokens(sourceImage = projection, tokenColor = "red")
# print("I found " + str(len(redTokens)) + " red tokens.")

# # Get yellow circles
# yellowTokens : list = findTokens(sourceImage = projection, tokenColor = "yellow")
# print("I found " + str(len(yellowTokens)) + " yellow tokens.")

# # Calculate token positions
# test = getGameBoard(shape = projection.shape, redTokens = redTokens, yellowTokens = yellowTokens)
# print(test)

# # Wait for input to end the display
# cv2.waitKey(0)
# cv2.destroyAllWindows()
