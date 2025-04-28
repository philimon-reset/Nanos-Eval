import multiprocessing
import sys
import time
import psutil
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import docker
import os
from plot_usage import compare_resource_usage_plot
from test_server import run_benchmark

num_cores = os.cpu_count()


def monitor(start_mem_kb, running_process, process_name):
    start_timestamp = time.time()
    log_file = f"metrics/{process_name}_usage_log.csv"
    with open(log_file, "w") as f:
        f.write("Time Stamp,CPU,Memory(KB)\n")

    print(f"Monitoring {process_name} PID: {running_process.pid}")
    process = multiprocessing.Process(target=run_benchmark, args=("nanos",))
    process.start()
    try:
        while process.is_alive():
            cpu = running_process.cpu_percent(interval=1)
            mem_kb = running_process.memory_info().rss
            timestamp = time.time()

            with open(log_file, "a") as f:
                f.write(f"{timestamp}, {cpu}, {mem_kb}\n")

    except psutil.NoSuchProcess as e:
        print(f"Error: {e}")
    running_process.kill()
    print(
        f"Monitoring {running_process.is_running()}")
    print(f"✅ Monitoring complete. Log saved to {log_file}")
    process_metrics(log_file, start_mem_kb, start_timestamp, process_name)
    plot_metrics(log_file, process_name)


def run_docker_and_monitor(process_name, image_name="host_run"):
    log_file = f"metrics/raw_{process_name}_usage_log.csv"
    with open(log_file, "w") as f:
        f.write("Time,TotalUsage,SystemUsage,MemoryUsage\n")

    print(f"Monitoring {process_name} : Image Name {image_name}")
    client = docker.from_env()
    container = client.containers.run(
        image=image_name,
        detach=True,
        remove=True,
        cpu_count=1,
        ports={'8080': '8080'},
        name="sdk_monitor_container"
    )
    process = multiprocessing.Process(
        target=run_benchmark, args=("docker",))
    process.start()
    start_timestamp = time.time()
    print(f"✅ Container started with ID: {container.id}")

    try:
        for stat in container.stats(decode=True, stream=True):
            while process.is_alive():
                cpu_total = stat["cpu_stats"]["cpu_usage"]["total_usage"]
                system_total = stat["cpu_stats"]["system_cpu_usage"]
                memory_usage = stat["memory_stats"]["usage"]

                with open(log_file, "a") as f:
                    f.write(
                        f"{time.time()},{cpu_total},{system_total},{memory_usage}\n")
                time.sleep(1)

            container.kill()
    except Exception as e:
        print(f"❌ Error while collecting stats: {e}")
    process_docker_metrics(log_file, start_timestamp, process_name)


def process_docker_metrics(raw_log, start_timestamp, process_name):
    df = pd.read_csv(raw_log)

    df["CPU%"] = 0.0
    for i in range(1, len(df)):
        cpu_delta = df.loc[i, "TotalUsage"] - df.loc[i - 1, "TotalUsage"]
        sys_delta = df.loc[i, "SystemUsage"] - df.loc[i - 1, "SystemUsage"]
        if sys_delta > 0:
            df.loc[i, "CPU%"] = (cpu_delta / sys_delta) * num_cores * 100.0

    df["Memory(KB)"] = df["MemoryUsage"] // 1024
    df["Memory(MB)"] = df["Memory(KB)"] // 1024
    df["Time"] = df["Time"] - start_timestamp

    df.rename(columns={"Time": "Time Elapsed"}, inplace=True)

    final_log = f"metrics/{process_name}_usage_log.csv"
    df[["Time Elapsed", "CPU%", "Memory(KB)", "Memory(MB)"]].to_csv(
        final_log, index=False)
    print(f"📄 Processed metrics saved to {final_log}")

    plot_metrics(final_log, process_name)


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


def run_script_and_monitor(command, ops_flag=False):
    original_process = subprocess.Popen(command)
    running_pid = original_process.pid
    process = psutil.Process(running_pid)
    starting_memory = 0
    print(f"✅ Command started with PID: {running_pid}")

    if sys.platform == "linux" or sys.platform == "linux2":
        qemu_process_name = "qemu-system-x86_64"
    else:
        qemu_process_name = "qemu-system-aarch64"
    if ops_flag:
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
    monitor(starting_memory, process, command[0])


if __name__ == "__main__":
    ops_command = ["ops", "run", "-c", "myconfig.json", "nanos_run"]
    if len(sys.argv) > 1:
        command_type = sys.argv[1]
        if command_type == "nanos":
            run_script_and_monitor(ops_command, True)
        else:
            run_docker_and_monitor("docker")
    else:
        run_script_and_monitor(ops_command, True)
        run_docker_and_monitor("docker")
    original_process_log = (
        "metrics/docker_usage_log.csv", "docker")
    ops_process_log = ("metrics/ops_usage_log.csv", "ops")
    compare_resource_usage_plot(original_process_log, ops_process_log)
