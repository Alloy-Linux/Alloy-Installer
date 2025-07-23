# Core NixOS configuration applied to all profiles
{ lib, pkgs, ... }:
let
    username = "user";
in
{
  # System basics
  networking.hostName = "alloy-linux";
  time.timeZone = "America/Chicago";

  # Keyboard layout
  services.xserver.layout = "us";
  services.xserver.xkbOptions = "intl";

  # Enable flakes and trust wheel users
  nix.extraOptions = "experimental-features = nix-command flakes";
  nix.settings.trusted-users = [ "@wheel" ];

  # Home Manager setup
  home-manager.useUserPackages = false;
  home-manager.backupFileExtension = "hm-backup";
  home-manager.useGlobalPkgs = false;
  home-manager.users.${username} = {
    programs.home-manager.enable = true;
    home.stateVersion = "25.05";
    home.packages = with pkgs; [
      sbctl # Secure boot
    ];
  };

  environment.systemPackages = with pkgs; [ ];

  security.tpm2.enable = false;


  # System version - don't change after initial install
  system.stateVersion = "25.05";

  # Main user account
  users.users.${username} = {
    isNormalUser = true;
    description = "";
    hashedPassword = "";
    extraGroups = [ "networkmanager" "wheel" ]; # network + sudo access
    uid = 1000;
    shell = pkgs.bash;

  };

  users.users.root.hashedPassword = "";

  # Enable zram swap and firewall
  services.zram-generator.enable = true;

  networking.firewall.enable = true;
  networking.networkmanager.enable = true;
  networking.wireless.enable = lib.mkForce false;

  # Boot config here.
  boot.loader.systemd-boot.enable = lib.mkForce false; # lanzaboote replaces this
  boot.loader.efi.canTouchEfiVariables = true;
  boot.lanzaboote.enable = true;  # Secure boot
  boot.lanzaboote.pkiBundle = "/var/lib/sbctl";
}
