# highrowglif, a shrimple way to store memes
highrowglif is a simple way to store images (and other files in the future) by
applying tags to them. Later, you can fuzzy-find through the tags (with fuzzle by default)
and copy the image you like to your clipboard.
## Instalation
Run the install script:
```
curl -sSL https://raw.githubusercontent.com/DobroSaBokja/highrowglif/refs/heads/main/install.sh | bash
```
The defualt install script installs the Python project to ```/usr/local/lib/highrowglif``` and the wrapper to ```/usr/local/bin/highrowglif```, which should be in path.
Alternatively, you can git clone the repository:
```
git clone https://github.com/DobroSaBokja/highrowglif.git
```
and move it where you want it to live.
### Dependencies
- a fuzzy-find tool - can be ```fzf```, ```rofi```, ```wofi```, ```fuzzel```...
- python-rich
- python-pillow

## Configuration
The main config file is in ```$XDG_CONFIG_HOME/highrowglif/config.toml```, which fallbacks to ```~/.config/highrowglif/config.toml```.
There is only a couple of things you can change right now, more features coming later!
