# Did very little testing/ documentation but the core functionality seems to work. Feel free to test on other datasets,
# I wll better document next time!

import glob
import cv2
import numpy as np
import matplotlib.pyplot as plt


# Main control for the program. Reads in images and iterates them through shape_outliner and then por_calc
def main():

	images = file_reader()  # Read in images

	crop_dimensions = crop_parameters(images)

	for i in range(len(images) - 2, len(images)):
		OG = images[i]
		images[i] = crop(images[i], crop_dimensions)
		show(OG, images[i])


# Reads in image files specified by the users
def file_reader():
	global file_location

	while True:
		file_location = input("Please specify the file path to where your images are stored: ")
		file_type = input("Please specify the file type. I.e bmp: ")
		files = (glob.glob(file_location + "/*." + file_type))  # Read all files in a folder using glob
		images = []
		for img_file in files:
			images.append(cv2.imread(img_file, 0))  # Turn the files into an array of images for easier access
		if len(images) == 0:
			print("The folder location or file type you selected were invalid, please try again")
			continue
		break

	return images


def crop_parameters(images):

	height = images[0].shape[0]
	width = images[0].shape[1]

	images_considered = 6
	top_images = np.zeros([images_considered, 2], np.int32)
	parameters = np.zeros([images_considered, 4], np.int32)
	final_parameters = np.zeros([1, 4], np.int32)

	# Approximates the images with the largest respective area (assume most white pixels = most area)
	for i in range(0, len(images)):
		if np.count_nonzero(images[i]) > min(top_images[:, 1]):
			top_images[np.argmin(top_images[:, 1])] = [i, np.count_nonzero(images[i])]

	# Generate the number of pixels required to reach the sample in all 4 directions which guides where to crop
	for i in range(0, images_considered):
		parameters[i, 0] = top_down_shutter_close(images[top_images[i, 0]], 0, width, 1)  # Top Down
		parameters[i, 1] = top_down_shutter_close(images[top_images[i, 0]], height - 1, width, -1)  # Bottom Up
		parameters[i, 2] = left_right_shutter_close(images[top_images[i, 0]], 0, height, 1)  # Left to Right
		parameters[i, 3] = left_right_shutter_close(images[top_images[i, 0]], width - 1, height, -1)  # Right to Left

	for i in range(0, 4):
		final_parameters[0, i] = max(parameters[:, i])

	return final_parameters[0]


# The key change/intuition here is too use a entire 2D row instead of just one col, almost like an elevator door closing
# around a sample.
def top_down_shutter_close(image, height_index, width, increment):

	counter = 0

	while np.count_nonzero(image[height_index, 0:width]) < 3:
		height_index += increment
		counter += 1

	return counter


def left_right_shutter_close(image, width_index, height, increment):

	counter = 0

	while np.count_nonzero(image[0:height, width_index]) < 3:
		width_index += increment
		counter += 1

	return counter


def crop(img, dimensions):

	return img[dimensions[0]//2:img.shape[0] - (dimensions[1]//2), dimensions[2]//2:img.shape[1] - (dimensions[3]//2)]


def show(crop_img, OG):

	plt.subplot(2, 1, 1)
	plt.imshow(crop_img, cmap="gray")
	plt.subplot(2, 1, 2)
	plt.imshow(OG, cmap="gray")
	plt.show()


main()
