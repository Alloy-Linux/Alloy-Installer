{ pkgs, settings, ... }: {
  home-manager.users.${settings.account.name} = {
    nixpkgs.config.allowUnfree = true;
    home.packages = with pkgs; [
      firefox
    ];
  };
}
