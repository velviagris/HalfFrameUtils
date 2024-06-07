import argparse
import cv2
import os
import threading

parser = argparse.ArgumentParser()

parser.add_argument("-hf", "--halfframe", action="store_true", help="Splits half frame exposures into two images.")
parser.add_argument("-bw", "--blackwhite", action="store_true", help="Converts images to grayscale.")
parser.add_argument("-i", "--input", help="Input folder path.", type=str, required=True)
parser.add_argument("-o", "--output", help="Output folder path.", type=str, required=True)

args = parser.parse_args()

if not os.path.exists(args.input):
    print("The input folder does not exist")
if not os.path.exists(args.output):
    print("The output folder does not exist")

import_folder_path = "./import"
export_folder_path = "./export"

def get_filenames():
    files = []
    for file in os.listdir(import_folder_path):
        if file.endswith(".jpg"):
            files.append(file)
    return(files)

def convert_bw(file):
    # Read the image
    img = cv2.imread(f"{import_folder_path}/{file}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Ensure output directory exists
    if not os.path.exists(f"{export_folder_path}/bw"):
        os.mkdir(f"{export_folder_path}/bw")
    # Save the photo
    cv2.imwrite(f"{export_folder_path}/bw/{file}", gray)

def split_half_frame(file):
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

def create_threads(files):
    threads = []
    for file in files:
        if args.halfframe:
            threads.append(threading.Thread(target=split_half_frame, args=(file,)))
        if args.blackwhite:
            threads.append(threading.Thread(target=convert_bw, args=(file,)))
    return threads

def start_threads(threads):
    for thread in threads:
        thread.start()

def join_threads(threads):
    for thread in threads:
        thread.join()

def main():
    import_files = get_filenames()
    threads = create_threads(import_files)
    start_threads(threads)
    join_threads(threads)

if __name__ == "__main__":
    main()