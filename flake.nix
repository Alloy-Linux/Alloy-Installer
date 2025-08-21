{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system: {
      devShell = nixpkgs.legacyPackages.${system}.mkShell {
        buildInputs = with nixpkgs.legacyPackages.${system}; [
          python313
          python313Packages.pygobject3
          python313Packages.pygobject-stubs
          pkg-config
          cairo
          gtk4
          git
          gparted
          parted
        ];

        shellHook = ''
          echo "dev shell loaded"
          alias run='python3 main.py'
        '';
      };
    });
}
