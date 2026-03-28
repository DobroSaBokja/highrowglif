# highrowglif, a shrimple way to store memes
highrowglif is a simple way to store images (and other files in the future) by
applying tags to them. Later, you can fuzzy-find through the tags (with fuzzle by default)
and copy the image you like, to your clipboard.
## Instalation
Clone the repo
```
git clone https://github.com/DobroSaBokja/highrowglif.git
```
Thats basicaly it, just run ```python main.py``` to start the program
### Dependencies
- a fuzzy-find tool - can be ```fzf```, ```rofi```, ```wofi```, ```fuzzel```...
- python-rich
- python-pillow

## Configuration
The main config file is in ```$XDG_CONFIG_HOME/highrowglif/config.toml``` by default.
There is only a couple of things you can change right now, more features coming later!
