{ lib, stdenv, fetchFromGitHub }:

stdenv.mkDerivation {
  pname = "setup-calamares-config";
  version = "0";
  #
  src = fetchFromGitHub {
    owner = "Alloy-Linux";
    repo = "calamares-config";
    rev = "";
    hash = "";
  };

  dontBuild = true;
  dontConfigure = true;

  installPhase = ''
    runHook preInstall

    mkdir -p $out/etc/calamares

    cp -r $src/* $out/etc/calamares/
    runHook postInstall
  '';

  meta = with lib; {
    description = "Unpack calamares config to etc";
    homepage = "https://github.com/Alloy-Linux";
    license = licenses.gpl3;
    maintainers = [ maintainers.miyu ];
    platforms = platforms.linux;
  };
}
