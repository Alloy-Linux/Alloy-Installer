import gi
gi.require_version('Gtk', '4.0')

from .partition_manager import PartitionManager
from .partition_ui import PartitionUI

def partition_slide(content_area, go_to_slide):
    partition_manager = PartitionManager()
    partition_ui = PartitionUI(partition_manager, go_to_slide)
    main_box = partition_ui.create_ui()

    content_area.append(main_box)
    content_area.show()