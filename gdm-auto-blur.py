#!/usr/bin/env python3

import os
import sys
import argparse
import textwrap
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
        usage='%(prog)s [-h] [-u] -i INPUT [-o OUTPUT] [-br BRIGHTNESS] [-b BLUR] [-p] [-d]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''
        Sets GDM background image while blurring it and changing brightness.
        Works well with \'Blur my Shell\' extension (https://github.com/aunetx/blur-my-shell)
        
        \'gdm-tools\' are required! (https://github.com/realmazharhussain/gdm-tools)
        '''))
    parser.add_argument('-u', action='store_true',
                        help='unset background image (set gray background)')
    parser.add_argument('-i', '--input', type=str,
                        required=('-u' not in sys.argv), help='specify the path of the image')
    parser.add_argument('-o', '--output', type=str,
                        help='specify output image directory (with a file name or without); input image directory by default')
    parser.add_argument('-br', '--brightness', type=float,
                        help='change brightness; from 0.00 to 1.00 and above')
    parser.add_argument('-b', '--blur', type=float,
                        help='change \'sigma\' parameter of gaussian blur (radius); from 0 to 50 and above')
    parser.add_argument('-p', '--preview', action='store_true',
                        help='preview an image without setting it as background (saves processed image)')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='delete output image after gdm background is set')

    return parser.parse_args()


def main():
    try:
        args = parse_args()

        # Unset image and exit
        if args.u:
            cmd = f'set-gdm-theme set -b none'
            print(f'Unsetting image, running \'{cmd}\'')
            os.system(cmd)
            return

        # Open image
        img_path = Path(args.input)
        img = Image.open(img_path)

        # Analyze output path
        if type(args.output) is NoneType:
            output_path = img_path.parent
        else:
            output_path = Path(args.output)

        if output_path.is_dir():
            output_path = output_path / f'{img_path.stem}-blur.png'
        else:
            output_path = output_path.with_suffix('.png')

        # Read amount of brightness and blur
        if type(args.brightness) is NoneType:
            brightness = BRIGHTNESS
        else:
            brightness = args.brightness

        if type(args.blur) is NoneType:
            blur = round(BLUR / 1920 * img.size[0])
        else:
            blur = round(args.blur / 1920 * img.size[0])

        # Apply filters
        img = img.filter(ImageFilter.GaussianBlur(radius=blur))
        img = img.filter(ImageFilter.SMOOTH_MORE)
        img_obj = ImageEnhance.Brightness(img)
        img = img_obj.enhance(brightness)

        # Save image and run a command
        img.save(output_path)

        # Preview the image
        if args.preview:
            os.system(f'xdg-open {output_path}')
            return

        cmd = f'set-gdm-theme set -b \'{output_path}\''
        print(f'Image saved as \'{output_path}\'')
        print(f'Parameters: brightness: {brightness}, blur: {blur}')
        print(f'Running \"{cmd}\"')

        os.system(cmd)

        # Optionally delete the image
        if args.delete:
            print('Image deleted')
            output_path.unlink(missing_ok=True)

    except OSError as e:
        print(e)


if __name__ == '__main__':
    main()
