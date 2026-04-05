import sqlite3
import shutil
import subprocess
import mimetypes
from pathlib import Path
import os
import sys
import tomllib

from rich import print

import lib

args = sys.argv[1:]

subcommand = ""
arguments = []
flags = []

for arg in args:
    if arg.startswith("--"):
        flags.append(arg)
    elif subcommand == "":
        subcommand = arg
    else:
        arguments.append(arg)

config_dir = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser() / "highrowglif"

# --- CONFIG ---
OPERATING_DIRECTORY = Path("~/Pictures/highrowglif-managed").expanduser()
FUZZY_FIND_TOOL = "fuzzel --dmenu"
FUZZY_FIND_MULTI_FLAG = ""
CLIPBOARD_TOOL = "wl-copy"

if not config_dir.exists():
    lib.print_warn("Config directory not created, using default config...")
elif not (config_dir / "config.toml").exists():
    lib.print_warn("Main config file not created, using default config...")
else:
    with open(config_dir / "config.toml", "rb") as f:
        config = tomllib.load(f)
        
        if "main" in config:
            main = config["main"]
            for key, value in main.items():
                match key:
                    case "operating_directory": OPERATING_DIRECTORY = Path(value).expanduser()
                    case "fuzzy_find_tool": FUZZY_FIND_TOOL = value
                    case "fuzzy_find_multi_tag": FUZZY_FIND_MULTI_FLAG = value
                    case "clipboard_tool": CLIPBOARD_TOOL = value
 
if not OPERATING_DIRECTORY.exists() and not "--create-directories" in flags:
    lib.print_error("Operating directory doesn't exist! Default is: ~/Pictures/highrowglif-managed. \n Edit the config to override.")    
    exit(1)

elif not OPERATING_DIRECTORY.exists():
    lib.print_warn("Operating directory doesn't exist! Creating it... (--create-directories is set)")
    OPERATING_DIRECTORY.mkdir(parents=True)

if not Path(OPERATING_DIRECTORY / "database.db").exists():
    lib.print_info("Database not initialized in", str(OPERATING_DIRECTORY) + ",", "creating it")

conn = sqlite3.connect(OPERATING_DIRECTORY / "database.db")

cursor = conn.cursor()

cursor.executescript('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        filename TEXT
    );
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS image_tags (
        image_id INTEGER,
        tag_id INTEGER
    );
