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
        self.main_paned.set_position(200)  # Sidebar width

        self.window.set_child(self.main_paned)
        self._update_content()
        self.window.present()

    def _build_sidebar(self):
        header = Gtk.Label(label="Alloy Installer", css_classes=['title-1'])
        self.sidebar.append(header)

        for slide in InstallerSlide:
            btn = Gtk.Button(
                label=slide.name.capitalize(),
                halign=Gtk.Align.START,
                css_classes=['flat'] if slide != self.current_slide else ['suggested-action']
            )
            btn.connect('clicked', self._on_navigate, slide)
            self.sidebar.append(btn)

    def _update_content(self):
        while self.content_area.get_first_child():
            self.content_area.remove(self.content_area.get_first_child())

        match self.current_slide: # this code is reachable, ignore pycharm
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

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.append(title)
        box.append(subtitle)
        box.append(description)
        box.append(next_btn)

        self.content_area.append(box)

    def _show_location(self):
        title = Gtk.Label(label="Select Your Location", css_classes=['title-1'])
        next_btn = Gtk.Button(label="Continue")
        next_btn.connect('clicked', lambda _: self._go_to_slide(InstallerSlide.KEYBOARD))

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.append(title)
        box.append(next_btn)
        self.content_area.append(box)

    def _show_placeholder(self):
        label = Gtk.Label(label=f"{self.current_slide.name} Screen (Not done)")
        self.content_area.append(label)

    def _on_navigate(self, button, slide):
        self._go_to_slide(slide)

    def _go_to_slide(self, slide):
        self.current_slide = slide
        self._update_content()
        for child in self.sidebar:
            if isinstance(child, Gtk.Button):
                child.set_css_classes(
                    ['suggested-action'] if child.get_label().lower() == slide.name.lower()
                    else ['flat']
                )


if __name__ == "__main__":
    app = AlloyInstaller()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)