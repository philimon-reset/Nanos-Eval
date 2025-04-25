import subprocess
import time
import csv
from datetime import datetime
from math import log

# CONFIG
TARGETS = {
    "nanos": "http://localhost:8080",
    "docker_host": "http://localhost:8081"
}

LOADS = [
    {"concurrency": 10, "duration": "10s"},
    {"concurrency": 50, "duration": "10s"},
    {"concurrency": 100, "duration": "10s"},
    {"concurrency": 200, "duration": "30s"},
]

def run_wrk(target, concurrency, duration):
    cmd = [
        "wrk",
        "-t", str(min(4, concurrency)),  # threads
        "-c", str(concurrency),
        "-d", duration,
        target
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout

def parse_wrk_output(output):
    lines = output.splitlines()
    metrics = {}
    for line in lines:
        if "Requests/sec:" in line:
            metrics["requests_per_sec"] = float(line.split(":")[1].strip())
        elif "Latency" in line:
            metrics["latency_avg"] = line.split()[1]
        elif "Socket errors" in line:
            metrics["errors"] = line
    return metrics

def main():
    for platform, url in TARGETS.items():
        log_file = f"metrics/webserver_metrics_{platform}.csv"
        with open(log_file, "w") as csvfile:
            fieldnames = ["concurrency", "duration", "requests_per_sec", "latency_avg", "errors"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for load in LOADS:
                output = run_wrk(url, load["concurrency"], load["duration"])
                metrics = parse_wrk_output(output)
                metrics |= {
                    "concurrency": load["concurrency"],
                    "duration": load["duration"],
                }
                writer.writerow(metrics)
                time.sleep(2)

if __name__ == "__main__":
    main()
