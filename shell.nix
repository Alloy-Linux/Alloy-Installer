{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pygobject3
    pkg-config
    cairo
    gtk4
  ];

  shellHook = ''
    echo "dev shell loaded"
  '';
}