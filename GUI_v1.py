from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
from PIL import ImageTk, Image
import PyPore_New_GUI as backend
import cv2
import sys
import threading

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

		master.progress = Progressbar(self, orient=HORIZONTAL, length=345, mode='determinate')
		master.label = Label(self, text="Loading in Images")

		self.columnconfigure(1, weight=1)

	def restart(self):
		self.destroy()
		IntroWindow(self.master)

	## OVERWRITE IN SUBCLASSES
	def undo(self):
		pass


class PopupWindow(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master

		master.title("PyPore")
		master.iconbitmap('PyPore.ico')
		master.geometry("350x350")
		master.resizable(width=False, height=False)
		master.columnconfigure(0, weight=1)
		master.grab_set()


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

		self.parent.label.grid(row=4, column=0, sticky=W, padx=100)
		self.parent.progress.grid(row=4, column=1, sticky=E)
		self.parent.progress.start()

		def load_images():
			if backend.file_reader(file_location):
				self.parent.button2.config(bg=green, state='normal')
				self.parent.button1.config(bg="SystemButtonFace")

			self.parent.label.grid_forget()
			self.parent.progress.grid_forget()

		# This threading allows us to see the status bar while images are loading, keeps system status visible
		threading.Thread(target=load_images).start()

	# Handle the creation or retrieval of an excel file to output the result of backend computation.
	def excel_browse(self):
		ExcelPopup(Toplevel(), self.parent)  # From Excel Handler, I need to change a button (Pass Master Window)

	# Gives the user the choice to compute volume (And input a voxel size), save processed images and toggle cropping.
	def add_info(self):
		AddInfoPopup(Toplevel(), self)  # From Add Info, I need to call a function in IntroWindow, that is what I pass.

	# Normally undo goes to the previous window; because this is the first window we just reset the program.
	def undo(self):
		self.destroy()
		IntroWindow(self.master)

	def transition(self):
		self.destroy()
		ThresholdWindow(self.parent)


class ExcelPopup(PopupWindow):
	def __init__(self, parent, bottom_window):
		super().__init__(parent)
		self.parent = parent
		self.bottom_window = bottom_window
		self.grid()

		var = IntVar()
		Label(self, text="Would you like to use an existing excel file?").grid(row=0, column=0, columnspan=2)
		Radiobutton(self, text="Yes", variable=var, value=1, command=lambda: self.excel_selector(True)).grid(row=1, column=0)
		Radiobutton(self, text="No", variable=var, value=2, command=lambda: self.excel_selector(False)).grid(row=1, column=1)

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
		self.parent.destroy()


class AddInfoPopup(PopupWindow):
	def __init__(self, parent, below_window):
		super().__init__(parent)

		self.parent = parent
		self.below_window = below_window
		self.grid()

		self.var1 = IntVar(0)
		Label(self, text="Would you like to measure volume?").grid(row=0, column=0, columnspan=2)
		Radiobutton(self, text="Yes", variable=self.var1, value=1, command=lambda: Empty_Label.lower()).grid(row=1, column=0)
		Radiobutton(self, text="No", variable=self.var1, value=2, command=lambda: Empty_Label.lift()).grid(row=1, column=1)

		Label(self, text="Pixel Resolution in um:").grid(row=2, column=0)
		self.Voxel_Entry = Entry(self)
		self.Voxel_Entry.grid(row=2, column=1)

		Empty_Label = Label(self, text="")
		Empty_Label.grid(row=2, column=0, columnspan=2, sticky=(E+W))

		Button(self, text="Save Images As", command=self.save_images).grid(row=5, column=0, columnspan=2)
		Empty_Label_2 = Label(self, text="")
		Empty_Label_2.grid(row=5, column=0, columnspan=2, ipady=10, sticky=(E+W))

		self.var2 = IntVar(0)
		Label(self, text="Would you like to save the new images?").grid(row=3, column=0, columnspan=2)
		Radiobutton(self, text="Yes", variable=self.var2, value=3, command=lambda: Empty_Label_2.lower()).grid(row=4, column=0)
		Radiobutton(self, text="No", variable=self.var2, value=4, command=lambda: Empty_Label_2.lift()).grid(row=4, column=1)

		self.var3 = IntVar(0)
		Label(self, text="Would you like to crop the images?").grid(row=6, column=0, columnspan=2)
		Radiobutton(self, text="Yes", variable=self.var3, value=5).grid(row=7, column=0)
		Radiobutton(self, text="No", variable=self.var3, value=6).grid(row=7, column=1)

		Button(self, text="Continue", command=self.submit_info).grid(row=10, column=0, columnspan=2)

	def submit_info(self):
		global crop

		if 0 in [self.var1.get(), self.var2.get(), self.var3.get()]:
			popupmsg("Please fill out all the fields")
		else:
			if self.var1.get() == 1:
				if validate_input(self.Voxel_Entry.get()):
					backend.voxel_size = self.Voxel_Entry.get()
				else:
					popupmsg("Please enter a number for pixel size")
					exit()
			# TODO SAVE IMAGES
			if self.var3.get() == 5:
				crop = True
				backend.crop_selector(True)
			self.parent.destroy()
			IntroWindow.transition(self.below_window)

	def save_images(self):
		img_file_path = (filedialog.asksaveasfilename(filetypes=[(".jpg", "*.jpg")]))
		if not backend.save_images_as(img_file_path):
			popupmsg("Please Input A Valid Filename")
			self.var3.set(0)


class ThresholdWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		parent.button1.config(text="Otsu", command=lambda: Image_Comparison(Toplevel(), 1, self, "Thresholding"))
		parent.button2.config(text="Global Means", command=lambda: Image_Comparison(Toplevel(), 2, self, "Thresholding"), padx=122)
		parent.button3.config(text="Phansalkar", command=lambda: Image_Comparison(Toplevel(), 3, self, "Thresholding"))

	def transition(self):
		self.destroy()
		DespeckleWindow(self.parent)


class DespeckleWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		parent.button1.config(text="Remove white specks less than: X", command=lambda: DespecklePopup(Toplevel(), 1))
		parent.button2.config(text="Remove white specks greater than: X", command=lambda: DespecklePopup(Toplevel(), 2), padx=45)
		parent.button3.config(text="Auto Despeckle", command=lambda: Image_Comparison(Toplevel(), 3, self, "Despeckeling", 10))

	def transition(self):
		if crop:
			self.destroy()
			CropWindow(self.parent)
		else:
			self.parent.destroy()
			call_backend()


class DespecklePopup(PopupWindow):
	def __init__(self, parent, choice):
		super().__init__(parent)
		self.choice = choice
		self.parent = parent
		self.grid()

		if choice == 1:
			Label(self, text="Remove white specks less than:").grid(row=0, column=0)
		else:
			Label(self, text="Remove white specks greater than:").grid(row=0, column=0)

		Button(self, text="Submit", command=self.transition).grid(row=1, column=0, columnspan=2)

		self.Area_Entry = Entry(self)
		self.Area_Entry.grid(row=0, column=1)

	def transition(self):
		if validate_input(self.Area_Entry.get()):
			Image_Comparison(Toplevel(), self.choice, self, "Despeckeling", self.Area_Entry.get())
		else:
			popupmsg("Please enter a valid area (Integer)")
			exit()


class CropWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		self.grid(sticky=(E + W + N + S))

		parent.button1.config(text="Preform Cropping", command=lambda: Image_Comparison(Toplevel(), 1, self, "Cropping", self.convert_scale(self.crop_scale.get())))
		parent.button2.grid_forget()
		parent.button3.config(text="Start Calculations", state='disable', padx=110)

		f1 = Frame(self)
		f1.grid(row=1, column=1)

		Label(f1, text="Select a scale:").grid(row=0, column=0, sticky=(E + W + N + S), padx=10)
		self.crop_scale = Scale(f1, from_=1, to=100, orient=HORIZONTAL)
		self.crop_scale.grid(row=0, column=1, sticky=(E + W + N + S))

	# Modified from https://stackoverflow.com/questions/929103/convert-a-number-range-to-another-range-maintaining-ratio
	def convert_scale(self, value):
		return (((value - 1) * (2 - 1)) / (100 - 1)) + 1

	def enable_button_3(self):
		self.parent.button3.config(state='enable', bg=green)


class Image_Comparison(ExtendedPopupWindow):
	def __init__(self, parent, choice, below_window, operation, area=10):
		super().__init__(parent)
		self.parent = parent
		self.below_window = below_window
		self.operation = operation
		self.choice = choice
		self.area = area
		self.grid()

		Label(self, text="Original").grid(row=0, column=0)
		Label(self, text="   New   ").grid(row=0, column=1)

		if self.operation == "Thresholding":
			backend.threshold_selector(choice)
			OG_images = backend.test_image
			New_images = backend.threshold_test_images
		elif self.operation == "Despeckeling":
			backend.despeckle_selector(choice, area)
			OG_images = backend.threshold_test_images
			New_images = backend.despeckle_test_images
		else:
			backend.crop_selector2(area)
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
			backend.despeckle_choice(self.choice, self.area)
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
	backend.main_flow()


if __name__ == "__main__":
	root = Tk()
	app = IntroWindow(root)
	root.mainloop()

