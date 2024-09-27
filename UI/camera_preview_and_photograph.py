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
        MainWindow.resize(600, 800)
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
        self.X_info.setDisabled(True)
        self.X_info.setMaximumWidth(50)
        y_label = QLabel("Y:")
        self.Y_info = QLineEdit()
        self.Y_info.setDisabled(True)
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

        self.verticalLayout_left.addWidget(QLabel())

        layout_test_times_info = QHBoxLayout()
        self.test_times_label = QLabel("用例压测次数设置")
        self.test_times = QComboBox()
        self.test_times.setEditable(True)
        layout_test_times_info.addWidget(self.test_times_label)
        layout_test_times_info.addWidget(self.test_times)
        layout_test_times_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_test_times_info)

        self.submit_button = QtWidgets.QPushButton("保存配置")
        self.verticalLayout_left.addWidget(self.submit_button)

        self.verticalLayout_left.addWidget(QLabel())

        # 显示预期截图和照片
        self.verticalLayout_left.addWidget(QLabel("展示预览图和拍照保存图："))
        self.image_edit = ScrollablePlainTextEdit()
        self.document = self.image_edit.document()
        self.verticalLayout_left.addWidget(self.image_edit)

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
        self.list_test_times_settings()
        self.submit_button.clicked.connect(self.handle_submit)
        self.is_front_and_rear_camera.clicked.connect(self.click_camera_change)
        self.is_front_or_rear_camera.clicked.connect(self.click_camera_change)

    def handle_submit(self):
        if not self.is_front_and_rear_camera.isChecked() and not self.is_front_or_rear_camera.isChecked():
            self.get_message_box("请勾选摄像头信息！！！")
            return

        if self.is_front_and_rear_camera.isChecked():
            try:
                self.x_value = float(self.X_info.text().strip())
                self.y_value = float(self.Y_info.text().strip())
            except Exception as e:
                print(e)
                self.get_message_box("坐标请填入数字！！！")
                return

        try:
            case_test_times = int(self.test_times.currentText().strip())
        except:
            self.get_message_box("测试次数请填入整数！！！")
            return
        if self.is_front_and_rear_camera.isChecked():
            self.ui_config.add_config_option(self.ui_config.section_ui_camera_check,
                                             self.ui_config.option_front_and_rear, "1")
        else:
            self.ui_config.add_config_option(self.ui_config.section_ui_camera_check,
                                             self.ui_config.option_front_and_rear, "0")
        if self.is_front_and_rear_camera.isChecked():
            self.ui_config.add_config_option(self.ui_config.section_ui_camera_check, self.ui_config.option_switch_x_value, self.X_info.text())
            self.ui_config.add_config_option(self.ui_config.section_ui_camera_check, self.ui_config.option_switch_y_value, self.Y_info.text())
        self.ui_config.add_config_option(self.ui_config.section_ui_camera_check, self.ui_config.option_camera_test_times, str(case_test_times))

        self.submit_flag = True
        self.get_message_box("相机压测用例保存成功")

    def click_camera_change(self):
        if self.is_front_or_rear_camera.isChecked():
            self.X_info.clear()
            self.X_info.setDisabled(True)
            self.Y_info.clear()
            self.Y_info.setDisabled(True)
        else:
            self.X_info.setEnabled(True)
            self.Y_info.setEnabled(True)

    def get_message_box(self, text):
        QMessageBox.warning(self, "错误提示", text)

    def list_test_times_settings(self):
        times = [str(j * 50) for j in range(1, 500)]
        self.test_times.addItems(times)


class ScrollablePlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 连接 rangeChanged 信号到 slot_scroll_to_bottom 槽
        self.verticalScrollBar().rangeChanged.connect(self.slot_scroll_to_bottom)

    @pyqtSlot(int, int)
    def slot_scroll_to_bottom(self, min, max):
        # 设置滚动条到底部
        self.verticalScrollBar().setValue(max)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    myshow = CameraStabilityDisplay()
    myshow.show()
    app.exec_()
