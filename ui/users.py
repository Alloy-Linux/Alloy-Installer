import gi
import backend.data as data

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from slides import InstallerSlide

def users_slide(content_area, go_to_slide, app):
    title = Gtk.Label(label="Create Your User Account", css_classes=['title-1'])

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    main_box.append(title)

    hostname_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hostname_label = Gtk.Label(label="Hostname:")
    hostname_label.set_halign(Gtk.Align.START)
    hostname_label.set_width_chars(19)
    hostname_entry = Gtk.Entry()
    hostname_entry.set_placeholder_text("Enter the computer's hostname")
    hostname_entry.set_hexpand(True)
    hostname_entry.set_max_length(64)
    if data.hostname:
        hostname_entry.set_text(data.hostname)
    hostname_row.append(hostname_label)
    hostname_row.append(hostname_entry)
    main_box.append(hostname_row)

    username_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    username_label = Gtk.Label(label="Username:")
    username_label.set_halign(Gtk.Align.START)
    username_label.set_width_chars(19)
    username_entry = Gtk.Entry()
    username_entry.set_placeholder_text("Enter your username")
    username_entry.set_hexpand(True)
    username_entry.set_max_length(32)
    if data.username:
        username_entry.set_text(data.username)
    username_row.append(username_label)
    username_row.append(username_entry)
    main_box.append(username_row)

    password_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    password_label = Gtk.Label(label="Password:")
    password_label.set_halign(Gtk.Align.START)
    password_label.set_width_chars(19)
    password_entry = Gtk.PasswordEntry()
    password_entry.set_show_peek_icon(True)
    password_entry.set_hexpand(True)
    if data.user_password:
        password_entry.set_text(data.user_password)
    password_row.append(password_label)
    password_row.append(password_entry)
    main_box.append(password_row)

    confirm_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    confirm_label = Gtk.Label(label="Confirm Password:")
    confirm_label.set_halign(Gtk.Align.START)
    confirm_label.set_width_chars(19)
    confirm_entry = Gtk.PasswordEntry()
    confirm_entry.set_hexpand(True)
    if data.user_password:
        confirm_entry.set_text(data.user_password)
    confirm_row.append(confirm_label)
    confirm_row.append(confirm_entry)
    main_box.append(confirm_row)

    match_label = Gtk.Label(label="")
    match_label.set_halign(Gtk.Align.START)
    def on_user_password_changed(_):
        p1 = password_entry.get_text()
        p2 = confirm_entry.get_text()
        if p1 and p2:
            if p1 == p2:
                match_label.set_text("Passwords match")
                match_label.remove_css_class('error')
            else:
                match_label.set_text("Passwords do not match")
                match_label.add_css_class('error')
        else:
            match_label.set_text("")
    password_entry.connect("changed", on_user_password_changed)
    confirm_entry.connect("changed", on_user_password_changed)
    main_box.append(match_label)

    separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    main_box.append(separator)

    same_pw_check = Gtk.CheckButton(label="Make root password same as user password")
    main_box.append(same_pw_check)

    root_pw_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    root_pw_label = Gtk.Label(label="Root Password:")
    root_pw_label.set_halign(Gtk.Align.START)
    root_pw_label.set_width_chars(19)
    root_pw_entry = Gtk.PasswordEntry()
    root_pw_entry.set_show_peek_icon(True)
    root_pw_entry.set_hexpand(True)
    if data.root_password:
        root_pw_entry.set_text(data.root_password)
    root_pw_row.append(root_pw_label)
    root_pw_row.append(root_pw_entry)
    main_box.append(root_pw_row)

    root_confirm_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    root_confirm_label = Gtk.Label(label="Confirm Root Password:")
    root_confirm_label.set_halign(Gtk.Align.START)
    root_confirm_label.set_width_chars(19)
    root_confirm_entry = Gtk.PasswordEntry()
    root_confirm_entry.set_hexpand(True)
    if data.root_password:
        root_confirm_entry.set_text(data.root_password)
    root_confirm_row.append(root_confirm_label)
    root_confirm_row.append(root_confirm_entry)
    main_box.append(root_confirm_row)

    root_match_label = Gtk.Label(label="")
    root_match_label.set_halign(Gtk.Align.START)
    main_box.append(root_match_label)

    error_label = Gtk.Label(label="")
    error_label.set_halign(Gtk.Align.START)
    error_label.add_css_class('error')
    main_box.append(error_label)

    def on_root_password_changed(_):
        p1 = root_pw_entry.get_text()
        p2 = root_confirm_entry.get_text()
        if p1 and p2:
            if p1 == p2:
                root_match_label.set_text("Root passwords match")
                root_match_label.remove_css_class('error')
            else:
                root_match_label.set_text("Root passwords do not match")
                root_match_label.add_css_class('error')
        else:
            root_match_label.set_text("")
    root_pw_entry.connect("changed", on_root_password_changed)
    root_confirm_entry.connect("changed", on_root_password_changed)

    def on_same_pw_toggled(button):
        active = button.get_active()
        if active:
            root_pw_entry.set_text(password_entry.get_text())
            root_confirm_entry.set_text(password_entry.get_text())
            root_pw_entry.set_editable(False)
            root_confirm_entry.set_editable(False)
            root_match_label.set_text("Root password is same as user password")
            root_match_label.remove_css_class('error')
        else:
            root_pw_entry.set_editable(True)
            root_confirm_entry.set_editable(True)
            root_match_label.set_text("")
    same_pw_check.connect("toggled", on_same_pw_toggled)

    def on_user_password_for_root(_):
        if same_pw_check.get_active():
            root_pw_entry.set_text(password_entry.get_text())
            root_confirm_entry.set_text(password_entry.get_text())
    password_entry.connect("changed", on_user_password_for_root)

    if data.user_password and data.root_password and data.user_password == data.root_password:
        same_pw_check.set_active(True)
        root_pw_entry.set_editable(False)
        root_confirm_entry.set_editable(False)
        root_match_label.set_text("Root password is same as user password")

    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_box.set_halign(Gtk.Align.END)
    back_btn = Gtk.Button(label="Back")
    back_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.PARTITIONING))

    def save_data():
        p1 = password_entry.get_text()
        p2 = confirm_entry.get_text()
        p3 = root_pw_entry.get_text()
        p4 = root_confirm_entry.get_text()
        if p1 == p2 and p3 == p4:
            app.hostname = hostname_entry.get_text()
            app.username = username_entry.get_text()
            app.user_password = password_entry.get_text()
            app.root_password = root_pw_entry.get_text()
            data.hostname = hostname_entry.get_text()
            data.username = username_entry.get_text()
            data.user_password = password_entry.get_text()
            data.root_password = root_pw_entry.get_text()
        else:
            return

    app.slide_save_callback = save_data

    def on_continue(_):
        hostname = hostname_entry.get_text().strip()
        username = username_entry.get_text().strip()
        user_pw = password_entry.get_text()
        user_pw_confirm = confirm_entry.get_text()
        root_pw = root_pw_entry.get_text()
        root_pw_confirm = root_confirm_entry.get_text()

        if not hostname or not username or not user_pw or not user_pw_confirm:
            error_label.set_text("Fill in all fields.")
            return

        if not same_pw_check.get_active():
            if not root_pw or not root_pw_confirm:
                error_label.set_text("Fill in all fields.")
                return
        if root_pw != root_pw_confirm:
            error_label.set_text("Root passwords do not match.")
            return
        else:
            root_pw = user_pw
            root_pw_confirm = user_pw_confirm

        if user_pw != user_pw_confirm:
            error_label.set_text("User passwords do not match.")
            return

        error_label.set_text("")
        app.hostname = hostname
        app.username = username
        app.user_password = user_pw
        app.root_password = root_pw
        data.hostname = hostname
        data.username = username
        data.user_password = user_pw
        data.root_password = root_pw

        go_to_slide(InstallerSlide.DESKTOP)

    next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
    next_btn.connect('clicked', on_continue)

    btn_box.append(back_btn)
    btn_box.append(next_btn)
    main_box.append(btn_box)

    content_area.append(main_box)
