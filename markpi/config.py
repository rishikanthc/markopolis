import os
from pathlib import Path
from dynaconf import Dynaconf


class Settings:
    def __init__(self):
        super().__init__()
        # Default settings file path (packaged with your application)
        default_settings = Path(__file__).parent / "default_config" / "settings.yaml"

        # Check for user-specified config file path in environment variable
        user_config_path = os.getenv("MARKPI_CONFIG_PATH")

        # Prepare the list of config files
        config_files = [str(default_settings)]
        if user_config_path:
            config_files.append(user_config_path)

        self._settings = Dynaconf(
            envvar_prefix="MARKPI_CONFIG",
            settings_files=config_files,
            environments=True,
            load_dotenv=True,
            merge_enabled=True,  # This ensures that user config overrides default config
        )

    def __getattr__(self, name):
        return getattr(self._settings, name)

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


settings = Settings.get_instance()
