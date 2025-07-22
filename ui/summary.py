import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from slides import InstallerSlide
import backend.data as data
from ui.partitions.constants import PartitioningMode

def summary_slide(content_area, go_to_slide, app):
    title = Gtk.Label(label="Summary", css_classes=['title-1'])
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    main_box.append(title)
    
    def add_row(label_text, value):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label = Gtk.Label(label=label_text + ":", halign=Gtk.Align.START)
        value_label = Gtk.Label(label=value or "Not set", halign=Gtk.Align.START)
        value_label.set_hexpand(True)
        box.append(label)
        box.append(value_label)
        main_box.append(box)
    
    def get_partitioning_mode_display(mode):
        if mode == PartitioningMode.INSTALL_ALONGSIDE:
            return "Install alongside"
        elif mode == PartitioningMode.REPLACE_PARTITION:
            return "Replace a partition"
        elif mode == PartitioningMode.ERASE_DISK:
            return "Erase disk"
        elif mode == PartitioningMode.MANUAL_PARTITIONING:
            return "Manual partitioning"
        elif mode == PartitioningMode.NONE:
            return "Not set"
        else:
            return "Unknown"
    
    add_row("Location", data.location)
    add_row("Keyboard Layout", data.keyboard_layout)
    add_row("Keyboard Variant", data.keyboard_variant)
    add_row("Hostname", data.hostname)
    add_row("Username", data.username)
    add_row("Full Disk Encryption", "Enabled" if data.full_disk_encryption else "Disabled")
    
    if data.partitioning_mode:
        add_row("Partitioning Mode", get_partitioning_mode_display(data.partitioning_mode))
        add_row("Selected Disk", data.selected_disk)
        add_row("Selected Partition", data.selected_partition)
    
    add_row("Desktop Environment", data.desktop_environment)
    add_row("Display Server", data.display_server)
    
    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_box.set_halign(Gtk.Align.END)
    
    back_btn = Gtk.Button(label="Back")
    back_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.DESKTOP))
    
    next_btn = Gtk.Button(label="Install", css_classes=['suggested-action'])
    next_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.INSTALL))
    
    btn_box.append(back_btn)
    btn_box.append(next_btn)
    main_box.append(btn_box)
    
    content_area.append(main_box)