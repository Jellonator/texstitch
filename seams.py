import os
import sys
import shutil
import itertools

from PIL import Image
from tkinter import filedialog as tk_fd
import util


def img_cmp(img1, img2, pos1, pos2, size):
    '''
    Compare sections two images and return if their pixels exactly match

    pos1 - top-left position of the first image to compare with
    pos2 - top-left position of the second image to compare with
    size - size of the section to compare

    Example: img_cmp(img1, img2, (0, 0), (6, 6), (4, 4)) will compare a 4x4
    area of img1 whose top-left position is (0, 0) with a 4x4 area of img2
    whose top-left position is (6, 6)
    '''
    px1 = img1.load()
    px2 = img2.load()
    for ix in range(size[0]):
        for iy in range(size[1]):
            a = px1[pos1[0]+ix, pos1[1]+iy]
            b = px2[pos2[0]+ix, pos2[1]+iy]
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
        if self.left is not None:
            return self.left.get_topleft(x+1)
        if self.top is not None:
            return self.top.get_topleft(x+1)
        return self

    def get_width(self, first=None):
        '''
        Returns how many nodes are to the right of this node including this
        node
        '''
        if first is None:
            first = self
        if self.right is None or self.right == first:
            return 1
        return self.right.get_width(first) + 1

    def get_height(self, first=None):
        '''
        Returns how many nodes below this node including this node
        '''
        if first is None:
            first = self
        if self.bottom is None or self.bottom == first:
            return 1
        return self.bottom.get_height(first) + 1

    def compare(self, other):
        '''
        Compare this node with another node, determining how these two nodes
        are oriented with each other
        '''
        # Error if nodes have different sizes
        if self.image.height != other.image.height\
                or self.image.width != other.image.width:
            print("Error! Size mismatch: {} and {}"
                  .format(self.fname, other.fname))
            sys.exit()
        w = self.image.width
        h = self.image.height
        pos_base = (0, 0)      # top-left corner
        pos_right = (w-1, 0)   # top-right corner
        pos_bottom = (0, h-1)  # bottom-left corner
        size_h = (1, h)  # 1px vertical line
        size_w = (w, 1)  # 1px horizontal line
        # other | self
        if img_cmp(self.image, other.image, pos_base, pos_right, size_h):
            if (self.left is not None and self.left != other) or\
                    (other.right is not None and other.right != self):
                print("OOP LEFT")
            self.left = other
            other.right = self
        # self | other
        if img_cmp(self.image, other.image, pos_right, pos_base, size_h):
            if (self.right is not None and self.right != other) or\
                    (other.left is not None and other.left != self):
                print("OOP RIGHT")
            self.right = other
            other.left = self
        #  other
        # -------
        #   self
        if img_cmp(self.image, other.image, pos_base, pos_bottom, size_w):
            if (self.top is not None and self.top != other) or\
                    (other.bottom is not None and other.bottom != self):
                print("OOP BOTTOM")
            self.top = other
            other.bottom = self
        #   self
        # -------
        #  other
        if img_cmp(self.image, other.image, pos_bottom, pos_base, size_w):
            if (self.bottom is not None and self.bottom != other) or\
                    (other.top is not None and other.top != self):
                print("OOP TOP")
            self.bottom = other
            other.top = self


def compare_image_nodes(imgnodes):
    for k1, k2 in itertools.combinations(imgnodes, 2):
        n1 = imgnodes[k1]
        n2 = imgnodes[k2]
        n1.compare(n2)


def move_unused_nodes(imgnodes, target):
    made_dir = False
    for n in imgnodes.values():
        if not n.used:
            if not made_dir:
                os.makedirs(target,
                            exist_ok=True)
                made_dir = True
            base = os.path.basename(n.fname)
            outname = os.path.join(target, base)
            shutil.move(n.fname, outname)


def put_nodes_into_data(imgnodes, data, path):
    # Get topleft node
    base_node = next(iter(imgnodes.values())).get_topleft()
    node = base_node
    width = node.get_width()
    data.width = width
    data.tex_width = node.image.width-1
    data.tex_height = node.image.height-1
    # Iterate nodes and put into StitchData
    while node is not None:
        xnode = node
        first_xnode = xnode
        for i in range(0, width):
            if xnode is None or (xnode == first_xnode and i != 0):
                print("Error: Width mismatch, expected {}, got {}"
                      .format(width, i+1))
                sys.exit()
            xnode.used = True
            file_path = os.path.relpath(xnode.fname, path)
            data.texlist.append(file_path)
            xnode = xnode.right
        if xnode is not None and xnode != first_xnode:
            print("Error: Width mismatch, expected {}, got {}"
                  .format(width, width+1))
            sys.exit()
        node = node.bottom


def pick_files_auto(data, path):
    '''
    Automatically pick a bunch of files given that their seams match
    Any unused textures will be moved to a folder named 'unused_textures'

    data - StitchData to put textures into
    path - Base path of StitchData
    '''
    # Ask for a bunch of files
    file_path_list = tk_fd.askopenfilenames(
        filetypes=util.FILES_IMG,
        initialdir=path,
        title='Select pictures')
    # Setup nodes
    imgnodes = {}
    for name in file_path_list:
        imgnodes[name] = ImageNode(name)
    compare_image_nodes(imgnodes)
    put_nodes_into_data(imgnodes, data, path)
    # Move unused textures into 'unused_textures' folder
    move_unused_nodes(imgnodes, os.path.join(path, 'unused_textures'))
