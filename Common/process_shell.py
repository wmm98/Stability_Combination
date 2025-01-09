import subprocess
from Common.log import MyLog
import select
import time
import threading
import queue

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
    def invoke(cmd, timeout=10):
        def enqueue_output(pipe, output_queue):
            for line in iter(pipe.readline, b''):
                output_queue.put(line.decode("utf-8"))
            pipe.close()

        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            output_queue = queue.Queue()

            stdout_thread = threading.Thread(target=enqueue_output, args=(process.stdout, output_queue))
            stderr_thread = threading.Thread(target=enqueue_output, args=(process.stderr, output_queue))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            start_time = time.time()
            output = []

            while True:
                try:
                    line = output_queue.get(timeout=0.1)
                    output.append(line)
                    print(line, end="")

                except queue.Empty:
                    if time.time() - start_time > timeout:
                        print("\nTimeout reached, terminating the process...")
                        # process.terminate() cannot stop the process
                        process.terminate()
                        break

            # stdout_thread.join()
            # stderr_thread.join()
            return ''.join(output)

        except Exception as e:
            print(f"Error: {e}")
            return ""


if __name__ == '__main__':
    print("***************************************")
    partial_output = ConShell.invoke("adb shell getevent -lt", timeout=5)
    print("\nPartial Output Captured:")
    print(partial_output)