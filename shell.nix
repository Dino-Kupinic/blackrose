let pkgs = import <nixpkgs> { };
in pkgs.mkShell {
  packages = with pkgs; [
    git
    python3
    nodejs_20
    curl
  ];
}
