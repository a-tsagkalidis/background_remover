import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from threading import Thread


def remove_background(image_path, tolerance):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        return None

    # Apply background removal using OpenCV's grabCut algorithm
    mask = np.zeros(image.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = (10, 10, image.shape[1] - 10, image.shape[0] - 10)  # Sample rectangle
    
    # Adjust the grabCut parameters based on tolerance
    tolerance_iterations = int(tolerance * 20)
    cv2.grabCut(image, mask, rect, bgdModel, fgdModel, tolerance_iterations, cv2.GC_INIT_WITH_RECT)

    # Create a mask where sure and likely foreground pixels are set to 1
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    # Apply the mask to the original image to get the foreground
    foreground = image * mask2[:, :, np.newaxis]

    return foreground


def process_images(input_folder, output_folder, tolerance, progress_callback):
    # Get a list of image files in the input folder
    image_files = [filename for filename in os.listdir(input_folder) if filename.lower().endswith('.jpg')]

    # Iterate through images in the input folder
    for index, filename in enumerate(image_files):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # Remove the background and replace with white
        foreground = remove_background(input_path, tolerance)
        if foreground is not None:
            white_background = np.ones_like(foreground) * 255
            result = white_background - (255 - foreground)

            # Save the processed image
            cv2.imwrite(output_path, result)
            print(f"Processed: {filename}")

        # Update the progress bar
        progress_percentage = (index + 1) / len(image_files) * 100
        progress_callback(progress_percentage)


def select_input_folder():
    input_folder = filedialog.askdirectory()
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, input_folder)


def select_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, output_folder)


def start_processing():
    start_button.config(state=tk.DISABLED)  # Disable the button during processing
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()
    tolerance = tolerance_slider.get() / 100.0

    processing_label.config(text="Processing...")  # Display a processing message

    # Create a separate thread for processing
    processing_thread = Thread(target=process_images, args=(input_folder, output_folder, tolerance, update_progress))
    processing_thread.start()
    print("Processing started")


def update_progress(progress_value):
    progress_bar['value'] = progress_value
    root.update_idletasks()

    if progress_value == 100:
        processing_label.config(text="Processing complete")


# Create the main GUI window
root = tk.Tk()
root.title("Background Remover")

# Input Folder Selection
input_folder_label = tk.Label(root, text="Select Input Folder:")
input_folder_label.pack()
input_folder_entry = tk.Entry(root, width=50)
input_folder_entry.pack()
input_folder_button = tk.Button(root, text="Browse", command=select_input_folder)
input_folder_button.pack()

# Output Folder Selection
output_folder_label = tk.Label(root, text="Select Output Folder:")
output_folder_label.pack()
output_folder_entry = tk.Entry(root, width=50)
output_folder_entry.pack()
output_folder_button = tk.Button(root, text="Browse", command=select_output_folder)
output_folder_button.pack()

# Tolerance Slider
tolerance_label = tk.Label(root, text="Tolerance:")
tolerance_label.pack()
tolerance_slider = ttk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
tolerance_slider.set(50)  # Default tolerance value
tolerance_slider.pack()

# Start Processing Button
start_button = tk.Button(root, text="Start Processing", command=start_processing)
start_button.pack()

# Processing Label
processing_label = tk.Label(root, text="", font=("Helvetica", 12))
processing_label.pack()

# Progress Bar
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate', maximum=100)
progress_bar.pack()

root.mainloop()
