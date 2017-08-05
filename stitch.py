#!/usr/bin/python3

import os
import sys
import json
import math
from PIL import Image
import tkinter as tk
from tkinter import filedialog as tk_fd
root = tk.Tk()
root.withdraw()

VALID_FILES = (("Image files", ("*.jpg", "*.png")), ("all files", "*.*"))


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


class StitchData:
    '''
    StitchData contains all of the necessary data to stitch textures together

    width      - how many textures in width the final output will be
    tex_width  - width of each individual texture
    tex_height - height of each individual texture
    texlist    - list of textures, in order, that make up the final image
    output     - filename of output
    '''
    width = 1
    tex_width = 1
    tex_height = 1
    texlist = []
    output = ""

    def export_to_json(self, fname):
        '''
        Export this StitchData to a json file

        fname - name of file to export to
        '''
        data = {
            "width": self.width,
            "tex_width": self.tex_width,
            "tex_height": self.tex_height,
            "files": self.texlist[:],
            "out": self.output
        }
        with open(fname, 'w') as fh:
            fh.write(json.dumps(data, indent=4, sort_keys=True))

    def import_from_json(fname):
        '''
        Create a new StitchData from a json file

        fname - name of file to import from
        '''
        sdata = StitchData()
        with open(fname, 'r') as fh:
            jdata = json.loads(fh.read())
            sdata.width = jdata["width"]
            sdata.tex_width = jdata["tex_width"]
            sdata.tex_height = jdata["tex_height"]
            sdata.texlist = jdata["files"][:]
            sdata.output = jdata["out"]
        return sdata


def pick_files_individual(data, path):
    '''
    Picks files one by one from a given path

    data - StitchData to put textures into
    path - Base path of StitchData
    '''
    data.tex_width = input_int("How wide is each texture? ")
    data.tex_height = input_int("How tall is each texture? ")
    data.width = input_int("How many textures wide should the output be? ")
    print("Input a list of textures from top to bottom: ")
    while True:
        file_path = tk_fd.askopenfilename(
            initialdir=path,
            title="Select an image",
            filetypes=VALID_FILES)
        if file_path == "":
            break
        file_path = os.path.relpath(file_path, path)
        data.texlist.append(file_path)
        print(file_path)


def stitch_new(path, args, pickf=pick_files_individual):
    '''
    Create a new StitchData and export it to a json file

    args - command line arguments
    auto - whether or not to use automatic method
    '''
    # Figure out paths
    if len(args) != 1:
        print("Invalid arguments")
        sys.exit()
    outfile = os.path.join(path, args[0])
    path = os.path.dirname(outfile)
    # Create data
    data = StitchData()
    data.output = tk_fd.asksaveasfilename(
        initialdir=path,
        title="Output should be saved as:",
        filetypes=VALID_FILES)
    data.output = os.path.relpath(data.output, path)
    # Get files
    pickf(data, path)
    # Output
    data.export_to_json(outfile)
    print("Created file.")


def stitch_pack(path, args):
    '''
    Use a StitchData json file to pack multiple textures into a single image
    '''
    # Figure out paths
    if len(args) != 1:
        print("Invalid arguments")
        sys.exit()
    datafile = os.path.join(path, args[0])
    path = os.path.dirname(datafile)
    # Get data
    data = StitchData.import_from_json(datafile)
    outfile = os.path.join(path, data.output)
    outwidth = data.width * data.tex_width
    outheight = data.tex_height * math.ceil(len(data.texlist) / data.width)
    # Create image
    image = Image.new('RGBA', (outwidth, outheight), (0, 0, 0, 0))
    x = 0
    y = 0
    for fname in data.texlist:
        fname = os.path.join(path, fname)
        part = Image.open(fname).convert("RGBA")
        part = part.crop((0, 0, data.tex_width, data.tex_height))
        ox = x * data.tex_width
        oy = y * data.tex_height
        image.paste(part, (ox, oy))
        x += 1
        if x >= data.width:
            x = 0
            y += 1
    # Save image
    image.save(outfile)
    print("Finished packing.")


def stitch_unpack(path, args):
    '''
    Use a StitchData json file to unpack an image into multiple textures
    '''
    # Figure out paths
    if len(args) != 1:
        print("Invalid arguments")
        sys.exit()
    datafile = os.path.join(path, args[0])
    path = os.path.dirname(datafile)
    # Get data
    data = StitchData.import_from_json(datafile)
    infile = os.path.join(path, data.output)
    image = Image.open(infile).convert("RGBA")
    x = 0
    y = 0
    # Unpack into multiple textures
    for fname in data.texlist:
        fname = os.path.join(path, fname)
        part = Image.open(fname).convert("RGBA")
        cx = x*data.tex_width
        cy = y*data.tex_height
        cw = part.width
        ch = part.height
        croparea = (cx, cy, min(cx+cw, image.width), min(cy+ch, image.height))
        cropped = image.crop(croparea)
        part.paste(cropped, (1, 0))
        part.paste(cropped, (0, 0))
        part.save(fname)
        x += 1
        if x >= data.width:
            x = 0
            y += 1
    print("Finished unpacking")
