from .constants import FSTYPE_COLORS_RGBA, PartitioningMode
from gi.repository import Gtk

class PartitionBar(Gtk.DrawingArea):
    MIN_SEGMENT_WIDTH_PIXELS = 10

    def __init__(self, partitions, total_size, on_partition_selected=None, alloy_partition_size_gb=0, selected_partition_total_size_bytes=0, erase_disk=False, current_partitioning_mode=None):
        super().__init__()
        self.set_draw_func(self.on_draw)
        self.set_hexpand(True)
        self.set_vexpand(False)
        self.set_size_request(-1, 50)

        self.partitions = partitions
        self.total_size = total_size
        self.on_partition_selected = on_partition_selected
        self.selected_partition = None
        self.alloy_partition_size_gb = alloy_partition_size_gb
        self.selected_partition_total_size_bytes = selected_partition_total_size_bytes
        self.erase_disk = erase_disk
        self.current_partitioning_mode = current_partitioning_mode

        click_controller = Gtk.GestureClick()
        self.add_controller(click_controller)
        click_controller.connect("pressed", self.on_bar_clicked)

    def on_bar_clicked(self, x):
        if not self.on_partition_selected or not self.partitions:
            return

        width = self.get_allocated_width()
        current_x = 0

        initial_widths = []
        small_partitions_count = 0
        total_size_of_large_partitions = 0

        for part in self.partitions:
            part_size = int(part.get("size", 0))
            initial_width = (part_size / self.total_size) * width if self.total_size > 0 else 0
            initial_widths.append(initial_width)

            if initial_width < self.MIN_SEGMENT_WIDTH_PIXELS:
                small_partitions_count += 1
            else:
                total_size_of_large_partitions += part_size

        min_width_consumed = small_partitions_count * self.MIN_SEGMENT_WIDTH_PIXELS
        remaining_width_for_proportional_parts = max(0, width - min_width_consumed)

        for i, part in enumerate(self.partitions):
            part_size = int(part.get("size", 0))
            segment_width = initial_widths[i]

            if segment_width < self.MIN_SEGMENT_WIDTH_PIXELS:
                segment_width = self.MIN_SEGMENT_WIDTH_PIXELS
            else:
                segment_width = (part_size / total_size_of_large_partitions) * remaining_width_for_proportional_parts if total_size_of_large_partitions > 0 else self.MIN_SEGMENT_WIDTH_PIXELS

            if current_x <= x < current_x + segment_width:
                self.selected_partition = part.get("name")
                self.on_partition_selected(self.selected_partition, part_size)
                self.queue_draw()
                return

            current_x += segment_width

    def on_draw(self, cr, width, height):
        global alloy_width
        cr.set_line_width(1)

        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        if self.erase_disk:
            color = FSTYPE_COLORS_RGBA["selected"]
            cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
            cr.rectangle(0, 0, width, height)
            cr.fill_preserve()
            cr.set_source_rgb(0.2, 0.2, 0.2)
            cr.set_line_width(2)
            cr.stroke()
            return

        if self.total_size == 0 or not self.partitions:
            cr.set_source_rgb(0.5, 0.5, 0.5)
            cr.rectangle(0, 0, width, height)
            cr.set_line_width(2)
            cr.stroke()
            return

        initial_widths = []
        small_partitions_count = 0
        total_size_of_large_partitions = 0

        for part in self.partitions:
            part_size = int(part.get("size", 0))
            initial_width = (part_size / self.total_size) * width if self.total_size > 0 else 0
            initial_widths.append(initial_width)

            if initial_width < self.MIN_SEGMENT_WIDTH_PIXELS:
                small_partitions_count += 1
            else:
                total_size_of_large_partitions += part_size

        min_width_consumed = small_partitions_count * self.MIN_SEGMENT_WIDTH_PIXELS
        remaining_width_for_proportional_parts = max(0, width - min_width_consumed)

        current_x = 0

        for i, part in enumerate(self.partitions):
            part_size = int(part.get("size", 0))
            part_fstype = part.get("fstype")
            part_name = part.get("name")

            segment_width = initial_widths[i]

            if segment_width < self.MIN_SEGMENT_WIDTH_PIXELS:
                segment_width = self.MIN_SEGMENT_WIDTH_PIXELS
            else:
                segment_width = (part_size / total_size_of_large_partitions) * remaining_width_for_proportional_parts if total_size_of_large_partitions > 0 else self.MIN_SEGMENT_WIDTH_PIXELS

            if part_name == self.selected_partition and \
               ((self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE and self.alloy_partition_size_gb > 0 and self.selected_partition_total_size_bytes > 0) or
                (self.current_partitioning_mode == PartitioningMode.REPLACE_PARTITION)):
                if self.current_partitioning_mode == PartitioningMode.INSTALL_ALONGSIDE:
                    alloy_width = (self.alloy_partition_size_gb * (1024**3) / self.selected_partition_total_size_bytes) * segment_width
                elif self.current_partitioning_mode == PartitioningMode.REPLACE_PARTITION:
                    alloy_width = segment_width
                else:
                    pass

                remaining_width = segment_width - alloy_width

                alloy_color = FSTYPE_COLORS_RGBA["selected"]
                cr.set_source_rgba(alloy_color.red, alloy_color.green, alloy_color.blue, alloy_color.alpha)
                cr.rectangle(current_x, 0, alloy_width, height)
                cr.fill_preserve()
                cr.set_source_rgb(0.2, 0.2, 0.2)
                cr.stroke()

                original_color = FSTYPE_COLORS_RGBA.get(part_fstype, FSTYPE_COLORS_RGBA["unknown"])
                cr.set_source_rgba(original_color.red, original_color.green, original_color.blue, original_color.alpha)
                cr.rectangle(current_x + alloy_width, 0, remaining_width, height)
                cr.fill_preserve()
                cr.set_source_rgb(0.2, 0.2, 0.2)
                cr.stroke()

            else:
                color = FSTYPE_COLORS_RGBA.get(part_fstype, FSTYPE_COLORS_RGBA["unknown"])
                cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
                cr.rectangle(current_x, 0, segment_width, height)
                cr.fill_preserve()
                cr.set_source_rgb(0.2, 0.2, 0.2)
                cr.stroke()

            current_x += segment_width

        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(0, 0, width, height)
        cr.set_line_width(2)
        cr.stroke()

    def update_selection(self):
        self.queue_draw()
