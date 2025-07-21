import re
import subprocess

import data
from ui.partitions.constants import PartitioningMode

boot_partition_size = 1024
swap_partition_size = 4092

def start_partitioning():
    if (data.location != "" and
        data.keyboard_layout != "" and
        data.keyboard_variant != "" and
        data.selected_disk != "" and
        data.selected_partition != "" and
        data.hostname != "" and
        data.username != "" and
        data.user_password != "" and
        data.root_password != "" and
        data.desktop_environment != "" and
        data.display_server != ""):
            match data.partitioning_mode:
                case PartitioningMode.REPLACE_PARTITION:
                    replace_partition(data.selected_partition)
                case PartitioningMode.INSTALL_ALONGSIDE:
                    pass
                case PartitioningMode.ERASE_DISK:
                    pass
    else:
        print("Not all settings were filled in!")


def replace_partition(partition_name: str):
    partition_path = f"/dev/{partition_name}"
    subprocess.run(["sudo", "umount", partition_path], check=True)
    subprocess.run(["sudo", "mkfs.ext4", "-F", partition_path], check=True)


def create_boot_partition(partition_name: str):
    partition_path = f"/dev/{partition_name}"
    subprocess.run(["sudo", "mkfs.fat", "-F", "32", partition_path], check=True)
    match = re.match(r'^(/dev/(?:sd[a-z]+|nvme\d+n\d+))(p?\d+)$', partition_path)

    if not match:
        raise ValueError(f"Could not find partition: {partition_path}. Unexpected format.")

    base_disk = match.group(1)
    partition_number = match.group(2)

    if partition_number.startswith('p'):
        partition_number = partition_number[1:]

    subprocess.run(["sudo", "parted", "-s", base_disk, "set", partition_number, "boot", "on"], check=True)

def create_swap_partition(disk_name: str):
    disk_path = f"/dev/{disk_name}"
    swap_size_mb = swap_partition_size

    parted_output = subprocess.check_output(["sudo", "parted", "-s", disk_path, "unit", "MiB", "print", "free"]).decode()

    matches = re.findall(r"(\d+)\s+MiB\s+(\d+)\s+MiB\s+free", parted_output)
    if not matches:
        raise RuntimeError(f"No free space found on {disk_path}")

    start_mib, end_mib = max(matches, key=lambda m: int(m[1]) - int(m[0]))
    start = int(start_mib)
    end = start + swap_size_mb
    if end > int(end_mib):
        raise RuntimeError("Not enough free space for swap partition")

    subprocess.run([
        "sudo", "parted", "-s", disk_path, "mkpart", "primary", "linux-swap", f"{start}MiB", f"{end}MiB"
    ], check=True)

    partition_output = subprocess.check_output(["lsblk", "-ln", "-o", "NAME", disk_path]).decode().splitlines()
    new_partition = [line for line in partition_output if line.startswith(disk_name) and line != disk_name][-1]
    new_partition_path = f"/dev/{new_partition}"

    subprocess.run(["sudo", "mkswap", new_partition_path], check=True)
    subprocess.run(["sudo", "swapon", new_partition_path], check=True)
