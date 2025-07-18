import zoneinfo
import gi
import json
import os

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from slides import InstallerSlide
from ui.welcome import welcome_slide
from ui.location import location_slide
from ui.keyboard import keyboard_slide
from ui.users import users_slide
from ui.placeholder import placeholder_slide


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

        self.keyboard_layouts = self._load_keyboard_layouts("keyboard_layouts.json")
        self.selected_keyboard = 'us'
        self.keyboard_listbox = None
        self.keyboard_search = None
        self.selected_keyboard_display = None

        self.hostname = "alloy"
        self.username = ""
        self.user_password = ""
        self.root_password = ""



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
                welcome_slide(self.content_area, self._go_to_slide)
            case InstallerSlide.LOCATION:
                location_slide(self.content_area, self._go_to_slide, self)
            case InstallerSlide.KEYBOARD:
                keyboard_slide(self.content_area, self._go_to_slide, self)
            case InstallerSlide.USERS:
                users_slide(self.content_area, self._go_to_slide, self)
            case _:
                placeholder_slide(self.content_area, self.current_slide.name)

# Time

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

# Keyboard

    def _load_keyboard_layouts(self, filename):
        try:
            filepath = os.path.join(os.path.dirname(__file__), filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading keyboard layouts: {e}")
            return {}

    def _populate_keyboards(self, layouts):
        while child := self.keyboard_listbox.get_first_child():
            self.keyboard_listbox.remove(child)

        for layout in layouts:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=layout, halign=Gtk.Align.START, margin_start=10)
            row.set_child(label)
            self.keyboard_listbox.append(row)

            if layout == self.selected_keyboard:
                self.keyboard_listbox.select_row(row)

    def _on_keyboard_search_changed(self, entry):
        search_text = entry.get_text().lower()
        if not search_text:
            filtered = self.keyboard_layouts
        else:
            filtered = [layout for layout in self.keyboard_layouts if search_text in layout.lower()]
        self._populate_keyboards(filtered)

    def _on_keyboard_selected(self, listbox, row):
        if row:
            layout = row.get_child().get_label()
            self.selected_keyboard = layout
            self.selected_keyboard_display.set_label(layout)

            variants = self.keyboard_layouts.get(layout, [])
            store = Gtk.StringList.new(variants)
            self.variant_dropdown.set_model(store)
            self.variant_dropdown.set_selected(0)
            self.selected_variant = "default"

    def _on_variant_selected(self, dropdown, _):
        model = dropdown.get_model()
        index = dropdown.get_selected()
        if model and index >= 0:
            self.selected_variant = model.get_string(index)



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
