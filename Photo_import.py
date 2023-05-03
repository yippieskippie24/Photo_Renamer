#!/usr/bin/env python3

import os
import subprocess
import logging
from datetime import datetime, date

source_dir = "/Users/tmj/Pictures/Import" # Replace with the path to your folder
destination_dir = "/Users/tmj/Pictures/Import/Organize_Photos"
prefix = "TMJ" # Replace with your desired prefix
sequence_number = 1 # Starting sequence number
prev_capture_date = None # Initialize previous capture date
prev_capture_time = None # Initialize previous capture time
prev_sequence_number = None # Initialize previous sequence number

# Camera ID map used to specificaly set the names I want in the files based on the camera make in the EXIF data
camera_id_map = {
    "Canon": "CANON",
    "FUJIFILM": "FUJI",
    "SONY": "IR"
}


# Configure logging
log_file = f"{source_dir}/renaming.log"
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Get list of image files and sort by capture time
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
            image_files.append((filename, img_path, capture_time, capture_date))
        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

# Sort image files by capture time
image_files.sort(key=lambda x: x[2])

# Rename image files
for filename, img_path, capture_time, capture_date in image_files:
    try:
        file_extension = os.path.splitext(filename)[1]
        camera_brand = None
        # Get camera brand from exif data using exiftool
        cmd = ["exiftool", "-s", "-Make", img_path]
        output = subprocess.check_output(cmd).decode().strip()
        camera_make = output.split(":", 1)[1].strip()
        logging.info(f"camera_make: {camera_make}")
        
        camera_id = camera_id_map.get(camera_make, "Unknown")
        
        # Reset sequence number if first image of a new day
        if prev_capture_date != capture_date:
            prev_capture_date = capture_date
            sequence_number = 1
        
        logging.info(f"Filename {filename}")
        logging.info(f"prev_capture_time: {prev_capture_time}")
        logging.info(f"Sequence_number: {sequence_number}")
        
        # Assign sequence number to current file
        if prev_capture_time is not None and prev_capture_time == capture_time:
            sequence_number -= 1
        prev_capture_time = capture_time
        
        
        # Rename File useing the info gathered and move to the soure directory
        new_filename = f"{prefix}_{capture_time.strftime('%y%m%d')}_{camera_id}_{str(sequence_number).zfill(4)}{file_extension}"
        os.rename(img_path, os.path.join(destination_dir, new_filename))
        logging.info(f"Renamed {filename} to {new_filename}")
        sequence_number += 1
    except Exception as e:
        logging.error(f"Error renaming {filename}: {e}")

    
logging.info("Renaming complete.")
