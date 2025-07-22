{
  description = "Nixos config flake";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager.url = "github:nix-community/home-manager/release-25.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
    lanzaboote.url = "github:nix-community/lanzaboote/v0.4.2";
    lanzaboote.inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs = inputs@{ ... }: {
    nixosConfigurations.workstation = inputs.nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      system = "x86_64-linux";
      modules = [
        inputs.lanzaboote.nixosModules.lanzaboote
        inputs.home-manager.nixosModules.home-manager
        ./profile/workstation/hardware.nix
        ./profile/workstation/configuration.nix
        ./compose.nix
      ];
    };
    nixosConfigurations.home = inputs.nixpkgs.lib.nixosSystem {
      specialArgs = { inherit inputs; };
      system = "x86_64-linux";
      modules = [
        inputs.lanzaboote.nixosModules.lanzaboote
        inputs.home-manager.nixosModules.home-manager
        ./profile/home/hardware.nix
        ./profile/home/configuration.nix
        ./compose.nix
      ];
    };
  };
}
