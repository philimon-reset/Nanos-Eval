# Nanos Evaluation

## Introduction

Nanos is a unikernel written in C, designed to run a single application per virtual machine (VM) with minimal overhead. Unlike traditional operating systems that support multiple processes, user accounts, and system services, Nanos provides only the essential components required to execute an application efficiently.

This project investigates the performance and usability of applications running on the Nanos unikernel. Specifically, we will evaluate how well different types of applications perform in a unikernel environment compared to traditional OS setups. The study focuses on applications with varying complexity and functionality.

## Goals of the Evaluation

- Porting Applications to Nanos: Understanding how to adapt various applications to run inside the unikernel.
- Performance Analysis: Measuring startup time, memory footprint, and execution speed.
- Usability Analysis: Assessing how Nanos handles system calls, I/O, and network communication, along with the effort required to port applications.
- Challenges and Solutions: Documenting difficulties encountered during testing and how they were resolved.

## Overview of Nanos and Ops

### What is Nanos?

Nanos is a unikernel designed for lightweight, secure, and high-performance execution of applications. It runs applications in isolated virtual machines, reducing attack surface and improving efficiency.

### What is Ops?

Ops is a tool that allows developers to easily build, package, and deploy applications on Nanos unikernels. It simplifies unikernel management by handling configuration, dependencies, and deployment.

### How to Run Applications in Nanos Using Ops

- Install Ops:

  ` curl https://ops.city/get.sh -sSfL | sh`

- Install qemu and other dependencies:

  `sudo apt-get install qemu-kvm qemu-utils `
  **Note:** May differ based on machine. Check [ops](https://docs.ops.city/ops/getting_started) docs.

- Load the required package (e.g., Python 3.10.6):

  `ops pkg load eyberg/python:3.10.6`

- Run an application inside Nanos:

  `ops run -p 8080 eyberg/python:3.10.6 -c myconfig.json`

## Setting Up the Environment

To ensure compatibility, create a virtual Python environment using pyenv and install dependencies.

1. Install Pyenv (if not installed)

   `curl https://pyenv.run | bash`

   **Note:** Follow instructions to add pyenv to path.

2. Set Up Python 3.10.6 and Virtual Environment

```
  pyenv install 3.10.6
  pyenv virtualenv 3.10.6 venv
  pyenv activate venv
```

3. Install Required Packages (Use the requirements.txt file to install dependencies):

   `pip install -r requirements.txt`

## Directory Structure

The repository is organized into different categories of applications:

```.
|-- compute-intensive/      # Scripts focused on CPU-heavy tasks (e.g., mathematical computations)
|-- io-bound/               # Scripts that involve disk or file I/O operations
|-- networking-based/       # Scripts that test network communication performance
|-- general-purpose/        # Miscellaneous scripts for testing general workloads
|-- requirements.txt        # Python dependencies
|-- myconfig.json           # Configuration file for running Nanos unikernel (found in each directory)
|-- README.md               # Project documentation
```

### Example: Running a Python Script in Nanos

Here’s an example of running a script both locally and inside Nanos.

**Python Script (compute-intensive/script.py)**

```
import time
import math

def compute():
    start = time.time()
    result = sum(math.sqrt(i) for i in range(10**6))
    end = time.time()
    print(f"Execution Time: {end - start} seconds")

compute()
```

- **Running Locally**

  `python compute-intensive/script.py`

**Running Inside Nanos**

1. Build the unikernel package:

   `ops pkg load eyberg/python:3.10.6`

2. Set up **myconfig.json** in the directory with the name of the script and other configuration.

   ```
   {
     "RunConfig": {
       "Verbose": true,
       "Ports": ["8083"]
     },
     "Env": {
       "Environment": "development",
       "TEST": "OPS"
     },
     "Args": ["script.py"],
     "Debugflags": ["trace:pf,threadrun,all", "debugsyscalls"]
   }
   ```

3. Run the script inside the unikernel:

   `ops run -p 8080 eyberg/python:3.10.6 -c myconfig.json`

## Conclusion

This project aims to provide insights into the benefits and limitations of using Nanos for various types of workloads. By systematically measuring execution time, memory footprint, and usability challenges, we can better understand the trade-offs involved in using unikernels versus traditional OS environments.
