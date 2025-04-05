import time
import os
import psutil
import numpy as np

# Measure startup time
start_time = time.time()

# Get process memory usage before computation
process = psutil.Process(os.getpid())
memory_before = process.memory_info().rss / (1024 * 1024)  # Convert to MB

# Function to generate prime numbers
def generate_primes(n):
    primes = []
    for num in range(2, n):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

# Function to perform matrix multiplication
def matrix_multiplication(size):
    A = np.random.randint(0, 100, (size, size))
    B = np.random.randint(0, 100, (size, size))
    return np.dot(A, B)

if "__name__" == __main__:
    # Compute intensive tasks
    primes = generate_primes(100000)
    matrix_result = matrix_multiplication(500)

    # Measure execution time
    execution_time = time.time() - start_time

    # Get memory usage after computation
    memory_after = process.memory_info().rss / (1024 * 1024)  # Convert to MB
    memory_used = memory_after - memory_before

    # Print results
    print(f"Startup Time: {start_time - time.time()} seconds")
    print(f"Execution Time: {execution_time} seconds")
    print(f"Memory Used: {memory_used:.2f} MB")
