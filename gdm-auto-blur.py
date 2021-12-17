#!/usr/bin/env python3

import os, sys, argparse, textwrap
from pathlib import Path
from types import NoneType

try:
    from PIL import Image, ImageFilter, ImageEnhance
    from PIL import UnidentifiedImageError
except ModuleNotFoundError as e:
    print(e)
    print('Please run \'pip3 install Pillow\'')
    sys.exit()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] [-r] -i INPUT [-o OUTPUT] -br BRIGHTNESS -b BLUR [-d]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''
        \'gdm-tools\' are required! (https://github.com/realmazharhussain/gdm-tools)

        Sets GDM background image adding blur and changing brightness.
        Works well with \'Blur my Shell\' extension (https://github.com/aunetx/blur-my-shell)
        '''),
        epilog='Parameters correspond to \'Blur my Shell\' ones, however additional tweaking may be needed')
    parser.add_argument('-u', action='store_true', help='unset background image (set gray background)')
    parser.add_argument('-i', '--input', type=str, required=('-u' not in sys.argv), help='specify the path of the image')
    parser.add_argument('-o', '--output', type=str, help='specify output image directory (with a name or without); input image directory by default')
    parser.add_argument('-br', '--brightness', type=float, required=('-u' not in sys.argv), help='change brightness; from 0.00 to 1.00 and above')
    parser.add_argument('-b', '--blur', type=float, required=('-u' not in sys.argv), help='change \'sigma\' parameter of gaussian blur (radius); from 0 to 50 and above')
    parser.add_argument('-d', '--delete', action='store_true', help='delete output image after gdm background is set')

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

        # Open image and change cwd
        img_path = Path(args.PATH)
        img = Image.open(img_path)

        # Analyze output path
        if type(args.output) is NoneType:
            output_path = img_path.parent
        else:
            output_path = Path(args.output)

        if output_path.is_dir():
            output_path = output_path / f'{img_path.stem}-blur{img_path.suffix}'
        else:
            output_path = output_path.with_suffix(img_path.suffix)

        # Read amount of brightness and blur
        brightness = args.brightness
        blur = round(args.blur / 50 * 200)

        # Apply filters
        img = img.filter(ImageFilter.GaussianBlur(radius = blur))
        img = img.filter(ImageFilter.SMOOTH_MORE)
        img_obj = ImageEnhance.Brightness(img)
        img = img_obj.enhance(brightness)

        # Save image and run a command
        img.save(output_path)

        cmd = f'set-gdm-theme set -b {output_path}'
        print(f'Image saved as {output_path}, running \'{cmd}\'')

        os.system(cmd)

        if args.delete:
            print('Image deleted')
            output_path.unlink(missing_ok=True)

    except OSError as e:
        print(e)

if __name__ == '__main__':
    main()
