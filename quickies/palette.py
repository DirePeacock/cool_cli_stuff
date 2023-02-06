import os
from PIL import Image
import pathlib
import sys
import argparse

test_img = pathlib.Path("E:\\pics\\reference\\trythis\\styleboard\\FF_tactics.png")
_default_palette = pathlib.Path(__file__).parent.joinpath("old_windows_palette.png")


def rgba_distance(left, right):
    """return the distance between two colors"""
    return sum([abs(left[i] - right[i]) for i in range(3)])


def new_image_file_path(palette, image):
    """return a new file path for the image
    new name is the image name + _ + palette name
    in the same directory as the image
    """
    palette_ = pathlib.Path(palette)
    image_ = pathlib.Path(image)
    new_name = image_.stem + "_" + palette_.stem + image_.suffix
    return image_.parent.joinpath(new_name)


class PaletteApplier:
    def __init__(self, palette, image, output=None):
        self.palette = palette
        self.colors = []
        self.image_path = image
        self.image = None
        self.output = (
            output
            if output is not None
            else new_image_file_path(self.palette, self.image_path)
        )

    def main(self, *args, **kwargs):
        """main function"""
        self._load_palette(self.palette)
        self._load_image()
        self.apply_palette()
        self.save_image()

    def get_path(self, path):
        """get the path to the file"""
        return pathlib.Path(path)

    def _load_palette(self, image_arg):
        """open image file to rgba list"""
        with Image.open(image_arg) as image_obj:
            for x in range(0, image_obj.width):
                for y in range(0, image_obj.height):
                    pixel = image_obj.getpixel((x, y))
                    if pixel[3] == 0:
                        continue
                    new_pixel = (pixel[0], pixel[1], pixel[2], 255)
                    if new_pixel not in self.colors:
                        self.colors.append(new_pixel)

    def _load_image(self):
        """open image as rgba mode image"""
        # with Image.open(
        #     "E:\\pics\\reference\\trythis\\styleboard\\FF_tactics.png"
        # ) as image_obj:
        with Image.open(self.image_path) as image_obj:
            self.image = image_obj.convert("RGBA")

    def apply_palette(self):
        """iterate over the image and replace each pixel with the nearest color in the palette"""
        for y in range(self.image.height):
            for x in range(self.image.width):
                pixel = self.image.getpixel((x, y))

                if pixel[3] == 0:
                    continue
                new_color = self.find_nearest_color(pixel)
                i = x * y + x
                end = self.image.width * self.image.height
                percent = 100 * i / end
                print(f"%{percent}")
                # os.system("clear")
                self.image.putpixel((x, y), new_color)

    def save_image(self):
        """save the new_image to the output path"""
        if not self.output:
            self.output = new_image_file_path(self.palette, self.image_path)
        self.image.save(self.output)

    def find_nearest_color(self, color):
        """find the nearest color in the palette to the given color"""
        nearest_color = self.colors[0]
        nearest_distance = rgba_distance(nearest_color, color)
        for palette_color in self.colors:
            distance = rgba_distance(palette_color, color)
            if distance < nearest_distance:
                nearest_color = palette_color
                nearest_distance = distance

        return (nearest_color[0], nearest_color[1], nearest_color[2], color[3])


def parse_args(args_):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--palette", type=str, default=_default_palette, help="basic argument"
    )
    parser.add_argument(
        "-i",
        "--image",
        type=str,
        default=test_img,
        help="image path to apply palette to",
    )
    parser.add_argument("-o", "--output", default=None, help="output path for image")
    return parser.parse_args(args_)


def main(args):
    print(__file__, args.__dict__)
    runner = PaletteApplier(args.palette, args.image, args.output)
    runner.main()


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
