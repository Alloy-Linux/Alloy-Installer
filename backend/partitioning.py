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
                    install_alongside(data.selected_partition, data.install_alongside_size)
                case PartitioningMode.ERASE_DISK:
                    erase_disk(data.selected_disk)
    else:
        print("Not all settings were filled in!")

def replace_partition(partition_name: str):
    partition_path = f"/dev/{partition_name}"
    subprocess.run(["sudo", "umount", partition_path], check=True)
    subprocess.run(["sudo", "mkfs.ext4", "-F", partition_path], check=True)

def install_alongside(partition_name: str, new_partition_size: int):
    partition_path = f"/dev/{partition_name}"
    subprocess.run([
        "sudo", "parted", "-s", partition_path,
        "resizepart", partition_name[-1], f"{new_partition_size}MiB"
    ], check=True)
    match = re.match(r"^(/dev/[a-z]+)(\d+)$", partition_path)
    disk = match.group(1)
    boot_part = create_partition(disk, boot_partition_size, "fat32")
    create_boot_partition(boot_part)
    create_swap_partition(disk.replace("/dev/", ""))
    root_part = create_partition(disk, None, "ext4")
    subprocess.run(["sudo", "mkfs.ext4", "-F", f"/dev/{root_part}"], check=True)

def erase_disk(disk_name: str):
    disk_path = f"/dev/{disk_name}"
    subprocess.run(["sudo", "wipefs", "-a", disk_path], check=True)
    subprocess.run(["sudo", "parted", "-s", disk_path, "mklabel", "gpt"], check=True)
    boot_part = create_partition(disk_path, boot_partition_size, "fat32")
    create_boot_partition(boot_part)
    create_swap_partition(disk_name)
    root_part = create_partition(disk_path, None, "ext4")
    subprocess.run(["sudo", "mkfs.ext4", "-F", f"/dev/{root_part}"], check=True)

def create_boot_partition(partition_name: str):
    partition_path = f"/dev/{partition_name}"
    subprocess.run(["sudo", "mkfs.fat", "-F", "32", partition_path], check=True)
    match = re.match(r'^(/dev/(?:sd[a-z]+|nvme\d+n\d+))(p?\d+)$', partition_path)
    base_disk = match.group(1)
    partition_number = match.group(2)
    if partition_number.startswith('p'):
        partition_number = partition_number[1:]
    subprocess.run(["sudo", "parted", "-s", base_disk, "set", partition_number, "boot", "on"], check=True)

def create_swap_partition(disk_name: str):
    disk_path = f"/dev/{disk_name}"
    partition_name = create_partition(disk_path, swap_partition_size, "linux-swap")
    subprocess.run(["sudo", "mkswap", f"/dev/{partition_name}"], check=True)
    subprocess.run(["sudo", "swapon", f"/dev/{partition_name}"], check=True)

def create_partition(disk: str, size_mib: int | None, fs_type: str) -> str:
    output = subprocess.check_output(
        ["sudo", "parted", "-s", disk, "unit", "MiB", "print", "free"]
    ).decode()
    free_spaces = re.findall(r"(\d+)\s+MiB\s+(\d+)\s+MiB\s+free", output)
    start, end = max(free_spaces, key=lambda x: int(x[1]) - int(x[0]))
    start, end = int(start), int(end)
    part_end = start + size_mib if size_mib else end
    subprocess.run(
        ["sudo", "parted", "-s", disk, "mkpart", "primary", fs_type, f"{start}MiB", f"{part_end}MiB"],
        check=True,
    )
    parts = subprocess.check_output(["lsblk", "-ln", "-o", "NAME", disk]).decode().splitlines()
    partition_name = [p for p in parts if p != disk.replace("/dev/", "")][-1]
    return partition_name
