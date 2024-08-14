import os
from pathlib import Path
from dynaconf import Dynaconf


class Settings:
    def __init__(self):
        super().__init__()
        package_dir = Path(__file__).parent
        default_settings = package_dir / "default_config" / "settings.yaml"
        default_md_path = str(package_dir / "md")

        # Check for user-specified config file path in environment variable
        user_config_path = os.getenv("MARKOPOLIS_CONFIG_PATH")
        config_files = [str(default_settings)]
        if user_config_path:
            config_files.append(user_config_path)

        self._settings = Dynaconf(
            envvar_prefix="MARKOPOLIS",
            settings_files=config_files,
            environments=True,
            load_dotenv=True,
            merge_enabled=True,
        )

        # Set default md_path if not specified in config
        if "md_path" not in self._settings:
            self._settings.set("md_path", default_md_path)

    def __getattr__(self, name):
        return getattr(self._settings, name)

    @property
    def md_path(self):
        return self._settings.get("md_path")

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


settings = Settings.get_instance()
