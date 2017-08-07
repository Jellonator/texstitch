import os
import sys
import json
import math
import util
from PIL import Image


class StitchData:
    '''
    StitchData contains all of the necessary data to stitch textures together

    width      - how many textures in width the final output will be
    tex_width  - width of each individual texture
    tex_height - height of each individual texture
    texlist    - list of textures, in order, that make up the final image
    output     - filename of output
    path       - path to this stitchdata

    All paths are dealt in absolutes
    The exported json file will have relative file names
    '''
    width = 1
    tex_width = 1
    tex_height = 1
    texlist = []
    path = ""

    def get_img_width(self):
        return self.width * self.tex_width

    def get_img_height(self):
        return self.tex_height * math.ceil(len(self.texlist) / self.width)

    def get_stitched_image(self):
        outwidth = self.width * self.tex_width
        outheight = self.tex_height * math.ceil(len(self.texlist) / self.width)
        # Create image
        image = Image.new('RGBA', (outwidth, outheight), (0, 0, 0, 255))
        x = 0
        y = 0
        for fname in self.texlist:
            try:
                part = Image.open(fname).convert("RGBA")
            except IOError:
                pass
            part = part.crop((0, 0, self.tex_width, self.tex_height))
            ox = x * self.tex_width
            oy = y * self.tex_height
            image.paste(part, (ox, oy))
            x += 1
            if x >= self.width:
                x = 0
                y += 1
        return image

    def unpack_image(self, image):
        x = 0
        y = 0
        # Unpack into multiple textures
        for fname in self.texlist:
            part = Image.open(fname).convert("RGBA")
            cx = x*self.tex_width
            cy = y*self.tex_height
            cw = part.width
            ch = part.height
            croparea = (cx, cy, min(cx+cw, image.width),
                        min(cy+ch, image.height))
            cropped = image.crop(croparea)
            part.paste(cropped, (1, 0))
            part.paste(cropped, (0, 0))
            part.save(fname)
            x += 1
            if x >= self.width:
                x = 0
                y += 1

    def get_dir(self):
        return os.path.dirname(self.path)

    def export_to_json(self, fname=None):
        '''
        Export this StitchData to a json file

        fname - name of file to export to

        Returns True if could not save
        '''
        if fname is None:
            fname = self.path
        if fname == "":
            return True
        path = self.get_dir()
        data = {
            "width": self.width,
            "tex_width": self.tex_width,
            "tex_height": self.tex_height,
            "files": [os.path.relpath(name, path) for name in self.texlist],
        }
        with open(fname, 'w') as fh:
            fh.write(json.dumps(data, indent=4, sort_keys=True))
        return False

    def import_from_json(fname):
        '''
        Create a new StitchData from a json file

        fname - name of file to import from
        '''
        sdata = StitchData()
        sdata.path = fname
        path = sdata.get_dir()
        with open(fname, 'r') as fh:
            jdata = json.loads(fh.read())
            sdata.width = jdata["width"]
            sdata.tex_width = jdata["tex_width"]
            sdata.tex_height = jdata["tex_height"]
            sdata.texlist = [
                os.path.abspath(os.path.join(path, name))
                for name in jdata["files"]
            ]
        return sdata


def pick_files_individual(data, path):
    '''
    Picks files one by one from a given path

    data - StitchData to put textures into
    path - Base path of StitchData
    '''
    data.tex_width = util.input_int("How wide is each texture? ")
    data.tex_height = util.input_int("How tall is each texture? ")
    data.width = util.input_int(
        "How many textures wide should the output be? ")
    print("Input a list of textures from top to bottom: ")
    while True:
        file_path = util.get_in_filename(
            initialdir=path,
            title="Select an image",
            filetypes=util.FILES_IMG)
        if file_path == "":
            break
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
    data.path = os.path.abspath(outfile)
    # Get files
    pickf(data, path)
    # Output
    data.export_to_json()
    print("Created file.")


def stitch_pack(path, args):
    '''
    Use a StitchData json file to pack multiple textures into a single image
    '''
    # Figure out paths
    if len(args) != 2:
        print("Invalid arguments")
        sys.exit()
    datafile = os.path.join(path, args[0])
    path = os.path.dirname(datafile)
    # Get data
    data = StitchData.import_from_json(datafile)
    # Create image
    image = data.get_stitched_image()
    # Save image
    image.save(args[1])
    print("Finished packing.")


def stitch_unpack(path, args):
    '''
    Use a StitchData json file to unpack an image into multiple textures
    '''
    # Figure out paths
    if len(args) != 2:
        print("Invalid arguments")
        sys.exit()
    datafile = os.path.join(path, args[0])
    path = os.path.dirname(datafile)
    # Get data
    data = StitchData.import_from_json(datafile)
    data.unpack_image(Image.open(args[1]).convert("RGBA"))
    print("Finished unpacking")
