import cv2
import numpy as np
import pytesseract

# Load the screenshot
img = cv2.imread('screenshot.png')

# Use pytesseract to detect text
text_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

# Draw the bounding boxes on the image
num_boxes = len(text_data['level'])
for i in range(num_boxes):
    (x, y, w, h) = (text_data['left'][i], text_data['top']
                    [i], text_data['width'][i], text_data['height'][i])
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Create a named window with the WINDOW_NORMAL and WINDOW_KEEPRATIO flags
cv2.namedWindow('Image with Text Bounding Boxes',
                cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

# Display the image with text bounding boxes
cv2.imshow('Image with Text Bounding Boxes', img)
cv2.waitKey(0)
cv2.destroyAllWindows()


# Optional matplotlib display

# import matplotlib.pyplot as plt
# # Display the image with contours using matplotlib
# plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
# plt.show()
