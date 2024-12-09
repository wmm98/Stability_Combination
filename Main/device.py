from Common.config import Config
from Common.log import MyLog
from Common.process_shell import Shell
from Main.public import publicInterface
from androguard.core.bytecodes.apk import APK
import time

log = MyLog()
shell = Shell()


class Device(publicInterface):
    def __init__(self, device):
        self.device_name = device
        self.camera_package_name = ""

    def start_app(self, package_name):
        self.send_adb_shell_command("monkey -p %s -c android.intent.category.LAUNCHER 1" % package_name)

    def get_connected_bt_mac(self):
        res = self.send_adb_shell_command("\"dumpsys bluetooth_manager |grep mCurrentDevice\"")
        connected_mac = res.split(":", 1)[1].strip()
        return connected_mac

    def bt_is_connected(self):
        res = self.send_adb_shell_command("\"dumpsys bluetooth_manager |grep ConnectionState\"")
        if "STATE_CONNECTED" in res:
            return True
        else:
            return False

    def network_is_unreachable(self, net_card):
        res = self.send_adb_shell_command("ping -c 4 -I wlan0 www.baidu.com")
        if self.deal_string("Network is unreachable") in self.deal_string(res):
            return True
        else:
            return False

    def is_screen_on(self):
        res = self.send_adb_shell_command("\"dumpsys window | grep mAwake\"")
        if "mAwake=true".upper() in self.deal_string(res):
            return True
        else:
            return False

    def is_eth0_internet(self, times=4):
        res = self.send_adb_shell_command("ping -c %d -I eht0 www.baidu.com" % times)
        # "%d packets transmitted, %d received, 0% packet loss" % (times, times)
        if self.deal_string(
                "%d packets transmitted, %d received, 0%%  packet loss" % (times, times)) in self.deal_string(res):
            return True
        else:
            return False
        # 处理下以太网的情况

    def is_wifi_internet(self, times=4):
        res = self.send_adb_shell_command("ping -c %d -I wlan0 www.baidu.com" % times)
        # 处理下wifi的情况
        if self.deal_string(
                "%d packets transmitted, %d received, 0%%  packet loss" % (times, times)) in self.deal_string(res):
            return True
        else:
            return False

    def is_mobile_internet(self, card_name, times):
        cmd = "ping -c %d -I %s www.baidu.com" % (card_name, times)
        res = self.send_adb_shell_command("ping -c 4 -I rmnet_data2 www.baidu.com")
        # 处理下wifi的情况
        if self.deal_string(
                "%d packets transmitted, %d received, 0%%  packet loss" % (times, times)) in self.deal_string(res):
            return True
        else:
            return False

    def back_home(self):
        self.send_adb_shell_command("input keyevent KEYCODE_BACK")

    def unlock(self):
        self.send_adb_shell_command("input swipe 300 500 300 0")

    def press_power_button(self):
        self.send_adb_shell_command("input keyevent KEYCODE_POWER")

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
        return True if "1" in boot_res else False

    def adb_btn_open(self):
        shell.invoke("adb -s %s shell setprop persist.telpo.debug.mode 1" % self.device_name)

    # Send adb standalone command Send adb shell command
    def send_adb_shell_command(self, cmd):
        cmd = "adb -s %s shell %s" % (self.device_name, cmd)
        # log.info(cmd)
        return shell.invoke(cmd)

    def get_file_md5_value(self, file_path):
        return self.send_adb_shell_command("md5sum %s | awk '{print $1}'" % file_path).strip()

    def send_adb_standalone_command(self, cmd):
        return shell.invoke("adb -s %s %s" % (self.device_name, cmd))

    def install_app(self, apk_path):
        self.send_adb_standalone_command("install -r %s" % apk_path)

    def uninstall_app(self, package_name):
        self.send_adb_shell_command("pm uninstall %s" % package_name)

    def external_app_installed_list(self):
        return self.send_adb_shell_command("pm list package -3")

    def app_is_installed(self, package_name):
        return True if package_name in self.external_app_installed_list() else False

    def adb_push_file(self, source, destination):
        self.send_adb_standalone_command("push %s %s" % (source, destination))

    def adb_pull_file(self, source, destination):
        self.send_adb_standalone_command("pull %s %s" % (source, destination))

    def rm_file(self, file_path):
        self.send_adb_shell_command("rm %s" % file_path)

    def rm_directory(self, dir_path):
        self.send_adb_shell_command("rm -rf %s" % dir_path)

    def touch_file(self, file_path):
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
            network_info = self.send_adb_shell_command(cmd)
            if network_info is not None:
                res = self.remove_info_space(network_info)
                log.info(res[:100])
                if len(res) != 0 and exp not in res:
                    return True
            if self.get_current_time() > self.return_end_time(now_time, timeout):
                return False
            time.sleep(3)

    def is_no_network(self, times=5, timeout=60):
        cmd = " ping -c %s %s" % (times, "www.baidu.com")
        exp = self.remove_info_space("ping: unknown host %s" % "www.baidu.com")
        now_time = self.get_current_time()
        while True:
            res = self.remove_info_space(self.send_adb_shell_command(cmd))
            if exp in res or len(res) == 0:
                return True
            if self.get_current_time() > self.return_end_time(now_time, timeout):
                return False
            time.sleep(3)

    def open_camera(self):
        shell.invoke("adb -s %s shell \"am start -a android.media.action.STILL_IMAGE_CAMERA\"" % self.device_name)

    def take_photo(self):
        shell.invoke("adb -s %s shell \"input keyevent 27\"" % self.device_name)

    def screen_shot(self, des_path, display_id=0):
        if display_id == 0:
            shell.invoke("adb -s %s exec-out screencap -p > %s" % (self.device_name, des_path))
        else:
            shell.invoke("adb -s %s exec-out screencap -d %d -p > %s" % (self.device_name, 1, des_path))

    def remove_img(self):
        shell.invoke("adb -s %s shell \"rm -rf /sdcard/DCIM/Camera/*\"" % self.device_name)

    def click_btn(self, x, y):
        cmd = "adb -s %s shell \"input tap %s %s\"" % (self.device_name, x, y)
        shell.invoke(cmd)

    def is_first_camera(self):
        if self.get_camera_id() == 1:
            return True
        else:
            return False

    def is_second_camera(self):
        if self.get_camera_id() == 2:
            return True
        else:
            return False

    def get_camera_id(self):
        cmd = "adb -s %s shell \"dumpsys media.camera |grep \"\"Camera ID\"\"" % self.device_name
        camera_info = shell.invoke(cmd)
        clear_info = camera_info.replace('\r', '').replace('\t', '').replace(' ', '').replace('\n', '')
        if "CameraId:0".upper() in clear_info.upper():
            return 1
        elif "CameraId:1".upper() in clear_info.upper() or "CameraId:2".upper() in clear_info.upper():
            return 2
        else:
            # no open camera
            return 3

    def get_latest_img(self):
        cmd = "adb -s %s shell \"ls /sdcard/DCIM/Camera\"" % self.device_name
        img_info = shell.invoke(cmd)
        if len(img_info) == 0:
            return ""
        else:
            return img_info.strip()

    def pull_img(self, des_path):
        cmd = "adb -s %s pull /sdcard/DCIM/Camera/%s %s" % (self.device_name, self.get_latest_img(), des_path)
        shell.invoke(cmd)

    def get_camera_package_name(self):
        # cmd = "dumpsys activity activities | grep mCurrentFocus"
        cmd = "adb -s %s shell \"dumpsys activity activities | grep mCurrentFocus\"" % self.device_name
        res = shell.invoke(cmd)
        package_name = res.split(" ")[-1].split("/")[0]
        self.camera_package_name = package_name

    def force_stop_camera_app(self):
        # cmd = "am force-stop  org.codeaurora.snapcam"
        cmd = "adb -s %s shell \"am force-stop %s\"" % (self.device_name, self.camera_package_name)
        shell.invoke(cmd)

    def clear_camera_app(self):
        cmd = "adb -s %s shell \"pm clear %s\"" % (self.device_name, self.camera_package_name)
        shell.invoke(cmd)

    def force_stop_app(self, package_name):
        # cmd = "am force-stop  org.codeaurora.snapcam"
        cmd = "adb -s %s shell \"am force-stop %s\"" % (self.device_name, package_name)
        shell.invoke(cmd)

    def clear_app(self, package_name):
        cmd = "adb -s %s shell \"pm clear %s\"" % (self.device_name, package_name)
        shell.invoke(cmd)

    def get_screen_center_position(self):
        cmd = "adb -s %s shell \"wm size\"" % self.device_name
        res = shell.invoke(cmd)
        info = res.split(" ")[-1].split("x")
        width = info[0]
        length = info[1].replace("\n", "").replace("\r", "").replace("\t", "")
        center_position = [int(width) / 2, int(length) / 2]
        return center_position

    def logcat_thread(self, log_path):
        # sdcard/camera.txt
        self.send_adb_shell_command("\"setsid logcat > %s &\"" % log_path)

    def get_current_logcat_process_id(self):
        process_id = self.send_adb_shell_command("\"ps -A | grep logcat | awk '{print $2}'\"")
        return process_id

    def kill_process(self, process_id):
        self.send_adb_shell_command("\"kill -9 %s\"" % process_id)

    def load_apk_package(self, path):
        apk = APK(path)
        return apk

    def get_apk_package_name(self, apk_file_path):
        try:
            return self.load_apk_package(apk_file_path).get_package()
        except Exception as e:
            log.error("获取apk包名出错")
            log.error(str(e))

    def connect_wifi(self, name, password):
        self.send_adb_shell_command("cmd wifi connect-network %s wpa2 %s" % (name, password))

    def get_wlan_mac(self):
        cmd = "cat sys/class/net/wlan0/address"
        return self.send_adb_shell_command(cmd)

    def scan_wifi(self):
        cmd = "\"cmd wifi start-scan\""
        self.send_adb_shell_command(cmd)

    def get_wifi_scan_list(self):
        cmd = "\"cmd wifi list-scan-results | awk '{print $3 \"            \" $5}'\""
        return self.send_adb_shell_command(cmd)

    def get_current_online_interface(self):
        result = self.send_adb_shell_command("dumpsys connectivity |grep -A 1 \"Idle timers\"| awk '!/Idle timers/'|awk '{print $1}'")
        if len(result) != 0:
            current_online_interface = result.split(":")[0]
        else:
            current_online_interface = None
        return current_online_interface

    def get_route_table(self):
        """
        查看活动连接
            通过查看路由表查看是否有通过 以太网， wlan0和移动数据的路由
            没有即表示以太网或者wlan或者移动数据为下电状态,此目的主要是用来查询移动流量数据下电，后续优化，disable eth0后，超过两行数据即表示 移动数据还下电，间接方法
            netstat -r 指令查询:
            Kernel IP routing table
            Destination     Gateway         Genmask         Flags   MSS Window  irtt Iface
            10.29.14.128    *               255.255.255.224 U         0 0          0 rmnet_data3
            192.168.60.0    *               255.255.255.0   U         0 0          0 wlan0
            注意：netstat -r | awk 'NR > 2' 可以打印第二行之后的数据：
            10.29.14.128    *               255.255.255.224 U         0 0          0 rmnet_data3
            192.168.60.0    *               255.255.255.0   U         0 0          0 wlan0
        """
        return self.send_adb_shell_command("netstat -r | awk 'NR > 2'")


if __name__ == '__main__':
    dev = Device("d")
    dev.logcat_thread("/sdcard/camera2.txt")
    process_id = dev.get_current_logcat_process_id()
    print(process_id)
    dev.kill_process(process_id)
    print("====")
    print(dev.get_current_logcat_process_id())
