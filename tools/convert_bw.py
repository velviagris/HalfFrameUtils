import cv2
import os

def process(file, import_folder_path, export_folder_path):
    # Read the image
    img = cv2.imread(f"{import_folder_path}/{file}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Ensure output directory exists
    if not os.path.exists(f"{export_folder_path}/bw"):
        os.mkdir(f"{export_folder_path}/bw")
    # Save the photo
    cv2.imwrite(f"{export_folder_path}/bw/{file}", gray)