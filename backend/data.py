from ui.partitions.constants import PartitioningMode

location: str = ""

keyboard_layout: str = ""
keyboard_variant: str = ""

full_disk_encryption: bool = False
encryption_password: str = ""
sopin: str = ""
tpm: bool = False
keyfile: bool = False
partitioning_mode: PartitioningMode = PartitioningMode.NONE
selected_disk: str = ""
selected_partition: str = ""
install_alongside_size: int

hostname: str = ""
username: str = ""
user_password: str = ""
root_password: str = ""

desktop_environment: str = ""

root_partition: str = ""
boot_partition: str = ""