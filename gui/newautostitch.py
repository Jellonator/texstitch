import util
import stitch
import seams
import tkinter as tk
from tkinter import messagebox as mbox


class NewAutoStitchFile(tk.Toplevel):
    ok = False
    default_path = ""

    def select_images(self):
        """
        Pick textures
        """
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

    def accept_ok(self):
        """
        Ok button is pressed
        """
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
        """
        Cancel button is pressed
        """
        self.ok = False
        self.destroy()

    def __init__(self, parent, default_path):
        # Init
        super().__init__(parent)
        self.texfiles = ()
        self.geometry("480x320")
        self.default_path = default_path
        # Create frames
        frame_image_select = tk.Frame(self, relief=tk.RAISED)
        frame_buttons = tk.Frame(self, relief=tk.RAISED)
        frame_buttons.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
        frame_image_select.pack(fill=tk.BOTH, padx=5, pady=5, expand=tk.TRUE)
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


def auto_new_file(root, default_path):
    f = NewAutoStitchFile(root, default_path)
    if not f.ok:
        return None
    data = stitch.StitchData()
    imgnodes = {}
    for name in f.texfiles:
        imgnodes[name] = seams.ImageNode(name)
    seams.compare_image_nodes(imgnodes)
    seams.put_nodes_into_data(imgnodes, data)

    could_move_unused = False
    for n in imgnodes.values():
        if not n.used:
            could_move_unused = True
            break
    if could_move_unused:
        result = mbox.askquestion(
            "Question",
            "There are unused textures.\n" +
            "Would you like to move them to another folder?")
        if result == "yes":
            folder = util.get_directory(
                initialdir=default_path,
                title="Choose folder for unused textures")
            if folder != () and folder != "":
                seams.move_unused_nodes(imgnodes, folder)

    return data
