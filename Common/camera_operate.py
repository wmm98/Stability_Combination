import cv2
import time
from Common.config import Config
from Common.debug_log import MyLog

log = MyLog()


class Camera:
    def __init__(self):
        pass

    def take_photo(self, photo_path, camera_id=0):

        camera = cv2.VideoCapture(camera_id)

        # 设置曝光参数
        camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # 关闭自动曝光
        camera.set(cv2.CAP_PROP_EXPOSURE, -3)  # 设置曝光值，具体数值需要根据摄像头和环境调整

        # 设置摄像头的分辨率
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # 读取一帧图像（拍照）
        time.sleep(1)
        ret, frame = camera.read()

        # 检查图像是否成功读取
        if not ret:
            log.info("无法从摄像头捕获图像")
        else:
            # 保存图像到当前目录下，文件名为 image1.jpg
            cv2.imwrite(photo_path, frame)
            log.info("照片已保存")

        # 释放摄像头资源
        camera.release()


if __name__ == '__main__':
    camera = Camera()
    camera.take_photo("12.png", 0)
