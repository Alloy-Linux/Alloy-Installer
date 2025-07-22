{ pkgs, ... }: {
  imports = [ ../../modules/desktop/gnome.nix ];
  boot.kernelPackages = pkgs.linuxPackages;
  boot.kernelParams = [ ];
  boot.blacklistedKernelModules = [ ];
}
