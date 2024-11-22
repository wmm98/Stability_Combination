import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import QTimer, QProcess, Qt, pyqtSlot
from tree_widget import Ui_MainWindow
from reboot_logo_ui import LogoDisplay
from ddr_emmc_ui import DDRDisplay
from boot_check_ui import BootCheckDisplay
from camera_preview_and_photograph import CameraStabilityDisplay
from wifi_btn_stability_ui import WifiBtnCheckDisplay
from mobile_btn_stability_ui import MobileBtnCheckDisplay
from eth_btn_stability_ui import EthBtnCheckDisplay
from usb_recognition_ui import USBFlashTestDisplay
from storage_read_write_speeds_ui import StorageTestDisplay
from factory_reset_ui import FactoryResetDisplay
from bt_connect_stability_ui import BtConnectDisplay
from boot_check_camera_sub_ui import BootCameraStabilityDisplay
from device_sleep_awake_ui import SleepAwakeDisplay
import os
import shutil
from PyQt5.QtGui import QPixmap
import serial.tools.list_ports
from PIL import Image
import rembg
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextImageFormat
import configparser
import time
import configfile
import config_path

conf_path = config_path.UIConfigPath()


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        return editor

    def setEditorData(self, editor, index):
        current_text = index.data()
        editor.setCurrentText(current_text)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())


class AllCertCaseValue:
    # 压测
    ROOT_PROTOCON_STA = 1
    # 立项压测
    ROOT_PROTOCON_L_X_STA_CHILD = 1.1
    ROOT_PROTOCON_L_X_STA_A1 = 1.11
    ROOT_PROTOCON_L_X_STA_A2 = 1.12
    ROOT_PROTOCON_L_X_STA_A3 = 1.13
    ROOT_PROTOCON_L_X_STA_A4 = 1.14
    ROOT_PROTOCON_L_X_STA_MAX = ROOT_PROTOCON_L_X_STA_A4 + 0.01

    # DDR,EMMC压测
    ROOT_PROTOCON_D_E_STA_CHILD = 1.2
    ROOT_PROTOCON_D_E_STA_TMISCAN_B0 = 1.21
    ROOT_PROTOCON_D_E_STA_TMISCAN_B1 = 1.22
    ROOT_PROTOCON_D_E_STA_TMISCAN_B2 = 1.23
    ROOT_PROTOCON_D_E_STA_TMISCAN_B3 = 1.24
    ROOT_PROTOCON_D_E_STA_MAX = ROOT_PROTOCON_D_E_STA_TMISCAN_B3 + 0.01

    # 卡logo压测
    ROOT_PROTOCON_L_G_STA_CHILD = 1.3
    ROOT_PROTOCON_L_G_STA_C1 = 1.31
    ROOT_PROTOCON_L_G_STA_C2 = 1.32
    ROOT_PROTOCON_L_G_STA_C3 = 1.33
    ROOT_PROTOCON_L_G_STA_MAX = ROOT_PROTOCON_L_G_STA_C3 + 0.01

    # 其他维护压测
    ROOT_PROTOCON_W_H_STA_CHILD = 1.4
    ROOT_PROTOCON_W_H_STA_d1 = 1.41
    ROOT_PROTOCON_W_H_STA_d2 = 1.42
    ROOT_PROTOCON_W_H_STA_d3 = 1.43
    ROOT_PROTOCON_W_H_STA_MAX = ROOT_PROTOCON_W_H_STA_d3 + 0.01


DictCommandInfo = {
    "压测": AllCertCaseValue.ROOT_PROTOCON_STA,
    "立项压测": AllCertCaseValue.ROOT_PROTOCON_L_X_STA_CHILD,
    "立项压测1": AllCertCaseValue.ROOT_PROTOCON_L_X_STA_A1,
    "立项压测2": AllCertCaseValue.ROOT_PROTOCON_L_X_STA_A2,
    "立项压测3": AllCertCaseValue.ROOT_PROTOCON_L_X_STA_A3,
    "立项压测4": AllCertCaseValue.ROOT_PROTOCON_L_X_STA_A4,

    "DDR/EMMC压测": AllCertCaseValue.ROOT_PROTOCON_D_E_STA_CHILD,
    "DDR-memtester压力测试": AllCertCaseValue.ROOT_PROTOCON_D_E_STA_TMISCAN_B0,
    "DDR-stressapptest": AllCertCaseValue.ROOT_PROTOCON_D_E_STA_TMISCAN_B1,
    "DDR-switch_stressapptest-高低内存切换": AllCertCaseValue.ROOT_PROTOCON_D_E_STA_TMISCAN_B2,
    "EMMC测试": AllCertCaseValue.ROOT_PROTOCON_D_E_STA_TMISCAN_B3,

    "开机卡logo压测": AllCertCaseValue.ROOT_PROTOCON_L_G_STA_CHILD,
    "适配器开关机": AllCertCaseValue.ROOT_PROTOCON_L_G_STA_C1,
    "适配器/电池+电源--正常关机": AllCertCaseValue.ROOT_PROTOCON_L_G_STA_C2,
    "适配器/电池+电源--异常关机": AllCertCaseValue.ROOT_PROTOCON_L_G_STA_C3,

    "其他维护压测": AllCertCaseValue.ROOT_PROTOCON_W_H_STA_CHILD,
    "压测1": AllCertCaseValue.ROOT_PROTOCON_W_H_STA_d1,
    "压测2": AllCertCaseValue.ROOT_PROTOCON_W_H_STA_d2,
    "压测3": AllCertCaseValue.ROOT_PROTOCON_W_H_STA_d3,

}


