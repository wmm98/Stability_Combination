from Common.config import Config
from Common.log import MyLog
from Common.process_shell import Shell
from Main.public import publicInterface
import time

log = MyLog()
shell = Shell()


class Device(publicInterface):
    def __init__(self, device):
        self.device_name = device

    def restart_adb(self):
        shell.invoke("adb kill-server")
        shell.invoke("adb start-server")

    def reboot(self):
        self.send_adb_standalone_command("reboot")

    def device_is_online(self):
        devices = shell.invoke("adb devices")
        # log.info(device_check.device_is_online())
        if self.device_name + "device" in devices.replace('\r', '').replace('\t', '').replace(' ', ''):
            return True
        else:
            return False

    def device_boot(self):
        boot_res = shell.invoke("adb -s %s shell getprop sys.boot_completed" % self.device_name)
        return boot_res

    def adb_btn_open(self):
        shell.invoke("adb -s %s shell setprop persist.telpo.debug.mode 1" % self.device_name)

    # Send adb standalone command Send adb shell command
    def send_adb_shell_command(self, cmd):
        return shell.invoke("adb -s %s shell %s" % (self.device_name, cmd))

    def send_adb_standalone_command(self, cmd):
        return shell.invoke("adb -s %s %s" % (self.device_name, cmd))

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

    def enable_wifi_btn(self):
        self.send_adb_shell_command("svc wifi enable")

    def disable_wifi_btn(self):
        self.send_adb_shell_command("svc wifi disable")

    def get_wifi_btn_status(self):
        return self.send_adb_shell_command("settings get global wifi_on")

    def wifi_is_enable(self):
        if "1" in self.get_wifi_btn_status():
            return True
        else:
            return False

    def enable_bt_btn(self):
        self.send_adb_shell_command("svc bluetooth enable")

    def disable_bt_btn(self):
        self.send_adb_shell_command("svc bluetooth disable")

    def get_bt_btn_status(self):
        return self.send_adb_shell_command("settings get global bluetooth_on")

    def bt_is_enable(self):
        if "1" in self.get_bt_btn_status():
            return True
        else:
            return False

    def enable_mobile_btn(self):
        self.send_adb_shell_command("svc data enable")

    def disable_mobile_btn(self):
        self.send_adb_shell_command("svc data disable")

    def mobile_is_enable(self):
        info = self.send_adb_shell_command("\"settings list global |grep mobile_data\"")
        # 先暂时设置有10个4G网卡
        flag = 0
        base_mobile = "mobile_data"
        for i in range(1, 8):
            mobile_info = base_mobile + "%d" % i
            mobile_info_detail = base_mobile + "%d=1" % i
            if mobile_info in info:
                if mobile_info_detail in info:
                    flag += 1
                    return True
        if flag == 0:
            return False

    def enable_nfc_btn(self):
        self.send_adb_shell_command("svc nfc enable")

    def disable_nfc_btn(self):
        self.send_adb_shell_command("svc nfc disable")

    def nfc_is_enable(self):
        if "on" in self.send_adb_shell_command("\"dumpsys nfc | grep mState\""):
            return True
        else:
            return False

    def enable_eth0_btn(self):
        self.send_adb_shell_command("ifconfig eth0 up")

    def disable_eth0_btn(self):
        self.send_adb_shell_command("ifconfig eth0 down")

    def eth0_is_enable(self):
        if "eth0" in self.send_adb_shell_command("\"ifconfig | grep eht0\""):
            return True
        else:
            return False

    def get_bt_bonded_devices(self):
        cmd = "dumpsys bluetooth_manager |grep \"BR/EDR\""
        bonded_device_info = self.remove_info_space(self.send_adb_shell_command(cmd))
        return bonded_device_info

    def ping_network(self, times=5, timeout=300):
        # 每隔0.6秒ping一次，一共ping5次
        # ping - c 5 - i 0.6 qq.com
        cmd = " ping -c %s %s" % (times, "www.baidu.com")
        exp = self.remove_info_space("ping: unknown host %s" % "www.baidu.com")
        now_time = self.get_current_time()
        while True:
            res = self.remove_info_space(self.send_adb_shell_command(cmd))
            if exp not in res:
                break
            if self.get_current_time() > self.return_end_time(now_time, timeout):
                assert False, "@@@@超过5分钟无法上网,请检查网络"
            time.sleep(3)
