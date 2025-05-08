import subprocess
import sys
import time
import csv
from datetime import datetime
from math import log

# CONFIG
TARGETS = {
    "nanos": "http://localhost:8080",
    "docker": "http://localhost:8080"
}

LOADS = [
    {"connection": 10, "duration": "10s", "warm_up": True}  # warm up
] + [
    {"connection": conn, "duration": "10s"}
    for conn in [10, 50, 100]
    for _ in range(10)
]


def run_wrk(target, connection, duration):
    cmd = [
        "wrk",
        "-t", str(min(4, connection)),  # threads
        "-c", str(connection),
        "-d", duration,
        target
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
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


def run_benchmark(platform):
    log_file = f"metrics/webserver/webserver_metrics_{platform}.csv"
    with open(log_file, "w") as csvfile:
        fieldnames = ["connection", "duration",
                      "requests_per_sec", "latency_avg", "errors"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for load in LOADS:
            output = run_wrk(TARGETS.get(platform),
                             load["connection"], load["duration"])
            metrics = parse_wrk_output(output)
            metrics |= {
                "connection": load["connection"],
                "duration": load["duration"],
            }
            if not load.get("warm_up"):
                writer.writerow(metrics)
            time.sleep(3)
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_benchmark(sys.argv[1])
