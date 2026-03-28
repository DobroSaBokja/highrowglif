from rich import print
import mimetypes
import subprocess
import os

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

def copy_image_to_clipboard(path):
    mime, _ = mimetypes.guess_type(path)

    if os.environ.get("WAYLAND_DISPLAY"):
        tool = ["wl-copy", "--type", mime]
    else:
        tool = ["xclip", "-selection", "clipboard", "-t", mime, "-i"]
    with open(path, "rb") as f:
        subprocess.run(tool, stdin=f)