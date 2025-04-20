{
  description = "Development flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
  };

  outputs =
    { nixpkgs, ... }:
    let
      x86 = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages."${x86}";
    in
    {
      devShells."${x86}".default = pkgs.mkShellNoCC {
        packages = with pkgs; [
          # Python
          (pkgs.python3.withPackages (python-pkgs: [
            python-pkgs.plexapi
          ]))

          # Formatters
          black
          beautysh
          mdformat
          deadnix
          nixfmt-rfc-style
        ];

        shellHook = ''
          git config --local core.hooksPath .githooks/
        '';

        # Environment Variables
        PPCR_BASE_URL = "http://192.168.1.1:32400";
        PPCR_TOKEN = "xxxx";
        PPCR_AMOUNT = 7;
        PPCR_MIN_AMOUNT_IN_COLLECTION = 5;
        PPCR_ALWAYS_PIN = "Plex Popular;Christmas Movies;Easter Movies;Father's Day Movies;Halloween Movies;LGBTQ Month Movies;Mother's Day Movies;New Year's Day Movies;Valentine's Day Movies";
      };
    };
}
