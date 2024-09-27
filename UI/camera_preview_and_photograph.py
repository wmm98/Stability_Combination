import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit
from PyQt5.QtCore import pyqtSlot
import configfile
import config_path
from PyQt5.QtCore import QTimer, QProcess, Qt
from PyQt5.QtWidgets import *

conf_path = config_path.UIConfigPath()


class PreviewPhotoGraph_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 300)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.verticalLayout_left = QtWidgets.QVBoxLayout(self.centralwidget)

        camera_config_label = QLabel("摄像头配置信息：")
        self.verticalLayout_left.addWidget(camera_config_label)
        layout_camera_config_info = QHBoxLayout()
        front_and_rear_label = QLabel("前和后镜头")
        self.is_front_and_rear_camera = QCheckBox()
        front_or_rear_label = QLabel("前或后镜头")
        self.is_front_or_rear_camera = QCheckBox()
        layout_camera_config_info.addWidget(front_and_rear_label)
        layout_camera_config_info.addWidget(self.is_front_and_rear_camera)
        layout_camera_config_info.addWidget(front_or_rear_label)
        layout_camera_config_info.addWidget(self.is_front_or_rear_camera)
        layout_camera_config_info.addStretch(1)
        self.camera_config_group = QButtonGroup()
        self.camera_config_group.addButton(self.is_front_and_rear_camera, id=1)
        self.camera_config_group.addButton(self.is_front_or_rear_camera, id=2)
        self.camera_config_group.setExclusive(True)
        self.verticalLayout_left.addLayout(layout_camera_config_info)

        self.verticalLayout_left.addWidget(QLabel())

        # 切换前后镜头坐标信息
        coordinate_config = QLabel("切换前后镜头按钮坐标信息填入：")
        self.verticalLayout_left.addWidget(coordinate_config)
        layout_coordinate_config = QHBoxLayout()
        x_label = QLabel("X:")
        self.X_info = QLineEdit()
        self.X_info.setMaximumWidth(50)
        y_label = QLabel("Y:")
        self.Y_info = QLineEdit()
        self.Y_info.setMaximumWidth(50)
        layout_coordinate_config.addWidget(x_label)
        layout_coordinate_config.addWidget(self.X_info)
        layout_coordinate_config.addWidget(y_label)
        layout_coordinate_config.addWidget(self.Y_info)
        layout_coordinate_config.addStretch(1)
        self.verticalLayout_left.addLayout(layout_coordinate_config)

        self.verticalLayout_left.addWidget(QLabel())

        self.verticalLayout_left.addWidget(QLabel("保存预览截图以及拍照保存的图片："))
        layout_getting_photo = QHBoxLayout()
        self.photograph_button = QPushButton("预览拍照保存")
        self.photograph_button.setMaximumWidth(100)
        self.photograph_tips = QLabel("未保存预期照片，请点击保存！")
        self.photograph_tips.setStyleSheet("color: blue;")
        layout_getting_photo.addWidget(self.photograph_button)
        layout_getting_photo.addWidget(self.photograph_tips)
        self.verticalLayout_left.addLayout(layout_getting_photo)



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
        MainWindow.setWindowTitle(_translate("MainWindow", "摄像头前/后镜头预览拍照压测配置"))


class CameraStabilityDisplay(QtWidgets.QMainWindow, PreviewPhotoGraph_MainWindow):

    def __init__(self):
        super(CameraStabilityDisplay, self).__init__()
        self.last_position = 0
        self.last_modify_time = 0
        self.bg_config = configfile.ConfigP(self.background_config_file_path)
        self.ui_config = configfile.ConfigP(self.ui_config_file_path)
        # 初始化子界面
        # self.ddr_window = DDR_MainWindow()
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        # 添加字段
        pass


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    myshow = CameraStabilityDisplay()
    myshow.show()
    app.exec_()
