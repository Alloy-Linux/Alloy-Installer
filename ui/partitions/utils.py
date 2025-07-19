def get_os(fstype):
    if not fstype:
        return "Unknown"
    fstype_lower = fstype.lower()
    if fstype_lower == "ntfs":
        return "Windows"
    elif fstype_lower == "unknown":
        return "Unknown"
    else:
        return "Linux"

def human_readable_size(size_bytes):
    if size_bytes is None:
        return "N/A"
    size_bytes = int(size_bytes)
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f}KiB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f}MiB"
    elif size_bytes < 1024 ** 4:
        return f"{size_bytes / (1024 ** 3):.2f}GiB"
    else:
        return f"{size_bytes / (1024 ** 4):.2f}TiB"
