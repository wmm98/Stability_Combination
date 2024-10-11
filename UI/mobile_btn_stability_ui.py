from PyQt5.QtWidgets import QHBoxLayout, QComboBox, QWidget, QSplitter, QLabel
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from configfile import ConfigP
import config_path


class Mobile_Btn_Check_MainWindow(config_path.UIConfigPath):

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
        MainWindow.setWindowTitle(_translate("MainWindow", "4G开关压测配置界面"))


class MobileBtnCheckDisplay(QtWidgets.QMainWindow, Mobile_Btn_Check_MainWindow):
    def __init__(self):
        super(MobileBtnCheckDisplay, self).__init__()
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        self.submit_button.clicked.connect(self.handle_submit)
        self.list_case_test_cases()

    def get_message_box(self, text):
        QMessageBox.warning(self, "提示", text)

    def handle_submit(self):
        if len(self.test_times.currentText()) == 0:
            self.get_message_box("请设置压测次数!!!")
            return

        # 检查完保存配置
        self.save_config()
        self.submit_flag = True
        self.get_message_box("4G开关压测用例配置保存成功")

    def save_config(self):
        config = ConfigP(self.ui_config_file_path)
        section = config.section_mobile_check
        config.add_config_section(section)

        # 保存用例压测次数设置
        config.add_config_option(section, config.option_mobile_btn_test_times, self.test_times.currentText())

    def list_case_test_cases(self):
        self.test_times.addItems([str(i * 50) for i in range(1, 101)])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    logo_show = MobileBtnCheckDisplay()
    logo_show.show()
    app.exec_()
