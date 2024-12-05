from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QWidget, QSplitter, QLabel
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from configfile import ConfigP
import config_path


class Sleep_Awake_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # 创建水平布局
        self.main_layout = QHBoxLayout(self.centralwidget)

        # 创建 QSplitter 控件，分割两个子窗口
        splitter = QSplitter()
        self.main_layout.addWidget(splitter)

        # 左侧所有部件
        left_widget = QWidget()
        self.verticalLayout_left = QtWidgets.QVBoxLayout(left_widget)

        self.verticalLayout_left.addWidget(QLabel("休眠唤醒设置："))
        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        layout_COM_config = QHBoxLayout()
        self.config_label = QLabel("接线配置:")
        # 测试COM
        self.COM_tips = QLabel("测试COM口:")
        self.test_COM = QComboBox()

        self.usb_label = QLabel("USB:")
        self.usb_config = QComboBox()
        self.config_tips = QLabel("接线提示:电源按键接常开端(COM,N0）,其他接常闭端(COM,NC)")
        self.config_tips.setStyleSheet("color: blue;")
        layout_COM_config.addWidget(self.COM_tips)
        layout_COM_config.addWidget(self.test_COM)
        layout_COM_config.addWidget(self.config_label)
        layout_COM_config.addWidget(self.usb_label)
        layout_COM_config.addWidget(self.usb_config)
        layout_COM_config.addStretch(1)
        self.verticalLayout_left.addLayout(layout_COM_config)
        self.verticalLayout_left.addWidget(self.config_tips)
        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        # 设备信息配置
        layout_device_config = QHBoxLayout()
        self.is_wifi_test = QCheckBox("WIFI")
        self.is_eth_test = QCheckBox("以太网")
        self.is_mobile_test = QCheckBox("4G")
        self.is_bt_test = QCheckBox("蓝牙")
        self.is_nfc_test = QCheckBox("NFC")
        # self.is_usb_test = QCheckBox("TF卡/U盘")
        # self.device_config_tips = QLabel("有些设备开启ADB不支持U盘")
        # self.device_config_tips.setStyleSheet("color: blue;")
        layout_device_config.addWidget(self.is_wifi_test)
        layout_device_config.addWidget(self.is_eth_test)
        layout_device_config.addWidget(self.is_mobile_test)
        layout_device_config.addWidget(self.is_bt_test)
        layout_device_config.addWidget(self.is_nfc_test)
        # layout_device_config.addWidget(self.is_usb_test)
        # layout_device_config.addWidget(self.device_config_tips)
        layout_device_config.addStretch(1)
        self.verticalLayout_left.addLayout(layout_device_config)
        config_tips1 = QLabel("提示：测试时请根据勾选的测试项打开并且连接上wifi、打开连接上以太网，插入4G卡")
        config_tips1.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(config_tips1)
        config_tips2 = QLabel("      打开蓝牙并且连接上仅一台设备、打开NFC")
        # config_tips2 = QLabel("      打开蓝牙并且连接上仅一台设备、打开NFC、插上U盘/TF卡")
        config_tips2.setStyleSheet("color: blue;")
        self.verticalLayout_left.addWidget(config_tips2)

        self.verticalLayout_left.addWidget(QLabel())

        # layout_device_type = QHBoxLayout()
        # self.device_type_label = QLabel("设备分类：")
        # self.is_team_one = QCheckBox("一部")
        # self.is_team_two = QCheckBox("二部")
        # self.device_type_group = QButtonGroup()
        # self.device_type_group.addButton(self.is_team_one, id=1)
        # self.device_type_group.addButton(self.is_team_two, id=2)
        # layout_device_type.addWidget(self.device_type_label)
        # layout_device_type.addWidget(self.is_team_one)
        # layout_device_type.addWidget(self.is_team_two)
        # layout_device_type.addStretch(1)
        # self.verticalLayout_left.addLayout(layout_device_type)
        #
        # self.verticalLayout_left.addWidget(QLabel())

        layout_sleep = QHBoxLayout()
        self.sleep_lable = QLabel("休眠时长(分钟)：")
        self.sleep_duration = QComboBox()
        self.sleep_duration.setEditable(True)
        # 每一轮之间间隔的时长
        self.interval_lable = QLabel("每一轮的间隔时间(秒)：")
        self.interval = QComboBox()
        self.interval.setEditable(True)

        layout_sleep.addWidget(self.sleep_lable)
        layout_sleep.addWidget(self.sleep_duration)
        layout_sleep.addWidget(self.interval_lable)
        layout_sleep.addWidget(self.interval)
        layout_sleep.addStretch(1)
        self.verticalLayout_left.addLayout(layout_sleep)

        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        # 压测次数
        layout_test_times_info = QHBoxLayout()
        self.test_times_label = QLabel("用例压测次数设置")
        self.test_times = QComboBox()
        self.test_times.setEditable(True)
        probability_test_label = QLabel("是否进行失败概率性统计")
        self.is_probability_test = QCheckBox()

        layout_test_times_info.addWidget(self.test_times_label)
        layout_test_times_info.addWidget(self.test_times)
        layout_test_times_info.addWidget(probability_test_label)
        layout_test_times_info.addWidget(self.is_probability_test)
        layout_test_times_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info)

        # 间隔
        self.verticalLayout_left.addWidget(QLabel())

        # 提交按钮
        self.submit_button = QtWidgets.QPushButton("保存配置")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.verticalLayout_left.addStretch(1)
        self.verticalLayout_left.setSpacing(10)  # 设置左侧垂直布局的间距为10像素

        splitter.addWidget(left_widget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "休眠唤醒压测参数配置"))


