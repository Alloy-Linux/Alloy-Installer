import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from slides import InstallerSlide

def desktop_slide(content_area, go_to_slide, app):
    title = Gtk.Label(label="Select Desktop Environment", css_classes=['title-1'])

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    main_box.append(title)

    if not app.selected_desktop:
        app.selected_desktop = app.desktop_environments[0]

    preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    app.desktop_image = Gtk.Image.new_from_file(
        app.desktop_info[app.selected_desktop]['image']
    )
    app.desktop_image.set_pixel_size(128)
    app.desktop_image.set_halign(Gtk.Align.CENTER)

    app.desktop_description = Gtk.Label(
        label=app.desktop_info[app.selected_desktop]['description'],
        wrap=True
    )
    app.desktop_description.set_justify(Gtk.Justification.CENTER)
    app.desktop_description.set_halign(Gtk.Align.CENTER)

    preview_box.append(app.desktop_image)
    preview_box.append(app.desktop_description)

    main_box.append(preview_box)

    de_label = Gtk.Label(label="Desktop Environment:")
    de_label.set_halign(Gtk.Align.START)
    de_scroll = Gtk.ScrolledWindow()
    de_scroll.set_min_content_height(100)
    de_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    app.desktop_listbox = Gtk.ListBox()
    app.desktop_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    app.desktop_listbox.connect("row-selected", app._on_desktop_selected)
    de_scroll.set_child(app.desktop_listbox)

    main_box.append(de_label)
    main_box.append(de_scroll)

    ds_label = Gtk.Label(label="Display Server:")
    ds_label.set_halign(Gtk.Align.START)

    app.display_dropdown = Gtk.DropDown()
    app.display_dropdown.set_hexpand(True)
    app.display_dropdown.connect("notify::selected", app._on_display_dropdown_selected)

    main_box.append(ds_label)
    main_box.append(app.display_dropdown)

    warning_label = Gtk.Label(
        label="⚠️ Do not change Display Server from the default unless you know what you're doing.",
        wrap=True
    )
    warning_label.set_halign(Gtk.Align.START)
    warning_label.add_css_class("dim-label")

    main_box.append(warning_label)

    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    back_btn = Gtk.Button(label="Back")
    back_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.USERS))

    next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
    next_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.SUMMARY))

    btn_box.append(back_btn)
    btn_box.append(next_btn)
    main_box.append(btn_box)

    app._populate_desktops()
    app._populate_display_dropdown()

    content_area.append(main_box)
