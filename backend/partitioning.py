import os
import re
import subprocess

import data
from backend.luks import enable_luks
from backend.make_config import create_config
from ui.partitions.constants import PartitioningMode

boot_partition_size = 1024
swap_partition_size = 4092

def start_partitioning():
    if (data.location != "" and
        data.keyboard_layout != "" and
        data.keyboard_variant != "" and
        data.selected_disk != "" and
        data.hostname != "" and
        data.username != "" and
        data.user_password != "" and
        data.root_password != "" and
        data.desktop_environment != ""):

        if data.partitioning_mode in [PartitioningMode.REPLACE_PARTITION, PartitioningMode.INSTALL_ALONGSIDE]:
            if data.selected_partition == "":
                print("Selected partition not filled in for this mode!")
                return

        match data.partitioning_mode:
            case PartitioningMode.REPLACE_PARTITION:
                replace_partition(data.selected_partition)
                install_alloy()
            case PartitioningMode.INSTALL_ALONGSIDE:
                install_alongside(data.selected_partition, data.install_alongside_size)
                install_alloy()
            case PartitioningMode.ERASE_DISK:
                erase_disk(data.selected_disk)
                install_alloy()
    else:
        print("Not all required settings were filled in!")

def replace_partition(partition_name: str):
    partition_path = f"/dev/{partition_name}"

    subprocess.run(["sudo", "umount", partition_path], check=True)
    subprocess.run(["sudo", "mkfs.ext4", "-F", partition_path], check=True)
    data.root_partition = partition_name

    disk_path_match = re.match(r"^(/dev/[a-z]+|/dev/nvme\d+n\d+)", partition_path)
    if not disk_path_match:
        raise ValueError(f"Invalid disk path derived from: {partition_path}")
    base_disk_path = disk_path_match.group(1)
    base_disk_name = base_disk_path.replace("/dev/", "")

    data.boot_partition = create_partition(base_disk_path, boot_partition_size, "fat32")
    create_boot_partition(data.boot_partition)

    create_swap_partition(base_disk_name)

def install_alongside(partition_name: str, new_partition_size: int):
    partition_path = f"/dev/{partition_name}"

    part_num_match = re.search(r'(\d+)$', partition_name)
    if not part_num_match:
        raise ValueError(f"Invalid partition name: {partition_name}")
    part_num = part_num_match.group(1)

    subprocess.run([
        "sudo", "parted", "-s", partition_path,
        "resizepart", part_num, f"{new_partition_size}MiB"
    ], check=True)

    disk_path_match = re.match(r"^(/dev/[a-z]+|/dev/nvme\d+n\d+)", partition_path)
    if not disk_path_match:
        raise ValueError(f"Invalid disk path: {partition_path}")
    base_disk_path = disk_path_match.group(1)
    base_disk_name = base_disk_path.replace("/dev/", "")
    data.boot_partition = create_partition(base_disk_path, boot_partition_size, "fat32")
    create_boot_partition(data.boot_partition)
    create_swap_partition(base_disk_name)
    data.root_partition = create_partition(base_disk_path, None, "ext4")
    subprocess.run(["sudo", "mkfs.ext4", "-F", f"/dev/{data.root_partition}"], check=True)

def erase_disk(disk_name: str):
    disk_path = f"/dev/{disk_name}"
    subprocess.run(["sudo", "wipefs", "-a", disk_path], check=True)
    subprocess.run(["sudo", "parted", "-s", disk_path, "mklabel", "gpt"], check=True)

    boot_part = create_partition(disk_path, boot_partition_size, "fat32")
    create_boot_partition(boot_part)
    data.boot_partition = boot_part
    create_swap_partition(disk_name)
    root_part = create_partition(disk_path, None, "ext4")
    subprocess.run(["sudo", "mkfs.ext4", "-F", f"/dev/{root_part}"], check=True)
    data.root_partition = root_part

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

def install_alloy():
    subprocess.run(["sudo", "mount", "/dev/" + data.root_partition, "/mnt"], check=True)
    subprocess.run(["sudo", "mkdir", "-p", "/mnt/boot"], check=True)
    subprocess.run(["sudo", "mount", "/dev/" + data.boot_partition, "/mnt/boot"], check=True)
    subprocess.run(["sudo", "nixos-generate-config", "--root", "/mnt"], check=True)
    enable_luks(data.selected_partition, data.encryption_password)
    create_config()
    subprocess.run(["sudo", "nixos-install"], check=True)

