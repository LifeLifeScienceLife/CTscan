from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image
import PyPore_New_GUI as backend
import cv2
import sys
import numpy as np
import threading
from matplotlib import pyplot as plt

crop = False
green = "#53c653"


# Basic outline of a window for which all other window variants will inherit from
class Window(Frame):

	# create default parameters for all windows
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.grid(sticky=(E + W + N + S))

		master.title("PyPore")
		master.iconbitmap('PyPore.ico')
		master.resizable(width=False, height=False)
		master.columnconfigure(0, weight=1)

		main_menu = Menu(master)
		master.config(menu=main_menu)
		sub_menu_1 = Menu(main_menu, tearoff=0)
		sub_menu_2 = Menu(main_menu, tearoff=0)

		main_menu.add_cascade(label="Options", menu=sub_menu_1)
		sub_menu_1.add_command(label="Undo", command=self.undo)
		sub_menu_1.add_command(label="Restart", command=self.restart)
		sub_menu_1.add_command(label="Quit", command=sys.exit)

		main_menu.add_cascade(label="Help", menu=sub_menu_2)
		sub_menu_2.add_command(label="General")
		sub_menu_2.add_command(label="Thresholding")

		master.button1 = Button(self, text="")
		master.button1.grid(row=0, column=1, sticky=(E + W + N + S))

		master.button2 = Button(self, text="")
		master.button2.grid(row=1, column=1, sticky=(E + W + N + S))

		master.button3 = Button(self, text="")
		master.button3.grid(row=2, column=1, sticky=(E + W + N + S))

		tk_img = ImageTk.PhotoImage(file="Logo.gif")
		img = Label(self, image=tk_img, width=350, height=350)
		img.image = tk_img
		img.grid(row=0, column=0, rowspan=3)

		self.master.progress = Progressbar(self, orient=HORIZONTAL, length=345, mode='determinate')
		self.master.label = Label(self, text="Loading in Images")

	def start_progress_bar(self):
		self.master.label.grid(row=4, column=0, sticky=W, padx=100)
		self.master.progress.grid(row=4, column=1, sticky=E)
		self.master.progress.start()

	def restart(self):
		self.destroy()
		IntroWindow(self.master)


class ExtendedPopupWindow(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master

		master.title("PyPore")
		master.iconbitmap('PyPore.ico')
		master.geometry("558x923+0+0")
		master.resizable(width=False, height=False)
		master.grab_set()


class IntroWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		parent.button1.config(text="Add Images", bg=green, command=self.img_browse)
		parent.button2.config(state='disable', text="Add Output Excel File", command=self.excel_browse)
		parent.button3.config(state='disable', text="Add Additional Information", command=self.add_info, padx=75)

	# Read in image files using tkinter filedialog. Uses threading to display loading bar while reading in images.
	def img_browse(self):
		file_location = filedialog.askopenfilename()
		Window.start_progress_bar(self)

		def load_images():
			if backend.file_reader(file_location):
				self.parent.button2.config(bg=green, state='normal')
				self.parent.button1.config(bg="SystemButtonFace")
			else:
				popupmsg("Please select a valid image")

			self.parent.label.grid_forget()
			self.parent.progress.grid_forget()

		# This threading allows us to see the status bar while images are loading, keeps system status visible
		threading.Thread(target=load_images).start()

	# Handle the creation or retrieval of an excel file to output the result of backend computation.
	def excel_browse(self):
		f1 = ExcelPopup(self, self.parent)  # From excel_browse, I need to change a button (Pass Master Window)
		f1.grid(row=0, column=0, rowspan=3, sticky=(E + W + N + S))

	# Gives the user the choice to compute volume (And input a voxel size), save processed images and toggle cropping.
	def add_info(self):
		f1 = AddInfoPopup(self, self.parent)
		f1.grid(row=0, column=0, rowspan=3, sticky=(E + W + N + S))

	def undo(self):
		self.destroy()
		IntroWindow(self.master)

	def transition(self):
		self.destroy()
		ThresholdWindow(self.parent)


class ExcelPopup(Frame):
	def __init__(self, parent, bottom_window):
		super().__init__(parent)
		self.parent = parent
		self.bottom_window = bottom_window
		self.grid()

		self.config(highlightbackground=green, highlightcolor=green, highlightthickness=2)

		var = IntVar()
		Label(self, text="Would you like to use an existing excel file?").grid(row=0, column=0, columnspan=2, padx=25, pady=(130, 0))
		Checkbutton(self, text="Yes", variable=var, onvalue=1, command=lambda: self.excel_selector(True)).grid(row=1, column=0)
		Checkbutton(self, text="No", variable=var, onvalue=2, command=lambda: self.excel_selector(False)).grid(row=1, column=1)

	# Make the appropriate button appear based upon users choice.
	def excel_selector(self, new_sheet):
		if new_sheet:
			Button(self, text="Please Select Your Excel File", command=lambda: self.excel_handler(True), padx=9).grid(row=2, column=0, columnspan=2)
		else:
			Button(self, text="Please Create a New Excel File", command=lambda: self.excel_handler(False)).grid(row=2, column=0, columnspan=2)

	# Handle the selection of the button.
	def excel_handler(self, new_sheet):
		if new_sheet:
			if backend.old_excel_reader(filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])):
				self.transition()
		else:
			if backend.new_excel_reader(filedialog.asksaveasfilename(filetypes=[("Excel files", "*.xlsx")])):
				self.transition()

	def transition(self):
		self.bottom_window.button3.config(state='normal', bg=green)
		self.bottom_window.button2.config(bg="SystemButtonFace")
		self.destroy()


