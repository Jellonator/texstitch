# import os
import util
import stitch
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mbox
from PIL import Image, ImageTk, ImageDraw

from gui import newstitchfile

ZOOM_STAGES = [0.125, 0.25, 0.5, 1, 2, 4, 8]

BASE_ZOOM = ZOOM_STAGES.index(1)

IMAGE_MODE_STITCHED = 1
IMAGE_MODE_WHOLE = 2

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


def create_selection_box(width, height):
    s = max(5, int(width*0.2), int(height*0.2))
    leny = min(height//2, s)
    lenx = min(width//2, s)
    x1 = 1
    x2 = 1 + lenx
    x3 = width - 1 - lenx
    x4 = width - 1
    y1 = 1
    y2 = 1 + leny
    y3 = height - 1 - leny
    y4 = height - 1
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.line(((x1, y2), (x1, y1), (x2, y1)), fill=WHITE)
    draw.line(((x4, y2), (x4, y1), (x3, y1)), fill=BLACK)
    draw.line(((x1, y3), (x1, y4), (x2, y4)), fill=BLACK)
    draw.line(((x4, y3), (x4, y4), (x3, y4)), fill=WHITE)
    return ImageTk.PhotoImage(image)


class StitchGui(ttk.Frame):
    data = None
    default_path = ""
    updated = False
    img = None
    select_index = 0
    image_full = None
    image_select = None
    elements_to_gray = None
    image_mode = None
    canvas = None
    zoom = BASE_ZOOM

    def __init__(self, root, default_path):
        super().__init__(root)
        self.default_path = default_path
        self.elements_to_gray = []
        self.image_mode = tk.IntVar()
        self.image_mode.set(IMAGE_MODE_STITCHED)
        self.f_init_ui()

    def reset_canvas(self):
        for child in self.mainframe.winfo_children():
            child.destroy()
        self.canvas = None
        self.refresh_data_panel()

    def set_data(self, data):
        """
        Set the data to a new value, resetting certain variables in the process
        """
        self.data = data
        self.image_full = None
        self.image_select = None
        self.updated = False
        self.img = None
        self.select_index = -1
        self.image_mode.set(IMAGE_MODE_STITCHED)
        self.zoom = BASE_ZOOM
        state = tk.NORMAL
        if data is None:
            state = tk.DISABLED
        for e in self.elements_to_gray:
            if isinstance(e, tuple):
                menu, name = e
                menu.entryconfig(name, state=state)
            else:
                e.config(state=state)
        self.reset_canvas()

    def set_select_index(self, canvas, value):
        """
        Set the selection index
        Updates the given canvas
        """
        self.select_index = value
        canvas.delete("all")
        ix = value % self.data.width
        iy = value // self.data.width
        x = ix * self.data.tex_width
        y = iy * self.data.tex_height
        img = self.image_full
        canvas.create_image(img.width()/2, img.height()/2, image=img)
        sel = self.image_select
        zoom = ZOOM_STAGES[self.zoom]
        canvas.create_image(sel.width()/2+x*zoom, sel.height()/2+y*zoom,
                            image=sel)

    def bind_select_index(self, event):
        """
        Binding of an event to a canvas to make canvas selectable
        """
        w = self.data.get_img_width()
        h = self.data.get_img_height()
        x = event.x
        y = event.y
        zoom = ZOOM_STAGES[self.zoom]
        x = x / zoom
        y = y / zoom
        if x < 0 or y < 0 or x >= w or y >= h:
            return
        ix = x // self.data.tex_width
        iy = y // self.data.tex_height
        i = int(ix + iy * self.data.width)
        if i < 0 or i >= len(self.data.texlist):
            return
        self.set_select_index(event.widget, i)

    def refresh_data_panel(self):
        """
        Refresh the currently displayed image
        """
        if self.data is None:
            for child in self.mainframe.winfo_children():
                child.destroy()
            self.canvas = None
            return
        w = self.data.tex_width
        h = self.data.tex_height
        # Create image
        if self.image_mode.get() == IMAGE_MODE_STITCHED:
            self.img = self.data.get_stitched_image()
        elif self.image_mode.get() == IMAGE_MODE_WHOLE:
            self.img = self.data.get_packed_image()
        else:
            mbox.showerror("Error", "Unknown image mode")
            return
        if self.img is None:
            emsg = "Could not open image"
            if self.image_mode.get() == IMAGE_MODE_STITCHED:
                emsg += "\nMake sure that all of this image's textures exist"
            else:
                emsg += "\nMake sure that this image's output exists"
            mbox.showerror("Error", emsg)
            return
        zoom = ZOOM_STAGES[self.zoom]
        mode = Image.NEAREST
        if zoom < 1:
            mode = Image.BICUBIC
        size = (int(zoom*self.img.width), int(zoom*self.img.height))
        self.img = self.img.transform(
            size, Image.EXTENT, (0, 0, self.img.width, self.img.height), mode)
        tkimg = ImageTk.PhotoImage(self.img)
        self.image_full = tkimg
        # Create selection image
        # image_select = Image.new('RGBA', (zoom*w, zoom*h), (0, 0, 0, 0))
        # draw = ImageDraw.Draw(image_select)
        # draw.rectangle([(0, 0), (zoom*w-1, zoom*h-1)],
        #                fill=(255, 255, 255, 50),
        #                outline=(0, 0, 0, 50))
        # self.image_select = ImageTk.PhotoImage(image_select)
        self.image_select = create_selection_box(zoom*w, zoom*h)
        # Create canvas
        if self.canvas is None:
            self.canvas = tk.Canvas(
                self.mainframe, width=size[0], height=size[1])
        self.canvas.pack(side=tk.TOP)
        self.canvas.bind("<Button-1>", self.bind_select_index)
        self.set_select_index(self.canvas, self.select_index)

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
        """
        Create a new stitch file through a dialog
        """
        if self.check_save(should_alert=True):
            return
        data = newstitchfile.create_new_file(self.master, self.default_path)
        if data is not None:
            self.set_data(data)
            self.updated = True

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
            self.set_data(stitch.StitchData.import_from_json(fname))

    def f_stitch_close(self):
        """
        Close current file
        """
        if self.data is None:
            mbox.showinfo("Information", "No data to close")
        if self.check_save(should_alert=True):
            return
        self.set_data(None)

    def f_quit(self):
        """
        Quit application
        """
        if self.check_save(should_alert=True):
            return
        self.master.destroy()

    def f_remove_current(self):
        """
        Remove currently selected texture
        """
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
        self.updated = True
        if i >= len(self.data.texlist) and i > 0:
            self.select_index -= 1
        self.refresh_data_panel()

    def f_add_texture(self):
        """
        Add a new texture to end of image
        """
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
        self.updated = True
        self.refresh_data_panel()

    def f_export_pieces(self):
        """
        Export pieces of image
        """
        if self.data is None:
            mbox.showinfo("Information",
                          "No data opened, can't export images.")
            return
        image = self.data.get_packed_image()
        x = 0
        y = 0
        # Unpack into multiple textures
        for fname in self.data.texlist:
            part = Image.open(fname).convert("RGBA")
            cx = x*self.data.tex_width
            cy = y*self.data.tex_height
            cw = part.width
            ch = part.height
            croparea = (cx, cy, min(cx+cw, image.width),
                        min(cy+ch, image.height))
            cropped = image.crop(croparea)
            part.paste(cropped, (1, 0))
            part.paste(cropped, (0, 0))
            part.save(fname)
            x += 1
            if x >= self.data.width:
                x = 0
                y += 1

    def f_export_whole(self):
        """
        Export whole of image
        """
        if self.data is None:
            mbox.showinfo("Information",
                          "No data opened, can't export image.")
            return
        # Create image
        image = self.data.get_stitched_image()
        # Save image
        image.save(self.data.output)

    def f_export_whole_as(self):
        """
        Export whole of image
        """
        if self.data is None:
            mbox.showinfo("Information",
                          "No data opened, can't export image.")
            return
        fname = util.get_out_filename(
            initialdir=self.default_path,
            title="Output image",
            filetypes=util.FILES_IMG)
        if fname == () or fname == "":
            mbox.showerror("Error", "Could not export.")
            return
        # Create image
        image = self.data.get_stitched_image()
        # Save image
        image.save(fname)

    def f_move_tile_to(self, ifrom, ito):
        """
        Move a tile from ifrom to ito
        """
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
        self.select_index = ito
        self.updated = True
        self.refresh_data_panel()

    def f_move_up(self, event=None):
        """
        Move selection up
        """
        if self.data is None:
            return
        self.f_move_tile_to(self.select_index,
                            self.select_index-self.data.width)

    def f_move_down(self, event=None):
        """
        Move selection down
        """
        if self.data is None:
            return
        self.f_move_tile_to(self.select_index,
                            self.select_index+self.data.width)

    def f_move_left(self, event=None):
        """
        Move selection left
        """
        if self.data is None:
            return
        self.f_move_tile_to(self.select_index, self.select_index-1)

    def f_move_right(self, event=None):
        """
        Move selection right
        """
        if self.data is None:
            return
        self.f_move_tile_to(self.select_index, self.select_index+1)

    def f_zoom_in(self):
        """
        Zoom in a little
        """
        if self.zoom + 1 >= len(ZOOM_STAGES):
            return
        self.zoom += 1
        self.reset_canvas()

    def f_zoom_out(self):
        """
        Zoom out a little
        """
        if self.zoom - 1 < 0:
            return
        self.zoom -= 1
        self.reset_canvas()

    def f_init_ui(self):
        """
        Create entire UI
        """
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.master.title("Stitch Editor")
        self.pack(fill=tk.BOTH, expand=True)
        # Left frame with buttons
        buttonframe = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        buttonframe.pack(fill=tk.Y, side=tk.LEFT)
        # Top frame with options
        optionframe = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        optionframe.pack(fill=tk.X, side=tk.TOP)
        # Centermost frame
        mainframe = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        mainframe.pack(fill=tk.BOTH, side=tk.LEFT)
        self.mainframe = mainframe
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
        # Export menu
        menu_export = tk.Menu(menu_root, tearoff=0)
        menu_export.add_command(label="Export Textures",
                                command=self.f_export_pieces)
        menu_export.add_command(label="Export Whole",
                                command=self.f_export_whole)
        menu_export.add_command(label="Export Whole As",
                                command=self.f_export_whole_as)
        menu_root.add_cascade(label="Export", menu=menu_export)
        # Radio buttons
        radio_stitched = tk.Radiobutton(optionframe, text="Stitched",
                                        variable=self.image_mode,
                                        value=IMAGE_MODE_STITCHED,
                                        command=self.refresh_data_panel)
        radio_stitched.pack(side=tk.LEFT, padx=5, pady=5)
        radio_whole = tk.Radiobutton(optionframe, text="Packed",
                                     variable=self.image_mode,
                                     value=IMAGE_MODE_WHOLE,
                                     command=self.refresh_data_panel)
        radio_whole.pack(side=tk.LEFT, padx=5, pady=5)
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
        button_zoom_in = ttk.Button(
            buttonframe,
            image=util.load_icon('icon/zoom_in.png'),
            command=self.f_zoom_in)
        button_zoom_in.pack(side=tk.TOP, padx=5, pady=5)
        button_zoom_out = ttk.Button(
            buttonframe,
            image=util.load_icon('icon/zoom_out.png'),
            command=self.f_zoom_out)
        button_zoom_out.pack(side=tk.TOP, padx=5, pady=5)
        # Bind keys
        self.master.bind("<Left>", self.f_move_left)
        self.master.bind("<Up>", self.f_move_up)
        self.master.bind("<Right>", self.f_move_right)
        self.master.bind("<Down>", self.f_move_down)
        # Gray out elements
        self.elements_to_gray.append(button_move_up)
        self.elements_to_gray.append(button_move_left)
        self.elements_to_gray.append(button_move_right)
        self.elements_to_gray.append(button_move_down)
        self.elements_to_gray.append(button_add)
        self.elements_to_gray.append(button_remove)
        self.elements_to_gray.append(button_zoom_in)
        self.elements_to_gray.append(button_zoom_out)
        self.elements_to_gray.append(radio_whole)
        self.elements_to_gray.append(radio_stitched)
        self.elements_to_gray.append((menu_file, "Save"))
        self.elements_to_gray.append((menu_file, "Save As"))
        self.elements_to_gray.append((menu_file, "Close"))
        self.elements_to_gray.append((menu_export, "Export Textures"))
        self.elements_to_gray.append((menu_export, "Export Whole"))
        self.elements_to_gray.append((menu_export, "Export Whole As"))
        # Set data
        self.set_data(None)
        # Override quit button
        self.master.protocol('WM_DELETE_WINDOW', self.f_quit)


def open_gui(path):
    root = tk.Tk()
    root.geometry("640x480")
    app = StitchGui(root, path) #NOQA
    root.mainloop()
