from tkinter import *
from tkinter.ttk import *

class statusbar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self,relief=SUNKEN, anchor=W, width=40)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()
