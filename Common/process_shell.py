import subprocess
from Common.log import MyLog
import select
import time

log = MyLog()


class Shell:
    @staticmethod
    def invoke(cmd, runtime=10):
        try:
            output, errors = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              creationflags=subprocess.CREATE_NO_WINDOW).communicate(timeout=runtime)
            o = output.decode("utf-8")
            return o
        except subprocess.TimeoutExpired as e:
            print(e)
            log.error(str(e))


class ConShell:
    @staticmethod
    def invoke(cmd, lines=30, timeout=10):
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            output = []
            start_time = time.time()
            for _ in range(lines):
                if time.time() - start_time > timeout:
                    break
                if process.stdout.readable():
                    line = process.stdout.readline()
                    if not line:
                        break
                    output.append(line.decode("utf-8"))
                else:
                    time.sleep(0.1)  # Sleep briefly to avoid busy-waiting
            process.terminate()
            return ''.join(output)
        except subprocess.TimeoutExpired as e:
            log.error(str(e))
            return ""


if __name__ == '__main__':
    # print(Shell.invoke("adb devices"))
    print(ConShell.invoke("adb shell getevent -lt"))
