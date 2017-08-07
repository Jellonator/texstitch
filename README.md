# TexStitch
Stitch multiple textures together into a single image.

This is a Texture stitching program.
It's useful for Nintendo 64 repaints.

Opening this program without any arguments or from the file manager will open
the Stitch Editor GUI.

You need python3 installed and the ability to use the command line to use
this program. Get it at https://www.python.org/. You will also need the Python
`pillow` library installed. Install it with `pip install pillow`.

## Commands
 * `stitch gui` - Open the Stitch Editor GUI
 * `stitch new {filename}` - Create a new stitch file by manually picking files.
 * `stitch newseam {filename}` - Create a new stitch file by automatically
matching seams.
 * `stitch pack {filename} {imagename}` - Pack a stitch project's textures into
a single image.
 * `stitch unpack {filename} {imagename}` - Split an image into multiple
textures as defined by a stitch project.

## Notes for GUI
Go to `File -> New` to create a new stitch file, or use `File -> Open` to open
an existing stitch file. Use `File -> Save` or `File -> Save As` to save the
Stitch file.

Once a stitch file is open, the program will generate a stitched image in the
center of the screen. You can click on this image to select a portion of this
image. After you make a selection, you can use the arrow buttons on the left or
the arrow keys on your keyboard to move your selection around.

After you have organized your image, you can export the completed image using
`Image -> Export`. You can edit this exported file all you want and no changes
to the existing stitch file and its textures will occur. Once you have edited
the exported image and you want to modify the original textures to match your
edits, you can use `Image -> Import`. This will import an image and split it up
into individual textures to overwrite your previous textures.

## Notes for command line
Auto stitch creation requires the given textures to have matching edges.
Any textures given to auto that aren't in the output image will be moved to a
new folder named 'unused_textures.'

If you are repainting the Legend of Zelda: Ocarina of Time / Master Quest for
the Nintendo Gamecube, then here are a few tips:
 * 64x32 textures can be easily stitched together using the `stitch auto`
command, since these textures share borders.
* If using the `stitch auto` command, make sure to only select environment
textures. Any junk or non-environment textures will likely break things since
they are not part of an environment.
 * 324x8 textures can not be automatically stitched together since they do not
share borders, so `stitch new` must be used instead.
 * 324x8 textures are actually 320x6 individually when stitched together.
Together, the final image will be 320x240, with a total of 40 textures used.
