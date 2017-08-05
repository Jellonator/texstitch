# TexStitch
Stitch multiple textures together into a single image.

This is a Texture stitching program.
It's useful for Nintendo 64 repaints.
 
Commands:
```
stitch new {filename}       Create a new stitch file
stitch auto {filename}      Create a new stitch file automatically
stitch pack {filename}      Pack multiple images into a single image
stitch unpack {filename}    Unpack a stitched image into multiple images
```
 
Auto stitch creation requires the given textures to have matching edges.
Any textures given to auto that aren't in the output image will be moved to a
new folder named 'unused_textures.'

If you are repainting the Legend of Zelda: Ocarina of Time / Master Quest for
the Nintendo Gamecube, then here are a few tips:
 * You need python3 installed and the ability to use the command line to use
this program.
 * 64x32 textures can be easily stitched together using the `stitch auto`
command, since these textures share borders.
* If using the `stitch auto` command, make sure to only select environment
textures. Any junk or non-environment textures will likely break things since
they are not part of an environment.
 * 324x8 textures can not be automatically stitched together since they do not
share borders, so `stitch new` must be used instead.
 * 324x8 textures are actually 320x6 individually when stitched together.
Together, the final image will be 320x240, with a total of 40 textures used.
