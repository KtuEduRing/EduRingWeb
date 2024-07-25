import json


class Config:
    def __init__(self, config_file):
        with open(config_file, "rt") as f:
            self.config = json.load(f)

        # --- general ---
        self.production_server: str = self.config["general"]["production_server"]
        self.email_domain: str = self.config["general"]["email_domain"]
        self.timezone: str = self.config["general"]["timezone"]

        # --- app ---
        self.api_token_sha256: str = self.config["app"]["api_token_sha256"]

        self.flask_secret_key: str = self.config["app"]["flask_secret_key"]
        self.flask_port: int = self.config["app"]["flask_port"]
        self.flask_host: str = self.config["app"]["flask_host"]

        # --- api ---
        self.spotify_client_secret: str = self.config["api"]["spotify"]["client_secret"]
        self.spotify_client_id: str = self.config["api"]["spotify"]["client_id"]

        # --- google ---
        self.google_oauth_client_id: str = self.config["api"]["google"]["oauth"][
            "client_id"
        ]
        self.google_oauth_client_secret: str = self.config["api"]["google"]["oauth"][
            "client_secret"
        ]
        self.google_oauth_redirect_uri: str = self.config["api"]["google"]["oauth"][
            "redirect_uri"
        ]

        # --- database ---
        self.mysql_host: str = self.config["db"]["mysql"]["host"]
        self.mysql_port: int = self.config["db"]["mysql"]["port"]
        self.mysql_name: str = self.config["db"]["mysql"]["name"]
        self.mysql_username: str = self.config["db"]["mysql"]["username"]
        self.mysql_password: str = self.config["db"]["mysql"]["password"]

        self.sqlite_path: str = self.config["db"]["sqlite"]["path"]