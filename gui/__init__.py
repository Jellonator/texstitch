# import os
import util
import stitch
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mbox
from PIL import Image, ImageTk, ImageDraw

from gui import newstitchfile


class StitchGui(ttk.Frame):
    data = None
    default_path = ""
    updated = False
    img = None
    select_index = 0
    image_full = None
    image_select = None

    def __init__(self, root, default_path):
        super().__init__(root)
        self.default_path = default_path
        self.f_init_ui()

    def mark_data_updated(self):
        self.updated = True

    def need_to_save(self):
        return self.data is not None and self.updated

    def set_select_index(self, canvas, value):
        print(value)
        self.select_index = value
        canvas.delete("all")
        ix = value % self.data.width
        iy = value // self.data.width
        x = ix * self.data.tex_width
        y = iy * self.data.tex_height
        img = self.image_full
        canvas.create_image(img.width()/2, img.height()/2, image=img)
        sel = self.image_select
        canvas.create_image(sel.width()/2+x, sel.height()/2+y, image=sel)

    def bind_select_index(self, event):
        w = self.data.get_img_width()
        h = self.data.get_img_height()
        x = event.x
        y = event.y
        if x < 0 or y < 0 or x >= w or y >= h:
            return
        ix = x // self.data.tex_width
        iy = y // self.data.tex_height
        i = int(ix + iy * self.data.width)
        if i < 0 or i >= len(self.data.texlist):
            return
        self.set_select_index(event.widget, i)

    def refresh_data_panel(self):
        for child in self.mainframe.winfo_children():
            child.destroy()
        if self.data is None:
            return
        w = self.data.tex_width
        h = self.data.tex_height
        # Create image
        self.img = self.data.get_stitched_image()
        tkimg = ImageTk.PhotoImage(self.img)
        self.image_full = tkimg
        # Create selection image
        image_select = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image_select)
        draw.rectangle([(0, 0), (w-1, h-1)],
                       fill=(255, 255, 255, 50),
                       outline=(0, 0, 0, 50))
        self.image_select = ImageTk.PhotoImage(image_select)

        canvas = tk.Canvas(self.mainframe,
                           width=self.data.get_img_width(),
                           height=self.data.get_img_height())
        canvas.pack(side=tk.TOP)
        canvas.bind("<Button-1>", self.bind_select_index)
        self.set_select_index(canvas, self.select_index)

    def check_save(self, should_alert=False):
        """
        Make sure that any unsaved changes are saved

        Returns True if changes were made but could not save (unless user chose
        not to save.)
        """
        if self.data is not None and self.updated:
            if should_alert:
                result = mbox.askquestion(
                    "Question",
                    "There are unsaved changes.\n" +
                    "Would you like to save?")
                if result == "yes":
                    if self.check_data_path():
                        return True
                    self.f_stitch_save()
            else:
                return True
        return False

    def check_data_path(self):
        """
        Make sure that data has a valid path to save to

        Returns True if path could not be set (user cancelled.)
        """
        if self.data.path == "":
            fname = util.get_out_filename(
                initialdir=self.default_path,
                title="Json data save path",
                filetypes=util.FILES_STITCH)
            if fname is None or fname == () or fname == "":
                return True
            self.data.path = fname
        return False

    def f_stitch_new(self):
        if self.check_save(should_alert=True):
            return
        data = newstitchfile.create_new_file(self.master, self.default_path)
        if data is not None:
            self.data = data
            self.updated = True
            self.refresh_data_panel()

    def f_stitch_save_as(self):
        """
        Save data to another name
        """
        if self.data is None:
            mbox.showinfo("Information", "No data to save.")
        fname = util.get_out_filename(
            initialdir=self.default_path,
            title="Json data save path",
            filetypes=util.FILES_STITCH)
        if fname == () or fname == "":
            mbox.showerror("Error", "Could not save.")
            return
        self.data.path = fname
        self.data.export_to_json()

    def f_stitch_save(self):
        """
        Save data
        Returns True if could not save
        """
        if self.data is None:
            mbox.showinfo("Information", "No data to save.")
        if self.check_data_path():
            return True
        return self.data.export_to_json()

    def f_stitch_open(self):
        """
        Open a file
        """
        if self.check_save(should_alert=True):
            return
        fname = util.get_in_filename(
            initialdir=self.default_path,
            title="Json data save path",
            filetypes=util.FILES_STITCH)
        if fname == () or fname == "":
            return
        else:
            self.data = stitch.StitchData.import_from_json(fname)
            self.refresh_data_panel()

    def f_stitch_close(self):
        """
        Close current file
        """
        if self.data is None:
            mbox.showinfo("Information", "No data to close")
        if self.check_save(should_alert=True):
            return
        self.data = None
        self.updated = False
        self.img = None
        self.refresh_data_panel()

    def f_quit(self):
        if self.check_save(should_alert=True):
            return
        self.master.destroy()

    def f_remove_current(self):
        i = self.select_index
        if self.data is None:
            mbox.showinfo("Information", "No data is currently opened")
            return
        if i < 0 or i >= len(self.data.texlist):
            if len(self.data.texlist) == 0:
                mbox.showinfo("Information", "There are no textures to remove")
            else:
                mbox.showinfo("Information",
                              "Please select a texture to remove")
            return
        del self.data.texlist[i]
        if i >= len(self.data.texlist) and i > 0:
            self.select_index -= 1
        self.refresh_data_panel()

    def f_add_texture(self):
        if self.data is None:
            mbox.showinfo("Information",
                          "No data opened, can't add texture.")
            return
        fnames = util.get_many_files(
            initialdir=self.default_path,
            title="Select textures",
            filetypes=util.FILES_IMG)
        for name in fnames:
            self.data.texlist.append(name)
        self.refresh_data_panel()

    def f_import_pieces(self):
        if self.data is None:
            mbox.showinfo("Information",
                          "No data opened, can't import images.")
        self.refresh_data_panel()

    def f_import_whole(self):
        if self.data is None:
            mbox.showinfo("Information",
                          "No data opened, can't import image.")
        self.refresh_data_panel()

    def f_export_pieces(self):
        if self.data is None:
            mbox.showinfo("Information",
                          "No data opened, can't export images.")

    def f_export_whole(self):
        if self.data is None:
            mbox.showinfo("Information",
                          "No data opened, can't export image.")

    def f_move_tile_to(self, ifrom, ito):
        if self.data is None:
            return
        if ifrom == ito:
            return
        if ifrom < 0 or ifrom >= len(self.data.texlist):
            return
        if ito < 0 or ito >= len(self.data.texlist):
            return
        self.data.texlist[ifrom], self.data.texlist[ito] =\
            self.data.texlist[ito], self.data.texlist[ifrom]
        print(ifrom, ito)
        self.select_index = ito
        self.refresh_data_panel()

    def f_move_up(self, event=None):
        if self.data is None:
            return
        self.f_move_tile_to(self.select_index,
                            self.select_index-self.data.width)

    def f_move_down(self, event=None):
        if self.data is None:
            return
        self.f_move_tile_to(self.select_index,
                            self.select_index+self.data.width)

    def f_move_left(self, event=None):
        if self.data is None:
            return
        self.f_move_tile_to(self.select_index, self.select_index-1)

    def f_move_right(self, event=None):
        if self.data is None:
            return
        self.f_move_tile_to(self.select_index, self.select_index+1)

    def f_init_ui(self):
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.master.title("Simple")
        self.pack(fill=tk.BOTH, expand=True)

        buttonframe = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        buttonframe.pack(fill=tk.Y, side=tk.LEFT)

        mainframe = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        mainframe.pack(fill=tk.BOTH, side=tk.LEFT)
        self.mainframe = mainframe

        # self.pack(fill=tk.BOTH, expand=1)

        # Create menu
        menu_root = tk.Menu(self.master)
        self.master.config(menu=menu_root)
        # File menu
        menu_file = tk.Menu(menu_root, tearoff=0)
        menu_file.add_command(label="New", command=self.f_stitch_new)
        menu_file.add_command(label="Save", command=self.f_stitch_save)
        menu_file.add_command(label="Save As", command=self.f_stitch_save_as)
        menu_file.add_command(label="Open", command=self.f_stitch_open)
        menu_file.add_command(label="Close", command=self.f_stitch_close)
        menu_file.add_command(label="Exit", command=self.f_quit)
        menu_root.add_cascade(label="File", menu=menu_file)
        # Import menu
        menu_import = tk.Menu(menu_root, tearoff=0)
        menu_import.add_command(label="Import Textures",
                                command=self.f_import_pieces)
        menu_import.add_command(label="Import Whole",
                                command=self.f_import_whole)
        menu_root.add_cascade(label="Import", menu=menu_import)
        # Export menu
        menu_export = tk.Menu(menu_root, tearoff=0)
        menu_export.add_command(label="Export Textures",
                                command=self.f_export_pieces)
        menu_export.add_command(label="Export Whole",
                                command=self.f_export_whole)
        menu_root.add_cascade(label="Export", menu=menu_export)
        # Up/Down buttons
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
        button_move_left = ttk.Button(
            buttonframe,
            image=util.load_icon('icon/left.png'),
            command=self.f_move_left)
        button_move_left.pack(side=tk.TOP, padx=5, pady=5)
        button_move_right = ttk.Button(
            buttonframe,
            image=util.load_icon('icon/right.png'),
            command=self.f_move_right)
        button_move_right.pack(side=tk.TOP, padx=5, pady=5)
        button_add = ttk.Button(
            buttonframe,
            image=util.load_icon('icon/add.png'),
            command=self.f_add_texture)
        button_add.pack(side=tk.TOP, padx=5, pady=5)
        button_remove = ttk.Button(
            buttonframe,
            image=util.load_icon('icon/remove.png'),
            command=self.f_remove_current)
        button_remove.pack(side=tk.TOP, padx=5, pady=5)
        self.master.bind("<Left>", self.f_move_left)
        self.master.bind("<Up>", self.f_move_up)
        self.master.bind("<Right>", self.f_move_right)
        self.master.bind("<Down>", self.f_move_down)


def open_gui(path):
    root = tk.Tk()
    root.geometry("640x480")
    app = StitchGui(root, path) #NOQA
    root.mainloop()
