import os
import secrets
import subprocess

from backend import data


def enable_luks(partition_device_name: str, encryption_password: str, mapping_name: str = "root"):
    partition_path = f"/dev/{partition_device_name}"

    if encryption_password == "":
        ValueError("Password not set!")

    format_command = [
        "sudo", "cryptsetup", "--batch-mode", "-v", "luksFormat", partition_path
    ]
    subprocess.run(
        format_command,
        input=f"YES\n{encryption_password}\n{encryption_password}\n",
        text=True,
        check=True,
        capture_output=True
    )

    open_command = [
        "sudo", "cryptsetup", "open", partition_path, mapping_name
    ]
    subprocess.run(
        open_command,
        input=f"{encryption_password}\n",
        text=True,
        check=True,
        capture_output=True
    )

    if data.tpm:
        enable_tpm_support(encryption_password)
    elif data.keyfile:
        configure_keyfile(data.selected_partition)

def enable_tpm_support(pin: str):
    hastpm = os.path.exists("/dev/tpmrm0")
    if not hastpm:
        print("This computer does not support TPM 2.0!")
        return

    else:
        config_path = "default-config/profile/home/compose.nix"

        with open(config_path, "r") as f:
            lines = f.readlines()

        with open(config_path, "w") as f:
            for line in lines:
                if line.strip().startswith("security.tpm2.enable"):
                    f.write(f'  security.tpm2.enable = true;\n'
                            f'  security.tpm2.pkcs11.enable = true;\n'
                            f'  security.tpm2.tctiEnvironment.enable = true;\n')
                elif line.strip().startswith('extraGroups = [ "networkmanager" "wheel" ];'):
                    f.write(f'  extraGroups = [ "networkmanager" "wheel" ];\n')
                else:
                    f.write(line)

        subprocess.run(["nix-shell", "-p", "tpm2-tools", "--run", "tpm2_ptool init"])
        subprocess.run(["nix-shell", "-p", "tpm2-tools", "--run", f"tpm2_ptool addtoken --pid=1 --label=ssh --userpin={pin} --sopin={data.sopin}"])
        subprocess.run(["nix-shell", "-p", "tpm2-tools", "--run", f"tpm2_ptool addkey --label=ssh --userpin={pin} --algorithm=ecc256"])

        subprocess.run(["ssh-keygen", "-D", "mnt/run/current-system/sw/lib/libtpm2_pkcs11.so"])
        subprocess.run(["nix-shell", "-p", "tpm2-tools", "PKCS11Provider", "/run/current-system/sw/lib/libtpm2_pkcs11.so"])



def configure_keyfile(
        device: str,
        keyfile_name: str = "cryptkey.bin",
        key_size: int = 4096,
        mount_point: str = "/mnt",
        crypttab_name: str = "cryptroot"
) -> str:
    etc_luks_keys = os.path.join(mount_point, "etc", "luks-keys")
    keyfile_path = os.path.join(etc_luks_keys, keyfile_name)

    os.makedirs(etc_luks_keys, mode=0o700, exist_ok=True)

    with open(keyfile_path, 'wb') as f:
        f.write(secrets.token_bytes(key_size))
    os.chmod(keyfile_path, 0o600)

    subprocess.run([ "nix-shell" "-p" "--run", "cryptsetup", "luksFormat","--key-file", keyfile_path, device], check=True)

    crypttab_path = os.path.join(mount_point, "etc", "crypttab")
    with open(crypttab_path, 'a') as f:
        f.write(
            f"{crypttab_name} {device} {keyfile_path} luks\n"
        )

    return keyfile_path