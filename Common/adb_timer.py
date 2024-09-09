import subprocess
import threading
import time
from Common.device_check import DeviceCheck
from Common.log import MyLog
from Common.m_serial import SerialD

log = MyLog()
ser_ = SerialD()

class ADBChecker:
    def __init__(self, device_name, timeout):
        self.timeout = timeout
        self.timer = None
        self.result = False
        self.usb = False
        self.usb_relay = None
        self.device = DeviceCheck(device_name)

    def start_check(self, boot=False):
        self.timer = threading.Timer(self.timeout, self.timeout_handler)
        self.timer.start()
        if boot:
            self.check_boot_complete()
        else:
            self.check_adb()

    def check_adb(self):
        try:
            if self.usb:
                ser_.open_relay(self.usb_relay)
                time.sleep(1)
                ser_.close_relay(self.usb_relay)
                time.sleep(1)
            if self.device.device_is_online():
                self.result = True

        except Exception as e:
            log.error("Error occurred during adb check: %s" % str(e))

        if not self.result:
            self.timer = threading.Timer(5, self.check_adb)
            self.timer.start()

    def timeout_handler(self):
        if self.timer:
            self.timer.cancel()

    def check_boot_complete(self):
        try:
            if "1" in self.device.device_boot():
                self.result = True
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            log.error("Error occurred during boot check: %s" % str(e))

        if not self.result:
            self.timer = threading.Timer(5, self.check_boot_complete)
            self.timer.start()


if __name__ == '__main__':

    def check_adb_online_with_thread(timeout=30):
        adb_checker = ADBChecker(timeout)
        adb_checker.start_check()

        # Wait until timeout or ADB is found
        start_time = time.time()
        while time.time() - start_time < timeout:
            if adb_checker.result:
                adb_checker.timeout_handler()
                return True
            time.sleep(1)

        return False


    # Example usage
    if check_adb_online_with_thread():
        print("ADB is online.")
    else:
        print("ADB is offline or timeout reached.")
