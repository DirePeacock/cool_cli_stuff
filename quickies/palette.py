#! python
import os
from PIL import Image
import pathlib
import sys
import argparse
import colorsys
import math

test_img = pathlib.Path("E:\\pics\\reference\\trythis\\styleboard\\FF_tactics.png")
_default_palette = pathlib.Path(__file__).parent.joinpath("old_windows_palette.png")


class rgba_distance:
    @classmethod
    def distance(cls, left, right):
        return sum([abs(left[i] - right[i]) for i in range(3)])


# def rgba_distance(left, right):
#     """return the distance between two colors"""
#     return sum([abs(left[i] - right[i]) for i in range(3)])


class hsv_distance:
    max_wieght = 255
    min_weight = 0

    hue_weight_multiplier = 1
    sat_weight_multiplier = 1
    val_weight_multiplier = 1
    weight_multipliers = [
        hue_weight_multiplier,
        sat_weight_multiplier,
        val_weight_multiplier,
    ]

    @classmethod
    def get_distances(cls, left, right):
        return [abs(left[i] - right[i]) for i in range(3)]

    @classmethod
    def get_weights(cls, left):
        # everytihng is a percent multiplier
        sat_weight = cls.get_sat_weight(left)
        val_weight = cls.get_val_weight(left)
        hue_weight = cls.get_hue_weight(left, val_weight, sat_weight)

        return (hue_weight, sat_weight, val_weight)

    @classmethod
    def get_hue_weight(cls, left, val_weight, sat_weight):
        """lower based on val weight and sat weight"""
        val_mod = 1 - val_weight
        sat_mod = 1 - sat_weight
        max_hue_weight = 1
        hue_weight = max_hue_weight * (val_mod + sat_mod) / 2
        return hue_weight / max_hue_weight

    @classmethod
    def get_sat_weight(cls, left):
        """"""
        return math.sqrt(left[1]) / math.sqrt(255)

    @classmethod
    def get_val_weight(cls, left):
        diff = abs(left[2] - 128)
        max_diff = 128
        return diff / max_diff

    @classmethod
    def distance(cls, left, right):
        weights = cls.get_weights(left)
        distances = cls.get_distances(left, right)
        total_distance = 0
        for i in range(3):
            total_distance += distances[i] * weights[i] * cls.weight_multipliers[i]

        return total_distance

    @classmethod
    def tests(cls):
        tests = {
            0: {
                "args": ((255)),
                "expected": (),
                "function": cls.get_weights,
            },
            # 1: {
            #     "args": (()),
            #     "expected": (),
            #     "function": cls.get_weights,
            # },
        }
        results = []
        for i in tests.keys():
            results.append(
                tests[i]["expected"] == tests[i]["function"](*tests[i]["args"])
            )


class PaletteApplier:
    def __init__(self, palette, image, output=None, using_hsv=False, normalize=False):
        self.using_hsv = True  # using_hsv
        self.palette = palette
        self.colors = []
        self.hsv_palette = []
        self.image_path = image
        self.image = None
        self.output = (
            output
            if output is not None
            else self.new_image_file_path(self.palette, self.image_path, self.using_hsv)
        )
        self.hash_table = {}

        self.num_px = 0
        self.i_px = 0
        self.percent_complete = 0

        self.hsv_image = None

    def new_image_file_path(self, palette, image, using_hsv=False):
        """return a new file path for the image
        new name is the image name + _ + palette name
        in the same directory as the image
        """
        palette_ = pathlib.Path(palette)
        image_ = pathlib.Path(image)
        hsv_string = "_hsv" if using_hsv else ""
        new_name = image_.stem + "_" + palette_.stem + hsv_string + image_.suffix
        return image_.parent.joinpath(new_name)

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
                    new_hsv = colorsys.rgb_to_hsv(pixel[0], pixel[1], pixel[2])
                    if new_pixel not in self.colors:
                        self.colors.append(new_pixel)
                    if new_hsv not in self.hsv_palette:
                        self.hsv_palette.append(new_hsv)

    def _load_image(self):
        """open image as rgba mode image"""
        with Image.open(self.image_path) as image_obj:
            self.image = image_obj.convert("RGBA")
            # self.hsv_image = image_obj.convert("HSV")
            self.num_px = self.image.width * self.image.height

    def apply_palette(self):
        """iterate over the image and replace each pixel with the nearest color in the palette"""
        for y in range(self.image.height):
            for x in range(self.image.width):
                pixel = self.image.getpixel((x, y))
                self.update_percent()
                if pixel[3] == 0:
                    continue
                # hsv_pixel = self.hsv_image.getpixel((x, y))
                new_color = self.find_nearest_color(pixel)

                self.image.putpixel((x, y), new_color)

    def update_percent(self):
        self.i_px += 1
        new_percent_complete = int(self.i_px / self.num_px * 100)
        if new_percent_complete > self.percent_complete:
            self.percent_complete = new_percent_complete
            print(f"%{self.percent_complete}")
            # os.system("clear")

    def save_image(self):
        """save the new_image to the output path"""
        if not self.output:
            self.output = self.new_image_file_path(
                self.palette, self.image_path, self.using_hsv
            )
        self.image.save(self.output)

    def find_nearest_color(self, color):
        """find the nearest color in the palette to the given color
        high or low brightness devalue the hue weight
        low saturation devalues the hue weight
        """
        this_color = color if not self.using_hsv else colorsys.rgb_to_hsv(*color[:3])

        if this_color in self.hash_table.keys():
            nearest_color = self.hash_table[this_color]
            return tuple(
                [nearest_color[0], nearest_color[1], nearest_color[2], color[3]]
            )

        this_palette = self.hsv_palette if self.using_hsv else self.colors
        color_distance_func = (
            rgba_distance.distance if not self.using_hsv else hsv_distance.distance
        )

        # find the color in the palette with the lowest distance
        nearest_color = this_palette[0]
        nearest_distance = color_distance_func(nearest_color, this_color)

        for i in range(1, len(this_palette)):
            palette_color = this_palette[i]
            distance = color_distance_func(palette_color, this_color)
            if distance < nearest_distance:
                nearest_color = palette_color
                nearest_distance = distance

        # convert back to rgba if needed
        nearest_color = (
            nearest_color if not self.using_hsv else colorsys.hsv_to_rgb(*nearest_color)
        )
        nearest_color = [math.floor(num) for num in nearest_color]

        self.hash_table[this_color] = nearest_color
        return tuple([nearest_color[0], nearest_color[1], nearest_color[2], color[3]])


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
    parser.add_argument(
        "-v", "--hsv", default=False, action="store_true", help="use hsv instead of rgb"
    )
    parser.add_argument(
        "-n",
        "--normalize",
        default=False,
        action="store_true",
        help="normalize to try and use more of the palette",
    )
    parser.add_argument("-o", "--output", default=None, help="output path for image")
    return parser.parse_args(args_)


def main(args):
    print(__file__, args.__dict__)
    runner = PaletteApplier(
        palette=args.palette, image=args.image, output=args.output, using_hsv=args.hsv
    )
    runner.main()


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
