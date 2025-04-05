import time
import subprocess
import os
import sys
current_dir = os.getcwd()

start = time.time()
subprocess.run([sys.executable, f"{current_dir}/script.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
end = time.time()
print(f"Default Execution Time: {end - start} seconds")

start = time.time()
subprocess.run(["ops", "run", "eyberg/python:3.10.6", "-c", f"{current_dir}/myconfig.json"],
               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
end = time.time()
print(f"Ops Execution Time: {end - start} seconds")