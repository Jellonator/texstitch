#!/usr/bin/python3
import stitch
import sys
import os
import seams
import gui

HELP_STRING = """
This is a Texture stitching program.
It's useful for Nintendo 64 repaints.

Commands:
stitch gui
Open the Stitch Editor GUI

stitch new {filename}
Create a new stitch file by manually picking files.

stitch newseam {filename}
Create a new stitch file by automatically matching
seams.

stitch pack {filename} {imagename}
Pack a stitch project's textures into a single image.

stitch unpack {filename} {imagename}
Split an image into multiple textures as defined by a stitch project.

Auto stitch creation requires the given textures to have matching edges.
Any textures given to auto that aren't in the output image will be moved to a
new folder named 'unused_textures.'
"""


def stitch_help():
    '''
    Help! I need sombody, help!
    '''
    print(HELP_STRING)


def main(args):
    base_path = os.getcwd()
    if len(args) < 2:
        # stitch_help()
        gui.open_gui(base_path)
    else:
        fname = args[1]
        passed_args = args[2:]
        if fname == "new":
            stitch.stitch_new(base_path, passed_args,
                              stitch.pick_files_individual)
        elif fname == "newseam":
            stitch.stitch_new(base_path, passed_args, seams.pick_files_auto)
        elif fname == "gui":
            gui.open_gui(base_path)
        elif fname == "pack":
            stitch.stitch_pack(base_path, passed_args)
        elif fname == "unpack":
            stitch.stitch_unpack(base_path, passed_args)
        elif fname == "help" or fname is None:
            stitch_help()
        else:
            print("Not a valid command.")


if __name__ == "__main__":
    main(sys.argv[:])
