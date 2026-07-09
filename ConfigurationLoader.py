from pathlib import Path
import yaml


class ConfigurationLoader:

    def __init__(self, configuration_path: str):
        self.configuration_path = Path(configuration_path)

    def load(self) -> dict:
        """Load experiment configuration."""

        if not self.configuration_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.configuration_path}"
            )

        with self.configuration_path.open("r", encoding="utf-8") as file:
            configuration = yaml.safe_load(file)

        if configuration is None:
            raise ValueError("Configuration file is empty.")

        return configuration