import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QCheckBox, QComboBox, QButtonGroup, QWidget, QSplitter, QTextEdit
from PyQt5.QtCore import pyqtSlot
import configfile
import config_path
from PyQt5.QtCore import QTimer, QProcess, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextImageFormat
from PyQt5.QtCore import QUrl, QFileInfo

conf_path = config_path.UIConfigPath()


class PreviewPhotoGraph_MainWindow(config_path.UIConfigPath):
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.ReadOnly

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.verticalLayout_left = QtWidgets.QVBoxLayout(self.centralwidget)

        layout_device_info = QHBoxLayout()
        self.device_label = QLabel("设备名称：")
        self.device_name = QtWidgets.QComboBox()
        layout_device_info.addWidget(self.device_label)
        layout_device_info.addWidget(self.device_name)
        layout_device_info.addStretch(1)
        self.verticalLayout_left.addLayout(layout_device_info)

        self.verticalLayout_left.addWidget(QLabel())

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
        width = self.image_edit.viewport().width()
        height = self.image_edit.viewport().height()
        self.image_width = width / 2
        self.image_height = height / 2
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
        self.exp_front_preview_last_modify_time = 0
        self.exp_front_photograph_last_modify_time = 0
        self.exp_rear_preview_last_modify_time = 0
        self.exp_rear_photograph_last_modify_time = 0
        self.exp_default_preview_last_modify_time = 0
        self.exp_default_photograph_last_modify_time = 0

        self.test_front_preview_last_modify_time = 0
        self.test_front_photograph_last_modify_time = 0
        self.test_rear_preview_last_modify_time = 0
        self.test_rear_photograph_last_modify_time = 0
        self.test_default_preview_last_modify_time = 0
        self.test_default_photograph_last_modify_time = 0

        self.bg_config = configfile.ConfigP(self.background_config_file_path)
        self.ui_config = configfile.ConfigP(self.ui_config_file_path)
        # 初始化子界面
        # self.ddr_window = DDR_MainWindow()
        self.setupUi(self)
        self.intiui()
        self.submit_flag = False

    def intiui(self):
        # 初始化进程
        self.get_exp_imag_process = QProcess()

        self.list_devices_name()
        self.list_test_times_settings()
        self.submit_button.clicked.connect(self.handle_submit)
        self.is_front_and_rear_camera.clicked.connect(self.click_camera_change)
        self.is_front_or_rear_camera.clicked.connect(self.click_camera_change)
        self.photograph_button.clicked.connect(self.preview_photograph_button_change)
        self.get_exp_imag_process.finished.connect(self.camera_finished_handle)

        # 初始化图片cursor
        self.cursor = QTextCursor(self.document)

    def handle_submit(self):
        # if len(self.device_name.currentText()) == 0:
        #     self.get_message_box("没检测到可用的设备，请重启界面！！！")
        #     return

        # if not self.is_front_and_rear_camera.isChecked() and not self.is_front_or_rear_camera.isChecked():
        #     self.get_message_box("请勾选摄像头信息！！！")
        #     return
        #
        # if self.is_front_and_rear_camera.isChecked():
        #     try:
        #         self.x_value = float(self.X_info.text().strip())
        #         self.y_value = float(self.Y_info.text().strip())
        #     except Exception as e:
        #         print(e)
        #         self.get_message_box("坐标请填入数字！！！")
        #         return
        try:
            case_test_times = int(self.test_times.currentText().strip())
        except:
            self.get_message_box("测试次数请填入整数！！！")
            return
        # if self.is_front_and_rear_camera.isChecked():
        #     self.ui_config.add_config_option(self.ui_config.section_ui_camera_check,
        #                                      self.ui_config.option_front_and_rear, "1")
        # else:
        #     self.ui_config.add_config_option(self.ui_config.section_ui_camera_check,
        #                                      self.ui_config.option_front_and_rear, "0")
        # if self.is_front_and_rear_camera.isChecked():
        #     self.ui_config.add_config_option(self.ui_config.section_ui_camera_check, self.ui_config.option_switch_x_value, self.X_info.text())
        #     self.ui_config.add_config_option(self.ui_config.section_ui_camera_check, self.ui_config.option_switch_y_value, self.Y_info.text())
        self.ui_config.add_config_option(self.ui_config.section_ui_camera_check, self.ui_config.option_camera_test_times, str(case_test_times))

        self.submit_flag = True
        self.get_message_box("相机压测用例保存成功")

    def camera_finished_handle(self):
        if self.is_front_and_rear_camera.isChecked():
            rear_pre_status = os.path.exists(self.camera_sta_exp_rear_preview_path)
            rear_photo_status = os.path.exists(self.camera_sta_exp_rear_photograph_path)
            front_pre_status = os.path.exists(self.camera_sta_exp_front_preview_path)
            front_photo_status = os.path.exists(self.camera_sta_exp_front_photograph_path)
            if rear_pre_status and rear_photo_status and front_pre_status and front_photo_status:
                self.photograph_tips.setText("已经获取到预期参照图片！")
                self.photograph_tips.setStyleSheet("color: red;")
            else:
                self.photograph_tips.setText("未获取到预期参照照片！！！")
                self.photograph_tips.setStyleSheet("color: yellow;")
        else:
            default_pre_status = os.path.exists(self.camera_sta_exp_default_preview_path)
            default_photo_status = os.path.exists(self.camera_sta_exp_default_photograph_path)
            if default_photo_status and default_pre_status:
                self.photograph_tips.setText("已经获取到预期参照图片！")
                self.photograph_tips.setStyleSheet("color: red;")
            else:
                self.photograph_tips.setText("未获取到预期参照照片！！！")
                self.photograph_tips.setStyleSheet("color: yellow;")

    def preview_photograph_button_change(self):
        if len(self.device_name.currentText()) == 0:
            self.get_message_box("没检测到可用的设备，请重启界面！！！")
            return

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

        self.ui_config.add_config_option(self.ui_config.section_ui_camera_check, self.ui_config.ui_option_device_name, self.device_name.currentText())

        if self.is_front_and_rear_camera.isChecked():
            self.ui_config.add_config_option(self.ui_config.section_ui_camera_check,
                                             self.ui_config.option_front_and_rear, "1")

            self.ui_config.add_config_option(self.ui_config.section_ui_camera_check,
                                             self.ui_config.option_switch_x_value, self.X_info.text())
            self.ui_config.add_config_option(self.ui_config.section_ui_camera_check,
                                             self.ui_config.option_switch_y_value, self.Y_info.text())

        else:
            self.ui_config.add_config_option(self.ui_config.section_ui_camera_check,
                                             self.ui_config.option_front_and_rear, "0")

        # 删除预期之前的照片
        try:
            if self.is_front_and_rear_camera.isChecked():
                if os.path.exists(self.camera_sta_exp_front_preview_path):
                    os.remove(self.camera_sta_exp_front_preview_path)
                if os.path.exists(self.camera_sta_exp_front_photograph_path):
                    os.remove(self.camera_sta_exp_front_photograph_path)
                if os.path.exists(self.camera_sta_exp_rear_photograph_path):
                    os.remove(self.camera_sta_exp_rear_photograph_path)
                if os.path.exists(self.camera_sta_exp_rear_preview_path):
                    os.remove(self.camera_sta_exp_rear_preview_path)
            else:
                if os.path.exists(self.camera_sta_exp_default_preview_path):
                    os.remove(self.camera_sta_exp_default_preview_path)
                if os.path.exists(self.camera_sta_exp_default_photograph_path):
                    os.remove(self.camera_sta_exp_default_photograph_path)
        except Exception as e:
            print(e)

        # 调起来进程， 获取预期照片
        try:
            print("****************************")
            print(self.bat_camera_stability_path)
            self.get_exp_imag_process.start(self.bat_camera_stability_path)
            self.photograph_tips.setText("正在拍照保存，请等待...")
            self.photograph_tips.setStyleSheet("color: green;")
            print("###################################")
            self.document.clear()
            self.file_timer = QTimer(self)
            self.file_timer.timeout.connect(self.check_image_modification)
            self.check_interval = 1000  # 定时器间隔，单位毫秒
        except Exception as e:
            print(e)

        self.file_timer.start(self.check_interval)

    def check_image_modification(self):
        """检查图片文件是否有修改"""
        # 检查双镜头
        try:
            if self.is_front_and_rear_camera.isChecked():
                exp_front_preview = os.path.exists(self.camera_sta_exp_front_preview_path)
                exp_front_photograph = os.path.exists(self.camera_sta_exp_front_photograph_path)
                exp_rear_photograph = os.path.exists(self.camera_sta_exp_rear_photograph_path)
                exp_rear_preview = os.path.exists(self.camera_sta_exp_rear_preview_path)
                if exp_front_preview and exp_front_photograph and exp_rear_preview and exp_rear_photograph:
                    # 前镜头
                    exp_front_preview_current_mod_time = self.get_file_modification_time(self.camera_sta_exp_front_preview_path)
                    if exp_front_preview_current_mod_time != self.exp_front_preview_last_modify_time:
                        self.exp_front_preview_last_modify_time = exp_front_preview_current_mod_time  # 更新为新的修改时间
                        self.add_logo_image(self.camera_sta_exp_front_preview_path)

                    exp_front_photograph_mod_time = self.get_file_modification_time(self.camera_sta_exp_front_photograph_path)
                    if exp_front_photograph_mod_time != self.exp_front_photograph_last_modify_time:
                        self.exp_front_photograph_last_modify_time = exp_front_photograph_mod_time  # 更新为新的修改时间
                        self.add_logo_image(self.camera_sta_exp_front_photograph_path)

                    # 后镜头
                    exp_rear_preview_current_mod_time = self.get_file_modification_time(self.camera_sta_exp_rear_preview_path)
                    if exp_rear_preview_current_mod_time != self.exp_rear_preview_last_modify_time:
                        self.exp_rear_preview_last_modify_time = exp_rear_preview_current_mod_time  # 更新为新的修改时间
                        self.add_logo_image(self.camera_sta_exp_rear_preview_path)

                    exp_rear_photograph_current_mod_time = self.get_file_modification_time(
                        self.camera_sta_exp_rear_photograph_path)
                    if exp_rear_photograph_current_mod_time != self.exp_rear_photograph_last_modify_time:
                        self.exp_rear_photograph_last_modify_time = exp_rear_photograph_current_mod_time  # 更新为新的修改时间
                        self.add_logo_image(self.camera_sta_exp_rear_photograph_path)
            else:
                # 预览截图
                if os.path.exists(self.camera_sta_exp_default_preview_path):
                    if os.path.exists(self.camera_sta_exp_default_photograph_path):
                        preview_current_mod_time = self.get_file_modification_time(self.camera_sta_exp_default_preview_path)
                        if preview_current_mod_time != self.exp_default_preview_last_modify_time:
                            self.exp_default_preview_last_modify_time = preview_current_mod_time  # 更新为新的修改时间
                            self.add_logo_image(self.camera_sta_exp_default_preview_path)

                        photograph_current_mod_time = self.get_file_modification_time(
                            self.camera_sta_exp_default_photograph_path)
                        if photograph_current_mod_time != self.exp_default_photograph_last_modify_time:
                            self.exp_default_photograph_last_modify_time = photograph_current_mod_time  # 更新为新的修改时间
                            self.add_logo_image(self.camera_sta_exp_default_photograph_path)
                        self.file_timer.stop()
                # 拍照
                # if os.path.exists(self.camera_sta_exp_default_photograph_path):
                #     photograph_current_mod_time = self.get_file_modification_time(self.camera_sta_exp_default_photograph_path)
                #     if photograph_current_mod_time != self.exp_default_photograph_last_modify_time:
                #         self.exp_default_photograph_last_modify_time = photograph_current_mod_time  # 更新为新的修改时间
                #         self.add_logo_image(self.camera_sta_exp_default_photograph_path)
        except Exception as e:
            print(e)

    def get_file_modification_time(self, file_path):
        """获取文件的最后修改时间"""
        file_info = QFileInfo(file_path)
        last_modify = file_info.lastModified()
        return last_modify

    def add_logo_image(self, img_path):
        # self.cursor = QTextCursor(self.document)
        # 将图片路径转为 QUrl
        # 创建 QTextImageFormat 对象
        # self.image_edit.clear()
        image_format = QTextImageFormat()

        # if self.double_screen.isChecked():
        #     image2_url = QUrl.fromLocalFile(img_path)
        #     self.document.addResource(QTextDocument.ImageResource, image2_url, image2_url)
        #     image_format.setName(image2_url.toString())
        #     image_format.setWidth(self.image_width)
        #     image_format.setHeight(self.image_height)
        #     self.cursor.insertImage(image_format)

        image_url = QUrl.fromLocalFile(img_path)
        # 添加图片资源到 QTextDocument
        self.document.addResource(QTextDocument.ImageResource, image_url, image_url)
        # 设置图片格式的 ID
        image_format.setName(image_url.toString())
        # 设置图片的大小
        image_format.setWidth(self.image_width)
        image_format.setHeight(self.image_height)
        #
        # # 插入图片到 QTextDocument
        # self.image_edit.insertPlainText("\n")
        self.cursor.insertImage(image_format)
        # self.image_edit.insertPlainText("\n")

    def click_camera_change(self):
        if self.is_front_or_rear_camera.isChecked():
            self.X_info.clear()
            self.X_info.setDisabled(True)
            self.Y_info.clear()
            self.Y_info.setDisabled(True)
        else:
            self.X_info.setEnabled(True)
            self.Y_info.setEnabled(True)

    def list_devices_name(self):
        devices = self.bg_config.get_option_value(self.bg_config.section_background_to_ui,
                                                  self.bg_config.bg_option_devices_name).split(",")
        self.device_name.addItems(devices)

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
