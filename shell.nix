{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
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
  '';
}