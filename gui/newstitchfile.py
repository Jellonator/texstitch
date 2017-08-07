import util
import stitch
import tkinter as tk
from tkinter import messagebox as mbox
# from tkinter import filedialog as tk_fd
# from tkinter import ttk
# from tkinter import messagebox as mbox


class NewStitchFile(tk.Toplevel):
    ok = False
    default_path = ""

    def select_images(self):
        file_path_list = util.get_many_files(
            filetypes=util.FILES_IMG,
            initialdir=self.default_path,
            title='Select textures')
        self.texfiles = file_path_list
        self.text_infiles.config(state=tk.NORMAL)
        self.text_infiles.delete("1.0", tk.END)
        for name in self.texfiles:
            self.text_infiles.insert(tk.END, name+'\n')
        self.text_infiles.config(state=tk.DISABLED)

    def select_output(self):
        out_name = util.get_out_filename(
            initialdir=self.default_path,
            title="Output image name",
            filetypes=util.FILES_IMG)
        if out_name != () and out_name != "":
            self.entry_outfile.delete(0, tk.END)
            self.entry_outfile.insert(0, out_name)
            self.outfile.set(out_name)

    def accept_ok(self):
        if self.outfile.get() == "":
            mbox.showerror("Error", "No output file specified")
            return
        if len(self.texfiles) == 0:
            result = mbox.askquestion(
                "Question",
                "No input files were specified.\n" +
                "Are you sure you wish to continue?")
            if result == "no":
                return
        self.ok = True
        self.destroy()

    def accept_cancel(self):
        self.ok = False
        self.destroy()

    def __init__(self, parent, default_path):
        # Init
        super().__init__(parent)
        self.texfiles = ()
        self.width = tk.IntVar()
        self.tex_width = tk.IntVar()
        self.tex_height = tk.IntVar()
        self.outfile = tk.StringVar()
        self.geometry("480x320")
        self.default_path = default_path
        # Create frames
        frame_width = tk.Frame(self, relief=tk.RAISED)
        frame_tex_width = tk.Frame(self, relief=tk.RAISED)
        frame_tex_height = tk.Frame(self, relief=tk.RAISED)
        frame_output_select = tk.Frame(self, relief=tk.RAISED)
        frame_image_select = tk.Frame(self, relief=tk.RAISED)
        frame_buttons = tk.Frame(self, relief=tk.RAISED)
        frame_width.pack(fill=tk.X, padx=5, pady=5)
        frame_tex_width.pack(fill=tk.X, padx=5, pady=5)
        frame_tex_height.pack(fill=tk.X, padx=5, pady=5)
        frame_output_select.pack(fill=tk.X, padx=5, pady=5)
        frame_buttons.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
        frame_image_select.pack(fill=tk.BOTH, padx=5, pady=5, expand=tk.TRUE)
        # Spinboxes
        spinbox_width = tk.Spinbox(frame_width, from_=1, to=65535,
                                   textvariable=self.width)
        spinbox_tex_width = tk.Spinbox(frame_tex_width, from_=1, to=65535,
                                       textvariable=self.tex_width)
        spinbox_tex_height = tk.Spinbox(frame_tex_height, from_=1, to=65535,
                                        textvariable=self.tex_height)
        spinbox_width.pack(side=tk.RIGHT)
        spinbox_tex_width.pack(side=tk.RIGHT)
        spinbox_tex_height.pack(side=tk.RIGHT)
        # Spinbox lables
        label_width = tk.Label(frame_width,
                               text="Width of output in tiles")
        label_tex_width = tk.Label(frame_tex_width,
                                   text="Width of each texture")
        label_tex_height = tk.Label(frame_tex_height,
                                    text="Height of each texture")
        label_width.pack(side=tk.RIGHT)
        label_tex_width.pack(side=tk.RIGHT)
        label_tex_height.pack(side=tk.RIGHT)
        # Outfile
        button_outfile = tk.Button(
            frame_output_select,
            image=util.load_icon('icon/open.png'),
            command=self.select_output)
        button_outfile.pack(side=tk.RIGHT)
        entry_outfile = tk.Entry(frame_output_select, text="",
                                 textvariable=self.outfile)
        entry_outfile.pack(side=tk.RIGHT)
        label_outfile = tk.Label(frame_output_select, text="Output Image")
        label_outfile.pack(side=tk.RIGHT)
        self.entry_outfile = entry_outfile
        # Infiles
        label_infiles = tk.Label(frame_image_select, text="Input images")
        label_infiles.pack(side=tk.TOP, anchor=tk.E)
        button_infiles = tk.Button(
            frame_image_select,
            image=util.load_icon('icon/open.png'),
            command=self.select_images)
        button_infiles.pack(side=tk.RIGHT, anchor=tk.N)
        text_infiles = tk.Text(frame_image_select, wrap="none",
                               state=tk.DISABLED)
        text_infiles_scroll = tk.Scrollbar(
            frame_image_select, orient=tk.VERTICAL, command=text_infiles.yview)
        text_infiles["yscrollcommand"] = text_infiles_scroll.set
        text_infiles_scroll.pack(side=tk.RIGHT, anchor=tk.N, fill=tk.Y)
        text_infiles.pack(side=tk.RIGHT, anchor=tk.N,
                          fill=tk.BOTH, expand=tk.YES)

        self.text_infiles = text_infiles
        # Accept buttons
        button_ok = tk.Button(
            frame_buttons,
            text="Done",
            command=self.accept_ok)
        button_cancel = tk.Button(
            frame_buttons,
            text="Cancel",
            command=self.accept_cancel)
        button_ok.pack(side=tk.RIGHT)
        button_cancel.pack(side=tk.RIGHT)

        # Make sure parent window is inactive
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)


def create_new_file(root, default_path):
    f = NewStitchFile(root, default_path)
    # print(f.width.get())
    if not f.ok:
        return None
    data = stitch.StitchData()
    data.width = f.width.get()
    data.texlist = [x for x in f.texfiles]
    data.tex_width = f.tex_width.get()
    data.tex_height = f.tex_height.get()
    data.output = f.outfile.get()

    return data
