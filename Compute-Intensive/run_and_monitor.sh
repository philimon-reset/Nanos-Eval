#!/bin/bash

# Start OPS in the background
ops pkg load eyberg/python:3.10.6 -c myconfig.json &
OPS_PID=$!

echo "✅ OPS started with PID: $OPS_PID"

# Get the actual QEMU PID (child of OPS)
while [ -z "$QEMU_PID" ]; do
    QEMU_PID=$(pgrep -f -P $OPS_PID qemu-system-x86_64)
done

if [ -z "$QEMU_PID" ]; then
    echo "QEMU process not found!"
    exit 1
fi


START_TIMESTAMP=$(date +%s)
STATS=$(ps -p $QEMU_PID -o rss --no-headers)
START_MEM_KB=$(echo $STATS | awk '{print $1}')
START_MEM_MB=$(echo "$START_MEM_KB/1024" | bc)


echo "Monitoring QEMU PID: $QEMU_PID"
echo "Time Elapsed, Timestamp, CPU%, Memory(KB), Memory(MB)" > metrics/bash_qemu_usage_log.csv

# Monitor until the QEMU process exits
while kill -0 "$QEMU_PID" 2>/dev/null || kill -0 "$OPS_PID" 2>/dev/null; do
    # Get CPU and memory usage
    STATS=$(ps -p $QEMU_PID -o %cpu,rss --no-headers)
    CPU=$(echo $STATS | awk '{print $1}')
    MEM_KB=$(echo $STATS | awk '{print $2}')
    END_KB=$(echo "$MEM_KB - $START_MEM_KB" | bc)
    END_MB=$(echo "$END_KB/1024" | bc)
    TIMESTAMP=$(date +%s)
    TIME_ELAPSED=$(echo "$TIMESTAMP - $START_TIMESTAMP" | bc)

    echo "$TIME_ELAPSED, $TIMESTAMP, $CPU, $END_KB, $END_MB" >> metrics/bash_qemu_usage_log.csv
done

echo "✅ Monitoring complete. Log saved to bash_qemu_usage_log.csv"
