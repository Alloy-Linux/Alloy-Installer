{ ... }: {
  services.xserver.enable = true;
  services.desktopManager.cosmic.enable = true;
  services.displayManager.cosmic-greeter.enable = true;

  security.rtkit.enable = true;
  services.pipewire.enable = true;
  services.pipewire.alsa.enable = true;
  services.pipewire.alsa.support32Bit = true;
  services.pipewire.pulse.enable = true;
  services.pipewire.jack.enable = true;

  boot.plymouth.enable = true;
}
