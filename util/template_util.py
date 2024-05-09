import os
import cv2


def check_for_generator(folder, screenshot_name, template_name, template_threshold):
    screenshot_path = os.path.join(folder, screenshot_name)
    template_path = template_name
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path, 0)
    result = cv2.matchTemplate(cv2.cvtColor(
        screenshot, cv2.COLOR_BGR2GRAY), template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    print(max_val)

    if max_val >= template_threshold:
        top_left = max_loc
        bottom_right = (top_left[0] + template.shape[1],
                        top_left[1] + template.shape[0])
        center_x = (top_left[0] + bottom_right[0]) // 2
        center_y = (top_left[1] + bottom_right[1]) // 2
        return True, center_x, center_y

    return False, None, None
