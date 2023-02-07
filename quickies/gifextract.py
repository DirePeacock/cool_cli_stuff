#! python
import sys
import os
import argparse
from PIL import Image
import pathlib


"""
Feb 2023
now you can call this script on an image, force frame disposal mode and also store as a texture png
"""

"""
copied & updated from https://gist.github.com/BigglesZX/4016539

I searched high and low for solutions to the "extract animated GIF frames in Python"
problem, and after much trial and error came up with the following solution based
on several partial examples around the web (mostly Stack Overflow).

There are two pitfalls that aren't often mentioned when dealing with animated GIFs -
firstly that some files feature per-frame local palettes while some have one global
palette for all frames, and secondly that some GIFs replace the entire image with
each new frame ('full' mode in the code below), and some only update a specific
region ('partial').

This code deals with both those cases by examining the palette and redraw
instructions of each frame. In the latter case this requires a preliminary (usually
partial) iteration of the frames before processing, since the redraw mode needs to
be consistently applied across all frames. I found a couple of examples of
partial-mode GIFs containing the occasional full-frame redraw, which would result
in bad renders of those frames if the mode assessment was only done on a
single-frame basis.

Nov 2012
"""


def analyseImage(path):
    """
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    """
    im = Image.open(path)
    results = {
        "size": im.size,
        "mode": "full",
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results["mode"] = "partial"
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results


def processImageToTexture(path, partial=None, texture=True):
    """the same as the last one but it makes a texture instead of a sequence of images"""
    mode = analyseImage(path)["mode"]

    im = Image.open(path)

    i = 0
    p = im.getpalette()
    last_frame = im.convert("RGBA")
    if texture:
        new_size = (im.width * im.n_frames, im.height)
        new_image = Image.new("RGBA", new_size)
    good_job = False
    new_files = []
    try:
        while True:
            if not im.getpalette() and im.mode in ("L", "LA", "P", "PA"):
                im.putpalette(p)

            new_frame = Image.new("RGBA", im.size)

            if mode == "partial" and partial is None or partial:
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert("RGBA"))

            if texture:
                new_image.paste(new_frame, (i * im.width, 0))

            else:
                new_path = pathlib.Path(path).parent / f"{pathlib.Path(path).stem}-{i}.png"
                new_frame.save(new_path, "PNG")
                new_files.append(new_path)

            i += 1
            good_job = i >= im.n_frames

            last_frame = new_frame
            im.seek(im.tell() + 1)

    except EOFError:
        if good_job:
            print("good job, we got all the frames")
    if good_job and texture:
        new_path = pathlib.Path(path).parent / f"{pathlib.Path(path).stem}_texture.png"

        print(new_path)
        new_image.save(new_path, "PNG")
        new_files.append(new_path)
    for file in new_files:
        print(f"{file}")


test_img = "E:\\files\\cod\\vandal5\\src\\vandal5\\artassets\\crit_slash.gif"


def main(args):
    processImageToTexture(args.image, partial=args.partial, texture=(not args.seq))


def parse_args(args_):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--image",
        type=str,
        default=test_img,
        help="image path to apply palette to",
    )
    parser.add_argument("-s", "--seq", action="store_true", help="sequence of images")
    parser.add_argument("-p", "--partial", action="store_true", help="use partial replace mode")
    return parser.parse_args(args_)


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
