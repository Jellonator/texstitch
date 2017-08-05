#!/usr/bin/python3

import os
import sys
import json
import math
import shutil
from PIL import Image
from PIL import ImageDraw
import tkinter as tk
from tkinter import filedialog as tk_fd
root = tk.Tk()
root.withdraw()

VALID_FILES = (("Image files",("*.jpg", "*.png")), ("all files","*.*"))

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
			if imin != None and val < imin:
				print("Number should be at least {}".format(imin))
			elif imax != None and val > imax:
				print("Number should be at most {}".format(imax))
			else:
				return val
		except:
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
		file_path = tk_fd.askopenfilename(\
			initialdir = path,\
			title      = "Select an image",\
			filetypes  = VALID_FILES)
		if file_path == "":
			break
		file_path = os.path.relpath(file_path, path)
		data.texlist.append(file_path)
		print(file_path)

def img_cmp(img1, img2, pos1, pos2, size):
	'''
	Compare sections two images and return if their pixels exactly match

	pos1 - top-left position of the first image to compare with
	pos2 - top-left position of the second image to compare with
	size - size of the section to compare

	Example: img_cmp(img1, img2, (0, 0), (6, 6), (4, 4)) will compare a 4x4 area
	of img1 whose top-left position is (0, 0) with a 4x4 area of img2 whose
	top-left position is (6, 6)
	'''
	px1 = img1.load()
	px2 = img2.load()
	for ix in range(size[0]):
		for iy in range(size[1]):
			a = px1[pos1[0]+ix,pos1[1]+iy]
			b = px2[pos2[0]+ix,pos2[1]+iy]
			if a != b:
				return False
	return True

class ImageNode:
	'''
	ImageNode represents how an image may be connected with other images

	fname - filename of node
	used - whether this node has been used
	image - This node's image data
	top - ImageNode on top of this node
	left - ImageNode to left of this node
	right - ImageNode to right of this node
	bottom - ImageNode on bottom of this node
	'''
	left = None
	right = None
	top = None
	bottom = None
	image = None
	fname = ""
	used = False
	def __init__(self, fname):
		self.fname = fname
		self.image = Image.open(fname).convert("RGBA")
	def get_topleft(self, x=0):
		'''
		Traverses through ImageNodes to get the upper-left most ImageNode
		'''
		if x > 100:
			return self
		if self.left != None:
			return self.left.get_topleft(x+1)
		if self.top != None:
			return self.top.get_topleft(x+1)
		return self
	def get_width(self, first=None):
		'''
		Returns how many nodes are to the right of this node including this node
		'''
		if first == None:
			first = self
		if self.right == None or self.right == first:
			return 1
		return self.right.get_width(first) + 1
	def get_height(self, first=None):
		'''
		Returns how many nodes below this node including this node
		'''
		if first == None:
			first = self
		if self.bottom == None or self.bottom == first:
			return 1
		return self.bottom.get_height(first) + 1
	def compare(self, other):
		'''
		Compare this node with another node, determining how these two nodes are
		oriented with each other
		'''
		# Error if nodes have different sizes
		if self.image.height != other.image.height or self.image.width != other.image.width:
			print("Error! Size mismatch: {} and {}".format(self.fname, other.fname))
			sys.exit()
		w = self.image.width
		h = self.image.height
		pos_base = (0, 0)     # top-left corner
		pos_right = (w-1, 0)  # top-right corner
		pos_bottom = (0, h-1) # bottom-left corner
		size_h = (1, h) # 1px vertical line
		size_w = (w, 1) # 1px horizontal line
		# other | self
		if img_cmp(self.image, other.image, pos_base, pos_right, size_h):
			if (self.left != None and self.left != other) or (other.right != None and other.right != self):
				print("OOP LEFT")
			self.left = other
			other.right = self
		# self | other
		if img_cmp(self.image, other.image, pos_right, pos_base, size_h):
			if (self.right != None and self.right != other) or (other.left != None and other.left != self):
				print("OOP RIGHT")
			self.right = other
			other.left = self
		#  other
		# -------
		#   self
		if img_cmp(self.image, other.image, pos_base, pos_bottom, size_w):
			if (self.top != None and self.top != other) or (other.bottom != None and other.bottom != self):
				print("OOP BOTTOM")
			self.top = other
			other.bottom = self
		#   self
		# -------
		#  other
		if img_cmp(self.image, other.image, pos_bottom, pos_base, size_w):
			if (self.bottom != None and self.bottom != other) or (other.top != None and other.top != self):
				print("OOP TOP")
			self.bottom = other
			other.top = self

