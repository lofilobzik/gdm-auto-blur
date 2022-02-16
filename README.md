# gdm-auto-blur

Sets GDM background image while blurring it and changing brightness.

Works well with [Blur my Shell](https://github.com/aunetx/blur-my-shell) extension. (Brightness and blur parameters correnspond to 'Blur my Shell' ones. Not perfectly, however, but closely)

Until such feature is implemented in future releases of GDM or Gnome, this script serves as a nice workaround

## Requirements

- Python 3

- [Pillow](https://pypi.org/project/Pillow/)
```bash
pip install Pillow
```
- [gdm-tools](https://github.com/realmazharhussain/gdm-tools)

- blur-my-shell (optional)

- gsettings

## Installation

Download repo as a zip or clone it somewhere

```bash
git clone https://github.com/lofilobzik/gdm-auto-blur
```
Copy `gdm-auto-blur.py` script to `~/.local/bin/` and make it executable

```bash
cd gdm-auto-blur
cp gdm-auto-blur.py ~/.local/bin/gdm-auto-blur
cd ~/.local/bin/
chmod +x gdm-auto-blur
```

## Usage

Just run

```bash
gdm-auto-blur
```
With options

```bash
gdm-auto-blur -i path/to/picture.jpg -br 0.5 -b 20 -p
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
