import zoneinfo
from enum import Enum, auto
import sys
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

class InstallerSlide(Enum):
    WELCOME = auto()
    LOCATION = auto()
    KEYBOARD = auto()
    PARTITIONING = auto()
    USERS = auto()
    DESKTOP = auto()
    SUMMARY = auto()
    INSTALL = auto()
    FINISH = auto()


class AlloyInstaller(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.alloy.installer")
        GLib.set_application_name('Alloy Installer')
        self.current_slide = InstallerSlide.WELCOME
        self.window = None
        self.main_paned = None
        self.sidebar = None
        self.content_area = None
        self.timezones = sorted(zoneinfo.available_timezones())
        self.selected_timezone = "Europe/Amsterdam"
        self.timezone_listbox = None
        self.timezone_search = None
        self.sidebar_buttons = {}

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(
            application=self,
            title="Alloy Linux Installer",
            default_width=800,
            default_height=600
        )

        self.main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        self.sidebar = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_start=10,
            margin_end=10,
            margin_top=10,
            margin_bottom=10
        )
        self._build_sidebar()

        self.content_area = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=20,
            margin_start=20,
            margin_end=20,
            margin_top=20,
            margin_bottom=20
        )

        self.main_paned.set_start_child(self.sidebar)
        self.main_paned.set_end_child(self.content_area)
        self.main_paned.set_position(200)

        self.window.set_child(self.main_paned)
        self._update_content()
        self.window.present()

    def _build_sidebar(self):
        header = Gtk.Label(label="Alloy Installer")
        self.sidebar.append(header)
        self.sidebar_buttons = {}

        button_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        for slide in InstallerSlide:
            btn = Gtk.Button(
                label=slide.name.capitalize(),
                halign=Gtk.Align.FILL,
                hexpand=True
            )
            btn.connect('clicked', self._on_navigate, slide)
            button_container.append(btn)
            self.sidebar_buttons[slide] = btn

        self.sidebar.append(button_container)

        self._update_sidebar_styles()

    def _update_content(self):
        while self.content_area.get_first_child():
            self.content_area.remove(self.content_area.get_first_child())

        match self.current_slide:
            case InstallerSlide.WELCOME:
                self._show_welcome()
            case InstallerSlide.LOCATION:
                self._show_location()
            case _:
                self._show_placeholder()

    def _show_welcome(self):
        title = Gtk.Label(label="Welcome to Alloy Linux", css_classes=['title-1'])
        subtitle = Gtk.Label(label="Thank you for choosing Alloy Linux!", css_classes=['title-2'])
        description = Gtk.Label(
            label="This installer will guide you through the setup process.",
            wrap=True,
            max_width_chars=50
        )

        next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
        next_btn.connect('clicked', lambda _: self._go_to_slide(InstallerSlide.LOCATION))

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, valign=Gtk.Align.CENTER)
        box.append(title)
        box.append(subtitle)
        box.append(description)
        box.append(next_btn)

        self.content_area.append(box)

    def _show_location(self):
        title = Gtk.Label(label="Select Your Location and Timezone", css_classes=['title-1'])

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.append(title)

        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        search_label = Gtk.Label(label="Search Timezones:")
        search_label.set_halign(Gtk.Align.START)

        self.timezone_search = Gtk.SearchEntry(placeholder_text="Type to search...")
        self.timezone_search.set_hexpand(True)
        self.timezone_search.connect("search-changed", self._on_search_changed)

        search_box.append(search_label)
        search_box.append(self.timezone_search)
        main_box.append(search_box)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(300)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.timezone_listbox = Gtk.ListBox()
        self.timezone_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.timezone_listbox.connect("row-selected", self._on_timezone_selected)

        selected_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        selected_label = Gtk.Label(label="Selected Timezone:")
        self.selected_display = Gtk.Label(label=self.selected_timezone)
        self.selected_display.set_hexpand(True)
        self.selected_display.set_halign(Gtk.Align.START)

        selected_box.append(selected_label)
        selected_box.append(self.selected_display)

        self._populate_timezones(self.timezones)
        scrolled.set_child(self.timezone_listbox)
        main_box.append(scrolled)
        main_box.append(selected_box)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        back_btn = Gtk.Button(label="Back")
        back_btn.connect('clicked', lambda _: self._go_to_slide(InstallerSlide.WELCOME))
        next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
        next_btn.connect('clicked', lambda _: self._go_to_slide(InstallerSlide.KEYBOARD))

        btn_box.append(back_btn)
        btn_box.append(next_btn)
        main_box.append(btn_box)

        self.content_area.append(main_box)

    def _populate_timezones(self, timezones):
        while child := self.timezone_listbox.get_first_child():
            self.timezone_listbox.remove(child)

        for tz in timezones:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=tz, halign=Gtk.Align.START, margin_start=10)
            row.set_child(label)
            self.timezone_listbox.append(row)

            if tz == self.selected_timezone:
                self.timezone_listbox.select_row(row)

    def _on_search_changed(self, entry):
        search_text = entry.get_text().lower()
        if not search_text:
            filtered = self.timezones
        else:
            filtered = [tz for tz in self.timezones if search_text in tz.lower()]
        self._populate_timezones(filtered)

    def _on_timezone_selected(self, listbox, row):
        if row is not None:
            label = row.get_child()
            self.selected_timezone = label.get_text()
            self.selected_display.set_text(self.selected_timezone)

    def _on_navigate(self, button, slide):
        self._go_to_slide(slide)

    def _go_to_slide(self, slide):
        self.current_slide = slide
        self._update_content()
        self._update_sidebar_styles()

    def _update_sidebar_styles(self):
        for slide, button in self.sidebar_buttons.items():
            if slide == self.current_slide:
                button.add_css_class('suggested-action')
            else:
                button.remove_css_class('suggested-action')

    def _show_placeholder(self):
        label = Gtk.Label(label=f"Placeholder for {self.current_slide.name}")
        self.content_area.append(label)


if __name__ == "__main__":
    app = AlloyInstaller()
    app.run(sys.argv)