import tkinter as tk


class NewAutoStitchFile(tk.Toplevel):
    ok = False

    def accept_ok(self):
        """
        Ok button is pressed
        """
        self.ok = True
        self.destroy()

    def accept_cancel(self):
        """
        Cancel button is pressed
        """
        self.ok = False
        self.destroy()

    def __init__(self, parent, data):
        # Init
        super().__init__(parent)
        self.texfiles = ()
        self.geometry("320x240")
        self.width = tk.IntVar()
        self.tex_width = tk.IntVar()
        self.tex_height = tk.IntVar()
        self.width.set(data.width)
        self.tex_width.set(data.tex_width)
        self.tex_height.set(data.tex_height)
        # Create frames
        frame_width = tk.Frame(self, relief=tk.RAISED)
        frame_tex_width = tk.Frame(self, relief=tk.RAISED)
        frame_tex_height = tk.Frame(self, relief=tk.RAISED)
        frame_buttons = tk.Frame(self, relief=tk.RAISED)
        frame_width.pack(fill=tk.X, padx=5, pady=5)
        frame_tex_width.pack(fill=tk.X, padx=5, pady=5)
        frame_tex_height.pack(fill=tk.X, padx=5, pady=5)
        frame_buttons.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
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


def config_data(root, data):
    f = NewAutoStitchFile(root, data)
    if not f.ok:
        return False
    data.width = f.width.get()
    data.tex_width = f.tex_width.get()
    data.tex_height = f.tex_height.get()
    return True