''')

match subcommand:
    case "add":
        file = Path(arguments[0])
        if not file.exists():
            lib.print_error("No file at specified path")
            exit(1)

        if not lib.is_image(file):
            lib.print_error("File is not an image")
            exit(1)

        cursor.execute("SELECT name FROM tags")
        all_tags = [row[0] for row in cursor.fetchall()]

        if FUZZY_FIND_MULTI_FLAG:
            selected_tags = lib.run_fuzzy(all_tags, FUZZY_FIND_TOOL, FUZZY_FIND_MULTI_FLAG)
        else:
            selected_tags = []
            remaining_tags = all_tags[:]
            while True:
                choice = lib.run_fuzzy(["END"] + remaining_tags, FUZZY_FIND_TOOL)
                if not choice or choice[0] == "END":
                    break
                tag = choice[0]
                selected_tags.append(tag)
                if tag in remaining_tags:
                    remaining_tags.remove(tag)

        dest = OPERATING_DIRECTORY / file.name
        if dest.exists():
            lib.print_error("A file with that name already exists in the operating directory")
            exit(1)
        
        copy_flag = False

        try:
            shutil.move(str(file), dest)
        except PermissionError:
            copy_flag = True

            lib.print_warn("Permission denied, will copy instead of move")
            shutil.copy2(str(file), dest)

        cursor.execute("INSERT INTO images (filename) VALUES (?)", (file.name,))
        image_id = cursor.lastrowid

        for tag in selected_tags:
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
            tag_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO image_tags VALUES (?, ?)", (image_id, tag_id))

        conn.commit()
        if not copy_flag: lib.print_info("File moved successfully")
        else: lib.print_info("File copied successfully")

    case "tag":
        cursor.execute("SELECT filename FROM images")
        all_filenames = [row[0] for row in cursor.fetchall()]

        if not all_filenames:
            lib.print_warn("No images in database")
            exit(0)

        choice = lib.run_fuzzy(all_filenames, FUZZY_FIND_TOOL)
        if not choice:
            exit(0)
        filename = choice[0]

        cursor.execute("SELECT id FROM images WHERE filename = ?", (filename,))
        row = cursor.fetchone()
        if row is None:
            lib.print_error("File not found in database")
            exit(1)
        image_id = row[0]

        cursor.execute("SELECT name FROM tags")
        all_tags = [row[0] for row in cursor.fetchall()]

        if FUZZY_FIND_MULTI_FLAG:
            selected_tags = lib.run_fuzzy(all_tags, FUZZY_FIND_TOOL, FUZZY_FIND_MULTI_FLAG)
        else:
            selected_tags = []
            remaining_tags = all_tags[:]
            while True:
                choice = lib.run_fuzzy(["END"] + remaining_tags, FUZZY_FIND_TOOL)
                if not choice or choice[0] == "END":
                    break
                tag = choice[0]
                selected_tags.append(tag)
                if tag in remaining_tags:
                    remaining_tags.remove(tag)

        cursor.execute("DELETE FROM image_tags WHERE image_id = ?", (image_id,))

        for tag in selected_tags:
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
            tag_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO image_tags VALUES (?, ?)", (image_id, tag_id))

        conn.commit()
        lib.print_info("Tags updated for", filename)

    case "remove":
        cursor.execute("SELECT filename FROM images")
        all_filenames = [row[0] for row in cursor.fetchall()]

        if not all_filenames:
            lib.print_warn("No images in database")
            exit(0)

        choice = lib.run_fuzzy(all_filenames, FUZZY_FIND_TOOL)
        if not choice:
            exit(0)
        filename = choice[0]

        cursor.execute("SELECT id FROM images WHERE filename = ?", (filename,))
        row = cursor.fetchone()

        file_exists_in_database = row is not None

        if not file_exists_in_database:
            lib.print_warn("File not found in database. Still will try to remove it from operating directory")
        else:
            image_id = row[0]
            cursor.execute("DELETE FROM image_tags WHERE image_id = ?", (image_id,))
            cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
            conn.commit()

        file = OPERATING_DIRECTORY / filename

        if not file.exists():
            if file_exists_in_database:
                lib.print_info("File removed from database successfully")
            else:
                lib.print_error("File not found in database or operating directory")
                exit(1)
        else:
            file.unlink()
            lib.print_info("File removed successfully")

    case "":
        cursor.execute("SELECT name FROM tags")
        all_tags = [row[0] for row in cursor.fetchall()]

        if not all_tags:
            lib.print_warn("No tags in database")
            exit(0)

        if FUZZY_FIND_MULTI_FLAG:
            selected_tags = lib.run_fuzzy(all_tags, FUZZY_FIND_TOOL, FUZZY_FIND_MULTI_FLAG)
        else:
            selected_tags = []
            remaining_tags = all_tags[:]
            while remaining_tags:
                choice = lib.run_fuzzy(["END"] + remaining_tags, FUZZY_FIND_TOOL)
                if not choice or choice[0] == "END":
                    break
                selected_tags.append(choice[0])
                if choice[0] in remaining_tags:
                    remaining_tags.remove(choice[0])

        if selected_tags:
            placeholders = ",".join("?" * len(selected_tags))
            cursor.execute(f"""
                SELECT DISTINCT i.filename FROM images i
                JOIN image_tags it ON i.id = it.image_id
                JOIN tags t ON it.tag_id = t.id
                WHERE t.name IN ({placeholders})
                GROUP BY i.id
                HAVING COUNT(DISTINCT t.id) = ?
            """, (*selected_tags, len(selected_tags)))
        else:
            cursor.execute("SELECT filename FROM images")

        filenames = [row[0] for row in cursor.fetchall()]

        if not filenames:
            lib.print_warn("No images found for selected tags")
            exit(0)

        choice = lib.run_fuzzy(filenames, FUZZY_FIND_TOOL)
        if not choice:
            exit(0)

        image_path = OPERATING_DIRECTORY / choice[0]
        
        lib.copy_image_to_clipboard(image_path)

        lib.print_info("Copied", choice[0], "to clipboard")
    
    case "help":
        print("""
[bold]highrowglif[/bold] — image manager

[bold]Usage:[/bold]
  highrowglif [bold]add[/bold] <file>       Move an image into the library and tag it
  highrowglif [bold]tag[/bold]              Re-tag an image (replaces existing tags)
  highrowglif [bold]remove[/bold]           Remove an image from the library and database
  highrowglif [bold]help[/bold]             Show this help message
  highrowglif                  Browse images by tag and copy to clipboard

[bold]Flags:[/bold]
  [bold]--create-directories[/bold]         Create the operating directory if it doesn't exist

[bold]Config:[/bold] ~/.config/highrowglif/config.toml
""")
