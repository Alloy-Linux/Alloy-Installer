import subprocess
import backend.data as data

def create_config():
    subprocess.run(["sudo", "nixos-generate-config", "--root", "/mnt"], check=True)
    subprocess.run(["sudo", "rm", "-f", "/mnt/etc/nixos/configuration.nix"], check=True)

    subprocess.run(["sudo", "cp", "/mnt/etc/nixos/hardware-configuration.nix", "default-config/profile/home/hardware.nix"], check=True)
    subprocess.run(["sudo", "cp", "/mnt/etc/nixos/hardware-configuration.nix", "default-config/profile/workstation/hardware.nix"], check=True)

    match data.desktop_environment.lower():
        case "gnome":
            to_remove = ["cinnamon", "cosmic", "plasma", "xfce", "lxqt", "budgie", "mate", "deepin", "pantheon"]
        case "kde":
            to_remove = ["cinnamon", "cosmic", "gnome", "xfce", "lxqt", "budgie", "mate", "deepin", "pantheon"]
        case "xfce":
            to_remove = ["cinnamon", "cosmic", "gnome", "plasma", "lxqt", "budgie", "mate", "deepin", "pantheon"]
        case "cinnamon":
            to_remove = ["gnome", "cosmic", "plasma", "xfce", "lxqt", "budgie", "mate", "deepin", "pantheon"]
        case "cosmic":
            to_remove = ["cinnamon", "gnome", "plasma", "xfce", "lxqt", "budgie", "mate", "deepin", "pantheon"]
        case "lxqt":
            to_remove = ["cinnamon", "cosmic", "gnome", "plasma", "xfce", "budgie", "mate", "deepin", "pantheon"]
        case "budgie":
            to_remove = ["cinnamon", "cosmic", "gnome", "plasma", "xfce", "lxqt", "mate", "deepin", "pantheon"]
        case "mate":
            to_remove = ["cinnamon", "cosmic", "gnome", "plasma", "xfce", "lxqt", "budgie", "deepin", "pantheon"]
        case "deepin":
            to_remove = ["cinnamon", "cosmic", "gnome", "plasma", "xfce", "lxqt", "budgie", "mate", "pantheon"]
        case "pantheon":
            to_remove = ["cinnamon", "cosmic", "gnome", "plasma", "xfce", "lxqt", "budgie", "mate", "deepin"]
        case "no desktop":
            to_remove = ["cinnamon", "cosmic", "gnome", "plasma", "xfce", "lxqt", "budgie", "mate", "deepin", "pantheon"]
        case _:
            to_remove = []

    for de in to_remove:
        subprocess.run(["sudo", "rm", "-f", f"default-config/profile/workstation/{de}.nix"], check=True)

    update_desktop_import_path(data.desktop_environment.lower())
    subprocess.run(["sudo", "cp", "-r", "default-config/.", "/mnt/etc/nixos/"], check=True)



def update_desktop_import_path(desktop: str):
    display = data.display_server.lower()
    suffix = "-x11" if display == "x11" and desktop in ["gnome", "kde"] else ""
    path = f"../../modules/desktop/{desktop}{suffix}.nix"

    config_path = "default-config/profile/home/configuration.nix"
    with open(config_path, "r") as f:
        lines = f.readlines()

    with open(config_path, "w") as f:
        for line in lines:
            if line.strip().startswith("imports ="):
                f.write(f"  imports = [ {path} ];\n")
            else:
                f.write(line)