import subprocess
from Common.config import Config
from Common.log import MyLog

log = MyLog()


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
            log.error(str(e))


class Device:
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

    def adb_btn_open(self):
        self.shell.invoke("adb -s %s shell setprop persist.telpo.debug.mode 1" % self.device_name)

    # Send adb standalone command Send adb shell command
    def send_adb_shell_command(self, cmd):
        return self.shell.invoke("adb -s %s shell %s" % (self.device_name, cmd))

    def send_adb_standalone_command(self, cmd):
        return self.shell.invoke("adb -s %s %s" % (self.device_name, cmd))

    def adb_push_file(self, source, destination):
        self.send_adb_standalone_command("push %s %s" % (source, destination))

    def adb_pull_file(self, source, destination):
        self.send_adb_standalone_command("pull %s %s" % (source, destination))

    def rm_file(self, file_path):
        self.send_adb_shell_command("touch %s" % file_path)

    def mkdir_directory(self, directory_path):
        self.send_adb_standalone_command("mkdir %s" % directory_path)

    def is_existed(self, str_path):
        directory_path, sub_name = str_path.rsplit("/", 1)
        if sub_name in self.send_adb_shell_command("ls %s" % directory_path):
            return True
        else:
            return False


