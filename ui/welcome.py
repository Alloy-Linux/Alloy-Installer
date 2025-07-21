import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from slides import InstallerSlide

def welcome_slide(content_area, go_to_slide):
    title = Gtk.Label(label="Welcome to Alloy Linux", css_classes=['title-1'])
    subtitle = Gtk.Label(label="Thank you for choosing Alloy Linux!", css_classes=['title-2'])
    description = Gtk.Label(
        label="This installer will guide you through the setup process.",
        wrap=True,
        max_width_chars=50
    )

    next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
    next_btn.connect('clicked', lambda _: go_to_slide(InstallerSlide.NETWORK))

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, valign=Gtk.Align.CENTER)
    box.append(title)
    box.append(subtitle)
    box.append(description)
    box.append(next_btn)

    content_area.append(box)
