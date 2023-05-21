#!/usr/bin/env python3

import os
import re
import subprocess
import logging
from datetime import datetime, date

# Set the source and destination directories, as well as the desired filename prefix
source_dir = "/Users/tmj/Pictures/Import" # Replace with the path to your folder
destination_dir = "/Users/tmj/Pictures/Import/Organize_Photos"
prefix = "TMJ" # Replace with your desired prefix

# Map of camera brands to desired camera ID strings (used in filenames)
camera_id_map = {
    "Canon": "CANON",
    "FUJIFILM": "FUJI",
    "SONY": "IR"
}


# Configure logging
log_file = f"{source_dir}/renaming.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Check for dependencies
def check_dependencies():
    dependencies = ['exiftool']
    missing_dependencies = []
    for dependency in dependencies:
        try:
            subprocess.check_output([dependency, '-ver'])
        except subprocess.CalledProcessError:
            missing_dependencies.append(dependency)
    if missing_dependencies:
        print(f"WARNING: The following dependencies are missing: {', '.join(missing_dependencies)}")
        print("Please install the missing dependencies before running the script.")
        sys.exit(1)
        
check_dependencies()


# Get list of image files in the source directory, filter out non-image files
image_files = []
for filename in os.listdir(source_dir):
    if filename.lower().endswith((".jpg", ".jpeg", ".cr2", ".cr3", ".raf", ".arw")):
        try:
            img_path = os.path.join(source_dir, filename)
            # Get capture time from exif data using exiftool
            cmd = ["exiftool", "-s", "-CreateDate", img_path]
            output = subprocess.check_output(cmd).decode().strip()
            capture_time_str = output.split(":", 1)[1].strip()
            capture_time = datetime.strptime(capture_time_str.split("-")[0].strip(), "%Y:%m:%d %H:%M:%S")
            capture_date = capture_time.date()
            file_extension = os.path.splitext(filename)[1]
            camera_brand = None
            # Get camera brand from exif data using exiftool
            cmd = ["exiftool", "-s", "-Make", img_path]
            output = subprocess.check_output(cmd).decode().strip()
            camera_make = output.split(":", 1)[1].strip()
            logging.debug(f"camera_make: {camera_make}")
            
            # Get the original sequence number of the file
            match = re.search(r'\d+', filename) # Matches one or more digits
            original_shoot_sequence = match.group()
            
            # Get the desired camera ID string for the current image based on its camera brand (using the camera_id_map)
            camera_id = camera_id_map.get(camera_make, "Unknown")
            logging.debug(f"camera_id: {camera_id}")
            image_files.append((filename, img_path, capture_time, capture_date, file_extension, camera_id, original_shoot_sequence))
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

logging.info(f"image_files: {image_files}")
# Sort image files by capture time
image_files.sort(key=lambda x: x[6])

# Rename image files function
def rename_image_files(image_files, camera_id_string):
    # Set the starting sequence number and initialize variables for tracking previous capture time/date and sequence number
    sequence_number = 1 # Starting sequence number
    prev_capture_date = None # Initialize previous capture date
    prev_capture_time = None # Initialize previous capture time
    prev_sequence_number = None # Initialize previous sequence number
    prev_original_shoot_sequence = None # Initalize previous file_extension
    
    for filename, img_path, capture_time, capture_date, file_extension, camera_id, original_shoot_sequence in image_files:
        try:
            # Check if the file's camera_id matches the provided value
            if camera_id_string != camera_id:
                continue
            
            # Reset sequence number if first image of a new day
            if prev_capture_date != capture_date:
                prev_capture_date = capture_date
                sequence_number = 1
            
            logging.debug(f"Filename {filename}")
            logging.debug(f"prev_capture_time: {prev_capture_time}")
            logging.debug(f"Sequence_number: {sequence_number}")
            
            # Assign sequence number to current file
            if original_shoot_sequence is not None and prev_original_shoot_sequence == original_shoot_sequence:
                sequence_number -= 1
            prev_original_shoot_sequence = original_shoot_sequence
            
            
            # Rename File useing the info gathered and move to the soure directory
            new_filename = f"{prefix}_{capture_time.strftime('%y%m%d')}_{camera_id}_{str(sequence_number).zfill(4)}{file_extension}"
            os.rename(img_path, os.path.join(destination_dir, new_filename))
            logging.info(f"Renamed {filename} to {new_filename}")
            sequence_number += 1


        except Exception as e:
            logging.error(f"Error renaming {filename}: {e}")

            
# Run the rename image function for each of the camera_is listed in the camera_id_map
for camera_id_string in camera_id_map.values():
    rename_image_files(image_files, camera_id_string)


logging.info("Renaming complete.")
