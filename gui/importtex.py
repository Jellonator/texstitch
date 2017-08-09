import tkinter as tk
import util
import stitch

OPTION_TOP = "Top"
OPTION_BOTTOM = "Bottom"
OPTION_LEFT = "Left"
OPTION_RIGHT = "Right"

default_option = OPTION_BOTTOM


class DropdownWindow(tk.Toplevel):
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
        self.geometry("400x120")
        self.value = tk.StringVar()
        self.value.set(default_option)
        # Create frames
        frame_drop = tk.Frame(self, relief=tk.RAISED)
        frame_buttons = tk.Frame(self, relief=tk.RAISED)
        frame_drop.pack(fill=tk.X, padx=5, pady=5)
        frame_buttons.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
        # Dropdowns
        option_direction = tk.OptionMenu(frame_drop, self.value, OPTION_TOP,
                                         OPTION_BOTTOM, OPTION_LEFT,
                                         OPTION_RIGHT)
        option_direction.pack(side=tk.RIGHT)
        # Spinbox lables
        label_drop = tk.Label(frame_drop,
                              text="Where should imported textures be placed?")
        label_drop.pack(side=tk.RIGHT)
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


def import_tex(root, data, default_path): #NOQA
    f = DropdownWindow(root, data)
    if not f.ok:
        return False
    fname = util.get_in_filename(
        initialdir=default_path,
        title="Json data to import",
        filetypes=util.FILES_STITCH)
    if fname == () or fname == "":
        return False
    odata = stitch.StitchData.import_from_json(fname)
    result = f.value.get()
    if result == OPTION_BOTTOM:
        for name in odata.texlist:
            data.texlist.append(name)
    elif result == OPTION_TOP:
        for name in odata.texlist:
            data.texlist.insert(0, name)
    elif result == OPTION_LEFT or result == OPTION_RIGHT:
        texiter = iter(odata.texlist)
        try:
            pos = 0
            if result == OPTION_RIGHT:
                pos = data.width
            while True:
                for i in range(odata.width):
                    value = next(texiter)
                    data.texlist.insert(pos, value)
                    pos += 1
                pos += data.width
        except StopIteration:
            pass
        data.width += odata.width
    else:
        print("Invalid result " + result)
        return False
    global default_option
    default_option = result

    return True
