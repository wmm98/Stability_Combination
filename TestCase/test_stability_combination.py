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
        self.device.send_adb_shell_command(" rm -rf /sdcard/stress_test_log")
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
            self.device.adb_push_file(os.path.join(Config.DDR_stressapptest_path, "libstlport.so"), "/system/lib/libstlport.so")
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
            self.device.send_adb_shell_command("\"setsid /data/test_demo_Android.sh > /sdcard/test_demo.log 2>&1 &\"")
        else:
            self.device.adb_push_file(os.path.join(Config.pretesting_path, "test_demo_Linux.sh"), "/data")
            self.device.send_adb_shell_command("chmod 777 /data/test_demo_Linux.sh")
            log.info(os.path.basename(Config.ui_config_ini_path))
            if self.device.is_existed("/data/%s" % os.path.basename(Config.ui_config_ini_path)):
                self.device.send_adb_shell_command("rm /data/%s" % os.path.basename(Config.ui_config_ini_path))
                self.device.adb_push_file(Config.ui_config_ini_path, "/data")
            self.device.send_adb_shell_command("setsid /data/test_demo_Linux.sh &")
        time.sleep(10)
        if "debug.txt" in self.device.send_adb_shell_command("ls /sdcard/stress_test_log"):
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
        try:
            test_times = int(self.ui_conf_file.get(Config.section_wifi_check, Config.option_wifi_btn_test_times))
            is_probability_test = int(self.ui_conf_file.get(Config.section_wifi_check, Config.is_probability_test))
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

            rounds_interval = int(self.ui_conf_file.get(Config.section_wifi_check, Config.test_interval))
            bt_interval = int(self.ui_conf_file.get(Config.section_wifi_check, Config.test_interval))

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
            # if self.device.mobile_is_enable():
            #     log.error("移动流量无法下电，请检查！！！")
            #     time.sleep(3)
            #     self.device.kill_process(logcat_process_id)
            #     self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
            #     raise

            disable_fail_flag = 0
            enable_fail_flag = 0
            network_enable_fail_flag = 0
            network_disable_fail_flag = 0
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
                    if is_probability_test:
                        disable_fail_flag += 1
                        continue
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
                        raise
                log.info("wifi下电")
                if not self.device.is_no_network():
                    log.error("wifi下电后还可上网请检查！！！")
                    if is_probability_test:
                        network_disable_fail_flag += 1
                        continue
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
                        raise

                time.sleep(bt_interval)

                self.device.enable_wifi_btn()
                time.sleep(2)
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(2)
                if not self.device.wifi_is_enable():
                    log.error("wifi按钮无法上电，请检查！！！")
                    if is_probability_test:
                        enable_fail_flag += 1
                        continue
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
                        raise

                log.info("wifi上电")
                if not self.device.ping_network():
                    log.error("wifi上电后5分钟内无法上网！！！")
                    if is_probability_test:
                        network_enable_fail_flag += 1
                        continue
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
                        raise
                log.info("当前可上网")
                self.device.scan_wifi()
                time.sleep(1)
                self.device.scan_wifi()
                time.sleep(4)
                log.info("wifi 扫描列表")
                wifi_scan_results = self.device.get_wifi_scan_list()
                log.info("\n %s" % wifi_scan_results)
                scan_ssid_list = self.device.get_wifi_ssid_list().replace("\r", "").split("\n")
                actual_wifi_list = []
                for ssid in scan_ssid_list:
                    if ssid not in actual_wifi_list[1:]:
                        if "WPA" not in ssid and "ESS" not in ssid:
                            actual_wifi_list.append(ssid)
                log.info("扫描到的wifi数量为:%d" % len(actual_wifi_list))
                log.info("***********wifi开关压测完成%d次" % times)
                time.sleep(rounds_interval)

            if is_probability_test:
                if disable_fail_flag > 0:
                    log.error("WIFI模块无法下电得次数为：%d" % enable_fail_flag)
                    log.error("WIFI模块无法下电得概率为： %s" % str(enable_fail_flag / test_times))
                if enable_fail_flag > 0:
                    log.error("WIFI模块无法上电得次数为：%d" % enable_fail_flag)
                    log.error("WIFI模块无法上电得概率为： %s" % str(enable_fail_flag / test_times))
                if network_enable_fail_flag > 0:
                    log.error("WIFI模块上电后无法上网得次数为：%d" % network_enable_fail_flag)
                    log.error("WIFI模块上电后无法上网得概率为： %s" % str(network_enable_fail_flag / test_times))
                if network_disable_fail_flag > 0:
                    log.error("WIFI模块下电后无法上网得次数为：%d" % network_disable_fail_flag)
                    log.error("WIFI模块下电后无后无法上网得概率为： %s" % str(network_disable_fail_flag / test_times))
                if disable_fail_flag == 0 and enable_fail_flag == 0 and network_enable_fail_flag == 0 and network_disable_fail_flag == 0:
                    log.info("压测未发发现异常")

            self.device.kill_process(logcat_process_id)
            self.device.adb_pull_file(log_path, os.path.dirname(Config.wifi_btn_sta_test_log_path))
            log.info("****************开关wifi压测结束******************")
        except Exception as e:
            log.error(str(e))
            log.error("开关wifi压测用例运行异常，请检查！！！")
            assert False

    @allure.feature("mt-mobile_btn_stability")
    @allure.title("4G开关压测")
    def test_mobile_btn_stability_test(self):
        log.info("****************开关4G压测开始******************")
        try:
            test_times = int(self.ui_conf_file.get(Config.section_mobile_check, Config.option_mobile_btn_test_times))
            is_probability_test = int(self.ui_conf_file.get(Config.section_mobile_check, Config.is_probability_test))
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
            rounds_interval = int(self.ui_conf_file.get(Config.section_mobile_check, Config.test_interval))
            bt_interval = int(self.ui_conf_file.get(Config.section_mobile_check, Config.test_interval))

            sim_log_path = "/sdcard/TestTeam/AutomationTestLog.txt"
            apk_path = os.path.join(Config.sim_apk_path, "SimRSRP.apk")
            des_apk_path = "/sdcard/SimRSRP.apk"
            ini_file_path = "/sdcard/TestTeam/TestResult.ini"
            package_name = self.device.get_apk_package_name(apk_path)

            # 先推送apk到sdcard、安装
            # self.device.adb_push_file(apk_path, "sdcard")
            self.device.install_app(apk_path)

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

            disable_fail_flag = 0
            enable_fail_flag = 0
            network_enable_fail_flag = 0
            network_disable_fail_flag = 0

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
                    if is_probability_test:
                        disable_fail_flag += 1
                        continue
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
                        raise
                log.info("移动流量模块下电")
                if not self.device.is_no_network():
                    log.error("移动流量下电后还可上网请检查！！！")
                    if self.device.mobile_is_enable():
                        network_disable_fail_flag += 1
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
                        raise
                log.info("设备当前无法上网")
                time.sleep(bt_interval)
                self.device.enable_mobile_btn()
                time.sleep(2)
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                    time.sleep(2)
                if not self.device.mobile_is_enable():
                    log.error("移动流量按钮无法上电，请检查！！！")
                    if is_probability_test:
                        enable_fail_flag += 1
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
                        raise

                log.info("移动流量上电")
                if not self.device.ping_network(timeout=180):
                    log.error("移动流量上电后3分钟内无法上网！！！")
                    if is_probability_test:
                        network_enable_fail_flag += 1
                    else:
                        time.sleep(3)
                        self.device.kill_process(logcat_process_id)
                        self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
                        raise
                else:
                    log.info("设备当前可上网")

                log.info("当前的SIM卡信号强度为: ")

                self.device.start_app(package_name)
                time.sleep(1)
                now_time = time.time()
                while True:
                    if self.device.remove_info_space("flag = end") in self.device.remove_info_space(self.device.send_adb_shell_command("cat %s" % ini_file_path)):
                        break
                    if time.time() > now_time + 60:
                        log.error("%s 运行有问题， 请检查！！！" % os.path.dirname(apk_path))
                        break
                    time.sleep(1)

                sim_log = self.device.send_adb_shell_command("cat %s" % sim_log_path)
                log.info("\n" + sim_log)
                self.device.rm_directory(os.path.dirname(sim_log_path) + "/")
                self.device.force_stop_app(package_name)
                self.device.clear_app(package_name)
                log.info("***********4G开关压测完成%d次" % times)
                time.sleep(rounds_interval)

            # 卸载app
            self.device.uninstall_app(package_name)

            if is_probability_test:
                if disable_fail_flag > 0:
                    log.error("4G模块无法下电得次数为：%d" % enable_fail_flag)
                    log.error("4G模块无法下电得概率为： %s" % str(enable_fail_flag / test_times))
                if enable_fail_flag > 0:
                    log.error("4G模块无法上电得次数为：%d" % enable_fail_flag)
                    log.error("4G模块无法上电得概率为： %s" % str(enable_fail_flag / test_times))
                if network_enable_fail_flag:
                    log.error("4G模块上电后无法上网得次数为：%d" % network_enable_fail_flag)
                    log.error("4G模块上电后无法上网得概率为： %s" % str(network_enable_fail_flag / test_times))
                if network_disable_fail_flag:
                    log.error("4G模块下电后无法上网得次数为：%d" % network_disable_fail_flag)
                    log.error("4G模块下电后无后无法上网得概率为： %s" % str(network_disable_fail_flag / test_times))
                if disable_fail_flag == 0 and enable_fail_flag == 0 and network_enable_fail_flag == 0 and network_disable_fail_flag == 0:
                    log.info("压测未发发现异常")

            self.device.kill_process(logcat_process_id)
            self.device.adb_pull_file(log_path, os.path.dirname(Config.mobile_btn_sta_test_log_path))
            log.info("****************开关4G压测结束******************")
        except Exception as e:
            log.error(str(e))
            log.error("开关4G压测用例运行过程中有异常，请检查！！！")
            assert False

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
            time.sleep(30)
            while flag < test_times:
                flag += 1
                # 上下电
                t_ser.open_relay(com_line)
                log.info("模拟U盘断开")
                time.sleep(10)
                t_ser.close_relay(com_line)
                log.info("模拟U盘插入")
                log.info("********U盘拔插%d次******" % flag)
                time.sleep(180)
        else:
            log.info(".sh脚本没跑起来，请检查！！！")

        log.info("****************U盘拔插识别用例结束***********************")

    @allure.feature("USB-Read-Write-stability")
    @allure.title("U盘/TF卡读取大数据压测")
    def test_usb_read_and_write_big_data_test(self):
        log.info("****************U盘/TF卡读取大数据压测用例开始***********************")

        # 后台启动捕捉log
        log_path = os.path.join("/sdcard/usb_speed/storage_read_write_speech_logcat.txt")  # log名称
        self.device.rm_file(log_path)  # 清除已存在的
        self.device.mkdir_directory("/sdcard/usb_speed")
        self.device.touch_file(log_path)
        # self.device.logcat_thread(log_path)

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

    @allure.feature("Sleep-Awake-stability")
    @allure.title("休眠唤醒检查基本功能")
    def test_sleep_awake_check_base_case(self):
        try:
            log.info("*************休眠唤醒检查基本功能压测用例开始**************")
            test_times = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.option_sleep_test_times))
            is_wifi = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.option_wifi_test))
            is_eth = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.option_eth_test))
            is_mobile = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.option_mobile_test))
            is_bt = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.option_bt_test))
            is_nfc = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.option_nfc_test))
            sleep_duration = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.option_sleep_duration))
            com_port = self.ui_conf_file.get(Config.section_sleep_wake, Config.option_sleep_com_port)
            com_line = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.option_sleep_config).split("_")[1])

            is_probability_test = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.is_probability_test))
            rounds_interval = int(self.ui_conf_file.get(Config.section_sleep_wake, Config.test_interval))

            # 开启模块
            # 测试前先检查所有的按钮开关
            if is_bt:
                log.info("****检查蓝牙当前状态")
                if not self.device.bt_is_enable():
                    self.device.enable_bt_btn()
                    time.sleep(3)
                if not self.device.bt_is_enable():
                    self.device.enable_bt_btn()
                    time.sleep(3)
                if not self.device.bt_is_enable():
                    log.error("无法开启蓝牙，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("蓝牙上电成功")

            # 检查蓝牙设备（从）是否连接上
            if not self.device.bt_is_connected():
                log.error("当前测试设备显示未连接上蓝牙设备（从）")

            # 需要跟彬哥确认NFC刷卡绑定app的问题
            if is_nfc:
                log.info("****检查nfc当前状态")
                if not self.device.nfc_is_enable():
                    self.device.enable_nfc_btn()
                    time.sleep(3)
                if not self.device.nfc_is_enable():
                    self.device.enable_nfc_btn()
                    time.sleep(3)
                if not self.device.nfc_is_enable():
                    log.error("无法开启NFC，请检查！！！")
                    time.sleep(3)
                    raise Exception
                log.info("NFC上电成功")

            if is_eth:
                log.info("****检查以太网当前状态")
                if not self.device.eth0_is_enable():
                    self.device.enable_eth0_btn()
                    time.sleep(3)
                    log.info("以太网上电")

            if is_wifi:
                log.info("****检查wifi当前状态")
                if not self.device.wifi_is_enable():
                    self.device.enable_wifi_btn()
                    time.sleep(3)
                log.info("wifi上电")

            if is_mobile:
                log.info("****检查4G当前当前状态")
                if not self.device.mobile_is_enable():
                    self.device.enable_mobile_btn()
                    time.sleep(3)
                log.info("4G上电")

            # 休眠
            flag = 0
            t_ser.loginSer(com_port)
            while flag < test_times:
                flag += 1
                if not self.device.is_screen_on():
                    self.device.press_power_button()
                    time.sleep(1)
                    self.device.unlock()

                t_ser.open_relay(com_line)
                log.info("USB调试线下电")
                self.device.restart_adb()
                if self.device.device_is_online():
                    time.sleep(3)
                    if self.device.device_is_online():
                        raise Exception("USB调试线下电失败，请检查！！！")
                log.info("15s后准备进入灭屏进入休眠")
                # time.sleep()
                time.sleep(sleep_duration * 60)
                t_ser.close_relay(com_line)
                log.info("USB调试线上电")
                self.device.restart_adb()
                now_time = time.time()
                while True:
                    if self.device.device_is_online():
                        log.info("检测到设备在线，设备唤醒，ADB唤醒")
                        break
                    if time.time() > now_time + 60:
                        log.error("ADB无法起来，无法设备未唤醒请检查！！！")
                        time.sleep(3)
                        raise Exception

                if not self.device.is_screen_on():
                    self.device.press_power_button()
                    time.sleep(1)
                self.device.unlock()

                log.info("检查基本功能")
                time.sleep(5)
                if is_bt:
                    log.info("********检查蓝牙开关状态")
                    if not self.device.bt_is_enable():
                        log.error("重启后蓝牙不是上电状态，请检查！！！")
                        raise Exception
                    log.info("启动后蓝牙当前为上电状态")
                    # 检查蓝牙设备是否连接上
                    if self.device.bt_is_connected():
                        log.info("当前显示已连接上蓝牙设备（从）")
                    else:
                        log.error("当前显示没连接上蓝牙设备，请检查！！！")
                        time.sleep(3)
                        raise Exception

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
                    # 检查从机蓝牙设备连接情况
                    time.sleep(3)
                    if self.device.bt_is_connected():
                        log.error("显示连接上蓝牙设备，蓝牙未断开，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    else:
                        log.info("已断开蓝牙设备（从）")

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
                    # 检查蓝牙设备（从）连接情况
                    time.sleep(10)
                    if self.device.bt_is_connected():
                        log.info("已经连接上蓝牙设备，请检查！！！")
                    else:
                        log.error("无法自动重连蓝牙设备，请检查！！！")
                        time.sleep(3)
                        raise Exception

                if is_nfc:
                    log.info("********检查NFC开关状态")
                    if not self.device.nfc_is_enable():
                        log.error("启动后nfc不是上电状态，请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("启动后nfc当前为上电状态")
                    # 对蓝牙进行关开操作
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

                # 检查各网络模块是否上电状态
                if is_eth:
                    log.info("********检查以太网状态")
                    if not self.device.eth0_is_enable():
                        log.error("启动后的以太网不是上电状态， 请检查！！！")
                        # if is_probability_test:
                        #     time.sleep(3)
                        #     raise Exception
                        time.sleep(3)
                        raise Exception
                    log.info("启动后以太网为上电状态")

                if is_wifi:
                    log.info("********检查以wifi态")
                    if not self.device.wifi_is_enable():
                        log.error("启动后的以wifi不是上电状态， 请检查！！！")
                        time.sleep(3)
                        raise Exception

                    log.info("启动后wifi为上电状态")

                if is_mobile:
                    log.info("********检查以流量数据态")
                    if not self.device.mobile_is_enable():
                        log.error("启动后的移动数据网络不是上电状态， 请检查！！！")
                        time.sleep(3)
                        raise Exception
                    log.info("启动后移动网络为上电状态")

                if not int(is_eth) and int(is_wifi) and int(is_mobile):
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
                        # if is_probability_test:
                        #     mobile_disable_fail_flag += 1
                        # else:
                        #     time.sleep(3)
                        #     raise Exception
                    log.info("移动数据下电")

                    if not self.device.ping_network(5, 60):
                        log.error("wifi无法上网， 请检查！！！")
                        time.sleep(3)
                        raise Exception
                        # if is_probability_test:
                        #     wifi_enable_no_network_fail += 1
                        # else:
                        #     time.sleep(3)
                        #     raise Exception
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
                        # if is_probability_test:
                        #     wifi_disable_fail_flag += 1
                        # else:
                        #     time.sleep(3)
                        #     raise Exception

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
                        # if is_probability_test:
                        #     mobile_enable_fail_flag += 1
                        # else:
                        #     time.sleep(3)
                        #     raise Exception
                    log.info("移动数据模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 35):
                        log.error("移动数据无法上网， 请检查！！！")
                        # if is_probability_test:
                        #     mobile_no_network_fail += 1
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
                        # if is_probability_test:
                        #     mobile_disable_fail_flag += 1
                        # else:
                        #     time.sleep(3)
                        #     raise Exception

                    self.device.enable_wifi_btn()
                    time.sleep(3)
                    if not self.device.wifi_is_enable():
                        self.device.enable_wifi_btn()
                        time.sleep(3)
                    if not self.device.wifi_is_enable():
                        log.error("wifi模块无法上电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                        # if is_probability_test:
                        #     wifi_enable_fail_flag += 1
                        # else:
                        #     time.sleep(3)
                        #     raise Exception
                    log.info("wifi模块上电成功")
                    # 检查网络
                    if not self.device.ping_network(5, 35):
                        log.error("wifi无法上网， 请检查！！！")
                        time.sleep(3)
                        raise Exception
                        # if is_probability_test:
                        #     wifi_enable_no_network_fail += 1
                        # else:
                        #     time.sleep(3)
                        #     raise Exception
                    log.info("wifi可正常上网")

                    self.device.enable_mobile_btn()
                    time.sleep(3)
                    if not self.device.mobile_is_enable():
                        self.device.enable_mobile_btn()
                        time.sleep(3)
                    if not self.device.mobile_is_enable():
                        log.error("移动数据模块无法上电，请检查！！！")
                        time.sleep(3)
                        raise Exception
                        # if is_probability_test:
                        #     mobile_enable_fail_flag += 1
                        # else:
                        #     time.sleep(3)
                        #     raise Exception
                    log.info("移动数据模块上电成功")
                time.sleep(rounds_interval)
                log.info("*************完成%d次压测**************" % flag)

            t_ser.logoutSer()
            log.info("**************休眠唤醒检查基本功能压测用例结束*************")
        except Exception as e:
            log.error(str(e))
            log.error("休眠唤醒检查基本功能压测用例运行过程中有异常，请检查！！！")
            assert False

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

        wlan_ini_address = self.device.get_wlan_mac()
        log.info("wifi初始地址为：%s" % wlan_ini_address)

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
            log.info("创建了文件：%s" % txt_file_path)

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

            current_wifi_address = self.device.get_wlan_mac()
            log.info("当前WIFI MAC地址为：%s" % current_wifi_address)

            if current_wifi_address != wlan_ini_address:
                log.error("恢复出厂设置前后wifi mac地址不一致，请检查！！！")
                time.sleep(3)
                raise Exception

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

            # current_wifi_address = self.device.get_wlan_mac()
            # log.info("当前WIFI MAC地址为：%s" % current_wifi_address)
            # if current_wifi_address != wlan_ini_address:
            #     log.error("恢复出厂设置前后wifi mac地址不一致，请检查！！！")
            #     time.sleep(3)
            #     raise Exception

            log.info("***************恢复出厂设置成功 %d 次" % times)

            time.sleep(1)
        log.info("***************恢复出厂设置检查压测结束***************")
