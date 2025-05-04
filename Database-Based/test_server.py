import subprocess
import sys
import time
import csv
from datetime import datetime
from math import log
FIELDNAMES = ['test', 'rps', 'avg_latency_ms', 'min_latency_ms', 'p50_latency_ms',
              'p95_latency_ms', 'p99_latency_ms', 'max_latency_ms', 'connection', 'requests']
# CONFIG
TARGETS = {
    "nanos": {"host": "127.0.0.1", "port": 6379},
    "docker": {"host": "127.0.0.1", "port": 6379}
}

LOADS = [
    {"connection": 10, "requests": 10000, "warm_up": True}  # warm up
] + [
    {"connection": conn, "requests": 40000}
    for conn in [10, 50, 100]
    for _ in range(10)
]


def run_redis_benchmark(host, port, connections, requests):
    cmd = [
        "redis-benchmark",
        "-h", host,
        "-p", str(port),
        "-c", str(connections),
        "-n", str(requests),
        "--csv",
        "-t", "set,get"  # test SET and GET commands
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    return result.stdout


def run_benchmark(platform):
    target = TARGETS.get(platform)
    log_file = f"metrics/database/database_metrics_{platform}.csv"
    with open(log_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for load in LOADS:
            output = run_redis_benchmark(
                target["host"],
                target["port"],
                load["connection"],
                load["requests"]
            ).splitlines()
            metrics = [
                x + f",{load['connection']},{load['requests']}" for x in output[1:]]
            for idx, row in enumerate(metrics):
                processed_row = []
                for x in row.split(","):
                    x = x.strip('"')
                    try:
                        x = float(x)
                    except ValueError:
                        pass
                    processed_row.append(x)
                metrics[idx] = dict(zip(FIELDNAMES, processed_row))
                if not load.get("warm_up"):
                    writer.writerow(metrics[idx])

            time.sleep(1)
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_benchmark(sys.argv[1])
    else:
        print("Usage: python redis_benchmark_runner.py [platform]")