class UIDisplay(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(UIDisplay, self).__init__()
        self.last_position = 0
        self.last_modify_time = 0
        self.last_modify_time_preview = 0
        self.last_modify_time_photo = 0

        self.bg_config = configfile.ConfigP(self.background_config_file_path)
        self.ui_config = configfile.ConfigP(self.ui_config_file_path)
        # 初始化子界面
        self.logo_window = LogoDisplay()
        self.DDR_EMMC_window = DDRDisplay()
        self.lx_boot_check_window = BootCheckDisplay()
        self.lx_preview_photograph_window = CameraStabilityDisplay()
        self.mt_wifi_btn_check_window = WifiBtnCheckDisplay()
        self.mt_mobile_btn_check_window = MobileBtnCheckDisplay()
        self.mt_eth_btn_check_window = EthBtnCheckDisplay()
        self.usb_recognition_window = USBFlashTestDisplay()
        self.storage_read_write_speed_window = StorageTestDisplay()
        self.factory_reset_window = FactoryResetDisplay()
        self.bt_connect_test_window = BtConnectDisplay()
        self.boot_camera_sub_window = BootCameraStabilityDisplay()
        self.sleep_awake_window = SleepAwakeDisplay()
        self.setupUi(self)
        self.AllTestCase = None
        self.intiui()
        self.cases_selected_sum = 0

    def intiui(self):
        # 初始化
        # 初始化图片cursor
        self.cursor = QTextCursor(self.document)
        self.cursor_camera = QTextCursor(self.document_camera)

        self.ui_config.init_config_file()
        self.ui_config.add_config_section(self.ui_config.section_ui_to_background)
        # 初始化进程
        self.qt_process = QProcess()
        self.root_process = QProcess()
        self.mem_free_process = QProcess()

        # 展示用例树
        self.list_tree_cases()
        # 节点全部展开
        self.treeWidget.expandAll()
        # self.item_D_E_STA.setExpanded(False)
        # self.item_L_X_STA.setExpanded(False)
        # self.item_L_G_STA.setExpanded(False)
        # self.item_sta_root.setExpanded(True)
        # 父节点选中全选子节点
        self.treeWidget.itemChanged.connect(self.handlechanged)
        # 显示相应需要配置的参数填入
        self.treeWidget.itemClicked.connect(self.on_item_clicked)
        # 链槽
        self.select_devices_name()
        self.list_COM()

        # self.root_button.clicked.connect(self.double_check_root)
        self.submit_button.clicked.connect(self.handle_submit)
        self.stop_process_button.clicked.connect(self.stop_process)
        # 进程完成
        self.qt_process.finished.connect(self.handle_finished)
        self.mem_free_process.finished.connect(self.mem_free_finished_handle)
        self.logo_window.submit_button.clicked.connect(self.display_boot_logo_cases_test_times)
        self.DDR_EMMC_window.submit_button.clicked.connect(self.display_ddr_emmc_cases_test_times)
        self.lx_boot_check_window.submit_button.clicked.connect(self.display_lx_boot_check_case_test_times)
        self.lx_preview_photograph_window.submit_button.clicked.connect(self.display_lx_camera_compare_test_times)
        self.mt_wifi_btn_check_window.submit_button.clicked.connect(self.display_wifi_btn_check_test_times)
        self.mt_mobile_btn_check_window.submit_button.clicked.connect(self.display_mobile_btn_check_test_times)
        # self.mt_eth_btn_check_window.submit_button.clicked.connect(self.display_eth_btn_check_test_times)
        self.usb_recognition_window.submit_button.clicked.connect(self.display_usb_recognize_test_times)
        self.storage_read_write_speed_window.submit_button.clicked.connect(self.display_storage_write_read_speed_test_times)
        self.factory_reset_window.submit_button.clicked.connect(self.display_factory_reset_test_times)
        self.bt_connect_test_window.submit_button.clicked.connect(self.display_bt_connect_test_times)
        self.sleep_awake_window.submit_button.clicked.connect(self.display_sleep_wake_test_times)
        # 初始化图片cursor
        # self.cursor = QTextCursor(self.document)

    def list_tree_cases(self):
        # 用例数结构
        # 设置列数
        self.treeWidget.setColumnCount(3)
        # 设置树形控件头部的标题
        self.treeWidget.setHeaderLabels(['测试场景', "运行时长/轮数", "单位"])
        self.treeWidget.setColumnWidth(0, 450)

        # 设置根节点
        self.AllTestCase = QTreeWidgetItem(self.treeWidget)
        # self.case_tree = self.AllTestCase.child()
        self.AllTestCase.setText(0, '测试项')

        # 压测根节点
        self.item_sta_root = QTreeWidgetItem(self.AllTestCase)
        self.item_sta_root.setText(0, "压测")
        self.item_sta_root.setFlags(self.item_sta_root.flags() | Qt.ItemIsSelectable)
        # 立项测试
        self.item_L_X_STA = QTreeWidgetItem(self.item_sta_root)
        self.item_L_X_STA.setText(0, "立项压测")
        self.item_L_X_STA.setCheckState(0, Qt.Unchecked)
        self.item_L_X_STA.setFlags(self.item_L_X_STA.flags() | Qt.ItemIsSelectable)
        # 立项测试子用例
        self.item_L_X_STA_child_boot_check = QTreeWidgetItem(self.item_L_X_STA)
        self.item_L_X_STA_child_boot_check.setText(0, "开关机检查基本功能")
        self.item_L_X_STA_child_boot_check.setCheckState(0, Qt.Unchecked)
        self.item_L_X_STA_child_boot_check.setText(1, "")
        self.item_L_X_STA_child_boot_check.setText(2, "次")
        self.item_L_X_STA_child_boot_check.setFlags(
            self.item_L_X_STA_child_boot_check.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_L_X_STA_child_camera_compare = QTreeWidgetItem(self.item_L_X_STA)
        self.item_L_X_STA_child_camera_compare.setText(0, "前后摄像头拍照问题对比")
        self.item_L_X_STA_child_camera_compare.setCheckState(0, Qt.Unchecked)
        self.item_L_X_STA_child_camera_compare.setText(1, "")
        self.item_L_X_STA_child_camera_compare.setText(2, "次")
        self.item_L_X_STA_child_camera_compare.setFlags(
            self.item_L_X_STA_child_camera_compare.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        # 蓝牙连压测
        self.item_L_X_STA_child_bt_conenct = QTreeWidgetItem(self.item_L_X_STA)
        self.item_L_X_STA_child_bt_conenct.setText(0, "蓝牙连接测试")
        self.item_L_X_STA_child_bt_conenct.setCheckState(0, Qt.Unchecked)
        self.item_L_X_STA_child_bt_conenct.setText(1, "")
        self.item_L_X_STA_child_bt_conenct.setText(2, "次")
        self.item_L_X_STA_child_bt_conenct.setFlags(
            self.item_L_X_STA_child_bt_conenct.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        # DDR、EMMC压测
        self.item_D_E_STA = QTreeWidgetItem(self.item_sta_root)
        self.item_D_E_STA.setText(0, "DDR/EMMC压测")
        self.item_D_E_STA.setCheckState(0, Qt.Unchecked)
        self.item_D_E_STA.setFlags(self.item_D_E_STA.flags() | Qt.ItemIsSelectable)
        # 子用例
        self.item_D_E_STA_memtester = QTreeWidgetItem(self.item_D_E_STA)
        self.item_D_E_STA_memtester.setText(0, "DDR-memtester压力测试")
        self.item_D_E_STA_memtester.setCheckState(0, Qt.Unchecked)
        self.item_D_E_STA_memtester.setText(1, "")
        self.item_D_E_STA_memtester.setText(2, "次")
        self.item_D_E_STA_memtester.setFlags(
            self.item_D_E_STA_memtester.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_D_E_STA_stressapptest = QTreeWidgetItem(self.item_D_E_STA)
        self.item_D_E_STA_stressapptest.setText(0, "DDR-stressapptest压力测试")
        self.item_D_E_STA_stressapptest.setCheckState(0, Qt.Unchecked)
        self.item_D_E_STA_stressapptest.setText(1, "")
        self.item_D_E_STA_stressapptest.setText(2, "小时")
        self.item_D_E_STA_stressapptest.setFlags(
            self.item_D_E_STA_stressapptest.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_D_E_STA_switch_stressapptest = QTreeWidgetItem(self.item_D_E_STA)
        self.item_D_E_STA_switch_stressapptest.setText(0, "DDR-switch_stressapptest-高低内存切换")
        self.item_D_E_STA_switch_stressapptest.setCheckState(0, Qt.Unchecked)
        self.item_D_E_STA_switch_stressapptest.setText(1, "")
        self.item_D_E_STA_switch_stressapptest.setText(2, "次")
        self.item_D_E_STA_switch_stressapptest.setFlags(
            self.item_D_E_STA_switch_stressapptest.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_D_E_EMMC = QTreeWidgetItem(self.item_D_E_STA)
        self.item_D_E_EMMC.setText(0, "EMMC测试")
        self.item_D_E_EMMC.setCheckState(0, Qt.Unchecked)
        self.item_D_E_EMMC.setText(1, "")
        self.item_D_E_EMMC.setText(2, "次")
        self.item_D_E_EMMC.setFlags(
            self.item_D_E_EMMC.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        # 开关机卡logo
        self.item_L_G_STA = QTreeWidgetItem(self.item_sta_root)
        self.item_L_G_STA.setText(0, "开机卡logo压测")
        self.item_L_G_STA.setCheckState(0, Qt.Unchecked)
        self.item_L_G_STA.setFlags(self.item_L_G_STA.flags() | Qt.ItemIsSelectable)
        # 子用例
        self.item_L_G_STA_adapter_boot = QTreeWidgetItem(self.item_L_G_STA)
        self.item_L_G_STA_adapter_boot.setText(0, "适配器开关机")
        self.item_L_G_STA_adapter_boot.setCheckState(0, Qt.Unchecked)
        self.item_L_G_STA_adapter_boot.setText(1, "")
        self.item_L_G_STA_adapter_boot.setText(2, "次")
        self.item_L_G_STA_adapter_boot.setFlags(
            self.item_L_G_STA_adapter_boot.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_L_G_STA_power_button_normal = QTreeWidgetItem(self.item_L_G_STA)
        self.item_L_G_STA_power_button_normal.setText(0, "适配器/电池+电源--正常关机")
        self.item_L_G_STA_power_button_normal.setCheckState(0, Qt.Unchecked)
        self.item_L_G_STA_power_button_normal.setText(1, "")
        self.item_L_G_STA_power_button_normal.setText(2, "次")
        self.item_L_G_STA_power_button_normal.setFlags(
            self.item_L_G_STA_power_button_normal.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_L_G_STA_adapter_battery_button_unormal = QTreeWidgetItem(self.item_L_G_STA)
        self.item_L_G_STA_adapter_battery_button_unormal.setText(0, "适配器/电池+电源--异常关机")
        self.item_L_G_STA_adapter_battery_button_unormal.setCheckState(0, Qt.Unchecked)
        self.item_L_G_STA_adapter_battery_button_unormal.setText(1, "")
        self.item_L_G_STA_adapter_battery_button_unormal.setText(2, "次")
        self.item_L_G_STA_adapter_battery_button_unormal.setFlags(
            self.item_L_G_STA_adapter_battery_button_unormal.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        # 其他维护压测
        self.item_M_T_STA = QTreeWidgetItem(self.item_sta_root)
        self.item_M_T_STA.setText(0, "其他维护压测")
        self.item_M_T_STA.setCheckState(0, Qt.Unchecked)
        self.item_M_T_STA.setFlags(self.item_M_T_STA.flags() | Qt.ItemIsSelectable)

        self.item_M_T_STA_wifi_btn = QTreeWidgetItem(self.item_M_T_STA)
        self.item_M_T_STA_wifi_btn.setText(0, "开关wifi检测网络压测")
        self.item_M_T_STA_wifi_btn.setCheckState(0, Qt.Unchecked)
        self.item_M_T_STA_wifi_btn.setText(1, "")
        self.item_M_T_STA_wifi_btn.setText(2, "次")
        self.item_M_T_STA_wifi_btn.setFlags(
            self.item_M_T_STA_wifi_btn.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_M_T_STA_mobile_btn = QTreeWidgetItem(self.item_M_T_STA)
        self.item_M_T_STA_mobile_btn.setText(0, "开关4G检测网络压测")
        self.item_M_T_STA_mobile_btn.setCheckState(0, Qt.Unchecked)
        self.item_M_T_STA_mobile_btn.setText(1, "")
        self.item_M_T_STA_mobile_btn.setText(2, "次")
        self.item_M_T_STA_mobile_btn.setFlags(
            self.item_M_T_STA_mobile_btn.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_M_T_STA_sleep_wake = QTreeWidgetItem(self.item_M_T_STA)
        self.item_M_T_STA_sleep_wake.setText(0, "休眠唤醒检查基本功能")
        self.item_M_T_STA_sleep_wake.setCheckState(0, Qt.Unchecked)
        self.item_M_T_STA_sleep_wake.setText(1, "")
        self.item_M_T_STA_sleep_wake.setText(2, "次")
        self.item_M_T_STA_sleep_wake.setFlags(
            self.item_M_T_STA_sleep_wake.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_M_T_STA_usb_recognize = QTreeWidgetItem(self.item_M_T_STA)
        self.item_M_T_STA_usb_recognize.setText(0, "U盘拔插识别压测")
        self.item_M_T_STA_usb_recognize.setCheckState(0, Qt.Unchecked)
        self.item_M_T_STA_usb_recognize.setText(1, "")
        self.item_M_T_STA_usb_recognize.setText(2, "次")
        self.item_M_T_STA_usb_recognize.setFlags(
            self.item_M_T_STA_usb_recognize.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_M_T_STA_storage_speed = QTreeWidgetItem(self.item_M_T_STA)
        self.item_M_T_STA_storage_speed.setText(0, "U盘/TF卡读写速率压测")
        self.item_M_T_STA_storage_speed.setCheckState(0, Qt.Unchecked)
        self.item_M_T_STA_storage_speed.setText(1, "")
        self.item_M_T_STA_storage_speed.setText(2, "次")
        self.item_M_T_STA_storage_speed.setFlags(
            self.item_M_T_STA_storage_speed.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

        self.item_M_T_STA_factory_reset = QTreeWidgetItem(self.item_M_T_STA)
        self.item_M_T_STA_factory_reset.setText(0, "恢复出厂设置检查压测")
        self.item_M_T_STA_factory_reset.setCheckState(0, Qt.Unchecked)
        self.item_M_T_STA_factory_reset.setText(1, "")
        self.item_M_T_STA_factory_reset.setText(2, "次")
        self.item_M_T_STA_factory_reset.setFlags(
            self.item_M_T_STA_factory_reset.flags() | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)

    def display_sleep_wake_test_times(self):
        time.sleep(1)
        if self.sleep_awake_window.submit_flag:
            if self.item_M_T_STA_sleep_wake.checkState(0) == 2:
                times = self.ui_config.get_option_value(self.ui_config.section_sleep_wake,
                                                        self.ui_config.option_sleep_test_times)
                self.item_M_T_STA_sleep_wake.setText(1, times)
                self.item_M_T_STA_sleep_wake.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_bt_connect_test_times(self):
        time.sleep(1)
        if self.bt_connect_test_window.submit_flag:
            if self.item_L_X_STA_child_bt_conenct.checkState(0) == 2:
                times = self.ui_config.get_option_value(self.ui_config.section_bt_connect_test,
                                                        self.ui_config.option_bt_connect_test_times)
                self.item_L_X_STA_child_bt_conenct.setText(1, times)
                self.item_L_X_STA_child_bt_conenct.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_factory_reset_test_times(self):
        time.sleep(1)
        if self.factory_reset_window.submit_flag:
            if self.item_M_T_STA_factory_reset.checkState(0) == 2:
                times = self.ui_config.get_option_value(self.ui_config.section_factory_reset_stability, self.ui_config.option_factory_reset_test_times)
                self.item_M_T_STA_factory_reset.setText(1, times)
                self.item_M_T_STA_factory_reset.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_storage_write_read_speed_test_times(self):
        time.sleep(1)
        if self.storage_read_write_speed_window.submit_flag:
            if self.item_M_T_STA_storage_speed.checkState(0) == 2:
                times = self.ui_config.get_option_value(self.ui_config.section_storage_stability, self.ui_config.option_storage_test_times)
                self.item_M_T_STA_storage_speed.setText(1, times)
                self.item_M_T_STA_storage_speed.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_usb_recognize_test_times(self):
        time.sleep(1)
        if self.usb_recognition_window.submit_flag:
            if self.item_M_T_STA_usb_recognize.checkState(0) == 2:
                times = self.ui_config.get_option_value(self.ui_config.section_usb_recognize, self.ui_config.option_usb_recognition_test_times)
                self.item_M_T_STA_usb_recognize.setText(1, times)
                self.item_M_T_STA_usb_recognize.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    # def display_eth_btn_check_test_times(self):
    #     time.sleep(1)
    #     if self.mt_eth_btn_check_window.submit_flag:
    #         if self.item_M_T_STA_eth_btn.checkState(0) == 2:
    #             times = self.ui_config.get_option_value(self.ui_config.section_eth_check, self.ui_config.option_eth_btn_test_times)
    #             self.item_M_T_STA_eth_btn.setText(1, times)
    #             self.item_M_T_STA_eth_btn.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_mobile_btn_check_test_times(self):
        time.sleep(1)
        if self.mt_mobile_btn_check_window.submit_flag:
            if self.item_M_T_STA_mobile_btn.checkState(0) == 2:
                times = self.ui_config.get_option_value(self.ui_config.section_mobile_check, self.ui_config.option_mobile_btn_test_times)
                self.item_M_T_STA_mobile_btn.setText(1, times)
                self.item_M_T_STA_mobile_btn.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_wifi_btn_check_test_times(self):
        time.sleep(1)
        if self.mt_wifi_btn_check_window.submit_flag:
            if self.item_M_T_STA_wifi_btn.checkState(0) == 2:
                times = self.ui_config.get_option_value(self.ui_config.section_wifi_check, self.ui_config.option_wifi_btn_test_times)
                self.item_M_T_STA_wifi_btn.setText(1, times)
                self.item_M_T_STA_wifi_btn.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_lx_camera_compare_test_times(self):
        time.sleep(1)
        if self.lx_preview_photograph_window.submit_flag:
            if self.item_L_X_STA_child_camera_compare.checkState(0) == 2:
                times = self.ui_config.get_option_value(self.ui_config.section_ui_camera_check, self.ui_config.option_camera_test_times)
                self.item_L_X_STA_child_camera_compare.setText(1, times)
                self.item_L_X_STA_child_camera_compare.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_lx_boot_check_case_test_times(self):
        time.sleep(1)
        if self.lx_boot_check_window.submit_flag:
            if self.item_L_X_STA_child_boot_check.checkState(0) == 2:
                boot_check_times = self.ui_config.get_option_value(self.ui_config.section_ui_boot_check, self.ui_config.ui_option_logo_test_times)
                self.item_L_X_STA_child_boot_check.setText(1, boot_check_times)
                self.item_L_X_STA_child_boot_check.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐

    def display_ddr_emmc_cases_test_times(self):
        time.sleep(1)
        if self.DDR_EMMC_window.submit_flag:
            if self.item_D_E_EMMC.checkState(0) == 2:
                emmc_times = self.ui_config.get_option_value(self.ui_config.section_DDR_EMMC,
                                                             self.ui_config.ui_option_emmmc_duration)

                self.item_D_E_EMMC.setText(1, emmc_times)
                self.item_D_E_EMMC.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐
            if self.item_D_E_STA_memtester.checkState(0) == 2:
                memtester_times = self.ui_config.get_option_value(self.ui_config.section_DDR_EMMC,
                                                                  self.ui_config.ui_option_memtester_duration)
                self.item_D_E_STA_memtester.setText(1, memtester_times)
                self.item_D_E_STA_memtester.setTextAlignment(1, Qt.AlignRight)
            if self.item_D_E_STA_stressapptest.checkState(0) == 2:
                stressapptest_times = self.ui_config.get_option_value(self.ui_config.section_DDR_EMMC,
                                                                      self.ui_config.ui_option_stressapptest_duration)
                self.item_D_E_STA_stressapptest.setText(1, stressapptest_times)
                self.item_D_E_STA_stressapptest.setTextAlignment(1, Qt.AlignRight)
            if self.item_D_E_STA_switch_stressapptest.checkState(0) == 2:
                stressapptest_switch_times = self.ui_config.get_option_value(self.ui_config.section_DDR_EMMC,
                                                                             self.ui_config.ui_option_switch_stressapptest_duration)
                self.item_D_E_STA_switch_stressapptest.setText(1, stressapptest_switch_times)
                self.item_D_E_STA_switch_stressapptest.setTextAlignment(1, Qt.AlignRight)

    def display_boot_logo_cases_test_times(self):
        time.sleep(1)
        if self.logo_window.submit_flag:
            times = self.ui_config.get_option_value(self.ui_config.section_ui_logo,
                                                    self.ui_config.ui_option_logo_test_times)
            if self.item_L_G_STA_adapter_boot.checkState(0) == 2:
                self.item_L_G_STA_adapter_boot.setText(1, times)
                self.item_L_G_STA_adapter_boot.setTextAlignment(1, Qt.AlignRight)  # 设置第二列文本右对齐
            if self.item_L_G_STA_power_button_normal.checkState(0) == 2:
                self.item_L_G_STA_power_button_normal.setText(1, times)
                self.item_L_G_STA_power_button_normal.setTextAlignment(1, Qt.AlignRight)
            if self.item_L_G_STA_adapter_battery_button_unormal.checkState(0) == 2:
                self.item_L_G_STA_adapter_battery_button_unormal.setText(1, times)
                self.item_L_G_STA_adapter_battery_button_unormal.setTextAlignment(1, Qt.AlignRight)

    def on_item_clicked(self, item):
        # 开关机卡logo窗口处理
        if item == self.item_L_G_STA or item.parent() == self.item_L_G_STA:
            if item.checkState(0) == 2:
                if not self.logo_window.isVisible():
                    self.logo_window.show()
        if item == self.item_D_E_STA or item.parent() == self.item_D_E_STA:
            if item.checkState(0) == 2:
                if not self.DDR_EMMC_window.isVisible():
                    self.DDR_EMMC_window.show()
                # 在子界面勾上的需要测试的选项
                if item == self.item_D_E_STA:
                    self.DDR_EMMC_window.is_EEMC_test.setChecked(True)
                    self.DDR_EMMC_window.is_DDR_memtester_test.setChecked(True)
                    self.DDR_EMMC_window.is_DDR_streessapptest_test.setChecked(True)
                    self.DDR_EMMC_window.is_DDR_streessapptest_switch_test.setChecked(True)
                if item == self.item_D_E_STA_memtester:
                    self.DDR_EMMC_window.is_DDR_memtester_test.setChecked(True)
                if item == self.item_D_E_STA_stressapptest:
                    self.DDR_EMMC_window.is_DDR_streessapptest_test.setChecked(True)
                if item == self.item_D_E_STA_switch_stressapptest:
                    self.DDR_EMMC_window.is_DDR_streessapptest_switch_test.setChecked(True)
                if item == self.item_D_E_EMMC:
                    self.DDR_EMMC_window.is_EEMC_test.setChecked(True)
            else:
                # 取消相关选项
                if item == self.item_D_E_STA:
                    self.DDR_EMMC_window.is_EEMC_test.setChecked(False)
                    self.DDR_EMMC_window.is_DDR_memtester_test.setChecked(False)
                    self.DDR_EMMC_window.is_DDR_streessapptest_test.setChecked(False)
                    self.DDR_EMMC_window.is_DDR_streessapptest_switch_test.setChecked(False)
                if item == self.item_D_E_STA_memtester:
                    self.DDR_EMMC_window.is_DDR_memtester_test.setChecked(False)
                if item == self.item_D_E_STA_stressapptest:
                    self.DDR_EMMC_window.is_DDR_streessapptest_test.setChecked(False)
                if item == self.item_D_E_STA_switch_stressapptest:
                    self.DDR_EMMC_window.is_DDR_streessapptest_switch_test.setChecked(False)
                if item == self.item_D_E_EMMC:
                    self.DDR_EMMC_window.is_EEMC_test.setChecked(False)

        if item == self.item_L_X_STA_child_boot_check:
            if item.checkState(0) == 2:
                if not self.lx_boot_check_window.isVisible():
                    self.lx_boot_check_window.show()
                # 相机窗口
                if not self.boot_camera_sub_window.isVisible():
                    self.boot_camera_sub_window.show()

        if item == self.item_L_X_STA_child_camera_compare:
            if item.checkState(0) == 2:
                if not self.lx_preview_photograph_window.isVisible():
                    self.lx_preview_photograph_window.show()

        if item == self.item_M_T_STA_wifi_btn:
            if item.checkState(0) == 2:
                if not self.mt_wifi_btn_check_window.isVisible():
                    self.mt_wifi_btn_check_window.show()

        if item == self.item_M_T_STA_mobile_btn:
            if item.checkState(0) == 2:
                if not self.mt_mobile_btn_check_window.isVisible():
                    self.mt_mobile_btn_check_window.show()

        if item == self.item_M_T_STA_sleep_wake:
            if item.checkState(0) == 2:
                if not self.sleep_awake_window.isVisible():
                    self.sleep_awake_window.show()

        if item == self.item_M_T_STA_usb_recognize:
            if item.checkState(0) == 2:
                if not self.usb_recognition_window.isVisible():
                    self.usb_recognition_window.show()

        if item == self.item_M_T_STA_storage_speed:
            if item.checkState(0) == 2:
                if not self.storage_read_write_speed_window.isVisible():
                    self.storage_read_write_speed_window.show()

        if item == self.item_M_T_STA_factory_reset:
            if item.checkState(0) == 2:
                if not self.factory_reset_window.isVisible():
                    self.factory_reset_window.show()

        if item == self.item_L_X_STA_child_bt_conenct:
            if item.checkState(0) == 2:
                if not self.bt_connect_test_window.isVisible():
                    self.bt_connect_test_window.show()

    def handlechanged(self, item, column):
        # 获取选中节点的子节点个数
        count = item.childCount()
        # 如果被选中,子节点全选中勾选
        if item.checkState(column) == Qt.Checked:
            for f in range(count):
                if item.child(f).checkState(0) != Qt.Checked:
                    item.child(f).setCheckState(0, Qt.Checked)
        # 如果取消选中,子节点全取消勾选
        if item.checkState(column) == Qt.Unchecked:
            for f in range(count):
                if item.child(f).checkState != Qt.Unchecked:
                    item.child(f).setCheckState(0, Qt.Unchecked)

    def mem_free_finished_handle(self):
        with open(conf_path.mem_log_path, "r", encoding="utf-8") as f:
            text = f.read()
        if len(text) != 0:
            self.text_edit.insertPlainText(text)
        else:
            self.text_edit.insertPlainText("读取可用运行内存数据失败， 请检查！！！")
        self.text_edit.insertPlainText("查询结束.")

    def double_check_root(self):
        # adb shell setprop persist.debuggable 1,adb reboot
        cmd = self.root_steps_edit.currentText()
        cmd_split = []
        if len(cmd) != 0:
            if "," in cmd:
                cmd_split = cmd.split(",")
            elif "，" in cmd:
                cmd_split = cmd.split("，")
            else:
                cmd_split.append(cmd)

            # 给指令加上设备区别 ['adb -s 5eea0becf3b0f513 root', 'adb -s 5eea0becf3b0f513 remount']
            self.new_cmds = []
            for s_p in cmd_split:
                add_d = "-s %s" % self.edit_device_name.currentText()
                cmd_list = s_p.split(" ")
                cmd_list.insert(1, add_d)
                self.new_cmds.append(" ".join(cmd_list))
            self.ui_config.add_config_option(self.ui_config.section_ui_to_background,
                                             self.ui_config.ui_option_root_steps,
                                             ",".join(self.new_cmds))
        else:
            self.ui_config.add_config_option(self.ui_config.section_ui_to_background,
                                             self.ui_config.ui_option_root_steps, "")

    def handle_finished(self):
        self.stop_process()

    # 获取所有节点的状态
    def get_tree_item_status(self, tree_item):
        status = tree_item.checkState(0)
        if status == 2:
            self.cases_selected_sum += 1
        result = {
            "text": tree_item.text(0),
            "status": status,
            "children": [],
            "duration": tree_item.text(1)
        }
        # 我添加的
        for i in range(tree_item.childCount()):
            child_item = tree_item.child(i)
            result["children"].append(self.get_tree_item_status(child_item))
        return result

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):
        try:
            # 初始化log文件
            with open(self.debug_log_path, "w") as f:
                f.close()

            # 检查用例是否为空
            self.tree_status = []
            # 用例跑的时间集
            self.tree_values = []
            for i in range(self.treeWidget.topLevelItemCount()):
                item = self.treeWidget.topLevelItem(i)
                # 2 表示已勾选，0 表示未勾选，1 表示半选中
                self.tree_status.append(self.get_tree_item_status(item))

            # 保存要跑的用例
            self.durations = []
            self.cases = []
            cases_duration = []
            tree_status = self.tree_status[0]["children"][0]["children"]

            # 提取压测用例
            for slave in tree_status:
                for children in slave['children']:
                    if children["status"] == 2:
                        if "适配器开关机" in children["text"]:
                            if "boot_logo" not in self.cases:
                                self.cases.append("boot_logo")
                            self.ui_config.add_config_option(self.ui_config.section_ui_logo,
                                                             self.ui_config.ui_option_logo_cases, "1")
                        elif "适配器/电池+电源--正常关机" in children["text"]:
                            if "boot_logo" not in self.cases:
                                self.cases.append("boot_logo")
                                if "boot_logo" not in self.cases:
                                    self.cases.append("boot_logo")
                            self.ui_config.add_config_option(self.ui_config.section_ui_logo,
                                                             self.ui_config.ui_option_logo_cases, "2")
                        elif "适配器/电池+电源--异常关机" in children["text"]:
                            if "boot_logo" not in self.cases:
                                self.cases.append("boot_logo")
                                if "boot_logo" not in self.cases:
                                    self.cases.append("boot_logo")
                            self.ui_config.add_config_option(self.ui_config.section_ui_logo,
                                                             self.ui_config.ui_option_logo_cases, "3")

                        elif children["text"] in ["DDR-memtester压力测试", "DDR-stressapptest压力测试",
                                                  "DDR-switch_stressapptest-高低内存切换", "EMMC测试"]:
                            if "DDR-Integration-testing" not in self.cases:
                                self.cases.append("DDR-Integration-testing")

                        else:
                            self.cases.append(children["text"])

            if len(self.cases) == 0:
                self.get_message_box("请勾选用例！！！")
                return

            # 相应用例转为英文标识
            self.transfer_cases = []
            for case in self.cases:
                if "开关机检查基本功能" in case:
                    self.transfer_cases.append("boot_check_stability")
                if "前后摄像头拍照问题对比" in case:
                    self.transfer_cases.append("front_rear_camera_stability")
                if "开关wifi检测网络压测" in case:
                    self.transfer_cases.append("mt-wifi_btn_stability")
                if "开关4G检测网络压测" in case:
                    self.transfer_cases.append("mt-mobile_btn_stability")
                if "开关以太网ping包压测" in case:
                    self.transfer_cases.append("mt-eth_btn_stability")
                if "DDR" in case or "EMMC" in case:
                    self.transfer_cases.append("DDR-Integration-testing")
                if "U盘拔插识别压测" in case:
                    self.transfer_cases.append("USB-recognition-stability")
                if "U盘/TF卡读写速率压测" in case:
                    self.transfer_cases.append("USB-Read-Write-stability")
                if "恢复出厂设置检查压测" in case:
                    self.transfer_cases.append("Factory-Reset-stability")
                if "蓝牙连接测试" in case:
                    self.transfer_cases.append("bt_connect_test")
                if "boot_logo" in case:
                    self.transfer_cases.append("boot_logo")
                if "休眠唤醒检查基本功能" in case:
                    self.transfer_cases.append("Sleep-Awake-stability")

            self.ui_config.add_config_option(self.ui_config.section_ui_to_background,
                                             self.ui_config.ui_option_device_name,
                                             self.edit_device_name.currentText())
            # 保存用例
            self.ui_config.add_config_option(self.ui_config.section_ui_to_background,
                                             self.ui_config.ui_option_cases, ",".join(self.transfer_cases))

            # 检查完保存配置
            # self.save_config(self.config_file_path)
            # 启动
            self.start_qt_process(self.run_bat_path)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_debug_log)
            self.file_timer = QTimer(self)
            self.file_camera_timer = QTimer(self)
            # 先删除之前测试的照片
            self.text_edit_final.clear()
            if os.path.exists(conf_path.logo_test_screen0_path):
                os.remove(conf_path.logo_test_screen0_path)
            self.file_timer.timeout.connect(self.check_image_modification)
            self.text_edit_final_camera.clear()
            if os.path.exists(conf_path.camera_sta_test_default_photograph_path):
                os.remove(conf_path.camera_sta_test_default_photograph_path)
            self.file_camera_timer.timeout.connect(self.check_image_camera_modification)

            self.check_interval = 1000  # 定时器间隔，单位毫秒
            self.timer.start(self.check_interval)  # 启动定时器
            self.file_timer.start(self.check_interval)
            self.file_camera_timer.start(self.check_interval)
            self.stop_process_button.setEnabled(True)
            self.submit_button.setDisabled(True)
            self.submit_button.setText("测试中...")
        except Exception as e:
            print(e)

    def check_image_modification(self):
        """检查图片文件是否有修改"""
        if os.path.exists(conf_path.logo_test_screen0_path):
            current_mod_time = self.get_file_modification_time(conf_path.logo_test_screen0_path)
            if current_mod_time != self.last_modify_time:
                self.last_modify_time = current_mod_time  # 更新为新的修改时间
                self.add_logo_image(conf_path.logo_test_screen0_path)

    def check_image_camera_modification(self):
        """检查图片文件是否有修改"""
        if os.path.exists(conf_path.camera_sta_test_default_photograph_path):

            current_mod_time_ph = self.get_file_modification_time(conf_path.camera_sta_test_default_photograph_path)
            if current_mod_time_ph != self.last_modify_time_photo:
                self.last_modify_time_photo = current_mod_time_ph  # 更新为新的修改时间
                self.add_logo_image_camera(conf_path.camera_sta_test_default_photograph_path)

    def get_file_modification_time(self, file_path):
        """获取文件的最后修改时间"""
        file_info = QFileInfo(file_path)
        last_modify = file_info.lastModified()
        return last_modify

    def get_COM_config(self):
        return ["1路", "2路", "3路", "4路"]

    def stop_process(self):
        # 文件位置初始化
        self.force_task_kill()
        self.last_position = 0
        self.stop_process_button.setDisabled(True)
        self.submit_button.setEnabled(True)
        self.submit_button.setText("开始测试")
        self.timer.stop()
        self.file_timer.stop()

    def start_qt_process(self, file):
        # 启动 外部 脚本
        self.qt_process.start(file)

    def force_task_kill(self):
        res = self.qt_process.startDetached("taskkill /PID %s /F /T" % str(self.qt_process.processId()))
        if res:
            self.text_edit.insertPlainText("任务已经结束" + "\n")
        else:
            self.text_edit.insertPlainText("任务还没结束" + "\n")

    def closeEvent(self, event):
        # 在窗口关闭时停止定时器,关闭任务运行
        # 停止 QProcess 进程
        self.qt_process.startDetached("taskkill /PID %s /F /T" % str(self.qt_process.processId()))
        if os.path.exists(self.ui_config_file_path):
            os.remove(self.ui_config_file_path)
        if os.path.exists(self.background_config_file_path):
            os.remove(self.background_config_file_path)
        self.timer.stop()
        event.accept()

    def copy_file(self, origin, des):
        shutil.copy(origin, des)

    def rename_file(self, origin, des):
        shutil.move(origin, des)

    def remove_file(self, path):
        if os.path.isfile(path):
            os.remove(path)

    def path_is_existed(self, path):
        if os.path.exists(path):
            return True
        else:
            return False

    def remove_space(self, s_tr):
        return s_tr.replace("", " ")

    def list_COM(self):
        ports = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                self.bg_config.bg_option_COM_ports).split(",")
        for port in ports:
            self.test_COM.addItem(port)

    def get_current_COM(self):
        serial_list = []
        ports = list(serial.tools.list_ports.comports())
        if len(ports) != 0:
            for port in ports:
                if 'SERIAL' in port.description:
                    COM_name = port.device.replace("\n", "").replace(" ", "").replace("\r", "")
                    serial_list.append(COM_name)
            return serial_list
        else:
            return []

    def list_logcat_duration(self):
        duration = [10, 20, 30, 40, 50, 60]
        for dur in duration:
            self.adb_log_duration.addItem(str(dur))
        self.adb_log_duration.setCurrentText("30")

    def select_devices_name(self):
        devices = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                  self.bg_config.bg_option_devices_name).split(",")
        for device in devices:
            self.edit_device_name.addItem(str(device))

    def update_debug_log(self):
        try:
            log_file = self.debug_log_path
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as file:
                    file.seek(self.last_position)
                    new_content = file.read()
                    if new_content:
                        self.text_edit.insertPlainText(new_content + "\n")
                        self.last_position = file.tell()
        except Exception as e:
            self.log_edit.insertPlainText(str(e) + "\n")

    def add_logo_image(self, file_path):
        # self.cursor = QTextCursor(self.document)
        # 将图片路径转为 QUrl
        # 创建 QTextImageFormat 对象
        self.text_edit_final.clear()
        image_format = QTextImageFormat()

        # if self.double_screen.isChecked():
        image2_url = QUrl.fromLocalFile(file_path)
        self.document.addResource(QTextDocument.ImageResource, image2_url, image2_url)
        image_format.setName(image2_url.toString())
        image_format.setWidth(self.image_width)
        image_format.setHeight(self.image_height)
        self.cursor.insertImage(image_format)

    def add_logo_image_camera(self, file_path):
        # self.cursor = QTextCursor(self.document)
        # 将图片路径转为 QUrl
        # 创建 QTextImageFormat 对象
        self.text_edit_final_camera.clear()
        image_format = QTextImageFormat()

        # if self.double_screen.isChecked():
        image2_url = QUrl.fromLocalFile(file_path)
        self.document_camera.addResource(QTextDocument.ImageResource, image2_url, image2_url)
        image_format.setName(image2_url.toString())
        image_format.setWidth(self.image_width_camera)
        image_format.setHeight(self.image_height_camera)
        self.cursor_camera.insertImage(image_format)

    def download_adb_file(self):
        if not self.stop_process_button.isEnabled():
            # 选择源文件
            source_file = self.adb_log_path
            if not os.path.exists(source_file):
                self.get_message_box("不存在adb log 文件！！！")
                return

            # 获取源文件的名字
            file_name = os.path.basename(source_file)

            # 选择目标保存位置，默认文件名为源文件名
            target_file, _ = QFileDialog.getSaveFileName(self, 'Save File As', file_name,
                                                         'Text Files (*.txt);;All Files (*)')
            if not target_file:
                return

            self.copy_file(source_file, target_file)
            self.get_message_box("成功下载adb log文件！")
        else:
            self.get_message_box("请等待压测停止再下载adb log！！！")


if __name__ == '__main__':
    print(conf_path.project_path)
    subprocess.Popen(conf_path.bat_pre_info_path, shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE).communicate(timeout=120)
    app = QtWidgets.QApplication(sys.argv)
    myshow = UIDisplay()
    myshow.show()
    app.exec_()
    # logo_show = LogoDisplay()
    # logo_show.show()
    # app.exec_()
