# import numpy as np
import time


# Measure startup time
start_time = time.time()


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
# def matrix_multiplication(size):
#     A = np.random.randint(0, 100, (size, size))
#     B = np.random.randint(0, 100, (size, size))
#     return np.dot(A, B)


if __name__ == "__main__":
    print("Starting computation...")
    # Compute intensive tasks
    primes = generate_primes(500000)
    # matrix_result = matrix_multiplication(500)

    # Measure execution time
    execution_time = time.time() - start_time

    # Print results
    print(f"Execution Time: {execution_time} seconds")
