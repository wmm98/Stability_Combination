from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QWidget, QSplitter, QLabel
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from configfile import ConfigP
import config_path


class Bt_Connect_MainWindow(config_path.UIConfigPath):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 200)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # 创建水平布局
        self.main_layout = QHBoxLayout(self.centralwidget)

        # 创建 QSplitter 控件，分割两个子窗口
        splitter = QSplitter()
        self.main_layout.addWidget(splitter)

        # 左侧所有部件
        left_widget = QWidget()
        self.verticalLayout_left = QtWidgets.QVBoxLayout(left_widget)

        device_info = QHBoxLayout()
        self.COM_tips = QtWidgets.QLabel("测试COM口:")
        self.test_COM = QComboBox()
        device_info.addWidget(self.COM_tips)
        device_info.addWidget(self.test_COM)
        device_info.addStretch(1)
        self.verticalLayout_left.addLayout(device_info)

        self.verticalLayout_left.addWidget(QLabel())

        # 压测次数
        layout_test_times_info = QHBoxLayout()
        self.test_times_label = QLabel("用例压测次数设置")
        self.test_times = QComboBox()
        self.test_times.setEditable(True)

        layout_test_times_info.addWidget(self.test_times_label)
        layout_test_times_info.addWidget(self.test_times)

        # 是否测概率测试
        probability_test_label = QLabel("是否进行失败概率性统计")
        self.is_probability_test = QCheckBox()
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
        MainWindow.setWindowTitle(_translate("MainWindow", "蓝牙连接测试压测配置界面"))


class BtConnectDisplay(QtWidgets.QMainWindow, Bt_Connect_MainWindow):
    def __init__(self):
        super(BtConnectDisplay, self).__init__()
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        self.submit_button.clicked.connect(self.handle_submit)
        self.list_case_test_cases()
        self.list_COM()

    def list_COM(self):
        ports = self.get_current_COM()
        for port in ports:
            self.test_COM.addItem(port)

    def get_current_COM(self):
        base_config = ConfigP(self.background_config_file_path)
        COM_list = base_config.get_option_value(base_config.section_background_to_ui, base_config.bg_option_COM_ports)
        return COM_list.split(",")

    def get_message_box(self, text):
        QMessageBox.warning(self, "提示", text)

    def handle_submit(self):
        if len(self.test_COM.currentText()) == 0:
            self.get_message_box("没检测到可用的COM口，请检查！！！")
            return

        if len(self.test_times.currentText()) == 0:
            self.get_message_box("请设置压测次数!!!")
            return

        # 检查完保存配置
        self.save_config()
        self.submit_flag = True
        self.get_message_box("蓝牙连接测试用例配置保存成功")

    def save_config(self):
        config = ConfigP(self.ui_config_file_path)
        section = config.section_bt_connect_test
        config.add_config_section(section)

        # 保存用例压测次数设置
        config.add_config_option(section, config.option_bt_connect_test_times, self.test_times.currentText())
        config.add_config_option(section, config.option_bt_connect_test_com, self.test_COM.currentText())
        if self.is_probability_test.isChecked():
            config.add_config_option(section, config.is_probability_test, "1")
        else:
            config.add_config_option(section, config.is_probability_test, "0")

    def list_case_test_cases(self):
        self.test_times.addItems([str(i * 50) for i in range(1, 101)])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    logo_show = BtConnectDisplay()
    logo_show.show()
    app.exec_()
