import configparser
import config_path


class ConfigP(config_path.UIConfigPath):
    config = configparser.ConfigParser()

    def add_config_section(self, section):
        self.config.add_section(section)
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)

    def add_config_option(self, section, option, value):
        self.config.set(section, option, value)
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)
