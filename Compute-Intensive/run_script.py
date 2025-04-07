
import sys
import time
import psutil
import subprocess


def monitor(original_process, running_process, start_mem_kb, start_timestamp, process_name):
    log_file = f"metrics/{process_name}_usage_log.csv"
    with open(log_file, "w") as f:
        f.write("Time Elapsed, Timestamp, CPU%, Memory(KB), Memory(MB)\n")

    print(f"Monitoring {process_name} PID: {running_process.pid}")
    try:
        while psutil.pid_exists(running_process.pid) and original_process.poll() is None:
            cpu = running_process.cpu_percent(interval=.1)
            mem_kb = running_process.memory_info().rss // 1024
            end_kb = mem_kb - start_mem_kb
            end_mb = end_kb // 1024
            timestamp = time.time()
            time_elapsed = timestamp - start_timestamp

            with open(log_file, "a") as f:
                f.write(
                    f"{time_elapsed}, {timestamp}, {cpu}, {end_kb}, {end_mb}\n")
    except psutil.NoSuchProcess as e:
        print(f"Running process: {running_process} not found. \nError: {e}")
    print(
        f"Monitoring {original_process.poll()} and {running_process.is_running()}")
    print(f"✅ Monitoring complete. Log saved to {log_file}")


def run_script_and_monitor(command, ops_flag=False):
    original_process = subprocess.Popen(command)
    running_pid = original_process.pid

    print(f"✅ Command started with PID: {running_pid}")

    if ops_flag:
        qemu_proc = None
        while qemu_proc is None:
            filtered_proc = filter(lambda proc: proc.info["ppid"] == running_pid and "qemu-system-x86_64" in proc.info["name"],
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
    command_type = sys.argv[1] if len(sys.argv) > 1 else "python"
    if command_type == "ops":
        run_script_and_monitor(ops_command, True)
    else:
        run_script_and_monitor(python_command)
