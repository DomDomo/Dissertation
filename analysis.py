import cv2

# Load the screenshot
img = cv2.imread('screenshot.png')

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply image thresholding
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Detect edges in the image
edges = cv2.Canny(thresh, 100, 200)

# Find contours in the image
contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Draw the contours on the original image
cv2.drawContours(img, contours, -1, (0, 255, 0), 3)

# Create a named window with the WINDOW_NORMAL and WINDOW_KEEPRATIO flags
cv2.namedWindow('Image with Contours',
                cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

# Display the image with contours
cv2.imshow('Image with Contours', img)
cv2.waitKey(0)
cv2.destroyAllWindows()


# Optional matplotlib display

# import matplotlib.pyplot as plt
# # Display the image with contours using matplotlib
# plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
# plt.show()
