import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

slide_data = [
    {"image": "./content/tux.png", "text": "To do"},
    {"image": "./content/tux.png", "text": "To do 2"},
    {"image": "./content/tux.png", "text": "To do 3"}
]

def install_slide(content_area, go_to_slide, app):
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    title = Gtk.Label(label="Installing Alloy Linux", css_classes=["title-1"])
    main_box.append(title)

    slideshow_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    revealer = Gtk.Revealer()
    revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
    revealer.set_transition_duration(800)

    image_widget = Gtk.Image()
    image_frame = Gtk.Box()
    image_frame.set_size_request(400, 250)
    image_frame.set_halign(Gtk.Align.CENTER)
    image_frame.append(image_widget)

    text_label = Gtk.Label(wrap=True, hexpand=True, max_width_chars=60, justify=Gtk.Justification.CENTER)
    text_label.set_css_classes(["subtitle"])
    text_label.set_valign(Gtk.Align.START)

    revealer_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    revealer_content.append(image_frame)
    revealer_content.append(text_label)
    revealer.set_child(revealer_content)

    slideshow_box.append(revealer)
    main_box.append(slideshow_box)

    progress = Gtk.ProgressBar()
    progress.set_valign(Gtk.Align.CENTER)
    progress.set_show_text(True)
    main_box.append(progress)

    log_view = Gtk.TextView()
    log_view.set_editable(False)
    log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
    log_buffer = log_view.get_buffer()

    log_scroll = Gtk.ScrolledWindow()
    log_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    log_scroll.set_vexpand(True)
    log_scroll.set_child(log_view)

    main_box.append(log_scroll)

    content_area.append(main_box)

    index = {"value": 0}

    def update_slide():
        data = slide_data[index["value"]]
        revealer.set_reveal_child(False)

        def switch_content():
            try:
                image_widget.set_from_file(data["image"])
            except Exception:
                image_widget.set_from_icon_name("image-missing")

            text_label.set_label(data["text"])
            revealer.set_reveal_child(True)

        GLib.timeout_add(300, lambda: (switch_content(), False))
        index["value"] = (index["value"] + 1) % len(slide_data)
        return True

    update_slide()
    GLib.timeout_add_seconds(5, update_slide)

    def set_progress(fraction, text=None):
        progress.set_fraction(fraction)
        if text:
            progress.set_text(text)

    def append_log(message):
        end_iter = log_buffer.get_end_iter()
        log_buffer.insert(end_iter, message + "\n")
        mark = log_buffer.create_mark(None, log_buffer.get_end_iter(), False)
        log_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    install_slide.set_progress = set_progress
    install_slide.append_log = append_log

# Example use:
#    install_slide.set_progress(0.1, "progress bar message")
#    install_slide.append_log("text for log")
