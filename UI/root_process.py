from UI.config_path import UIConfigPath
from UI.configfile import ConfigP
from Common.process_shell import Shell
from Main.device import Device




config_file = ConfigP()
shell = Shell()
dev = Device()

class RootSteps:

    def root_device(self):
        for cmd in config_file.get_option_value(config_file.section_ui_to_background, config_file.ui_option_root_steps):
            shell.invoke(cmd)
            if cmd == "reboot":


