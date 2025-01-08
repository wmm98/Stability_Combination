import subprocess
from Common.log import MyLog

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
    def invoke(cmd, lines=30):
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            output = []
            for _ in range(lines):
                line = process.stdout.readline()
                if not line:
                    break
                output.append(line.decode("utf-8"))
            process.terminate()
            return ''.join(output)
        except subprocess.TimeoutExpired as e:
            log.error(str(e))


if __name__ == '__main__':
    # print(Shell.invoke("adb devices"))
    print(ConShell.invoke("adb shell getevent -lt"))
