import binascii
import serial
import time
from Common.log import MyLog

log = MyLog()


class SerialD:
    def __init__(self):
        pass

    # 打开串口
    def loginSer(self, COM):
        global ser
        global port
        port = COM  # 设置端口号
        baudrate = 9600  # 设置波特率
        bytesize = 8  # 设置数据位
        stopbits = 1  # 设置停止位
        parity = "N"  # 设置校验位

        try:
            ser = serial.Serial(port, baudrate)
            if (ser.isOpen()):  # 判断串口是否打开
                log.info("串口：%s 已经打开！！！" % port)
            else:
                ser.open()
                log.info("串口：%s 打开！！！" % port)
                print()
        except Exception as e:
            log.error(e)

    def logoutSer(self):
        if ser.isOpen():
            ser.close()
            log.info("串口： %s 关闭！！！" % port)
        else:
            log.info("串口： %s 关闭！！！" % port)

    def send_status_cmd(self):
        num = ser.write(bytes.fromhex("A0 01 05 A6"))
        time.sleep(2)  # sleep() 与 inWaiting() 最好配对使用
        ser.inWaiting()
        data = str(binascii.b2a_hex(ser.read(num)))[2:-1]  # 十六进制显示方法2
        if "a00100a1" in data:
            return False
        elif "a00101a2" in data:
            return True

    def send_ser_connect_cmd(self):
        ser.write(bytes.fromhex("A0 01 01 A2"))
        log.info("发送闭合指令")

    def send_ser_disconnect_cmd(self):
        log.info("发送断开指令")
        ser.write(bytes.fromhex("A0 01 00 A1"))

    def confirm_ser_connected(self):
        limit = 10
        interval = 1
        while True:
            if self.send_status_cmd():
                log.info("继电器已经闭合")
                return True
            else:
                interval += 1
            self.send_ser_connect_cmd()
            if interval >= limit:
                log.error("继电器无法闭合,请检查!!!")
                return False
            time.sleep(1)

    def open_relay(self, num):
        if num == 1:
            ser.write(bytes.fromhex("A0 01 01 A2"))
        elif num == 2:
            ser.write(bytes.fromhex("A0 02 01 A3"))
        elif num == 3:
            ser.write(bytes.fromhex("A0 03 01 A4"))
        elif num == 4:
            ser.write(bytes.fromhex("A0 04 01 A5"))

    def close_relay(self, num):
        if num == 1:
            ser.write(bytes.fromhex("A0 01 00 A1"))
        elif num == 2:
            ser.write(bytes.fromhex("A0 02 00 A2"))
        elif num == 3:
            ser.write(bytes.fromhex("A0 03 00 A3"))
        elif num == 4:
            ser.write(bytes.fromhex("A0 04 00 A4"))


if __name__ == '__main__':
    se = SerialD()
    # print(se.COM)
    se.loginSer("COM27")
    se.send_ser_disconnect_cmd()
    # print(se.send_status_cmd())
    time.sleep(2)
    se.send_ser_connect_cmd()
    # print(se.send_status_cmd())
    se.logoutSer()
