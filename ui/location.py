import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from slides import InstallerSlide

def location_slide(content_area, go_to_slide, app):
    title = Gtk.Label(label="Select Your Location and Timezone", css_classes=['title-1'])

    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    main_box.append(title)

    search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    search_label = Gtk.Label(label="Search Timezones:")
    search_label.set_halign(Gtk.Align.START)

    app.timezone_search = Gtk.SearchEntry(placeholder_text="Type to search...")
    app.timezone_search.set_hexpand(True)
    app.timezone_search.connect("search-changed", app._on_search_changed)

    search_box.append(search_label)
    search_box.append(app.timezone_search)
    main_box.append(search_box)

    scrolled = Gtk.ScrolledWindow()
    scrolled.set_min_content_height(300)
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    app.timezone_listbox = Gtk.ListBox()
    app.timezone_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    app.timezone_listbox.connect("row-selected", app._on_timezone_selected)

    selected_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    selected_label = Gtk.Label(label="Selected Timezone:")
    app.selected_display = Gtk.Label(label=app.selected_timezone)
    app.selected_display.set_hexpand(True)
    app.selected_display.set_halign(Gtk.Align.START)

    selected_box.append(selected_label)
    selected_box.append(app.selected_display)

    app._populate_timezones(app.timezones)
    scrolled.set_child(app.timezone_listbox)
    main_box.append(scrolled)
    main_box.append(selected_box)

    btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_box.set_halign(Gtk.Align.END)
    back_btn = Gtk.Button(label="Back")
    back_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.NETWORK))
    next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
    next_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.KEYBOARD))

    btn_box.append(back_btn)
    btn_box.append(next_btn)
    main_box.append(btn_box)

    content_area.append(main_box)
