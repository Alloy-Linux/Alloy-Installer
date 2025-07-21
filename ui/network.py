import subprocess
import urllib.request
import threading

from gi.repository import Gtk, GLib

from slides import InstallerSlide


def has_internet(timeout=3):
    try:
        urllib.request.urlopen('https://www.google.com', timeout=timeout)
        return True
    except urllib.error.URLError:
        return False

def create_network_widget(network, on_network_click):
    row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    row_box.set_margin_top(6)
    row_box.set_margin_bottom(6)
    row_box.set_margin_start(6)
    row_box.set_margin_end(6)

    click_controller = Gtk.GestureClick()
    click_controller.connect("pressed", lambda gesture, n_press, x, y: on_network_click(network, row_box))
    row_box.add_controller(click_controller)

    row_box.set_css_classes(['network-row'])

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
        connected_icon = Gtk.Image.new_from_icon_name("system-lock-screen-symbolic")
        connected_icon.set_halign(Gtk.Align.END)
        row_box.append(connected_icon)
    elif network['security'] == 'None':
        connected_icon = Gtk.Image.new_from_icon_name("applications-internet-symbolic")
        connected_icon.set_halign(Gtk.Align.END)
        row_box.append(connected_icon)

    return row_box

def show_password_dialog(parent, network, on_connect):
    dialog = Gtk.Dialog()
    dialog.set_transient_for(parent)
    dialog.set_modal(True)
    dialog.set_title(f"Connect to {network['ssid']}")
    dialog.set_default_size(350, 200)

    content_area = dialog.get_content_area()
    content_area.set_spacing(12)
    content_area.set_margin_top(12)
    content_area.set_margin_bottom(12)
    content_area.set_margin_start(12)
    content_area.set_margin_end(12)

    info_label = Gtk.Label()
    info_label.set_markup(f"<b>{GLib.markup_escape_text(network['ssid'])}</b>\nSecurity: {network['security']}")
    info_label.set_xalign(0)
    content_area.append(info_label)

    password_label = Gtk.Label(label="Password:")
    password_label.set_xalign(0)
    content_area.append(password_label)

    password_entry = Gtk.PasswordEntry()
    password_entry.set_show_peek_icon(True)
    content_area.append(password_entry)

    error_label = Gtk.Label()
    error_label.set_css_classes(['error'])
    error_label.set_visible(False)
    content_area.append(error_label)

    button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    button_box.set_halign(Gtk.Align.END)

    cancel_btn = Gtk.Button(label="Cancel")
    cancel_btn.connect('clicked', lambda _: dialog.close())

    connect_btn = Gtk.Button(label="Connect")
    connect_btn.set_css_classes(['suggested-action'])
    
    def on_connect_clicked(_):
        password = password_entry.get_text()
        connect_btn.set_sensitive(False)
        connect_btn.set_label("Connecting...")
        
        def connect_callback():
            try:
                success = connect_to_network(network['ssid'], password)
                GLib.idle_add(lambda: handle_connect_result(success, dialog, error_label, connect_btn))
            except Exception as e:
                GLib.idle_add(lambda: handle_connect_result(False, dialog, error_label, connect_btn, str(e)))
        
        threading.Thread(target=connect_callback, daemon=True).start()

    def handle_connect_result(success, dialog, error_label, connect_btn, error_msg=None):
        if success:
            dialog.close()
            on_connect()
        else:
            error_label.set_text(error_msg or "Failed to connect. Please check your password.")
            error_label.set_visible(True)
            connect_btn.set_sensitive(True)
            connect_btn.set_label("Connect")

    connect_btn.connect('clicked', on_connect_clicked)

    password_entry.connect('activate', lambda _: connect_btn.emit('clicked'))

    button_box.append(cancel_btn)
    button_box.append(connect_btn)
    content_area.append(button_box)

    dialog.show()

def is_ethernet_connected():
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.strip().split('\n'):
            device, dev_type, state = line.split(':')
            if dev_type == 'ethernet' and state == 'connected':
                return True
    except Exception:
        pass
    return False

def is_wifi_connected():
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.strip().split('\n'):
            device, dev_type, state = line.strip().split(':')
            if dev_type == 'wifi' and state == 'connected':
                return True
    except Exception:
        pass
    return False

def connect_to_network(ssid, password=None):
    try:
        if password:
            cmd = f"nmcli device wifi connect '{ssid}' password '{password}'"
        else:
            cmd = f"nmcli device wifi connect '{ssid}'"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

def disconnect_from_network(ssid):
    try:
        result = subprocess.run(f"nmcli connection down '{ssid}'", shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def show_confirmation_dialog(parent, message, on_confirm):
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        modal=True,
        message_type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.YES_NO,
        text=message
    )
    
    def on_response(dialog, response_id):
        if response_id == Gtk.ResponseType.YES:
            on_confirm()
        dialog.destroy()
    
    dialog.connect('response', on_response)
    dialog.show()

