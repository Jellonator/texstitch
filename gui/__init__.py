# import os
import util
# import stitch
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mbox

from gui import newstitchfile


class StitchGui(ttk.Frame):
    data = None
    default_path = ""
    updated = False
    img = None

    def __init__(self, root, default_path):
        super().__init__(root)
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
            self.data.path = util.get_out_filename(
                initialdir=self.default_path,
                title="Json data save path",
                filetypes=util.FILES_STITCH)

    def f_stitch_new(self):
        if self.check_save(should_alert=True):
            return
        data = newstitchfile.create_new_file(self.master, self.default_path)
        if data is not None:
            print("Got data!")

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

    def f_move_up(self):
        pass

    def f_move_down(self):
        pass

    def f_init_ui(self):
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.master.title("Simple")
        self.pack(fill=tk.BOTH, expand=True)

        buttonframe = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        buttonframe.pack(fill=tk.Y, side=tk.LEFT)
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

        button_move_up = ttk.Button(
            buttonframe,
            image=util.load_icon('icon/up.png'),
            command=self.f_move_up)
        button_move_up.pack(side=tk.TOP, padx=5, pady=5)

        button_move_down = ttk.Button(
            buttonframe,
            image=util.load_icon('icon/down.png'),
            command=self.f_move_down)
        button_move_down.pack(side=tk.TOP, padx=5, pady=5)


def open_gui(path):
    root = tk.Tk()
    root.geometry("640x480")
    app = StitchGui(root, path) #NOQA
    root.mainloop()
