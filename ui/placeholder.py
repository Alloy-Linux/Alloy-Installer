import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

def placeholder_slide(content_area, slide_name):
    label = Gtk.Label(label=f"Placeholder for {slide_name}")
    content_area.append(label)
