import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gdk

from enum import Enum

FSTYPE_COLORS_RGBA = {
    "vfat": Gdk.RGBA(0.12, 0.58, 0.95, 1.0),
    "btrfs": Gdk.RGBA(0.18, 0.80, 0.44, 1.0),
    "ext4": Gdk.RGBA(0.95, 0.76, 0.23, 1.0),
    "swap": Gdk.RGBA(0.60, 0.40, 0.80, 1.0),
    "unknown": Gdk.RGBA(0.6, 0.6, 0.6, 1.0),
    "ntfs": Gdk.RGBA(0.85, 0.25, 0.25, 1.0),
    None: Gdk.RGBA(0.6, 0.6, 0.6, 1.0),
    "selected": Gdk.RGBA(0.54, 0.17, 0.89, 1.0)
}

FSTYPE_COLOR_CLASSES = {
    'ext4': 'color-ext4',
    'ext3': 'color-ext4',
    'ext2': 'color-ext4',
    'ntfs': 'color-ntfs',
    'fat32': 'color-fat32',
    'vfat': 'color-vfat',
    'fat': 'color-fat32',
    'swap': 'color-swap',
    'linux-swap': 'color-swap',
    '': 'color-unknown',
    None: 'color-unknown',
}

class PartitioningMode(Enum):
    INSTALL_ALONGSIDE = "install_alongside"
    REPLACE_PARTITION = "replace_partition"
    ERASE_DISK = "erase_disk"
    MANUAL_PARTITIONING = "manual_partitioning"
    NONE = "none"