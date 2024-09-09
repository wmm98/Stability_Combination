import subprocess
from Common.config import Config


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
            print(str(e))


class DeviceCheck:
    def __init__(self, device):
        self.shell = Shell()
        self.device_name = device

    def restart_adb(self):
        self.shell.invoke("adb kill-server")
        self.shell.invoke("adb start-server")

    def device_is_online(self):
        devices = self.shell.invoke("adb devices")
        # log.info(device_check.device_is_online())
        if self.device_name + "device" in devices.replace('\r', '').replace('\t', '').replace(' ', ''):
            return True
        else:
            return False

    def device_boot(self):
        boot_res = self.shell.invoke("adb -s %s shell getprop sys.boot_completed" % self.device_name)
        return boot_res

    def device_shutdown(self):
        self.shell.invoke("adb -s %s shell reboot -p" % self.device_name)

    def logcat(self, log_time):
        self.shell.invoke("adb -s %s logcat -t %d >> %s" % (self.device_name, log_time, Config.system_failed_log_path))

    def adb_btn_open(self):
        self.shell.invoke("adb -s %s shell setprop persist.telpo.debug.mode 1" % self.device_name)
