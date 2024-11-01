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
        log_path = os.path.join("/sdcard/storage_read_write_speech_logcat.txt")  # log名称
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

    @allure.feature("Factory-Reset-stability")
    @allure.title("恢复出厂设置检查压测")
    def test_factory_reset_stability_test(self):
        log.info("***************恢复出厂设置检查压测开始***************")
        test_times = int(
            self.ui_conf_file.get(Config.section_factory_reset_stability, Config.option_factory_reset_test_times))
        # 获取所有需要测试模块
        is_wifi_test = int(self.ui_conf_file.get(Config.section_factory_reset_stability, Config.option_wifi_test))
        is_eth_test = int(self.ui_conf_file.get(Config.section_factory_reset_stability, Config.option_eth_test))
        is_mobile_test = int(self.ui_conf_file.get(Config.section_factory_reset_stability, Config.option_mobile_test))
        is_bt_test = int(self.ui_conf_file.get(Config.section_factory_reset_stability, Config.option_bt_test))
        is_nfc_test = int(self.ui_conf_file.get(Config.section_factory_reset_stability, Config.option_nfc_test))

        apk_path = os.path.join(Config.factory_reset_pak_path, "Bus_Recharge_System.apk")
        app_package_name = self.device.get_apk_package_name(apk_path)
        txt_file_path = "sdcard/factory_reset.txt"

        if not os.path.exists(apk_path):
            log.error("不存在apk：%s" % apk_path)
            time.sleep(3)
            raise

        # 恢复出厂设置获取模块初始状态
        log.info("压测前先恢复出厂设置，检查各模块的初始状态")
        self.device.send_adb_shell_command("\"am broadcast -a android.intent.action.MASTER_CLEAR\"")
        time.sleep(10)
        if self.device.device_is_online():
            log.error("恢复出厂设置指令下达失败！！！")
            time.sleep(3)
            raise Exception

        now_time = time.time()
        while True:
            if self.device.device_is_online():
                break
            if time.time() > now_time + 300:
                log.error("超过5分钟ADB没起来，恢复出厂设置失败")
                raise Exception
        log.info("恢复出厂完成")

        now_time0 = time.time()
        while True:
            if self.device.device_boot():
                break
            if time.time() > now_time0 + 120:
                log.error("超过2分钟设备没完全重启，请检查！！！")
                raise Exception
        log.info("设备完全开机")

        if int(is_wifi_test):
            wifi_init_status = self.device.wifi_is_enable()
            if wifi_init_status:
                log.info("WIFI的初始为上电状态")
            else:
                log.info("WIFI的初始为下电状态")
        self.device.connect_wifi("Telpo", "86337898")

        if int(is_bt_test):
            bt_init_status = self.device.bt_is_enable()
            if bt_init_status:
                log.info("蓝牙的初始为上电状态")
            else:
                log.info("蓝牙的初始为下电状态")

        if int(is_mobile_test):
            mobile_init_status = self.device.mobile_is_enable()
            if mobile_init_status:
                log.info("移动数据的初始为上电状态")
            else:
                log.info("移动数据的初始为下电状态")

        if int(is_nfc_test):
            nfc_init_status = self.device.nfc_is_enable()
            if nfc_init_status:
                log.info("NFC的初始为上电状态")
            else:
                log.info("NFC的初始为下电状态")

        if int(is_eth_test):
            eth_init_status = self.device.eth0_is_enable()
            if eth_init_status:
                log.info("以太网的初始为上电状态")
            else:
                log.info("以太网的初始为下电状态")

        times = 0
        while times < int(test_times):
            times += 1
            # 安装app:
            self.device.install_app(apk_path)
            time.sleep(1)
            if not self.device.app_is_installed(app_package_name):
                self.device.install_app(apk_path)
            time.sleep(3)
            log.info("安装app 成功")

            if not self.device.app_is_installed(app_package_name):
                log.error("无法安装app:%s，请检查！！！" % apk_path)
                raise

            # 创建文件
            self.device.touch_file(txt_file_path)

            if int(is_wifi_test):
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()

            if int(is_mobile_test):
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                time.sleep(3)
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()

            if int(is_bt_test):
                if not self.device.bt_is_enable():
                    self.device.enable_bt_btn()
                time.sleep(3)
                if not self.device.bt_is_enable():
                    self.device.enable_bt_btn()

            if int(is_nfc_test):
                if not self.device.nfc_is_enable():
                    self.device.enable_nfc_btn()
                time.sleep(3)
                if not self.device.nfc_is_enable():
                    self.device.enable_nfc_btn()

            if int(is_eth_test):
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()
                time.sleep(3)
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()

            # 恢复出厂设置
            self.device.send_adb_shell_command("am broadcast -a android.intent.action.MASTER_CLEAR")
            time.sleep(10)
            if self.device.device_is_online():
                log.error("恢复出厂设置指令下达失败！！！")
                time.sleep(3)
                raise Exception

            now_time = time.time()
            while True:
                if self.device.device_is_online():
                    break
                if time.time() > now_time + 300:
                    log.error("超过5分钟ADB没起来，恢复出厂设置失败")
                    raise Exception
            log.info("开机成功，ADB起来")

            now_time1 = time.time()
            while True:
                if self.device.device_boot():
                    break
                if time.time() > now_time1 + 120:
                    log.error("超过2分钟设备没完全重启，请检查！！！")
                    raise Exception
            log.info("设备完全开机")

            # 检查恢复出厂设置之后基本功能检查
            if self.device.app_is_installed(app_package_name):
                log.error("恢复出厂设置之后设备存在第三方app:%s，请检查！！！" % app_package_name)
                time.sleep(3)
                raise

            if self.device.is_existed(txt_file_path):
                log.error("恢复出厂设置之后设备存在非内部文件:%s，请检查！！！" % txt_file_path)
                time.sleep(3)
                raise

            # wifi test
            if int(is_wifi_test):
                if self.device.wifi_is_enable() != wifi_init_status:
                    if self.device.wifi_is_enable():
                        log.error("恢复出厂设置设置后之后wifi的的状态为：wifi上电状态, 与初始状态不一致，请检查！！！")
                    else:
                        log.error("恢复出厂设置设置后之后wifi的的状态为：wifi状态, 与初始状态不一致，请检查！！！")
                    time.sleep(3)
                    raise Exception
                else:
                    if self.device.wifi_is_enable():
                        log.info("WIFI当前为上电状态，与初始状态一致")
                    else:
                        log.info("WIFI当前状态为下电状态，与初始状态一致")

            # mobile test
            if int(is_mobile_test):
                if self.device.mobile_is_enable() != mobile_init_status:
                    if self.device.mobile_is_enable():
                        log.error("恢复出厂设置设置后之后移动数据当前为上电状态, 与初始状态不一致，请检查！！！")
                    else:
                        log.error("恢复出厂设置设置后之后移动数据当前为下电状态, 与初始状态不一致，请检查！！！")
                    time.sleep(3)
                    raise Exception
                else:
                    if self.device.mobile_is_enable():
                        log.info("移动数据当前为上电状态，与初始状态一致")
                    else:
                        log.info("移动数据当前状态为下电状态，与初始状态一致")

            # eth test
            if int(is_eth_test):
                if self.device.eth0_is_enable() != eth_init_status:
                    if self.device.eth0_is_enable():
                        log.error("恢复出厂设置设置后之后以太网当前为上电状态, 与初始状态不一致，请检查！！！")
                    else:
                        log.error("恢复出厂设置设置后之后以太网当前为下电状态, 与初始状态不一致，请检查！！！")
                    time.sleep(3)
                    raise Exception
                else:
                    if self.device.eth0_is_enable():
                        log.info("以太网当前为上电状态，与初始状态一致")
                    else:
                        log.info("以太网当前状态为下电状态，与初始状态一致")

            # bt test
            if int(is_bt_test):
                if self.device.bt_is_enable() != bt_init_status:
                    if self.device.bt_is_enable():
                        log.error("恢复出厂设置设置后之后蓝牙当前为上电状态, 与初始状态不一致，请检查！！！")
                    else:
                        log.error("恢复出厂设置设置后之后蓝牙当前为下电状态, 与初始状态不一致，请检查！！！")
                    time.sleep(3)
                    raise Exception
                else:
                    if self.device.bt_is_enable():
                        log.info("蓝牙当前为上电状态，与初始状态一致")
                    else:
                        log.info("蓝牙当前状态为下电状态，与初始状态一致")

            # wifi上下点相关测试
            if int(is_eth_test) and int(is_wifi_test) and int(is_mobile_test):
                # 禁用wifi
                self.device.disable_wifi_btn()
                time.sleep(3)
                if self.device.wifi_is_enable():
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                if self.device.wifi_is_enable():
                    log.error("wifi模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                log.info("wifi下电")
                # 禁用4G
                self.device.disable_mobile_btn()
                time.sleep(3)
                if self.device.mobile_is_enable():
                    self.device.disable_mobile_btn()
                    time.sleep(3)
                if self.device.mobile_is_enable():
                    log.error("移动数据模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("移动数据下电成功")
                if not self.device.ping_network(5, 35):
                    log.error("启动后以太网无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("启动后以太网可正常上网")

                # 禁用以太网
                self.device.disable_eth0_btn()
                time.sleep(3)
                if self.device.eth0_is_enable():
                    self.device.disable_eth0_btn()
                    time.sleep(3)
                if self.device.eth0_is_enable():
                    log.error("以太网模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网下电成功")
                # 上电
                self.device.enable_eth0_btn()
                time.sleep(3)
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()
                    time.sleep(3)
                if not self.device.eth0_is_enable():
                    log.error("以太网模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("以太网无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网可正常上网")

                # 以太网下电
                self.device.disable_eth0_btn()
                time.sleep(3)
                if self.device.eth0_is_enable():
                    self.device.disable_eth0_btn()
                    time.sleep(3)
                if self.device.eth0_is_enable():
                    log.error("以太网模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                # wifi上电
                # 上电
                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                if not self.device.wifi_is_enable():
                    log.error("wifi模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi模块上电成功")
                self.device.connect_wifi("Telpo", "86337898")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

                # wifi下电
                self.device.disable_wifi_btn()
                time.sleep(3)
                if self.device.wifi_is_enable():
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                if self.device.wifi_is_enable():
                    log.error("wifi模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                # 移动数据上电
                # 上电
                self.device.enable_mobile_btn()
                time.sleep(3)
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                    time.sleep(3)
                if not self.device.mobile_is_enable():
                    log.error("移动数据模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("移动数据模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("移动数据无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("移动数据可正常上网")

                # 以太网上电，wifi上电
                # wifi上电
                # 上电
                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                if not self.device.wifi_is_enable():
                    log.error("wifi模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi模块上电成功")
                self.device.connect_wifi("Telpo", "86337898")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

                # 以太网上电
                self.device.enable_eth0_btn()
                time.sleep(3)
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()
                    time.sleep(3)
                if not self.device.eth0_is_enable():
                    log.error("以太网模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("以太网无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("以太网可正常上网")
            if not int(is_eth_test) and int(is_wifi_test) and int(is_mobile_test):
                # 禁用4G
                self.device.disable_mobile_btn()
                time.sleep(3)
                if self.device.mobile_is_enable():
                    self.device.disable_mobile_btn()
                    time.sleep(3)
                if self.device.mobile_is_enable():
                    log.error("移动数据模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("移动数据下电")

                if not self.device.ping_network(5, 60):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

                # wifi下电
                self.device.disable_wifi_btn()
                time.sleep(3)
                if self.device.wifi_is_enable():
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                if self.device.wifi_is_enable():
                    log.error("wifi模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                # 移动数据上电
                # 上电
                self.device.enable_mobile_btn()
                time.sleep(3)
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                    time.sleep(3)
                if not self.device.mobile_is_enable():
                    log.error("移动数据模块无法上电，请检查！！！")
                    raise Exception
                log.info("移动数据模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("移动数据无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception

                log.info("移动数据可正常上网")

                # 以太网上电，wifi上电
                # wifi上电
                # 上电
                log.info("移动数据下电")
                if self.device.mobile_is_enable():
                    self.device.disable_mobile_btn()
                    time.sleep(3)
                if self.device.mobile_is_enable():
                    log.error("移动数据模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                if not self.device.wifi_is_enable():
                    log.error("wifi模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi模块上电成功")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

                self.device.enable_mobile_btn()
                time.sleep(3)
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                    time.sleep(3)
                if not self.device.mobile_is_enable():
                    log.error("移动数据模块无法上电，请检查！！！")
                    raise Exception
                log.info("移动数据模块上电成功")

            if not int(is_eth_test) and int(is_wifi_test) and not int(is_mobile_test):
                # wifi下电
                self.device.disable_wifi_btn()
                time.sleep(3)
                if self.device.wifi_is_enable():
                    self.device.disable_wifi_btn()
                    time.sleep(3)
                if self.device.wifi_is_enable():
                    log.error("wifi模块无法下电，请检查！！！")
                    time.sleep(3)
                    raise Exception

                self.device.enable_wifi_btn()
                time.sleep(3)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                if not self.device.wifi_is_enable():
                    log.error("wifi模块无法上电，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi模块上电成功")
                self.device.connect_wifi("Telpo", "86337898")
                # 检查网络
                if not self.device.ping_network(5, 35):
                    log.error("wifi无法上网， 请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("wifi可正常上网")

            # 蓝牙上下电相关测试
            if int(is_bt_test):
                log.info("********检查蓝牙开关状态")
                if bt_init_status:
                    # 对蓝牙进行关开操作
                    log.info("给蓝牙下电")
                    self.device.disable_bt_btn()
                    time.sleep(3)
                    if self.device.bt_is_enable():
                        self.device.disable_bt_btn()
                        time.sleep(3)
                    if self.device.bt_is_enable():
                        log.error("蓝牙无法下电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("蓝牙下电成功")
                    log.info("给蓝牙上电")
                    self.device.enable_bt_btn()
                    time.sleep(3)
                    if not self.device.bt_is_enable():
                        self.device.enable_bt_btn()
                        time.sleep(3)
                    if not self.device.bt_is_enable():
                        log.error("蓝牙无法上电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("蓝牙上电成功")
                else:
                    log.info("给蓝牙上电")
                    self.device.enable_bt_btn()
                    time.sleep(3)
                    if not self.device.bt_is_enable():
                        self.device.enable_bt_btn()
                        time.sleep(3)
                    if not self.device.bt_is_enable():
                        log.error("蓝牙无法上电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("蓝牙上电成功")

                    log.info("给蓝牙下电")
                    self.device.disable_bt_btn()
                    time.sleep(3)
                    if self.device.bt_is_enable():
                        self.device.disable_bt_btn()
                        time.sleep(3)
                    if self.device.bt_is_enable():
                        log.error("蓝牙无法下电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("蓝牙下电成功")

            if int(is_nfc_test):
                # 对蓝牙进行关开操作
                if nfc_init_status:
                    log.info("给nfc下电")
                    self.device.disable_nfc_btn()
                    time.sleep(3)
                    if self.device.nfc_is_enable():
                        self.device.disable_nfc_btn()
                        time.sleep(3)
                    if self.device.nfc_is_enable():
                        log.error("nfc无法下电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("nfc下电成功")

                    log.info("给nfc上电")
                    self.device.enable_nfc_btn()
                    time.sleep(3)
                    if not self.device.nfc_is_enable():
                        self.device.enable_nfc_btn()
                        time.sleep(3)
                    if not self.device.nfc_is_enable():
                        log.error("nfc无法上电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("nfc上电成功")
                else:
                    log.info("给nfc上电")
                    self.device.enable_nfc_btn()
                    time.sleep(3)
                    if not self.device.nfc_is_enable():
                        self.device.enable_nfc_btn()
                        time.sleep(3)
                    if not self.device.nfc_is_enable():
                        log.error("nfc无法上电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("nfc上电成功")

                    log.info("给nfc下电")
                    self.device.disable_nfc_btn()
                    time.sleep(3)
                    if self.device.nfc_is_enable():
                        self.device.disable_nfc_btn()
                        time.sleep(3)
                    if self.device.nfc_is_enable():
                        log.error("nfc无法下电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("nfc下电成功")

            log.info("***************恢复出厂设置成功 %d 次" % times)

            time.sleep(1)
        log.info("***************恢复出厂设置检查压测结束***************")
