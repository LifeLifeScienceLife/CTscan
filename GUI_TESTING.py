from tkinter import *
from tkinter import filedialog


# Basic outline of a window for which all other window variants will inherit from
class Window(Frame):

	# create default parameters for all windows
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master

		master.title("PyPore")
		master.geometry("400x400")
		master.resizable(width=False, height=False)
		master.iconbitmap('PyPore.ico')


class BasicWindow(Window):

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		self.grid()

		self.create_grid(0, 1, parent)

		self.filename = None
		self.enter_button = Button(self, text="Add Files", command=self.browse)
		self.enter_button.grid(row=1, column=1)

	def create_grid(self, rows, columns, parent):
		row_counter = 0
		while rows > row_counter:
			parent.rowconfigure(row_counter, weight=1)
			row_counter += 1

		column_counter = 0
		while columns > column_counter:
			parent.columnconfigure(column_counter, weight=1)
			column_counter += 1

	def browse(self):
		self.filename = filedialog.asksaveasfilename()


if __name__ == "__main__":
	root = Tk()
	app = BasicWindow(root)
	root.mainloop()

