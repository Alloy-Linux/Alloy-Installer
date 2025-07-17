{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    pkg-config
    cairo
    gtk4
  ];

  shellHook = ''
    echo "dev shell loaded"
  '';
}