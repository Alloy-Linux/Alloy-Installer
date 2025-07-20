import subprocess
import urllib.request
import socket

from gi.repository import Gtk, GLib

from slides import InstallerSlide


def has_internet(timeout=3):
    urllib.request.urlopen('https://www.google.com', timeout=timeout)
    return True


def create_network_widget(network):
    row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    row_box.set_margin_top(8)
    row_box.set_margin_bottom(8)
    row_box.set_margin_start(8)
    row_box.set_margin_end(8)

    signal = network['signal']
    if signal > 80:
        icon_name = "network-wireless-signal-excellent-symbolic"
    elif signal > 55:
        icon_name = "network-wireless-signal-good-symbolic"
    elif signal > 30:
        icon_name = "network-wireless-signal-ok-symbolic"
    else:
        icon_name = "network-wireless-signal-weak-symbolic"

    signal_icon = Gtk.Image.new_from_icon_name(icon_name)
    signal_icon.set_icon_size(Gtk.IconSize.LARGE)
    row_box.append(signal_icon)

    ssid_label = Gtk.Label()
    ssid_label.set_markup(f"<b>{GLib.markup_escape_text(network['ssid'])}</b>")
    ssid_label.set_xalign(0)
    ssid_label.set_hexpand(True)
    row_box.append(ssid_label)

    if network['in_use']:
        connected_icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
        connected_icon.set_halign(Gtk.Align.END)
        row_box.append(connected_icon)
    elif network['security'] != 'None':
        lock_icon = Gtk.Image.new_from_icon_name("network-wireless-encrypted-symbolic")
        lock_icon.set_halign(Gtk.Align.END)
        row_box.append(lock_icon)

    return row_box


def network_slide(content_area, go_to_slide):
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    status_label = Gtk.Label(label="Checking internet...")
    box.append(status_label)

    network_slide.has_connection = False

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_vexpand(True)
    box.append(scrolled_window)

    box_networks = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    scrolled_window.set_child(box_networks)

    def update_network_list():
        while child := box_networks.get_first_child():
            box_networks.remove(child)

        networks = get_placeholder_networks()

        if not networks:
            placeholder = Gtk.Label(label="No Wi-Fi networks found")
            placeholder.set_margin_top(24)
            placeholder.set_margin_bottom(24)
            box_networks.append(placeholder)
        else:
            for network in networks:
                network_widget = create_network_widget(network)
                box_networks.append(network_widget)

        scrolled_window.set_visible(True)

    def update_internet_status():
        connected = has_internet()
        network_slide.has_connection = connected
        status_label.set_label(
            "Internet connected" if connected else "No internet, please connect to a network.")
        update_network_list()
        return True

    update_internet_status()
    GLib.timeout_add_seconds(5, update_internet_status)

    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    back_btn = Gtk.Button(label="Back")
    back_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.WELCOME))

    next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
    next_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.LOCATION))

    btn_box.append(back_btn)
    btn_box.append(next_btn)

    box.append(btn_box)
    content_area.append(box)


def get_nearby_networks():
    result = subprocess.run("nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY device wifi list",
                            capture_output=True, text=True, shell=True, check=True)

    output_lines = result.stdout.strip().split('\n')

    networks = []
    for line in output_lines:
        parts = line.strip().split(':', 3)
        if len(parts) >= 4:
            network = {
                "in_use": parts[0] == '*',
                "ssid": parts[1] or "Hidden Network",
                "signal": int(parts[2]),
                "security": parts[3] if parts[3] else "None"
            }
            networks.append(network)
    return networks

def get_placeholder_networks():
    return [
        {
            "in_use": False,
            "ssid": "Network 1",
            "signal": 69,
            "security": "WPA2"
        },
        {
            "in_use": False,
            "ssid": "Network 2",
            "signal": 50,
            "security": "None"
        },
        {
            "in_use": True,
            "ssid": "Network 3",
            "signal": 21,
            "security": "WPA"
        },
        {
            "in_use": False,
            "ssid": "Network 3",
            "signal": 3,
            "security": "WPA2"
        },
        {
            "in_use": False,
            "ssid": "Network 3",
            "signal": 69,
            "security": "WPA2 Enterprise"
        }
    ]