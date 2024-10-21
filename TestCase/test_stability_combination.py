import allure
import os
import time
import pytest
import configparser
from Common.log import MyLog
from Main.device import Device
from Common.config import Config
from Common import m_serial

log = MyLog()
t_ser = m_serial.SerialD()


class TestStabilityCombination:

    def setup_class(self):
        self.bg_conf_file = configparser.ConfigParser()
        self.bg_conf_file.read(Config.bg_config_ini_path)
        self.ui_conf_file = configparser.ConfigParser()
        self.ui_conf_file.read(Config.ui_config_ini_path)
        self.device_name = self.ui_conf_file.get(Config.section_ui_to_background,
                                                 Config.ui_option_device_name)
        self.device = Device(self.device_name)

    def teardown_class(self):
        log.info("压测运行完毕")
        time.sleep(3)

    @allure.feature("DDR-Integration-testing")
    @allure.title("DDR-EMMC压力测试")
    def test_stability_combination_all(self):
        log.info("********测试开始*********")
        # 删除相关log文件夹
        self.device.send_adb_shell_command(" rm -rf /data/stress_test_log")
        # try:
        # 1.推送memtester的相关
        # root设备
        if self.ui_conf_file.get(Config.section_DDR_EMMC, Config.ui_option_is_memtester) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_memtester_path, "memtester"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/memtester")
        # 2.推送stressapptest
        if self.ui_conf_file.get(Config.section_DDR_EMMC, Config.ui_option_is_stress_app_test) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_path, "stressapptest"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/stressapptest")
            time.sleep(2)
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_path, "libstlport.so"),
                                      "/system/lib/libstlport.so")
            self.device.send_adb_shell_command("chmod 644 /system/lib/libstlport.so")
        # 2.推送stressapptest-cut
        if self.ui_conf_file.get(Config.section_DDR_EMMC, Config.ui_option_is_stress_app_switch) == "yes":
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_switch_path, "stressapptest"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/stressapptest")
            time.sleep(2)
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_switch_path, "libstlport.so"),
                                      "/system/lib/")
            self.device.send_adb_shell_command("chmod 644 /system/lib/libstlport.so")
        # 推送shell脚本
        if self.ui_conf_file.get(Config.section_DDR_EMMC, Config.ui_option_system_type) == "Android":
            self.device.adb_push_file(os.path.join(Config.pretesting_path, "test_demo_Android.sh"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/test_demo_Android.sh")
            self.device.adb_push_file(Config.ui_config_ini_path, "/data")
            self.device.send_adb_shell_command("\"setsid /data/test_demo_Android.sh > /data/test_demo.log 2>&1 &\"")
        else:
            self.device.adb_push_file(os.path.join(Config.pretesting_path, "test_demo_Linux.sh"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/test_demo_Linux.sh")
            log.info(os.path.basename(Config.ui_config_ini_path))
            if self.device.is_existed("/data/%s" % os.path.basename(Config.ui_config_ini_path)):
                self.device.send_adb_shell_command("rm /data/%s" % os.path.basename(Config.ui_config_ini_path))
                self.device.adb_push_file(Config.ui_config_ini_path, "/data")
            self.device.send_adb_shell_command("setsid /data/test_demo_Linux.sh &")
        time.sleep(10)
        if "debug.txt" in self.device.send_adb_shell_command("ls /data/stress_test_log"):
            log.info("可脱机测试")
        else:
            log.info(".sh脚本没跑起来，请检查！！！")
        # except Exception as e:
        #     print(e)
        log.info("测试结束")
        log.info("********测试结束*********")

    @allure.feature("mt-wifi_btn_stability")
    @allure.title("开关wifi压测")
    def test_wifi_btn_stability_test(self):
        log.info("****************开关wifi压测开始******************")
        test_times = int(self.ui_conf_file.get(Config.section_wifi_check, Config.option_wifi_btn_test_times))
        # 删除已存在的logcat文件
        if os.path.exists(Config.wifi_btn_sta_test_log_path):
            os.remove(Config.wifi_btn_sta_test_log_path)
        # 后台启动捕捉log
        log_path = os.path.join("/sdcard/%s" % os.path.basename(Config.wifi_btn_sta_test_log_path))  # log名称
        self.device.rm_file(log_path)  # 清除已存在的
        self.device.touch_file(log_path)
        self.device.logcat_thread(log_path)

        log.info("捕捉设备log")
        # 获取后台logcat进程id
        logcat_process_id = self.device.get_current_logcat_process_id()

        # 给以太网， 4G下电，清理环境
        if self.device.eth0_is_enable():
            self.device.disable_eth0_btn()
            time.sleep(2)
        if self.device.eth0_is_enable():
            self.device.disable_eth0_btn()
            time.sleep(2)
        if self.device.eth0_is_enable():
            log.error("以太网无法下电，请检查！！！")
            time.sleep(3)
            self.device.kill_process(logcat_process_id)
            self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
            raise

        if self.device.mobile_is_enable():
            self.device.disable_mobile_btn()
            time.sleep(2)
        if self.device.mobile_is_enable():
            self.device.disable_mobile_btn()
            time.sleep(2)
        if self.device.mobile_is_enable():
            log.error("移动流量无法下电，请检查！！！")
            time.sleep(3)
            self.device.kill_process(logcat_process_id)
            self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
            raise

        times = 0
        while times < test_times:
            times += 1
            self.device.disable_wifi_btn()
            time.sleep(2)
            if self.device.wifi_is_enable():
                self.device.disable_wifi_btn()
                time.sleep(2)
            if self.device.wifi_is_enable():
                log.error("wifi按钮无法下电，请检查！！！")
                time.sleep(3)
                self.device.kill_process(logcat_process_id)
                self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
                raise
            log.info("wifi下电")
            if not self.device.is_no_network():
                log.error("wifi下电后还可上网请检查！！！")
                time.sleep(3)
                self.device.kill_process(logcat_process_id)
                self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
                raise

            self.device.enable_wifi_btn()
            time.sleep(2)
            if not self.device.wifi_is_enable():
                self.device.enable_wifi_btn()
                time.sleep(2)
            if not self.device.wifi_is_enable():
                log.error("wifi按钮无法上电，请检查！！！")
                time.sleep(3)
                self.device.kill_process(logcat_process_id)
                self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
                raise
            log.info("wifi上电")
            if not self.device.ping_network():
                log.error("wifi上电后5分钟内无法上网！！！")
                time.sleep(3)
                self.device.kill_process(logcat_process_id)
                self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
                raise

            log.info("***********wifi开关压测完成%d次" % times)
            time.sleep(3)

        self.device.kill_process(logcat_process_id)
        self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
        log.info("****************开关wifi压测结束******************")

    @allure.feature("mt-mobile_btn_stability")
    @allure.title("4G开关压测")
    def test_wifi_btn_stability_test(self):
        log.info("****************开关4G压测开始******************")
        test_times = int(self.ui_conf_file.get(Config.section_mobile_check, Config.option_mobile_btn_test_times))
        # 删除已存在的logcat文件
        if os.path.exists(Config.mobile_btn_sta_test_log_path):
            os.remove(Config.mobile_btn_sta_test_log_path)
        # 后台启动捕捉log
        log_path = os.path.join("/sdcard/%s" % os.path.basename(Config.mobile_btn_sta_test_log_path))  # log名称
        self.device.rm_file(log_path)  # 清除已存在的
        self.device.touch_file(log_path)
        self.device.logcat_thread(log_path)

        log.info("捕捉设备log")
        # 获取后台logcat进程id
        logcat_process_id = self.device.get_current_logcat_process_id()

        # 给以太网， 4G下电，清理环境
        if self.device.eth0_is_enable():
            self.device.disable_eth0_btn()
            time.sleep(2)
        if self.device.eth0_is_enable():
            self.device.disable_eth0_btn()
            time.sleep(2)
        if self.device.eth0_is_enable():
            log.error("以太网无法下电，请检查！！！")
            time.sleep(3)
            self.device.kill_process(logcat_process_id)
            self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
            raise

        if self.device.wifi_is_enable():
            self.device.disable_wifi_btn()
            time.sleep(2)
        if self.device.wifi_is_enable():
            self.device.disable_wifi_btn()
            time.sleep(2)
        if self.device.wifi_is_enable():
            log.error("wifi下电，请检查！！！")
            time.sleep(3)
            self.device.kill_process(logcat_process_id)
            self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
            raise

        times = 0
        while times < test_times:
            times += 1
            self.device.disable_mobile_btn()
            time.sleep(2)
            if self.device.mobile_is_enable():
                self.device.disable_mobile_btn()
                time.sleep(2)
            if self.device.mobile_is_enable():
                log.error("移动流量按钮无法下电，请检查！！！")
                time.sleep(3)
                self.device.kill_process(logcat_process_id)
                self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
                raise
            log.info("wifi下电")
            if not self.device.is_no_network():
                log.error("移动流量下电后还可上网请检查！！！")
                time.sleep(3)
                self.device.kill_process(logcat_process_id)
                self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
                raise

            self.device.enable_mobile_btn()
            time.sleep(2)
            if not self.device.mobile_is_enable():
                self.device.enable_mobile_btn()
                time.sleep(2)
            if not self.device.mobile_is_enable():
                log.error("移动流量按钮无法上电，请检查！！！")
                time.sleep(3)
                self.device.kill_process(logcat_process_id)
                self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
                raise
            log.info("移动流量上电")
            if not self.device.ping_network():
                log.error("移动流量上电后5分钟内无法上网！！！")
                time.sleep(3)
                self.device.kill_process(logcat_process_id)
                self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
                raise

            log.info("***********4G开关压测完成%d次" % times)
            time.sleep(3)

        self.device.kill_process(logcat_process_id)
        self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
        log.info("****************开关4G压测结束******************")

    @allure.feature("USB-recognition-stability")
    @allure.title("U盘拔插识别压测")
    def test_usb_recognition_stability_test(self):
        log.info("****************U盘拔插识别用例开始***********************")

        # 后台启动捕捉log
        log_path = os.path.join("/sdcard/usb_flash_recognize_logcat.log")  # log名称
        self.device.rm_file(log_path)  # 清除已存在的
        self.device.touch_file(log_path)
        self.device.logcat_thread(log_path)

        # 删除相关log文件夹
        self.device.send_adb_shell_command("rm -rf /data/debug.txt")
        # 推送shell脚本
        if self.ui_conf_file.get(Config.section_usb_recognize, Config.ui_option_system_type) == "Android":
            demo_name = os.path.basename(Config.USB_recognition_demo_path)
            self.device.adb_push_file(Config.USB_recognition_demo_path, "/data")
            self.device.send_adb_shell_command("chmod 777 /data/%s" % demo_name)
            self.device.adb_push_file(Config.ui_config_ini_path, "/data")
            self.device.send_adb_shell_command("\"setsid /data/%s > /data/test_demo.log 2>&1 &\"" % demo_name)

        time.sleep(10)
        if "debug.txt" in self.device.send_adb_shell_command("ls /data"):
            log.info("可脱机测试....")
            # 继电器
            com_port = self.ui_conf_file.get(Config.section_usb_recognize, Config.ui_option_usb_com)
            com_line = int(
                self.ui_conf_file.get(Config.section_usb_recognize, Config.ui_option_usb_config_line).split("_")[1])
            test_times = int(
                self.ui_conf_file.get(Config.section_usb_recognize, Config.option_usb_recognition_test_times))
            flag = 0

            try:
                t_ser.loginSer(com_port)
            except Exception as e:
                log.error("串口已经被占用， 请检查！！！")
                log.error(str(e))
                raise

            while flag < test_times:
                flag += 1
                # 上下电
                t_ser.open_relay(com_line)
                log.info("模拟U盘断开")
                time.sleep(3)
                t_ser.close_relay(com_line)
                log.info("模拟U盘插入")
                log.info("********U盘拔插%d次******" % flag)
                time.sleep(10)
        else:
            log.info(".sh脚本没跑起来，请检查！！！")

        log.info("****************U盘拔插识别用例结束***********************")

    @allure.feature("USB-Read-Write-stability")
    @allure.title("U盘/TF卡读取大数据压测")
    def test_usb_read_and_write_big_data_test(self):
        log.info("****************U盘/TF卡读取大数据压测用例开始***********************")

        # 后台启动捕捉log
        log_path = os.path.join("/sdcard/storage_read_write_speech_logcat.log")  # log名称
        self.device.rm_file(log_path)  # 清除已存在的
        self.device.touch_file(log_path)
        self.device.logcat_thread(log_path)

        # 删除相关log文件夹
        self.device.send_adb_shell_command("rm -rf /data/debug.txt")
        # 推送shell脚本
        if self.ui_conf_file.get(Config.section_storage_stability, Config.ui_option_system_type) == "Android":
            demo_name = os.path.basename(Config.storage_speed_path)
            self.device.adb_push_file(Config.storage_speed_path, "/data")
            self.device.send_adb_shell_command("chmod 777 /data/%s" % demo_name)
            self.device.adb_push_file(Config.ui_config_ini_path, "/data")
            self.device.send_adb_shell_command("\"setsid /data/%s > /data/test_demo.log 2>&1 &\"" % demo_name)

        time.sleep(10)
        if "debug.txt" in self.device.send_adb_shell_command("ls /data"):
            log.info("可脱机测试....")
        else:
            log.info(".sh脚本没跑起来，请检查！！！")

        log.info("****************U盘拔插识别用例结束***********************")


