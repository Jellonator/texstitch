# import os
import util
import stitch
import tkinter as tk
from tkinter import filedialog as tk_fd
from tkinter import ttk


def get_out_filename(initialdir, title, filetypes):
    value = None
    while value is None or value == "" or value == ():
        value = tk_fd.asksaveasfilename(
            initialdir=initialdir,
            title=title,
            filetypes=filetypes)
        print(value)


def get_many_files(initialdir, title, filetypes):
    value = None
    while value is None or len(value) == 0:
        value = tk_fd.askopenfilenames(
            initialdir=initialdir,
            title=title,
            filetypes=filetypes)
        print(value)


class StitchGui(ttk.Frame):
    data = None
    default_path = ""
    updated = False
    img = None

    def __init__(self, default_path):
        super().__init__()
        self.default_path = default_path
        self.f_init_ui()

    def mark_data_updated(self):
        self.updated = True

    def need_to_save(self):
        return self.data is not None and self.updated

    def check_save(self, should_alert=False):
        if self.data is not None:
            self.check_data_path()
            # TODO: actually save

    def check_data_path(self):
        if self.data.path == "":
            self.data.path = get_out_filename(
                initialdir=self.default_path,
                title="Json data save path",
                filetypes=util.FILES_STITCH)

    def check_output_path(self):
        if self.data.output == "":
            self.data.output = get_out_filename(
                initialdir=self.default_path,
                title="Output image name",
                filetypes=util.FILES_IMG)

    def f_stitch_new(self):
        file_path_list = get_many_files(
            filetypes=util.FILES_IMG,
            initialdir=self.default_path,
            title='Select textures')

        data = stitch.StitchData()
        for fname in file_path_list:
            data.texlist.append(fname)

    def f_stitch_save_as(self):
        pass

    def f_stitch_save(self):
        pass

    def f_stitch_open(self):
        pass

    def f_stitch_close(self):
        pass

    def f_quit(self):
        pass

    def f_import_pieces(self):
        pass

    def f_import_whole(self):
        pass

    def f_export_pieces(self):
        pass

    def f_export_whole(self):
        pass

    def f_init_ui(self):
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.master.title("Simple")
        self.pack(fill=tk.BOTH, expand=True)

        buttonframe = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        buttonframe.pack(fill=tk.X, side=tk.TOP)
        # self.pack(fill=tk.BOTH, expand=1)

        menu_root = tk.Menu(self.master)
        self.master.config(menu=menu_root)

        menu_file = tk.Menu(menu_root, tearoff=0)
        menu_file.add_command(label="New", command=self.f_stitch_new)
        menu_file.add_command(label="Save", command=self.f_stitch_save)
        menu_file.add_command(label="Save As", command=self.f_stitch_save_as)
        menu_file.add_command(label="Open", command=self.f_stitch_open)
        menu_file.add_command(label="Close", command=self.f_stitch_close)
        menu_file.add_command(label="Exit", command=self.f_quit)
        menu_root.add_cascade(label="File", menu=menu_file)

        menu_import = tk.Menu(menu_root, tearoff=0)
        menu_import.add_command(label="Import Textures",
                                command=self.f_import_pieces)
        menu_import.add_command(label="Import Whole",
                                command=self.f_import_whole)
        menu_root.add_cascade(label="Import", menu=menu_import)

        menu_export = tk.Menu(menu_root, tearoff=0)
        menu_export.add_command(label="Export Textures",
                                command=self.f_export_pieces)
        menu_export.add_command(label="Export Whole",
                                command=self.f_export_whole)
        menu_root.add_cascade(label="Export", menu=menu_export)

        # button_new = ttk.Button(
        #     buttonframe,
        #     text="new",
        #     command=self.f_stitch_new)
        # button_new.pack(side=tk.LEFT, padx=5, pady=5)


def open_gui(path):
    root = tk.Tk()
    root.geometry("640x480")
    app = StitchGui(path) #NOQA
    root.mainloop()
