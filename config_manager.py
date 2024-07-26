import yaml


class ConfigManager:

    def __init__(self):
        self.config_path = "config.yaml"
        self.configs = self.read_config()

    def read_config(self):
        with open(self.config_path, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                return None

    def __getitem__(self, item):
        if isinstance(self.configs, dict):
            return self.configs[item]


if __name__ == '__main__':
    c = ConfigManager()
    print(c['products'].keys())