import tkinter as tk
from tkinter import ttk
import time
import BackEnd

# Start coding here


class StartQuestions(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)
		self.file_path = tk.StringVar()
		self.file_type = tk.StringVar()
		self.file_name = tk.StringVar() #this is what prints
		self.file_name.set("N/A")
		self.var = tk.StringVar()
		FP_label = ttk.Label(self, text="Please specify the file path to where your images are stored: ")
		FT_label = ttk.Label(self, text="Please specify the file type. I.e bmp: ")
		FP_entry = ttk.Entry(self, textvariable=self.file_path)
		FT_entry = ttk.Entry(self, textvariable=self.file_type)
		ch_button = ttk.Button(self, text="change", command=self.on_change)
		File_label = ttk.Label(self, textvariable=self.file_name, font=("TkDefaultFont", 64), wraplength=600)
		FP_label.grid(row=0, column=0, sticky=tk.W)
		FT_label.grid(row=1, column=0, sticky=tk.W)
		FP_entry.grid(row=0, column=1, sticky=(tk.W + tk.E))
		FT_entry.grid(row=1, column=1, sticky=(tk.W + tk.E))
		ch_button.grid(row=0, column=2, sticky=tk.E)
		File_label.grid(row=2, column=0, columnspan=3)
		self.columnconfigure(1, weight=1)

	def on_change(self):
		if self.file_type.get().strip():
			self.file_name.set(self.file_path.get() + "." + self.file_type.get())
			time.sleep(2)
			BackEnd.globalize(self.file_name)
			BackEnd.main()
		else:
			self.file_name.set("N/A")

class MyApplication(tk.Tk):
	"""Main Application"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.title("Pypore")
		self.geometry("800x600")
		self.resizable(width=False, height=False)
		StartQuestions(self).grid(sticky=(tk.E + tk.W + tk.N + tk.S))
		self.columnconfigure(0, weight=1)

def main():
	app = MyApplication()
	app.mainloop()

main()