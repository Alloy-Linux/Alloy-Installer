{ ... }: {
  services.xserver.enable = true;
services.xserver.desktopManager.budgie.enable = true;
services.xserver.displayManager.lightdm.enable = true;

  # Audio.
  security.rtkit.enable = true;
  services.pipewire.enable = true;
  services.pipewire.alsa.enable = true;
  services.pipewire.alsa.support32Bit = true;
  services.pipewire.pulse.enable = true;
  services.pipewire.jack.enable = true;

  boot.plymouth.enable = true;
}