def pick_files_auto(data, path):
	'''
	Automatically pick a bunch of files given that their seams match
	Any unused textures will be moved to a folder named 'unused_textures'

	data - StitchData to put textures into
	path - Base path of StitchData
	'''
	# Ask for a bunch of files
	file_path_list = tk_fd.askopenfilenames(\
		filetypes=VALID_FILES,\
		initialdir=path,\
		title='Select pictures')
	# Setup nodes
	imgnodes = {}
	for name in file_path_list:
		imgnodes[name] = ImageNode(name)
	for i in range(0, len(file_path_list)):
		iname = file_path_list[i]
		inode = imgnodes[iname]
		for j in range(i+1, len(file_path_list)):
			jname = file_path_list[j]
			jnode = imgnodes[jname]
			inode.compare(jnode)
	# Get topleft node
	base_node = next(iter(imgnodes.values())).get_topleft()
	node = base_node
	width = node.get_width()
	height = node.get_height()
	data.width = width
	data.tex_width = node.image.width-1
	data.tex_height = node.image.height-1
	# Iterate nodes and put into StitchData
	while node != None:
		xnode = node
		first_xnode = xnode
		for i in range(0, width):
			if xnode == None or (xnode == first_xnode and i != 0):
				print("Error: Width mismatch, expected {}, got {}".format(width, i+1))
				sys.exit()
			xnode.used = True
			file_path = os.path.relpath(xnode.fname, path)
			data.texlist.append(file_path)
			xnode = xnode.right
		if xnode != None and xnode != first_xnode:
			print("Error: Width mismatch, expected {}, got {}".format(width, width+1))
			sys.exit()
		node = node.bottom
	# Move unused textures into 'unused_textures' folder
	made_dir = False
	for n in imgnodes.values():
		if not n.used:
			if not made_dir:
				os.makedirs(os.path.join(path, "unused_textures"), exist_ok=True)
				made_dir = True
			base = os.path.basename(n.fname)
			outname = os.path.join(path, "unused_textures", base)
			shutil.move(n.fname, outname)

def stitch_new(path, args, auto=False):
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
	data.output = tk_fd.asksaveasfilename(\
		initialdir = path,\
		title      = "Output should be saved as:",\
		filetypes  = VALID_FILES)
	data.output = os.path.relpath(data.output, path)
	# Get files
	if auto:
		pick_files_auto(data, path)
	else:
		pick_files_individual(data, path)
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
	image = ret = Image.new('RGBA', (outwidth, outheight), (0,0,0,0))
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
		cropped = image.crop((cx,cy,min(cx+cw, image.width),min(cy+ch, image.height)))
		part.paste(cropped, (1, 0))
		part.paste(cropped, (0, 0))
		part.save(fname)
		x += 1
		if x >= data.width:
			x = 0
			y += 1
	print("Finished unpacking")

def stitch_help():
	'''
	Help! I need sombody, help!
	'''
	print("This is a Texture stitching program.")
	print("It's useful for Nintendo 64 repaints.")
	print("")
	print("Commands:")
	print("stitch new {filename}       Create a new stitch file")
	print("stitch auto {filename}      Create a new stitch file automatically")
	print("stitch pack {filename}      Pack multiple images into a single image")
	print("stitch unpack {filename}    Unpack a stitched image into multiple images")
	print("")
	print("Auto stitch creation requires the given textures to have matching edges.")
	print("Any textures given to auto that aren't in the output image will be moved to a")
	print("new folder named 'unused_textures.'")

def main(args):
	base_path = os.getcwd()
	if len(args) < 2:
		stitch_help()
	else:
		fname = args[1]
		passed_args = args[2:]
		if fname in ["new", "create", "make"]:
			stitch_new(base_path, passed_args, auto=False)
		elif fname in ["autonew", "automake", "autocreate", "auto"]:
			stitch_new(base_path, passed_args, auto=True)
		elif fname in ["pack", "merge"]:
			stitch_pack(base_path, passed_args)
		elif fname in ["unpack", "extract"]:
			stitch_unpack(base_path, passed_args)
		elif fname in ["help", None]:
			stitch_help()
		else:
			print("Not a valid command.")

if __name__ == "__main__":
   main(sys.argv[:])
