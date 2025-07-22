{ pkgs, ... }: {
  imports = [ ];
  boot.kernelPackages = pkgs.linuxPackages;
  boot.kernelParams = [ ];
  boot.blacklistedKernelModules = [ ];
}
