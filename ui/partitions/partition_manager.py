import subprocess
import json
from .utils import human_readable_size


class PartitionManager:
    def get_partition_info(self, disk_name):
        try:
            result = subprocess.run(
                ["lsblk", "--json", "-o", "NAME,TYPE,SIZE,FSTYPE,MOUNTPOINT", "-b", f"/dev/{disk_name}"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"Error getting partition info for {disk_name}: {result.stderr}")
                return None
            data = json.loads(result.stdout)
            selected_device = None
            for device in data.get("blockdevices", []):
                if device.get("name") == disk_name:
                    selected_device = device
                    break
            return selected_device
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error parsing partition info: {e}")
            return None
    def __init__(self):
        self.all_disks_info = {}
        self.selected_disk_name = None
        self.selected_partition = None
        self.selected_partition_size = 0
        self.selected_partition_for_alongside = None

    def get_disks(self):
        try:
            result = subprocess.run(
                ["lsblk", "--json", "-o", "NAME,TYPE,SIZE", "-b"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for device in data.get("blockdevices", []):
                    if device.get("type") == "disk" and not device.get("name").startswith("loop"):
                        name = device.get("name")
                        size = device.get("size")
                        size_hr = human_readable_size(size) if size is not None else "Unknown Size"
                        display_text = f"/{name} - {size_hr}"
                        self.all_disks_info[display_text] = name
                return self.all_disks_info
            else:
                return {}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error getting disks: {e}")
            return {}

    def set_selected_disk(self, disk_name):
        self.selected_disk_name = disk_name

    def set_selected_partition(self, part_name, part_size_bytes=0):
        self.selected_partition = part_name
        self.selected_partition_size = part_size_bytes

    def set_selected_partition_for_alongside(self, part_name, part_size_bytes):
        self.selected_partition_for_alongside = part_name
        self.selected_partition_size = part_size_bytes