"""
添加关掉窗口检查保存配置是否成功/是否有进行配置保存
"""


class SleepAwakeDisplay(QtWidgets.QMainWindow, Sleep_Awake_MainWindow):
    def __init__(self):
        super(SleepAwakeDisplay, self).__init__()
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        self.list_test_times_settings()
        self.submit_button.clicked.connect(self.handle_submit)
        self.list_COM()
        self.get_COM_config()
        self.list_sleep_duration()
        self.list_interval_duration()

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def list_COM(self):
        ports = self.get_current_COM()
        for port in ports:
            self.test_COM.addItem(port)

    def get_current_COM(self):
        base_config = ConfigP(self.background_config_file_path)
        COM_list = base_config.get_option_value(base_config.section_background_to_ui, base_config.bg_option_COM_ports)
        return COM_list.split(",")

    def handle_submit(self):
        if len(self.test_COM.currentText()) == 0:
            self.get_message_box("没有可用的COM口，请检查并重启界面！！！")
            return

        if not self.is_wifi_test.isChecked() and not self.is_bt_test.isChecked() and not self.is_eth_test.isChecked() and not self.is_mobile_test.isChecked() and not self.is_nfc_test.isChecked():
            self.get_message_box("请勾选配置！！！")
            return

        if len(self.sleep_duration.currentText()) == 0:
            self.get_message_box("休眠时长为空，请写入！！")
            return

        if len(self.interval.currentText()) == 0:
            self.get_message_box("每一轮的间隔时间为空，请检查！！！")
            return

        if len(self.test_times.currentText()) == 0:
            self.get_message_box("请填入用例压测次数配置！！！")
            return

        # 检查完保存配置
        self.save_config()
        self.submit_flag = True
        self.get_message_box("休眠唤醒压测例配置保存成功")

    def get_COM_config(self):
        self.usb_config.addItems(["1路", "2路", "3路", "4路"])

    def list_sleep_duration(self):
        times = [str(j * 5) for j in range(1, 200)]
        self.sleep_duration.addItems(times)

    def list_interval_duration(self):
        times = [str(j * 60) for j in range(1, 200)]
        self.interval.addItems(times)

    def list_test_times_settings(self):
        times = [str(j * 50) for j in range(1, 500)]
        self.test_times.addItems(times)

    def save_config(self):
        config = ConfigP(self.ui_config_file_path)
        section = config.section_sleep_wake
        config.add_config_section(section)

        # 保存用例压测次数设置
        config.add_config_option(section, config.option_sleep_test_times, self.test_times.currentText())
        # 保存测试点配置信息
        if self.is_wifi_test.isChecked():
            config.add_config_option(section, config.option_wifi_test, "1")
        else:
            config.add_config_option(section, config.option_wifi_test, "0")

        if self.is_eth_test.isChecked():
            config.add_config_option(section, config.option_eth_test, "1")
        else:
            config.add_config_option(section, config.option_eth_test, "0")

        if self.is_mobile_test.isChecked():
            config.add_config_option(section, config.option_mobile_test, "1")
        else:
            config.add_config_option(section, config.option_mobile_test, "0")

        if self.is_bt_test.isChecked():
            config.add_config_option(section, config.option_bt_test, "1")
        else:
            config.add_config_option(section, config.option_bt_test, "0")

        if self.is_nfc_test.isChecked():
            config.add_config_option(section, config.option_nfc_test, '1')
        else:
            config.add_config_option(section, config.option_nfc_test, "0")

        # if self.is_usb_test.isChecked():
        #     config.add_config_option(section, config.option_usb_test, "1")
        # else:
        #     config.add_config_option(section, config.option_usb_test, "0")

        if self.usb_config.currentText() == "1路":
            config.add_config_option(section, config.option_sleep_config, "relay_1")
        elif self.usb_config.currentText() == "2路":
            config.add_config_option(section, config.option_sleep_config, "relay_2")
        elif self.usb_config.currentText() == "3路":
            config.add_config_option(section, config.option_sleep_config, "relay_3")
        else:
            config.add_config_option(section, config.option_sleep_config, "relay_4")

        config.add_config_option(section, config.option_sleep_com_port, self.test_COM.currentText())

        config.add_config_option(section, config.option_sleep_duration, self.sleep_duration.currentText())
        config.add_config_option(section, config.test_interval, self.interval.currentText())
        if self.is_probability_test.isChecked():
            config.add_config_option(section, config.is_probability_test, "1")
        else:
            config.add_config_option(section, config.is_probability_test, "0")


class ScrollablePlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalScrollBar().rangeChanged.connect(self.slot_scroll_to_bottom)

    @pyqtSlot(int, int)
    def slot_scroll_to_bottom(self, min, max):
        self.verticalScrollBar().setValue(max)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    logo_show = SleepAwakeDisplay()
    logo_show.show()
    app.exec_()
