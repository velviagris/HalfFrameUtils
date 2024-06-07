import os
import cv2

def process(file, import_folder_path, export_folder_path):
    # Read the image
    img = cv2.imread(f"{import_folder_path}/{file}")
    if img is None:
        print("Error: Image not found or unable to open.")
        return
    
    height, width = img.shape[:2]
    center_x = width // 2

    # Define the region around the center to search for the black line
    region_start = center_x - 100
    region_end = center_x + 100

    # Extract the center region of the image
    center_region = img[:, region_start:region_end]

    # Convert to grayscale
    gray = cv2.cvtColor(center_region, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to get a binary image
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours by area and take the largest one which should be the black line
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    largest_contour = contours[0]
    
    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Determine the splitting line and the width of the black line
    splitting_line = region_start + x + w // 2
    line_width = w

    if line_width < 175:
        line_width = 175
    elif line_width > 190:
        line_width = 190
    
    # Split the image into two halves without the black line
    left_image = img[:, :splitting_line - line_width // 2]
    right_image = img[:, splitting_line + line_width // 2:]
    
    # Ensure output directory exists
    if not os.path.exists(f"{export_folder_path}/hf"):
        os.mkdir(f"{export_folder_path}/hf")

    # Save the two halves
    cv2.imwrite(f"{export_folder_path}/hf/{file}-1.jpg", left_image)
    cv2.imwrite(f"{export_folder_path}/hf/{file}-2.jpg", right_image)