from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QWidget, QSplitter, QLabel
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from configfile import ConfigP
import config_path


class Factory_Reset_MainWindow(config_path.UIConfigPath):
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

        self.verticalLayout_left.addWidget(QLabel("恢复出厂设置："))
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

        # 压测次数
        layout_test_times_info = QHBoxLayout()
        self.test_times_label = QLabel("用例压测次数设置")
        self.test_times = QComboBox()
        self.test_times.setEditable(True)
        layout_test_times_info.addWidget(self.test_times_label)
        layout_test_times_info.addWidget(self.test_times)
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
        MainWindow.setWindowTitle(_translate("MainWindow", "恢复出厂设置压测参数配置"))


"""
添加关掉窗口检查保存配置是否成功/是否有进行配置保存
"""


class FactoryResetDisplay(QtWidgets.QMainWindow, Factory_Reset_MainWindow):
    def __init__(self):
        super(FactoryResetDisplay, self).__init__()
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        self.list_test_times_settings()
        self.submit_button.clicked.connect(self.handle_submit)

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def handle_submit(self):

        if not self.is_wifi_test.isChecked() and not self.is_bt_test.isChecked() and not self.is_eth_test.isChecked() and not self.is_mobile_test.isChecked() and not self.is_nfc_test.isChecked():
            self.get_message_box("请勾选配置！！！")
            return

        if len(self.test_times.currentText()) == 0:
            self.get_message_box("请填入用例次数配置！！！")
            return

        # 检查完保存配置
        self.save_config()
        self.submit_flag = True
        self.get_message_box("恢复出厂设置压测检测用例配置保存成功")

    def list_test_times_settings(self):
        times = [str(j * 50) for j in range(1, 500)]
        self.test_times.addItems(times)

    def save_config(self):
        config = ConfigP(self.ui_config_file_path)
        section = config.section_factory_reset_stability
        config.add_config_section(section)

        # 保存用例压测次数设置
        config.add_config_option(section, config.option_factory_reset_test_times, self.test_times.currentText())
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


class ScrollablePlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalScrollBar().rangeChanged.connect(self.slot_scroll_to_bottom)

    @pyqtSlot(int, int)
    def slot_scroll_to_bottom(self, min, max):
        self.verticalScrollBar().setValue(max)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    logo_show = FactoryResetDisplay()
    logo_show.show()
    app.exec_()
