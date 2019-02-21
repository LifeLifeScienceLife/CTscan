from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import PyPore_New_GUI
import cv2
import sys

skip_threshold = False
skip_despeckle = False
green = "#53c653"


# Basic outline of a window for which all other window variants will inherit from
class Window(Frame):

	# create default parameters for all windows
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master

		master.title("PyPore")
		master.iconbitmap('PyPore.ico')
		master.resizable(width=False, height=False)
		master.columnconfigure(0, weight=1)

		# Trying to make a menu

		main_menu = Menu(master)
		master.config(menu=main_menu)
		sub_menu_1 = Menu(main_menu, tearoff=0)
		sub_menu_2 = Menu(main_menu, tearoff=0)

		main_menu.add_cascade(label="Options", menu=sub_menu_1)
		sub_menu_1.add_command(label="Restart", command=self.restart)
		sub_menu_1.add_command(label="Quit", command=sys.exit)

		main_menu.add_cascade(label="Help", menu=sub_menu_2)
		sub_menu_2.add_command(label="General")
		sub_menu_2.add_command(label="Thresholding")

	def restart(self):
		self.destroy()
		IntroWindow(self.master)


class PopupWindow(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master

		master.title("PyPore")
		master.iconbitmap('PyPore.ico')
		master.geometry("350x400")
		master.resizable(width=False, height=False)
		master.columnconfigure(0, weight=1)
		master.grab_set()


class ExtendedPopupWindow(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master

		master.title("PyPore")
		master.iconbitmap('PyPore.ico')
		master.geometry("610x800")
		master.resizable(width=False, height=False)
		master.grab_set()


class IntroWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		self.grid(sticky=(E + W + N + S))

		self.add_files = Button(self, text="Add Images", command=self.img_browse, bg=green, padx=75)
		self.add_files.grid(row=0, column=1, sticky=(E + W + N + S))

		self.add_excel = Button(self, text="Add Output Excel File", command=self.excel_browse, padx=75)
		self.add_excel.grid(row=1, column=1, sticky=(E + W + N + S))
		self.add_excel.config(state='disable')

		self.add_info = Button(self, text="Add Additional Information", command=self.additional_info, padx=75)
		self.add_info.grid(row=2, column=1, sticky=(E + W + N + S))
		self.add_info.config(state='disable')

		tk_img = ImageTk.PhotoImage(file="Logo.gif")
		img = Label(self, image=tk_img, width=350, height=350)
		img.image = tk_img
		img.grid(row=0, column=0, rowspan=3)

		self.columnconfigure(1, weight=1)

	def img_browse(self):
		if PyPore_New_GUI.file_reader(filedialog.askopenfilename()):
			self.add_excel.config(bg=green, state='normal')
			self.add_files.config(bg="SystemButtonFace")

	def excel_browse(self):
		ExcelPopup(Toplevel(), self)

	def additional_info(self):
		AddInfoPopup(Toplevel(), self)

	def transition(self):
		self.destroy()
		if skip_threshold and skip_despeckle:
			self.parent.destroy()
			call_backend()
		elif skip_threshold:
			DespeckleWindow(self.parent)
		else:
			ThresholdWindow(self.parent)


class ExcelPopup(PopupWindow):
	def __init__(self, parent, bottom_window):
		super().__init__(parent)
		self.parent = parent
		self.bottom_window = bottom_window
		self.grid()

		var = IntVar()
		Label(self, text="Would you like to use an existing excel file?").grid(row=0, column=0, columnspan=2)
		Radiobutton(self, text="Yes", variable=var, value=1, command=lambda: self.excel_handler(True)).grid(row=1, column=0)
		Radiobutton(self, text="No", variable=var, value=2, command=lambda: self.excel_handler(False)).grid(row=1, column=1)

	def excel_handler(self, new_sheet):
		if new_sheet:
			Button(self, text="Please Select Your Excel File", command=self.old_excel_browse, padx=9).grid(row=2, column=0, columnspan=2)
		else:
			Button(self, text="Please Create a New Excel File", command=self.new_excel_browse).grid(row=2, column=0, columnspan=2)

	def old_excel_browse(self):
		if PyPore_New_GUI.old_excel_reader(filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])):
			self.bottom_window.add_info.config(state='normal', bg=green)
			self.bottom_window.add_excel.config(bg="SystemButtonFace")
			self.parent.destroy()

	def new_excel_browse(self):
		if PyPore_New_GUI.new_excel_reader(filedialog.asksaveasfilename(filetypes=[("Excel files", "*.xlsx")])):
			self.bottom_window.add_info.config(state='normal', bg=green)
			self.bottom_window.add_excel.config(bg="SystemButtonFace")
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
		Label(self, text="Are images in black\white (skip thresholding)?").grid(row=6, column=0, columnspan=2)
		Radiobutton(self, text="Yes", variable=self.var3, value=5).grid(row=7, column=0)
		Radiobutton(self, text="No", variable=self.var3, value=6).grid(row=7, column=1)

		self.var4 = IntVar(0)
		Label(self, text="Are images denoised (skip despeckeling)?").grid(row=8, column=0, columnspan=2)
		Radiobutton(self, text="Yes", variable=self.var4, value=7).grid(row=9, column=0)
		Radiobutton(self, text="No", variable=self.var4, value=8).grid(row=9, column=1)

		Button(self, text="Continue", command=self.submit_info).grid(row=10, column=0, columnspan=2)

	def submit_info(self):
		global skip_despeckle, skip_threshold

		if 0 in [self.var1.get(), self.var2.get(), self.var3.get(), self.var4.get()]:
			popupmsg("Please fill out all the fields")
		else:
			if self.var1.get() == 1:
				if validate_input(self.Voxel_Entry.get()):
					PyPore_New_GUI.set_voxel_size(self.Voxel_Entry.get())
				else:
					popupmsg("Please enter a number for pixel size")
					exit()
			if self.var3.get() == 5:
				skip_threshold = True
			if self.var4.get() == 7:
				skip_despeckle = True
			self.parent.destroy()
			IntroWindow.transition(self.below_window)

	def save_images(self):
		img_file_path = (filedialog.asksaveasfilename(filetypes=[(".jpg", "*.jpg")]))
		if not PyPore_New_GUI.save_images_as(img_file_path):
			popupmsg("Please Input A Valid Filename")
			self.var3.set(0)


class ThresholdWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		self.grid(sticky=(E + W + N + S))

		self.Otsu = Button(self, text="Otsu", command=lambda: Image_Comparison(Toplevel(), 1, self, "Thresholding"), padx=122)
		self.Otsu.grid(row=0, column=1, sticky=(E + W + N + S))

		self.Gmeans = Button(self, text="Global Means", command=lambda: Image_Comparison(Toplevel(), 2, self, "Thresholding"), padx=122)
		self.Gmeans.grid(row=1, column=1, sticky=(E + W + N + S))

		self.Phan = Button(self, text="Phansalkar", command=lambda: Image_Comparison(Toplevel(), 3, self, "Thresholding"), padx=122)
		self.Phan.grid(row=2, column=1, sticky=(E + W + N + S))

		tk_img = ImageTk.PhotoImage(file="Logo.gif")
		img = Label(self, image=tk_img, width=350, height=350)
		img.image = tk_img
		img.grid(row=0, column=0, rowspan=3)

		self.columnconfigure(1, weight=1)

	def transition(self):
		self.destroy()
		if not skip_despeckle:
			DespeckleWindow(self.parent)
		else:
			self.parent.destroy()
			call_backend()


class DespeckleWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		self.grid(sticky=(E + W + N + S))

		self.less = Button(self, text="Remove white specks less than: X", command=lambda: DespecklePopup(Toplevel(), 1), padx=45)
		self.less.grid(row=0, column=1, sticky=(E + W + N + S))

		self.more = Button(self, text="Remove white specks greater than: X", command=lambda: DespecklePopup(Toplevel(), 2), padx=45)
		self.more.grid(row=1, column=1, sticky=(E + W + N + S))

		self.skip = Button(self, text="Auto Despeckle", command=lambda: Image_Comparison(Toplevel(), 3, self, "Despeckeling", 10), padx=45)
		self.skip.grid(row=2, column=1, sticky=(E + W + N + S))

		tk_img = ImageTk.PhotoImage(file="Logo.gif")
		img = Label(self, image=tk_img, width=350, height=350)
		img.image = tk_img
		img.grid(row=0, column=0, rowspan=3)

		self.columnconfigure(1, weight=1)

	def transition(self):
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
			images = PyPore_New_GUI.threshold_selector(choice)
		else:
			images = PyPore_New_GUI.despeckle_selector(choice, area)

		OG = images[0]
		OG = cv2.resize(OG, (300, 300))
		OG = ImageTk.PhotoImage(Image.fromarray(OG))
		img1 = Label(self, image=OG, width=300, height=300)
		img1.image = OG
		img1.grid(row=1, column=0, rowspan=3)

		New = images[1]
		New = cv2.resize(New, (300, 300))
		New = ImageTk.PhotoImage(Image.fromarray(New))
		img2 = Label(self, image=New, width=300, height=300)
		img2.image = New
		img2.grid(row=1, column=1, rowspan=3)

		Label(self, text="Are you happy with this %s: " % operation).grid(row=5, column=0, columnspan=2)
		Button(self, text="Yes", command=self.pass_values).grid(row=6, column=0)
		Button(self, text="no", command=self.parent.destroy).grid(row=6, column=1)

	def pass_values(self):
		if self.operation == "Thresholding":
			ThresholdWindow.transition(self.below_window)
			PyPore_New_GUI.threshold_choice(self.choice)
			self.parent.destroy()
		else:
			PyPore_New_GUI.despeckle_choice(self.choice, self.area)
			self.parent.destroy()
			DespeckleWindow.transition(self.below_window)



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
	PyPore_New_GUI.main_flow()


if __name__ == "__main__":
	root = Tk()
	app = IntroWindow(root)
	root.mainloop()

