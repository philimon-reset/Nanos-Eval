import sys
import time
import psutil
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import docker
import os
from plot_usage import comparative_plot

execution_log = "metrics/execution_time.csv"
with open(execution_log, "w") as f:
    f.write("Platform,Time\n")


def monitor(start_mem_kb, running_process, process_name):
    start_timestamp = time.time()
    log_file = f"metrics/{process_name}_usage_log.csv"
    with open(log_file, "w") as f:
        f.write("Time Stamp,CPU,Memory(KB)\n")

    print(f"Monitoring {process_name} PID: {running_process.pid}")
    try:
        while running_process.is_running():
            cpu = running_process.cpu_percent(interval=0.5)
            mem_kb = running_process.memory_info().rss
            timestamp = time.time()

            with open(log_file, "a") as f:
                f.write(f"{timestamp}, {cpu}, {mem_kb}\n")

    except psutil.NoSuchProcess as e:
        print(f"Error: {e}")

    with open(execution_log, "a+") as f:
        f.write(f"{process_name},{time.time() - start_timestamp}\n")
    print(
        f"Monitoring {running_process.is_running()}")
    print(f"✅ Monitoring complete. Log saved to {log_file}")
    process_metrics(log_file, start_mem_kb, start_timestamp, process_name)
    plot_metrics(log_file, process_name)


def run_docker_and_monitor(process_name, image_name="run_script"):
    print(f"Starting {process_name} : Image Name {image_name}")
    client = docker.from_env()

    container = client.containers.run(
        image=image_name,
        detach=True,
        remove=True,
        cpu_count=4,
        mem_limit="2g",
        pid_mode="host",
        name="sdk_monitor_container"
    )

    container.reload()
    container_process = psutil.Process(container.attrs["State"]["Pid"])
    monitor(container_process.memory_info().rss,
            container_process, process_name)


def process_metrics(raw_log, start_mem_kb, start_timestamp, process_name):
    df = pd.read_csv(raw_log)
    df["Memory(KB)"] = (df["Memory(KB)"] // 1024) - (start_mem_kb // 1024)
    df["Memory(MB)"] = df["Memory(KB)"] // 1024
    df["Time Stamp"] = df["Time Stamp"] - start_timestamp

    df.rename(columns={"CPU": "CPU%",
              "Time Stamp": "Time Elapsed"}, inplace=True)

    final_log = f"metrics/{process_name}_usage_log.csv"
    df[["Time Elapsed", "CPU%", "Memory(KB)", "Memory(MB)"]].to_csv(
        final_log, index=False)
    print(f"📄 Processed metrics saved to {final_log}")
    plot_metrics(final_log, process_name)


def plot_metrics(log_file, process_name):
    df = pd.read_csv(log_file)

    plt.figure(figsize=(12, 6))
    plt.plot(df["Time Elapsed"], df["CPU%"],
             label=f"{process_name} CPU Usage (%)")
    plt.plot(df["Time Elapsed"], df["Memory(MB)"],
             label=f"{process_name} Memory Usage (MB)")

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


def run_script_and_monitor(command):
    original_process = subprocess.Popen(command)
    running_pid = original_process.pid
    process = psutil.Process(running_pid)
    starting_memory = 0
    print(f"✅ Command started with PID: {running_pid}")

    if sys.platform == "linux" or sys.platform == "linux2":
        qemu_process_name = "qemu-system-x86_64"
    else:
        qemu_process_name = "qemu-system-aarch64"

    qemu_proc = None
    while qemu_proc is None:
        filtered_proc = filter(
            lambda proc: proc.info["ppid"] == running_pid and qemu_process_name in proc.info["name"],
            psutil.process_iter(attrs=["ppid", "name"]))
        qemu_proc = next(filtered_proc, None)
    running_pid = qemu_proc.pid
    if running_pid is None:
        print("QEMU process not found!")
        original_process.terminate()
        return
    starting_memory = process.memory_info().rss

    process = psutil.Process(running_pid)
    monitor(starting_memory, process, "nanos")


if __name__ == "__main__":
    ops_command = ["ops", "pkg", "load",
                   "eyberg/python:3.10.6", "-c", "myconfig.json"]

    if len(sys.argv) > 1:
        command_type = sys.argv[1]
        if command_type == "nanos":
            run_script_and_monitor(ops_command)
        else:
            run_docker_and_monitor("docker")
    else:
        run_script_and_monitor(ops_command)
        run_docker_and_monitor("docker")
    original_process_log = (
        "metrics/docker_usage_log.csv", "docker")
    nanos_process_log = ("metrics/nanos_usage_log.csv", "nanos")
    comparative_plot(original_process_log, nanos_process_log)
