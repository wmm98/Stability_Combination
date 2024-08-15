import serial.tools.list_ports
from configfile import ConfigP
import subprocess

conf_file = ConfigP(ConfigP.background_config_file_path)


class Shell:
    @staticmethod
    def invoke(cmd, runtime=120):
        try:
            output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              creationflags=subprocess.CREATE_NO_WINDOW).communicate(timeout=runtime)
            o = output.decode("utf-8")
            return o
        except subprocess.TimeoutExpired as e:
            print(e)


shell = Shell()


class PreInfo:
    def __init__(self):
        pass

    def get_devices_list(self):
        devices_info = shell.invoke("adb devices").split("\r\n")[1:-2]
        devices = [device_str.split("\t")[0] for device_str in devices_info if device_str.split("\t")[1] == "device"]

        conf_file.add_config_section(conf_file.section_background_to_ui)
        conf_file.add_config_option(conf_file.section_background_to_ui, conf_file.bg_option_devices_name,
                                    ",".join(devices))

    def get_COM_ports(self):
        serial_list = []
        ports = list(serial.tools.list_ports.comports())
        if len(ports) != 0:
            for port in ports:
                if 'SERIAL' in port.description:
                    COM_name = port.device.replace("\n", "").replace(" ", "").replace("\r", "")
                    serial_list.append(COM_name)
            conf_file.add_config_option(conf_file.section_background_to_ui, conf_file.bg_option_COM_ports,
                                        ",".join(serial_list))
        else:
            conf_file.add_config_option(conf_file.section_background_to_ui, conf_file.bg_option_COM_ports, "")


if __name__ == '__main__':
    info = PreInfo()
    info.get_devices_list()
    info.get_COM_ports()
