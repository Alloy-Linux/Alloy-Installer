{ pkgs, settings, ... }: {
  home-manager.users.${settings.account.name} = {
    home.packages = with pkgs; [
      glib
      glibc
    ];
    programs.zsh.enable = true;

    programs.fish.enable = false;

    programs.bash.enable = true;

    programs.powerline-go.enable = true;

    programs.atuin.enable = true;
    programs.zoxide.enable = true;

    programs.zoxide.enableFishIntegration = true;
    programs.zoxide.enableBashIntegration = true;
    programs.zoxide.enableZshIntegration = true;

    programs.git.enable = true;
    programs.git.userName = settings.account.name;
    programs.git.userEmail = settings.account.email;
  };
}
