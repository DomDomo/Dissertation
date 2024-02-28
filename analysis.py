import cv2
import numpy as np
import pytesseract

# Load the screenshot
img = cv2.imread('screenshot.png')


def display_modified_image(img):
    # Create a named window with the WINDOW_NORMAL and WINDOW_KEEPRATIO flags
    cv2.namedWindow('Image with Contours',
                    cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

    # Display the image with contours
    cv2.imshow('Image with Contours', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Alternative matplotlib display

    # import matplotlib.pyplot as plt

    # # Display the image with contours using matplotlib
    # plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # plt.show()


def display_text_detection():
    # Use pytesseract to detect text
    text_data = pytesseract.image_to_data(
        img, output_type=pytesseract.Output.DICT)

    # Draw the bounding boxes on the image
    num_boxes = len(text_data['level'])
    for i in range(num_boxes):
        (x, y, w, h) = (text_data['left'][i], text_data['top']
                        [i], text_data['width'][i], text_data['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    display_modified_image(img)


def display_boundries():
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply image thresholding
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Detect edges in the image
    edges = cv2.Canny(thresh, 100, 200)

    # Find contours in the image
    contours, _ = cv2.findContours(
        edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Draw the contours on the original image
    cv2.drawContours(img, contours, -1, (0, 255, 0), 3)

    display_modified_image(img)


# display_text_detection()
display_boundries()
