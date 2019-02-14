import cv2
import glob
import random
import re
import sys
import numpy as np
import openpyxl
from openpyxl import load_workbook
from skimage.morphology import remove_small_objects
from scipy.ndimage import label

test_image = None
glob_file = None
workbook = None
worksheet = None
image_file_name = None
threshold_type = None
despeckle_type = None
width_inc = 1  # Represents the inc/decrement step in shape outliner (Increase to speed up runtime)


def main_flow():
	pass
	# Read in all images
	images = []
	for img_file in glob_file:
		images.append(cv2.imread(img_file, 0))  # Turn the files into an array of images for easier access

	# Preform Thresholding
	# Preform Despeckeling
	# Preform AutoCropping
	# Call Analyzer


def file_reader(file_location):
	global test_image, glob_file

	if file_location is not None and len(file_location) > 1:

		# Need to get file location into proper format for glob
		file_type = file_location.split(".")[-1]
		for i in range(len(file_location) - 1, -1, -1):
			if file_location[i] == "/":
				file_path = file_location[0:i]
				break

		file_location = file_path + "/*." + file_type
		glob_file = (glob.glob(file_location))  # Read all files in a folder using glob
		test_image = (cv2.imread(glob_file[len(glob_file)//2], 0))  # Try to read a file

		return True

	return False


def old_excel_reader(excel_file):
	global workbook, worksheet

	if excel_file is not None and len(excel_file) > 1:
		workbook = load_workbook(excel_file)
		worksheet = workbook.active
		return True

	return False


def new_excel_reader(excel_file):
	global workbook, worksheet

	if excel_file is not None and len(excel_file) > 1:
		workbook = openpyxl.Workbook(excel_file)
		worksheet = workbook.active
		return True

	return False


def save_images_as(img_name):
	global image_file_name

	if img_name is not None and len(img_name) > 1:
		image_file_name = img_name
		return True

	return False


def threshold_choice(user_choice):
	global threshold_type
	if threshold_type is None:
		threshold_type = user_choice


def threshold_selector(user_choice):
	if user_choice == 1:
		return otsu_threshold()
	elif user_choice == 2:
		return phanstalker_threshold()
	elif user_choice == 3:
		return global_threshold()


# TODO IMPLEMENT THE OTHER THRESHOLDING TECHNIQUES
def otsu_threshold(image=None):
	if image is None:
		image = test_image

	null, thres_img = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
	return image, thres_img


def phanstalker_threshold(image=None):
	if image is None:
		image = test_image

	null, thres_img = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
	return image, thres_img


def global_threshold(image=None):
	if image is None:
		image = test_image

	null, thres_img = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
	return image, thres_img


def despeckle_choice(user_choice, area=None):
	global despeckle_type
	if despeckle_type is None:
		despeckle_type = user_choice, area


def despeckle_selector(user_choice, area):
	if user_choice == 1:
		return despeckle(test_image, area)
	elif user_choice == 2:
		return np.logical_xor(test_image, despeckle(test_image, area))


# Despeckle images using a remove small objects function, size of objects is either user determined or found
# automatically via random experimentation in auto crop parameters
def despeckle(image, min_area):
	bool_arr = np.array(image, bool)
	despeckeled_img = remove_small_objects(bool_arr, min_area)
	return np.array(despeckeled_img, dtype=int)
