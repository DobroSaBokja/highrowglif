from rich import print
import mimetypes
import subprocess
import os
import platform

def print_info(*args):
    print("[bold green][INFO]:[/bold green]", "[green]" + " ".join(str(a) for a in args) + "[/green]")

def print_error(*args):
    print("[bold red][ERROR]:[/bold red]", "[red]" + " ".join(str(a) for a in args) + "[/red]")

def print_warn(*args):
    print("[bold yellow][WARN]:[/bold yellow]", "[yellow]" + " ".join(str(a) for a in args) + "[/yellow]")

def is_image(path):
    mime, _ = mimetypes.guess_type(path)
    return mime is not None and mime.startswith("image/")

def run_fuzzy(items, tool, multi_flag=""):
    tool_parts = tool.split()
    if multi_flag:
        tool_parts.append(multi_flag)
    result = subprocess.run(tool_parts, input="\n".join(items), capture_output=True, text=True)
    return [line for line in result.stdout.splitlines() if line.strip()]

import platform
import subprocess

def copy_image_to_clipboard(path):
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "image/png"
    system = platform.system()
    if system == "Linux":
        if os.environ.get("WAYLAND_DISPLAY"):
            tool = ["wl-copy", "--type", mime]
        else:
            tool = ["xclip", "-selection", "clipboard", "-t", mime, "-i"]
        with open(path, "rb") as f:
            subprocess.run(tool, stdin=f)
    elif system == "Darwin":
        subprocess.run(["osascript", "-e", f'set the clipboard to (read (POSIX file "{path}") as JPEG picture)'])
    elif system == "Windows":
        from PIL import Image
        import io
        import win32clipboard
        img = Image.open(path)
        output = io.BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
