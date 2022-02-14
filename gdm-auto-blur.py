#!/usr/bin/env python3

import sys
import argparse
import textwrap
import tempfile
import subprocess
from pathlib import Path
from types import NoneType

try:
    from PIL import Image, ImageFilter, ImageEnhance

except ModuleNotFoundError as e:
    print(e)
    print('Please run \'pip3 install Pillow\'')
    sys.exit()

BRIGHTNESS = 0.5
BLUR = 20


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] [-u] [-i INPUT] [-br BRIGHTNESS] [-b BLUR] [-p]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''
        Sets GDM background image while blurring it and changing brightness.
        Works well with \'Blur my Shell\' extension (https://github.com/aunetx/blur-my-shell)
        
        \'gdm-tools\' are required! (https://github.com/realmazharhussain/gdm-tools)
        '''))
    parser.add_argument('-u', '--unset', action='store_true',
                        help='unset background image (set gray background)')
    parser.add_argument('-i', '--input', type=str,
                        help='specify the path of the image')
    parser.add_argument('-br', '--brightness', type=float,
                        help='change brightness; from 0.00 to 1.00 and above')
    parser.add_argument('-b', '--blur', type=float,
                        help='change \'sigma\' parameter of gaussian blur (radius); from 0 to 50 and above')
    parser.add_argument('-p', '--preview', action='store_true',
                        help='preview an image without setting it as background')

    return parser.parse_args()


def main():
    args = parse_args()

    # Unset image and exit
    if args.unset:
        cmd = f'set-gdm-theme set -b none'
        print(f'Unsetting image, running: {cmd}')
        subprocess.run(cmd.split())
        return

    # Open image
    if type(args.input) is NoneType:
        get_cmd = 'gsettings get org.gnome.desktop.background picture-uri'
        output = subprocess.run(
            get_cmd.split(), stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

        if output[1:8] == 'file://':
            img_path = Path(output[8:-1])
        else:
            print('Please set your wallpaper from gnome-settings')
            return

    else:
        img_path = Path(args.input)

    try:
        img = Image.open(img_path)
    except OSError as e:
        print(e)
        return

    temp = tempfile.NamedTemporaryFile(suffix='.png')
    output_path = temp.name

    # Read amounts of brightness and blur
    brightness = BRIGHTNESS if type(args.brightness) is NoneType else args.brightness
    blur = round(BLUR if type(args.blur) is NoneType else args.blur / 1920 * img.size[0])

    # Apply filters
    img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img_obj = ImageEnhance.Brightness(img)
    img = img_obj.enhance(brightness)

    # Preview the image
    if args.preview:
        img.show()
        return

    # Save image and run a command
    img.save(output_path)

    set_cmd = f'set-gdm-theme set -b {output_path}'
    print(f'Parameters: brightness: {brightness}, blur: {blur}')
    print(f'Running: {set_cmd}')

    subprocess.run(set_cmd.split())

if __name__ == '__main__':
    main()