class AddInfoPopup(Frame):
	def __init__(self, parent, root_window):
		super().__init__(parent)
		self.root_window = root_window
		self.parent = parent
		self.grid()

		self.config(highlightbackground=green, highlightcolor=green, highlightthickness=2)

		self.img_file_path = None

		# Measure Volume Option
		self.var1 = IntVar(0)
		Label(self, text="Would you like to measure volume?").grid(row=0, column=0, columnspan=2, pady=(25, 0))
		Checkbutton(self, text="Yes", variable=self.var1, onvalue=1, command=lambda: Empty_Label.lower()).grid(row=1, column=0)
		Checkbutton(self, text="No", variable=self.var1, onvalue=2, command=lambda: Empty_Label.lift()).grid(row=1, column=1)

		Label(self, text="Pixel Resolution in um:").grid(row=2, column=0)
		self.Voxel_Entry = Entry(self)
		self.Voxel_Entry.grid(row=2, column=1)

		# Save Images Option
		self.var2 = IntVar(0)
		Label(self, text="Would you like to save the new images?").grid(row=3, column=0, columnspan=2, padx=40)
		self.save_img_yes = Checkbutton(self, text="Yes", variable=self.var2, onvalue=3,  command=lambda: self.Empty_Label_2.lower())
		self.save_img_yes.grid(row=4, column=0)
		self.save_img_no = Checkbutton(self, text="No", variable=self.var2, onvalue=4, command=lambda: self.Empty_Label_2.lift())
		self.save_img_no.grid(row=4, column=1)

		Empty_Label = Label(self, text="")
		Empty_Label.grid(row=2, column=0, columnspan=2, sticky=(E+W))

		Button(self, text="Save Images As", command=self.save_images).grid(row=5, column=0, columnspan=2)
		self.Empty_Label_2 = Label(self, text="")
		self.Empty_Label_2.grid(row=5, column=0, columnspan=2, ipady=10, sticky=(E+W))

		# Crop Images Option
		self.var3 = IntVar(0)
		Label(self, text="Would you like to crop the images?").grid(row=6, column=0, columnspan=2)
		Checkbutton(self, text="Yes", variable=self.var3, onvalue=5).grid(row=7, column=0)
		Checkbutton(self, text="No", variable=self.var3, onvalue=6).grid(row=7, column=1)

		Button(self, text="Continue", command=self.submit_info).grid(row=10, column=0, columnspan=2)

	def submit_info(self):

		valid_voxel = True
		valid_image = True

		if 0 in [self.var1.get(), self.var2.get(), self.var3.get()]:
			popupmsg("Please fill out all the fields")
		else:
			# Ensure voxel size is valid
			if self.var1.get() == 1:
				if validate_input(self.Voxel_Entry.get()):
					voxel_size = np.float64(self.Voxel_Entry.get()) * (10 ** -4)  # Converting um to cm
					voxel_size = voxel_size ** 3  # Cubing cm
					backend.voxel_size = voxel_size
				else:
					valid_voxel = False
					popupmsg("Please enter a number for pixel size")

			# Ensures user selects a valid image file name
			if self.var2.get() == 3:
				if self.img_file_path is None:
					popupmsg("Please input a valid image filename")
					valid_image = False
				else:
					backend.save_images = True

			def set_crop_parameters():
				global crop

				if self.var3.get() == 5:
					crop = True
					backend.crop_choice(True)

				self.root_window.label.grid_forget()
				self.root_window.progress.grid_forget()

				self.destroy()
				IntroWindow.transition(self.parent)

			if valid_voxel and valid_image:
				self.root_window.label.config(text="Submitting Information")
				Window.start_progress_bar(self.parent)
				threading.Thread(target=set_crop_parameters).start()

	def save_images(self):

		mask = [
			("JPEG", "*.jpg"),
			("BMP", "*.bmp"),
			("TIFF", "*.tif"),
			("PNG", "*.png")]

		img_file_path = (filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=mask, confirmoverwrite=False))
		if not backend.save_images_as(img_file_path):
			popupmsg("Please Input A Valid Filename")
		else:
			self.img_file_path = img_file_path


class ThresholdWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		parent.button1.config(text="Otsu", command=lambda: Image_Comparison(Toplevel(), 1, self, "Thresholding"))
		parent.button2.config(text="Global Means", command=self.global_means_thresh_popup, padx=122)
		parent.button3.config(text="Phansalkar", command=lambda: Image_Comparison(Toplevel(), 3, self, "Thresholding"))

	def global_means_thresh_popup(self):

		f1 = Frame(self)
		f1.grid(row=0, column=0, rowspan=3, sticky=(E + W + N + S))
		f1.config(highlightbackground=green, highlightcolor=green, highlightthickness=2)

		plt.hist(backend.test_image[1].ravel(), 256, [0, 256])
		plt.savefig("Histogram.png")
		New = cv2.imread("Histogram.png", 1)
		New = cv2.resize(New, (350, 275))
		New = ImageTk.PhotoImage(Image.fromarray(New))
		img = Label(f1, image=New, width=350, height=275)
		img.image = New
		img.grid(row=0, column=0)

		thresh_scale = Scale(f1, from_=0, to=255, orient=HORIZONTAL, length=270)
		thresh_scale.grid(row=1, column=0)
		Label(f1, text="Select a threshold value:").grid(row=2, column=0, sticky=(E + W + N + S), padx=10)

		submit = Button(f1, text="submit", command=lambda: Image_Comparison(Toplevel(), 2, self, "Thresholding", thresh_scale.get()))
		submit.grid(row=3, column=0)

	def transition(self):
		self.destroy()
		DespeckleWindow(self.parent)

	def undo(self):
		self.destroy()
		IntroWindow(self.master)


class DespeckleWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		parent.button1.config(text="Remove white specks less than: X", command=lambda: self.create_pop_up(1))
		parent.button2.config(text="Remove white specks greater than: X", command=lambda: self.create_pop_up(2), padx=45)
		parent.button3.config(text="Auto Despeckle", command=self.auto_despeckle_threading)

	def auto_despeckle_threading(self):

		Window.start_progress_bar(self)
		self.parent.label.config(text="Auto Despeckeling")

		def thread():
			area = backend.auto_despeckle_parameters()
			self.parent.label.grid_forget()
			self.parent.progress.grid_forget()

			Image_Comparison(Toplevel(), 3, self, "Despeckeling", area)

		# This threading allows us to see the status bar while images are loading, keeps system status visible
		threading.Thread(target=thread).start()

	def create_pop_up(self, choice):
		f1 = DespecklePopup(self, choice)
		f1.grid(row=0, column=0, rowspan=3, sticky=(E + W + N + S))

	def transition(self):
		if crop:
			self.destroy()
			CropWindow(self.parent)
		else:
			self.parent.destroy()
			call_backend()

	def undo(self):
		self.destroy()
		ThresholdWindow(self.master)


class DespecklePopup(Frame):
	def __init__(self, parent, choice):
		super().__init__(parent)
		self.choice = choice
		self.parent = parent
		self.grid()

		self.config(highlightbackground=green, highlightcolor=green, highlightthickness=2)

		if choice == 1:
			Label(self, text="Remove white specks less than:").grid(row=0, column=0, padx=15, pady=(130, 0))
		else:
			Label(self, text="Remove white specks greater than:").grid(row=0, column=0, padx=10, pady=(130, 0))

		Button(self, text="Submit", command=self.transition).grid(row=1, column=0, columnspan=2)

		self.Area_Entry = Entry(self, width=10)
		self.Area_Entry.grid(row=0, column=1, pady=(130, 0))

	def transition(self):
		if validate_input(self.Area_Entry.get()):
			Image_Comparison(Toplevel(), self.choice, self.parent, "Despeckeling", self.Area_Entry.get())
		else:
			popupmsg("Please enter a valid area (Integer)")
			exit()

	def undo(self):
		self.destroy()
		ThresholdWindow(self.master)


class CropWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		self.grid(sticky=(E + W + N + S))

		parent.button1.config(text="Preform Cropping", command=lambda: Image_Comparison(Toplevel(), 1, self, "Cropping", self.convert_scale(self.crop_scale.get())))
		parent.button2.grid_forget()
		parent.button3.config(text="Start Calculations", state='disable', padx=110, command=self.transition)

		f1 = Frame(self)
		f1.grid(row=1, column=1)

		Label(f1, text="Select a scale:").grid(row=0, column=0, sticky=(E + W + N + S), padx=10)
		self.crop_scale = Scale(f1, from_=1, to=100, orient=HORIZONTAL)
		self.crop_scale.grid(row=0, column=1, sticky=(E + W + N + S))

	# Modified from https://stackoverflow.com/questions/929103/convert-a-number-range-to-another-range-maintaining-ratio
	def convert_scale(self, value):
		return (((value - 1) * (2 - 1)) / (100 - 1)) + 1

	def enable_button_3(self):
		self.parent.button3.config(state='normal', bg=green)

	def transition(self):
		self.parent.destroy()
		call_backend()

	def undo(self):
		self.destroy()
		DespeckleWindow(self.master)


class Image_Comparison(ExtendedPopupWindow):
	def __init__(self, parent, choice, below_window, operation, secondary_value=None):
		super().__init__(parent)
		self.parent = parent
		self.below_window = below_window
		self.operation = operation
		self.choice = choice
		self.secondary_value = secondary_value
		self.grid()

		Label(self, text="Original").grid(row=0, column=0)
		Label(self, text="   New   ").grid(row=0, column=1)

		if self.operation == "Thresholding":
			if choice == 2:
				backend.global_means_thresh_value = secondary_value  # Set the global means threshold value
			backend.threshold_test_image_generator(choice)
			OG_images = backend.test_image
			New_images = backend.threshold_test_images
		elif self.operation == "Despeckeling":
			backend.despeckle_test_image_generator(choice, secondary_value)
			OG_images = backend.threshold_test_images
			New_images = backend.despeckle_test_images
		else:
			backend.crop_test_image_generator(secondary_value)
			OG_images = backend.despeckle_test_images
			New_images = backend.cropped_test_images

		j = 1
		for i in range(0, 3):

			OG = OG_images[i]
			OG = cv2.resize(OG, (275, 275))
			OG = ImageTk.PhotoImage(Image.fromarray(OG))
			img1 = Label(self, image=OG, width=275, height=275)
			img1.image = OG
			img1.grid(row=j, column=0, rowspan=3)

			New = New_images[i]
			New = cv2.resize(New, (275, 275))
			New = ImageTk.PhotoImage(Image.fromarray(New))
			img2 = Label(self, image=New, width=275, height=275)
			img2.image = New
			img2.grid(row=j, column=1, rowspan=3)

			j += 4

		Label(self, text="Are you happy with this %s: " % operation).grid(row=14, column=0, columnspan=2)
		Button(self, text="Yes", command=self.pass_values).grid(row=15, column=0, sticky=(E, W))
		Button(self, text="No", command=self.parent.destroy).grid(row=15, column=1, sticky=(E, W))

	def pass_values(self):
		if self.operation == "Thresholding":
			ThresholdWindow.transition(self.below_window)
			backend.threshold_type = self.choice
			self.parent.destroy()
		elif self.operation == "Despeckeling":
			backend.despeckle_choice(self.choice, self.secondary_value)
			self.parent.destroy()
			DespeckleWindow.transition(self.below_window)
		else:
			CropWindow.enable_button_3(self.below_window)
			self.parent.destroy()

############################### HELPER FUNCTIONS THAT CAN BE CALLED BY ANY CLASS########################################


# FROM https://pythonprogramming.net/tkinter-popup-message-window/
def popupmsg(msg):
	popup = Tk()
	popup.iconbitmap('PyPore.ico')
	popup.title("!")
	label = Label(popup, text=msg)
	label.pack(side="top", fill="x", pady=10)
	B1 = Button(popup, text="Okay", command=popup.destroy)
	B1.pack()
	popup.mainloop()


# Ensures user puts in a number in relevant entry field
def validate_input(value):
	try:
		float(value)
		return True
	except ValueError:
		return False


def call_backend():
	backend.loading_backend()


if __name__ == "__main__":
	root = Tk()
	app = IntroWindow(root)
	root.mainloop()