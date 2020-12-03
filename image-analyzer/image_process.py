import cv2 # In Visual Studio Code use: from cv2 import cv2
import numpy as np

picture = cv2.imread("./pictures/test_1.jpg", 1)
picture = cv2.resize(picture, (400, 300))

# Convert BGR to HSV
hsv = cv2.cvtColor(picture, cv2.COLOR_BGR2HSV)

# define range of blue color in HSV 
new_lower = np.array([111, 50, 147])
new_upper = np.array([132, 205, 255])

# Threshold the HSV image to get only blue colors
mask = cv2.inRange(hsv, new_lower, new_upper)

# Bitwise-AND mask and original image
res = cv2.bitwise_and(picture,picture, mask=mask)

# Get Contours
retval, thresh_gray = cv2.threshold(mask, thresh=100, maxval=255, type=cv2.THRESH_BINARY)#_INV)

contours, hierarchy = cv2.findContours(thresh_gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) # use HOUGH

mx = (0, 0, 0, 0)
mx_area = 0
for cont in contours:
    x, y, w, h = cv2.boundingRect(cont)
    area = w*h
    if area > mx_area:
        mx = x, y, w, h
        mx_area = area

x,y,w,h = mx
roi=picture[y:y+h, x:x+w]

# Displaying images

cv2.imshow("Image_crop.jpg", roi)
cv2.rectangle(picture,(x,y), (x+w,y+h), (200,0,0),2)

cv2.imshow('picture',picture)
cv2.imshow('mask',mask)
cv2.imshow('res',res)

### SEAM

image = res.copy()

#cv2.imshow("Image", image)
output = res.copy()

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#cv2.imshow("gray", gray)

blur = cv2.GaussianBlur(gray, (5, 5), 0)
#cv2.imshow("blur", blur)

thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)
cv2.imshow("thresh", thresh)

circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, 1.1, 18, param1=100, param2=10,minRadius=8, maxRadius=12)

if circles is not None:
	# convert the (x, y) coordinates and radius of the circles to integers
	circles = np.round(circles[0, :]).astype("int")
	# loop over the (x, y) coordinates and radius of the circles
	for (x, y, r) in circles:
		# draw the circle in the output image, then draw a rectangle
		# corresponding to the center of the circle
		cv2.circle(output, (x, y), r, (0, 255, 0), 1)
		cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), 1)
	# show the output image
	cv2.imshow("output", np.hstack([image, output]))

circle_coordinates = []
for elem in circles[:42]:
    circle_coordinates.append(elem)
for elem in circle_coordinates:
    cv2.circle(picture, (elem[0], elem[1]), 2, (255, 255, 255), 1)
cv2.imshow("FINAL", picture)

cv2.waitKey(0)
cv2.destroyAllWindows()