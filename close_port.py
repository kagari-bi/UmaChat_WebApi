import os
import psutil
import signal

def find_process_by_port(port):
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for connection in process.connections():
                if connection.laddr.port == port:
                    return process
        except Exception as e:
            pass
    return None

def kill_process_by_port(port):
    process = find_process_by_port(port)
    if process:
        os.kill(process.pid, signal.SIGTERM)
        print(f"进程 {process.pid} (运行在端口 {port}) 已经被终止。")
    else:
        print(f"没有找到运行在端口 {port} 的进程。")

if __name__ == "__main__":
    target_port = 8000
    kill_process_by_port(target_port)