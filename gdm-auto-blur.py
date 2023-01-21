#!/usr/bin/env python3

import sys
import argparse
import textwrap
import tempfile
import subprocess
from pathlib import Path

try:
    # Python 3.10+
    from types import NoneType
except:
    NoneType = type(None)

try:
    from PIL import Image, ImageFilter, ImageEnhance
except ModuleNotFoundError as e:
    print(e)
    print('Please run \'pip3 install Pillow\'')
    sys.exit()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] [-u] [-i INPUT] [-br BRIGHTNESS] [-b BLUR] [-p]',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''
        Blurs and sets gdm background.
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
        print('Unsetting image')
        subprocess.run(['set-gdm-theme', 'set', '-b', 'none'])
        return

    # Open image
    if type(args.input) is NoneType:
        get_cmd = ['gsettings', 'get', 'org.gnome.desktop.background', 'picture-uri']
        output = subprocess.run(get_cmd, stdout=subprocess.PIPE, text=True).stdout.strip()

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

    print(f'Using image \'{img_path}\'')

    temp = tempfile.NamedTemporaryFile(suffix='.png')
    output_path = temp.name

    # Determine which values to use
    if type(args.brightness) is not NoneType and type(args.blur) is not NoneType:
        brightness = args.brightness
        blur = args.blur
    
    else:
        base_cmd = 'gsettings --schemadir ~/.local/share/gnome-shell/extensions/blur-my-shell@aunetx/schemas/ get org.gnome.shell.extensions.blur-my-shell'
        sigma_cmd = base_cmd + ' sigma'
        brightness_cmd = base_cmd + ' brightness'

        try:
            brightness = float(subprocess.run(brightness_cmd, stdout=subprocess.PIPE, shell=True, text=True).stdout.strip())
            blur = float(subprocess.run(sigma_cmd, stdout=subprocess.PIPE, shell=True, text=True).stdout.strip())
        except ValueError:
            print(f'\'blur-my-shell\' is not installed, using other values')
            brightness = 0.5
            blur = 20

    if type(args.brightness) is not NoneType:
        brightness = args.brightness

    if type(args.blur) is not NoneType:
        blur = args.blur
    
    print(f'Parameters: brightness: {brightness}, blur: {round(blur, 3)}')

    # Determine screen size
    import tkinter
    root = tkinter.Tk()
    root.withdraw()
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    
    # Resize image (to apply filters properly)
    if screen_width > screen_height:
        proportional_width = round(screen_height * img.size[0] / img.size[1])
        img = img.resize((proportional_width, screen_height))
        img = img.crop((round(proportional_width / 2 - screen_width / 2), 0, round(proportional_width / 2 + screen_width / 2), screen_height))

    # Apply filters
    img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img_obj = ImageEnhance.Brightness(img)
    img = img_obj.enhance(brightness)

    # Preview the image if needed
    if args.preview:
        img.show()
        return

    # Save image and run a command
    img.save(output_path)

    subprocess.run(['set-gdm-theme', 'set', '-b', output_path])

    print('Done!')

if __name__ == '__main__':
    main()
