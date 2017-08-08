from PIL import Image, ImageTk
from tkinter import filedialog as tk_fd
import tkinter as tk

FILES_IMG = (("Image files", ("*.jpg", "*.png")), ("All files", "*.*"))
FILES_STITCH = (("Json file", ("*.json")), ("All files", "*.*"))


def input_int(prompt, imin=None, imax=None):
    '''
    Prompt the user to input an integer, and don't stop prompting until a valid
    integer is given.

    prompt - Prompt given to user
    imin   - Minimum value that will be accepted
    imax   - Maximum value that will be accepted
    '''
    while True:
        i = input(prompt)
        try:
            val = int(i)
            if imin is not None and val < imin:
                print("Number should be at least {}".format(imin))
            elif imax is not None and val > imax:
                print("Number should be at most {}".format(imax))
            else:
                return val
        except ValueError:
            print("Not a valid integer!")


_icon_cache = {}


def load_icon(name):
    if name in _icon_cache:
        return _icon_cache[name]
    img = Image.open(name)
    imgtk = ImageTk.PhotoImage(img)
    _icon_cache[name] = imgtk
    return imgtk


def get_in_filename(initialdir, title, filetypes):
    root = tk.Tk()
    root.withdraw()
    value = None
    # while value is None or value == "" or value == ():
    value = tk_fd.askopenfilename(
        initialdir=initialdir,
        title=title,
        filetypes=filetypes)
    root.destroy()
    return value


def get_out_filename(initialdir, title, filetypes):
    root = tk.Tk()
    root.withdraw()
    value = None
    # while value is None or value == "" or value == ():
    value = tk_fd.asksaveasfilename(
        initialdir=initialdir,
        title=title,
        filetypes=filetypes)
    root.destroy()
    return value


def get_directory(initialdir, title):
    root = tk.Tk()
    root.withdraw()
    value = None
    # while value is None or value == "" or value == ():
    value = tk_fd.askdirectory(
        initialdir=initialdir,
        title=title)
    root.destroy()
    return value


def get_many_files(initialdir, title, filetypes):
    root = tk.Tk()
    root.withdraw()
    value = None
    # while value is None or len(value) == 0:
    value = tk_fd.askopenfilenames(
        initialdir=initialdir,
        title=title,
        filetypes=filetypes)
    root.destroy()
    return value
