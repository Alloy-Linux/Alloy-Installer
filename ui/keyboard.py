import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from slides import InstallerSlide
import backend.data as data

def keyboard_slide(content_area, go_to_slide, app):
    title = Gtk.Label(label="Select Your Keyboard Layout", css_classes=['title-1'])

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    main_box.append(title)

    search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    search_label = Gtk.Label(label="Search Layouts:")
    search_label.set_halign(Gtk.Align.START)

    app.keyboard_search = Gtk.SearchEntry(placeholder_text="Type to search...")
    app.keyboard_search.set_hexpand(True)
    app.keyboard_search.connect("search-changed", app._on_keyboard_search_changed)

    search_box.append(search_label)
    search_box.append(app.keyboard_search)
    main_box.append(search_box)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_min_content_height(200)
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    app.keyboard_listbox = Gtk.ListBox()
    app.keyboard_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    app.keyboard_listbox.connect("row-selected", app._on_keyboard_selected)

    scrolled.set_child(app.keyboard_listbox)
    main_box.append(scrolled)

    variant_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    variant_label = Gtk.Label(label="Variant:")
    variant_label.set_halign(Gtk.Align.START)

    app.variant_dropdown = Gtk.DropDown()
    app.variant_dropdown.set_hexpand(True)
    app.variant_dropdown.connect("notify::selected", app._on_variant_selected)

    variant_box.append(variant_label)
    variant_box.append(app.variant_dropdown)
    main_box.append(variant_box)

    selected_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    selected_label = Gtk.Label(label="Selected Layout:")
    app.selected_keyboard_display = Gtk.Label(label=app.selected_keyboard)
    app.selected_keyboard_display.set_hexpand(True)
    app.selected_keyboard_display.set_halign(Gtk.Align.START)

    selected_box.append(selected_label)
    selected_box.append(app.selected_keyboard_display)
    main_box.append(selected_box)

    test_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    test_label = Gtk.Label(label="Test keyboard layout here:")
    test_label.set_halign(Gtk.Align.START)

    test_entry = Gtk.Entry()
    test_entry.set_placeholder_text("Type here to test")
    test_entry.set_hexpand(True)

    test_box.append(test_label)
    test_box.append(test_entry)
    main_box.append(test_box)

    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_box.set_halign(Gtk.Align.END)
    back_btn = Gtk.Button(label="Back")
    back_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.LOCATION))

    def save_data():
        data.keyboard_layout = app.selected_keyboard
        data.keyboard_variant = app.selected_variant

    app.slide_save_callback = save_data

    def on_continue(_):
        save_data()
        go_to_slide(InstallerSlide.PARTITIONING)

    next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
    next_btn.connect('clicked', on_continue)

    btn_box.append(back_btn)
    btn_box.append(next_btn)
    main_box.append(btn_box)

    app._populate_keyboards(app.keyboard_layouts)
    content_area.append(main_box)