def network_slide(content_area, go_to_slide):
    title = Gtk.Label(label="Connect to a WiFi network", css_classes=['title-1'])

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    main_box.append(title)
    
    status_label = Gtk.Label(label="Checking internet...")
    main_box.append(status_label)

    network_slide.has_connection = False
    network_slide.selected_network = None
    network_slide.selected_widget = None

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.set_vexpand(True)
    main_box.append(scrolled_window)

    box_networks = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    scrolled_window.set_child(box_networks)

    control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    control_box.set_margin_top(10)
    
    selected_label = Gtk.Label(label="No network selected")
    selected_label.set_xalign(0)
    selected_label.set_hexpand(True)
    control_box.append(selected_label)

    action_btn = Gtk.Button(label="Connect")
    action_btn.set_sensitive(False)
    control_box.append(action_btn)

    main_box.append(control_box)

    def get_parent_window():
        widget = content_area
        while widget and not isinstance(widget, Gtk.Window):
            widget = widget.get_parent()
        return widget

    def on_network_click(network, widget):

        if network_slide.selected_widget:
            network_slide.selected_widget.set_opacity(1)

        widget.set_opacity(0.7)
        network_slide.selected_widget = widget

        network_slide.selected_network = network
        selected_label.set_text(f"Selected: {network['ssid']}")
        
        if network['in_use']:
            action_btn.set_label("Disconnect")
            action_btn.set_css_classes(['destructive-action'])
        else:
            action_btn.set_label("Connect")
            action_btn.set_css_classes(['suggested-action'])
        
        action_btn.set_sensitive(True)

    def on_action_clicked(_):
        if not network_slide.selected_network:
            return
            
        network = network_slide.selected_network
        parent = get_parent_window()
        
        if network['in_use']:
            show_confirmation_dialog(
                parent,
                f"Disconnect from {network['ssid']}?",
                lambda: perform_disconnect(network)
            )
        else:
            if network['security'] == 'None':
                perform_connect(network)
            else:
                show_password_dialog(parent, network, update_network_list)

    def perform_connect(network, password=None):
        action_btn.set_sensitive(False)
        action_btn.set_label("Connecting...")
        
        def connect_callback():
            success = connect_to_network(network['ssid'], password)
            GLib.idle_add(lambda: handle_action_result(success, "connect"))
        
        threading.Thread(target=connect_callback, daemon=True).start()

    def perform_disconnect(network):
        action_btn.set_sensitive(False)
        action_btn.set_label("Disconnecting...")
        
        def disconnect_callback():
            success = disconnect_from_network(network['ssid'])
            GLib.idle_add(lambda: handle_action_result(success, "disconnect"))
        
        threading.Thread(target=disconnect_callback, daemon=True).start()

    def handle_action_result(success, action):
        if success:
            network_slide.selected_network = None
            selected_label.set_text("No network selected")
            action_btn.set_sensitive(False)
            action_btn.set_label("Connect")
            action_btn.set_css_classes(['suggested-action'])
            update_network_list()
        else:
            action_btn.set_sensitive(True)
            action_btn.set_label("Connect" if action == "connect" else "Disconnect")

    action_btn.connect('clicked', on_action_clicked)

    def update_network_list():
        while child := box_networks.get_first_child():
            box_networks.remove(child)

        networks = get_nearby_networks()

        if not networks:
            placeholder = Gtk.Label(label="No WiFi networks found")
            placeholder.set_margin_top(24)
            placeholder.set_margin_bottom(24)
            box_networks.append(placeholder)
        else:
            for network in networks:
                network_widget = create_network_widget(network, on_network_click)
                box_networks.append(network_widget)
                if network_slide.selected_network and network['ssid'] == network_slide.selected_network['ssid']:
                    network_slide.selected_network = network
                    network_slide.selected_widget = network_widget
                    network_widget.set_opacity(0.7)
                    action_btn.set_sensitive(True)
                    selected_label.set_text(f"Selected: {network['ssid']}")

                    if network['in_use']:
                        action_btn.set_label("Disconnect")
                        action_btn.set_css_classes(['destructive-action'])
                    else:
                        action_btn.set_label("Connect")
                        action_btn.set_css_classes(['suggested-action'])

        scrolled_window.set_visible(True)

    def update_internet_status():
        ethernet = is_ethernet_connected()
        wifi = is_wifi_connected()
        internet = has_internet()

        network_slide.has_connection = ethernet or wifi or internet

        if ethernet and internet:
            status_label.set_label("Connected via Ethernet")
        elif wifi and internet:
            status_label.set_label("Connected via WiFi")
        elif ethernet and not internet:
            status_label.set_label("Connected via Ethernet (no internet access)")
        elif wifi and not internet:
            status_label.set_label("Connected via WiFi (no internet access)")
        else:
            status_label.set_label("Not connected to any network")

        update_network_list()
        return True

    update_internet_status()
    GLib.timeout_add_seconds(5, update_internet_status)

    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_box.set_halign(Gtk.Align.END)

    back_btn = Gtk.Button(label="Back")
    back_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.WELCOME))

    next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
    next_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.LOCATION))

    btn_box.append(back_btn)
    btn_box.append(next_btn)

    main_box.append(btn_box)
    content_area.append(main_box)


def get_nearby_networks():
    try:
        result = subprocess.run(
            "nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY device wifi list",
            capture_output=True, text=True, shell=True, check=True
        )

        output_lines = result.stdout.strip().split('\n')

        networks = {}
        for line in output_lines:
            parts = line.strip().split(':', 3)
            if len(parts) >= 4:
                network = {
                    "in_use": parts[0] == '*',
                    "ssid": parts[1] or "Hidden Network",
                    "signal": int(parts[2]) if parts[2] else 0,
                    "security": parts[3] if parts[3] else "None"
                }

                ssid = network["ssid"]

                if ssid not in networks:
                    networks[ssid] = network
                else:
                    existing = networks[ssid]
                    if network["in_use"]:
                        networks[ssid] = network
                    elif existing["in_use"]:
                        pass
                    else:
                        if network["signal"] > existing["signal"]:
                            networks[ssid] = network

        return list(networks.values())
    except Exception:
        return []


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
        }
    ]