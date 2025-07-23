import gi
import subprocess

import backend.data

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from .constants import FSTYPE_COLOR_CLASSES, PartitioningMode
from .utils import get_os, human_readable_size
from .partition_bar import PartitionBar
from slides import InstallerSlide

class PartitionUI:
    def __init__(self, partition_manager, go_to_slide_callback):
        self.partition_manager = partition_manager
        self.go_to_slide = go_to_slide_callback

        self.selected_partition_value = None
        self.partition_bar = None
        self.current_partitioning_mode = PartitioningMode.INSTALL_ALONGSIDE
        self.size_adjustment = Gtk.Adjustment(value=10, lower=10, upper=10, step_increment=1, page_increment=10)
        self.size_value_label = None
        self.min_size_label = None
        self.max_size_label = None
        self.size_slider_frame = None
        self.current_disk_label = None
        self.current_partition_label = None
        self.selected_partition_box = None

    def create_ui(self):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_css_classes(['installer-page'])
        scrolled_window.set_child(main_box)


        title = Gtk.Label(label="Partitioning settings", css_classes=['title-1'])
        main_box.append(title)

        disk_selection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        disk_selection_box.set_valign(Gtk.Align.CENTER)

        disk_label = Gtk.Label(label="Select storage device:")
        disk_selection_box.append(disk_label)

        disk_combo = Gtk.ComboBoxText()
        disk_combo.set_hexpand(True)
        disk_selection_box.append(disk_combo)

        all_disks_info = self.partition_manager.get_disks()
        if all_disks_info:
            for display_text in all_disks_info.keys():
                disk_combo.append_text(display_text)
            disk_combo.set_active(0)
        else:
            disk_combo.append_text("No disks found")
            disk_combo.set_sensitive(False)

        main_box.append(disk_selection_box)

        self.selected_partition_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.selected_partition_box.set_margin_top(10)
        selected_partition_label = Gtk.Label(label="Selected partition to replace:", css_classes=['bold'])
        self.selected_partition_value = Gtk.Label(label="None", css_classes=['bold'])
        self.selected_partition_box.append(selected_partition_label)
        self.selected_partition_box.append(self.selected_partition_value)
        self.selected_partition_box.set_visible(False)
        main_box.append(self.selected_partition_box)

        options_frame = Gtk.Frame()
        options_frame.set_margin_top(15)
        options_frame.set_margin_bottom(15)
        options_frame_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        options_frame_content_box.set_margin_start(10)
        options_frame_content_box.set_margin_end(10)
        options_frame.set_child(options_frame_content_box)

        install_alongside_radio = Gtk.CheckButton()
        install_alongside_radio.set_label("Install alongside")
        install_alongside_radio.set_group(None)
        install_alongside_radio.set_active(True)

        desc_alongside = Gtk.Label(label="The installer will shrink a partition to make room for Alloy.", xalign=0)
        desc_alongside.set_margin_start(25)

        box_alongside = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box_alongside.append(install_alongside_radio)
        box_alongside.append(desc_alongside)
        options_frame_content_box.append(box_alongside)

        replace_partition_radio = Gtk.CheckButton()
        replace_partition_radio.set_label("Replace a partition")
        replace_partition_radio.set_group(install_alongside_radio)

        desc_replace = Gtk.Label(label="Replaces a partition with Alloy.", xalign=0)
        desc_replace.set_margin_start(25)

        box_replace = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box_replace.append(replace_partition_radio)
        box_replace.append(desc_replace)
        options_frame_content_box.append(box_replace)

        erase_disk_radio = Gtk.CheckButton()
        erase_disk_radio.set_label("Erase disk")
        erase_disk_radio.set_group(install_alongside_radio)

        desc_erase = Gtk.Label(label="This will <b>delete all data</b> currently present on the selected storage device.",
                               use_markup=True, xalign=0)
        desc_erase.set_margin_start(25)

        box_erase = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box_erase.append(erase_disk_radio)
        box_erase.append(desc_erase)
        options_frame_content_box.append(box_erase)

        manual_partitioning_button = Gtk.Button()
        manual_partitioning_button.set_label("Launch manual partitioner")
        manual_partitioning_button.connect("clicked", self.on_manual_partitioning_clicked)

        box_manual = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box_manual.append(manual_partitioning_button)
        options_frame_content_box.append(box_manual)

        main_box.append(options_frame)

        self.size_slider_frame = Gtk.Frame()
        self.size_slider_frame.set_margin_top(10)
        self.size_slider_frame.set_margin_bottom(10)
        size_slider_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        size_slider_content_box.set_margin_start(15)
        size_slider_content_box.set_margin_end(15)
        size_slider_content_box.set_margin_top(15)
        size_slider_content_box.set_margin_bottom(15)
        self.size_slider_frame.set_child(size_slider_content_box)

        size_slider_label = Gtk.Label(label="Partition size for Alloy:", xalign=0, css_classes=['bold'])
        size_slider_content_box.append(size_slider_label)

        size_info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        size_info_box.set_halign(Gtk.Align.CENTER)

        self.min_size_label = Gtk.Label(label="10 GB", css_classes=['dim-label'])
        self.size_value_label = Gtk.Label(label="10 GB", css_classes=['bold'])
        self.max_size_label = Gtk.Label(label="0 GB", css_classes=['dim-label'])

        size_info_box.append(self.min_size_label)
        size_info_box.append(self.size_value_label)
        size_info_box.append(self.max_size_label)
        size_slider_content_box.append(size_info_box)

        size_slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.size_adjustment)
        size_slider.set_digits(0)
        size_slider.set_draw_value(False)
        size_slider.set_hexpand(True)
        size_slider_content_box.append(size_slider)

        size_slider.connect("value-changed", self.on_size_slider_value_changed)

        self.size_slider_frame.set_visible(True)
        main_box.append(self.size_slider_frame)

        current_label = Gtk.Label(label="Current:", xalign=0, css_classes=['bold'])
        main_box.append(current_label)

        current_info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        current_info_box.set_margin_start(10)
        main_box.append(current_info_box)

        self.current_disk_label = Gtk.Label(label="Disk: None selected", xalign=0)
        self.current_partition_label = Gtk.Label(label="Partition: None selected", xalign=0)
        current_info_box.append(self.current_disk_label)
        current_info_box.append(self.current_partition_label)

        for radio in [install_alongside_radio, replace_partition_radio, erase_disk_radio]:
            radio.connect("toggled", lambda *_: self.update_option_ui(install_alongside_radio, replace_partition_radio, erase_disk_radio, disk_combo))

        encryption_button = Gtk.CheckButton()
        encryption_button.connect("toggled", lambda btn: setattr(backend.data, 'full_disk_encryption', btn.get_active()))
        encryption_button.set_label("Enable LUKS encryption?")
        main_box.append(encryption_button)

        encryption_options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        encryption_options_box.set_margin_start(20)
        main_box.append(encryption_options_box)

        password_label = Gtk.Label(label="Encryption password:")
        password_label.set_halign(Gtk.Align.START)
        encryption_options_box.append(password_label)

        password_entry = Gtk.PasswordEntry()
        password_entry.set_show_peek_icon(True)
        password_entry.connect("changed", lambda entry: setattr(backend.data, 'encryption_password', entry.get_text()))
        encryption_options_box.append(password_entry)

        radio_options = {
            "Use a password": "use_password",
            "Use TPM (Trusted Platform Module)": "tpm",
            "Use keyfile": "use_keyfile"
        }

        tpm_password_label = Gtk.Label(label="TPM password:")
        tpm_password_label.set_halign(Gtk.Align.START)
        tpm_password_entry = Gtk.PasswordEntry()
        tpm_password_entry.set_show_peek_icon(True)
        tpm_password_entry.connect("changed", lambda entry: setattr(backend.data, 'tpm_password', entry.get_text()))
        tpm_password_label.set_visible(False)
        tpm_password_entry.set_visible(False)
        encryption_options_box.append(tpm_password_label)
        encryption_options_box.append(tpm_password_entry)


        def on_encryption_option_toggled(button, field_name):
            if button.get_active():
                for name in radio_options.values():
                    setattr(backend.data, name, name == field_name)

                show_tpm = field_name == "tpm"
                tpm_password_label.set_visible(show_tpm)
                tpm_password_entry.set_visible(show_tpm)

        group = None
        for label, field_name in radio_options.items():
            btn = Gtk.CheckButton.new_with_label(label)
            btn.set_group(group)
            if group is None:
                group = btn
                btn.set_active(True)
            btn.connect("toggled", on_encryption_option_toggled, field_name)
            encryption_options_box.append(btn)


        def toggle_encryption_options(btn):
            enabled = btn.get_active()
            encryption_options_box.set_sensitive(enabled)

        encryption_button.connect("toggled", toggle_encryption_options)
        toggle_encryption_options(encryption_button)

        self.partition_display_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.partition_display_area.set_margin_start(10)
        self.partition_display_area.set_size_request(-1, 100)
        self.partition_display_area.set_vexpand(True)
        main_box.append(self.partition_display_area)

        disk_combo.connect("changed", lambda _: self.on_disk_selected(disk_combo))

        if disk_combo.get_active() != -1:
            self.on_disk_selected(disk_combo)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(20)
        btn_box.set_halign(Gtk.Align.END)

        back_btn = Gtk.Button(label="Back")
        back_btn.connect('clicked', lambda _: self.go_to_slide(InstallerSlide.KEYBOARD))

        next_btn = Gtk.Button(label="Continue", css_classes=['suggested-action'])
        next_btn.connect('clicked', lambda _: self.go_to_slide(InstallerSlide.USERS))

        btn_box.append(back_btn)
        btn_box.append(next_btn)
        main_box.append(btn_box)

        return scrolled_window

    def on_manual_partitioning_clicked(self, button):
        try:
            subprocess.run(["gparted"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error launching gparted: {e}")

    def on_size_slider_value_changed(self, scale):
        value = scale.get_value()
        self.size_value_label.set_label(f"{int(value)} GB")
        backend.data.install_alongside_size = value / 1024
        if self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE and self.partition_manager.selected_partition_for_alongside and self.partition_bar:
            self.partition_bar.alloy_partition_size_gb = value
            self.partition_bar.selected_partition_total_size_bytes = self.partition_manager.selected_partition_size
            self.partition_bar.queue_draw()

    def update_size_slider(self, partition_size_bytes):
        self.partition_manager.selected_partition_size = partition_size_bytes

        partition_size_gb = partition_size_bytes / (1024 ** 3)
        min_size_gb = 10

        self.size_adjustment.set_lower(min_size_gb)
        self.size_adjustment.set_upper(max(min_size_gb, partition_size_gb))
        self.size_adjustment.set_value(max(min_size_gb, partition_size_gb))
        self.max_size_label.set_label(f"{int(max(min_size_gb, partition_size_gb))} GB")
        

        if self.partition_bar:
            self.partition_bar.alloy_partition_size_gb = self.size_adjustment.get_value()
            self.partition_bar.selected_partition_total_size_bytes = self.partition_manager.selected_partition_size
            self.partition_bar.queue_draw()

    def on_partition_selected(self, part_name, part_size_bytes=0):
        if self.current_partitioning_mode == PartitioningMode.REPLACE_PARTITION:
            self.partition_manager.set_selected_partition(part_name, part_size_bytes)
            self.selected_partition_value.set_label(f"/dev/{part_name}" if part_name else "None")
            self.current_partition_label.set_label(
                f"Partition: /dev/{part_name}" if part_name else "Partition: None selected")
            self.update_size_slider(part_size_bytes)
            self.size_adjustment.set_value(self.size_adjustment.get_upper())
            if self.partition_bar:
                self.partition_bar.selected_partition = self.partition_manager.selected_partition
                self.partition_bar.queue_draw()
        else:
            self.partition_manager.set_selected_partition(None)
            self.selected_partition_value.set_label("None")
            self.current_partition_label.set_label("Partition: None selected")

        if self.partition_manager.selected_disk_name:
            self.update_partition_display(self.partition_manager.selected_disk_name)
        backend.data.selected_partition = part_name

    def on_partition_selected_alongside(self, part_name, part_size_bytes):
        self.partition_manager.set_selected_partition_for_alongside(part_name, part_size_bytes)
        self.update_size_slider(part_size_bytes)
        self.current_partition_label.set_label(f"Partition: /dev/{part_name}" if part_name else "Partition: None selected")

        if self.partition_bar:
            self.partition_bar.selected_partition = self.partition_manager.selected_partition_for_alongside
            self.partition_bar.queue_draw()

        if self.partition_manager.selected_disk_name:
            self.update_partition_display(self.partition_manager.selected_disk_name)

    def update_option_ui(self, install_alongside_radio, replace_partition_radio, erase_disk_radio, disk_combo):
        old_mode = self.current_partitioning_mode

        if install_alongside_radio.get_active():
            self.current_partitioning_mode = PartitioningMode.INSTALL_ALONGSIDE
            backend.data.partitioning_mode = PartitioningMode.INSTALL_ALONGSIDE
        elif replace_partition_radio.get_active():
            self.current_partitioning_mode = PartitioningMode.REPLACE_PARTITION
            self.size_adjustment.set_value(self.size_adjustment.get_upper())
            backend.data.partitioning_mode = PartitioningMode.REPLACE_PARTITION
        elif erase_disk_radio.get_active():
            self.current_partitioning_mode = PartitioningMode.ERASE_DISK
            backend.data.partitioning_mode = PartitioningMode.ERASE_DISK

        if old_mode == PartitioningMode.INSTALL_ALONGSIDE and self.current_partitioning_mode == PartitioningMode.REPLACE_PARTITION and self.partition_manager.selected_partition_for_alongside:
            self.partition_manager.selected_partition = self.partition_manager.selected_partition_for_alongside
            self.selected_partition_value.set_label(f"/dev/{self.partition_manager.selected_partition}" if self.partition_manager.selected_partition else "None")

        self.selected_partition_box.set_visible(self.current_partitioning_mode == PartitioningMode.REPLACE_PARTITION)

        if self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE:
            self.size_slider_frame.set_visible(True)
        else:
            self.size_slider_frame.set_visible(False)

        if self.current_partitioning_mode != PartitioningMode.REPLACE_PARTITION:
            self.partition_manager.selected_partition = None
            self.selected_partition_value.set_label("None")

        if self.current_partitioning_mode != PartitioningMode.INSTALL_ALONGSIDE:
            self.partition_manager.selected_partition_for_alongside = None

        if self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE and self.partition_manager.selected_partition_for_alongside:
            self.current_partition_label.set_label(f"Partition: /dev/{self.partition_manager.selected_partition_for_alongside}")
        elif self.current_partitioning_mode == PartitioningMode.REPLACE_PARTITION and self.partition_manager.selected_partition:
            self.current_partition_label.set_label(f"Partition: /dev/{self.partition_manager.selected_partition}")
        else:
            self.current_partition_label.set_label("Partition: None selected")

        if disk_combo.get_active() != -1:
            self.on_disk_selected(disk_combo)

    def update_partition_display(self, selected_disk_name):
        while self.partition_display_area.get_first_child():
            self.partition_display_area.remove(self.partition_display_area.get_first_child())

        if not selected_disk_name:
            self.partition_display_area.append(Gtk.Label(label="Please select a disk.", xalign=0))
            return

        selected_device = self.partition_manager.get_partition_info(selected_disk_name)


        if selected_device and selected_device.get("children"):
            total_disk_size = int(selected_device.get("size", 0))
            partitions_to_display = [child for child in selected_device.get("children", [])
                                     if child.get("type") == "part"]

            if self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE and partitions_to_display:
                if self.partition_manager.selected_partition_for_alongside:
                    selected_part = next(
                        (p for p in partitions_to_display if p.get("name") == self.partition_manager.selected_partition_for_alongside),
                        None)
                    if selected_part:
                        part_size_bytes = int(selected_part.get("size", 0))
                        self.update_size_slider(part_size_bytes)

            if self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE:
                def partition_bar_alongside_callback(part_name, part_size_bytes):
                    self.on_partition_selected_alongside(part_name, part_size_bytes)

                if self.partition_bar is None:
                    self.partition_bar = PartitionBar(partitions_to_display, total_disk_size,
                                                 partition_bar_alongside_callback,
                                                 alloy_partition_size_gb=self.size_adjustment.get_value(),
                                                 selected_partition_total_size_bytes=self.partition_manager.selected_partition_size,
                                                 erase_disk=(
                                                         self.current_partitioning_mode == PartitioningMode.ERASE_DISK),
                                                 current_partitioning_mode=self.current_partitioning_mode)
                else:
                    self.partition_bar.partitions = partitions_to_display
                    self.partition_bar.total_size = total_disk_size
                    self.partition_bar.alloy_partition_size_gb = self.size_adjustment.get_value()
                    self.partition_bar.selected_partition_total_size_bytes = self.partition_manager.selected_partition_size
                    self.partition_bar.on_partition_selected = partition_bar_alongside_callback
                    self.partition_bar.erase_disk = (self.current_partitioning_mode == PartitioningMode.ERASE_DISK)
                    self.partition_bar.queue_draw()

                if self.partition_manager.selected_partition_for_alongside:
                    self.partition_bar.selected_partition = self.partition_manager.selected_partition_for_alongside
                    if hasattr(self.partition_bar, 'update_selection'):
                        self.partition_bar.update_selection()
            else:
                if self.partition_bar is None:
                    self.partition_bar = PartitionBar(partitions_to_display, total_disk_size, self.on_partition_selected,
                                                 erase_disk=(
                                                         self.current_partitioning_mode == PartitioningMode.ERASE_DISK),
                                                 current_partitioning_mode=self.current_partitioning_mode)
                else:
                    self.partition_bar.partitions = partitions_to_display
                    self.partition_bar.total_size = total_disk_size
                    self.partition_bar.on_partition_selected = self.on_partition_selected
                    self.partition_bar.erase_disk = (self.current_partitioning_mode == PartitioningMode.ERASE_DISK)
                    self.partition_bar.queue_draw()

                if self.partition_manager.selected_partition:
                    self.partition_bar.selected_partition = self.partition_manager.selected_partition
                    if hasattr(self.partition_bar, 'update_selection'):
                        self.partition_bar.update_selection()
            self.partition_display_area.append(self.partition_bar)

            legend_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            legend_box.set_margin_top(10)
            self.partition_display_area.append(legend_box)

            for part in partitions_to_display:
                part_name = part.get("name")
                part_size = int(part.get("size", 0))
                part_fstype = part.get("fstype", "unknown")
                part_mountpoint = part.get("mountpoint", "")
                part_size_hr = human_readable_size(part_size)
                os_guess = get_os(part_fstype)

                legend_entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                legend_entry_box.set_halign(Gtk.Align.START)
                legend_entry_box.set_valign(Gtk.Align.CENTER)

                if self.current_partitioning_mode == PartitioningMode.REPLACE_PARTITION:
                    legend_entry_box.set_css_classes(['clickable-entry'])

                    click_controller = Gtk.GestureClick()
                    legend_entry_box.add_controller(click_controller)

                    def on_partition_click(p=part):
                        part_size_bytes = int(p.get("size", 0))
                        self.on_partition_selected(p.get("name"), part_size_bytes)

                    click_controller.connect("pressed", on_partition_click)

                elif self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE:
                    legend_entry_box.set_css_classes(['clickable-entry'])
                    click_controller = Gtk.GestureClick()
                    legend_entry_box.add_controller(click_controller)

                    def on_partition_click_alongside(gesture, clicks, x, y, p=part):
                        part_size_bytes = int(p.get("size", 0))
                        self.on_partition_selected_alongside(p.get("name"), part_size_bytes)

                    click_controller.connect("pressed", on_partition_click_alongside)

                color_square = Gtk.Box()
                color_square.set_size_request(20, 20)

                is_selected = False
                if self.current_partitioning_mode == PartitioningMode.REPLACE_PARTITION and part_name == self.partition_manager.selected_partition:
                    is_selected = True
                elif self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE and part_name == self.partition_manager.selected_partition_for_alongside:
                    is_selected = True

                if not part_fstype:
                    color_class = "color-unknown"
                else:
                    clean_fstype = part_fstype.strip().lower()
                    color_class = FSTYPE_COLOR_CLASSES.get(clean_fstype, "color-unknown")

                if is_selected:
                    color_square.set_css_classes(['color-square', color_class, 'color-selected'])
                else:
                    color_square.set_css_classes(['color-square', color_class])

                legend_entry_box.append(color_square)

                label_text = f"/dev/{part_name} - {part_size_hr} [Type: {part_fstype}"
                if part_mountpoint:
                    label_text += f", Mount: {part_mountpoint}"
                label_text += f", OS: {os_guess}]"

                part_label = Gtk.Label(label=label_text, xalign=0)
                if is_selected:
                    part_label.set_css_classes(['bold'])
                legend_entry_box.append(part_label)

                legend_box.append(legend_entry_box)

        else:
            self.partition_display_area.append(
                Gtk.Label(label=f"No partitions found on /dev/{selected_disk_name} or device not parsed.",
                          xalign=0))

    def on_disk_selected(self, combo_box):
        selected_text = combo_box.get_active_text()
        all_disks_info = self.partition_manager.all_disks_info
        if selected_text in all_disks_info:
            selected_disk_name = all_disks_info[selected_text]
            self.partition_manager.set_selected_disk(selected_disk_name)
            self.current_disk_label.set_label(f"Disk: /dev/{selected_disk_name}")
            backend.data.selected_disk = selected_disk_name
            self.update_partition_display(selected_disk_name)
        else:
            self.current_disk_label.set_label("Disk: None selected")
            self.current_partition_label.set_label("Partition: None selected")
            self.update_partition_display(None)
