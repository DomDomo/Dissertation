import cv2

# Load the screenshot image
screenshot = cv2.imread('heroes_main.jpg')

# Load the template image
template = cv2.imread('ch_skull.jpg', 0)

# Perform template matching
result = cv2.matchTemplate(cv2.cvtColor(
    screenshot, cv2.COLOR_BGR2GRAY), template, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)


print(max_val, min_val, min_loc, max_loc)

# Set a threshold for template matching
threshold = 0.8

# Check if a match is found
if max_val >= threshold:
    # Calculate the coordinates of the matched region
    top_left = max_loc
    bottom_right = (top_left[0] + template.shape[1],
                    top_left[1] + template.shape[0])

    print("Match found!")
    print("Coordinates: Top Left:", top_left, "Bottom Right:", bottom_right)
else:
    print("No match found.")
