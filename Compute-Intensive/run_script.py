
import sys
import time
import psutil
import pandas as pd
import matplotlib.pyplot as plt
import subprocess


def monitor(original_process, running_process, start_mem_kb, start_timestamp, process_name):
    log_file = f"metrics/{process_name}_usage_log.csv"
    with open(log_file, "w") as f:
        f.write("Time Stamp,CPU,Memory(KB)\n")

    print(f"Monitoring {process_name} PID: {running_process.pid}")
    try:
        while psutil.pid_exists(running_process.pid) and original_process.poll() is None:
            cpu = running_process.cpu_percent(interval=.1)
            mem_kb = running_process.memory_info().rss
            timestamp = time.time()
            with open(log_file, "a") as f:
                f.write(
                    f"{timestamp}, {cpu}, {mem_kb}\n")
    except psutil.NoSuchProcess as e:
        print(f"Running process: {running_process} not found. \nError: {e}")
    print(
        f"Monitoring {original_process.poll()} and {running_process.is_running()}")
    print(f"✅ Monitoring complete. Log saved to {log_file}")
    process_metrics(log_file, start_mem_kb, start_timestamp, process_name)
    plot_metrics(log_file, process_name)

def process_metrics(raw_log, start_mem_kb, start_timestamp, process_name):
    df = pd.read_csv(raw_log)
    df["Memory(KB)"] = (df["Memory(KB)"] // 1024) - start_mem_kb
    df["Memory(MB)"] = df["Memory(KB)"] // 1024
    df["Time Stamp"] = df["Time Stamp"] - start_timestamp

    df.rename(columns={"CPU": "CPU%", "Time Stamp": "Time Elapsed"}, inplace=True)

    final_log = f"metrics/{process_name}_usage_log.csv"
    df[["Time Elapsed", "CPU%", "Memory(KB)", "Memory(MB)"]].to_csv(final_log, index=False)
    print(f"📄 Processed metrics saved to {final_log}")

def plot_metrics(log_file, process_name):
    df = pd.read_csv(log_file)

    plt.figure(figsize=(12, 6))
    plt.plot(df["Time Elapsed"], df["CPU%"], label=f"{process_name} CPU Usage (%)")
    plt.plot(df["Time Elapsed"], df["Memory(MB)"], label=f"{process_name} Memory Usage (MB)")

    plt.title(f"{process_name} Resource Usage Over Time")
    plt.xlabel("Time Elapsed (s)")
    plt.ylabel("Usage")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plot_path = f"metrics/plots/{process_name}_usage_plot.png"
    plt.savefig(plot_path)
    plt.close()
    print(f"📈 Plot saved to {plot_path}")

def run_script_and_monitor(command, ops_flag=False):
    original_process = subprocess.Popen(command)
    running_pid = original_process.pid

    print(f"✅ Command started with PID: {running_pid}")

    if sys.platform == "linux" or sys.platform == "linux2":
        qemu_process_name = "qemu-system-x86_64"
    else:
        qemu_process_name = "qemu-system-aarch64"
    if ops_flag:
        qemu_proc = None
        while qemu_proc is None:
            filtered_proc = filter(lambda proc: proc.info["ppid"] == running_pid and qemu_process_name in proc.info["name"],
                                   psutil.process_iter(attrs=["ppid", "name"]))
            qemu_proc = next(filtered_proc, None)
        running_pid = qemu_proc.pid
        if running_pid is None:
            print("QEMU process not found!")
            original_process.terminate()
            return

    start_timestamp = time.time()
    process = psutil.Process(running_pid)
    start_mem_kb = process.memory_info().rss // 1024
    monitor(original_process, process, start_mem_kb, start_timestamp,
            command[0])


if __name__ == "__main__":
    ops_command = ["ops", "pkg", "load",
                   "eyberg/python:3.10.6", "-c", "myconfig.json"]
    python_command = ["python3", "script.py"]
    if len(sys.argv) > 1:
        command_type = sys.argv[1]
        if command_type == "ops":
            run_script_and_monitor(ops_command, True)
        else:
            run_script_and_monitor(python_command)
    else:
        run_script_and_monitor(ops_command, True)
        run_script_and_monitor(python_command)
