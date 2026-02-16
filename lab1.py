import time
import matplotlib.pyplot as plt

# polynomial 
def fibonacci_polynomial(n):
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b

# fast doubling 
def fib_fast_doubling(n):
    def fib_pair(n):
        if n == 0:
            return (0, 1)
        else:
            a, b = fib_pair(n // 2)
            c = a * (2 * b - a)
            d = a * a + b * b
            if n % 2 == 0:
                return (c, d)
            else:
                return (d, c + d)
    return fib_pair(n)[0]

# fraction aproximation
def fibonacci_continued_fraction(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result = 1 + 1 / result
    return round(result)

#matrix exponentiation 
def fibonacci_matrix(n):
    def matrix_multiply(a, b):
        return [
            [a[0][0]*b[0][0] + a[0][1]*b[1][0], a[0][0]*b[0][1] + a[0][1]*b[1][1]],
            [a[1][0]*b[0][0] + a[1][1]*b[1][0], a[1][0]*b[0][1] + a[1][1]*b[1][1]]
        ]
    
    def matrix_power(matrix, n):
        if n == 1:
            return matrix
        if n % 2 == 0:
            half = matrix_power(matrix, n // 2)
            return matrix_multiply(half, half)
        return matrix_multiply(matrix, matrix_power(matrix, n - 1))
    
    if n <= 1:
        return n
    result = matrix_power([[1, 1], [1, 0]], n)
    return result[0][1]

# time measurement function 
def measure_time(n_values):
    times_poly = []
    times_fast_doubling = []
    times_continued_fraction = []
    times_matrix = []

    print("{:<15}{:<15}".format("Method", " ".join([f"{n:<9}" for n in n_values])))
    methods = ["Polynomial", "Fast Doubling", "Continued Fraction", "Matrix Exponentiation"]

    for method in methods:
        times = []
        for n in n_values:
            start = time.perf_counter()  # Renamed to avoid 'time' conflict
            if method == "Polynomial":
                fibonacci_polynomial(n)
            elif method == "Fast Doubling":
                fib_fast_doubling(n)
            elif method == "Continued Fraction":
                fibonacci_continued_fraction(n)
            elif method == "Matrix Exponentiation":
                fibonacci_matrix(n)
            elapsed_time = (time.perf_counter() - start) * 1000
            times.append(elapsed_time)

        # Print results
        print(f"{method:<15}", end="")
        for time_taken in times:
            print(f"{time_taken:<10.5f}", end="")
        print()

        # Store times based on the method
        if method == "Polynomial":
            times_poly = times
        elif method == "Fast Doubling":
            times_fast_doubling = times
        elif method == "Continued Fraction":
            times_continued_fraction = times
        elif method == "Matrix Exponentiation":
            times_matrix = times

    return times_poly, times_fast_doubling, times_continued_fraction, times_matrix

# Values for Fibonacci calculation
n_values = [501, 631, 794, 1000, 1259, 1585, 1995, 2512, 3162, 3981, 5012, 6310, 7943, 10000, 12589, 15849]

# Measure the time for each n
times_poly, times_fast_doubling, times_continued_fraction, times_matrix = measure_time(n_values)

def plot_results(n_values, times, method_name, color, marker):
    plt.figure(figsize=(10, 5))
    plt.plot(n_values, times, marker=marker, color=color, linestyle='-', markersize=5)
    plt.xlabel('Nth Fibonacci Term')
    plt.ylabel('Time (ms)')
    plt.title(f'{method_name} Method: Time vs Nth Fibonacci Term')
    plt.grid(True)
    plt.show()

# Plot individual methods
plot_results(n_values, times_poly, "Polynomial", 'b', 'o')
plot_results(n_values, times_fast_doubling, "Fast Doubling", 'r', 's')
plot_results(n_values, times_continued_fraction, "Continued Fraction", 'g', '^')
plot_results(n_values, times_matrix, "Matrix Exponentiation", 'm', 'd')

# Plot all methods together
plt.plot(n_values, times_poly, marker='o', color='b', linestyle='-', markersize=5, label="Polynomial")
plt.plot(n_values, times_fast_doubling, marker='s', color='r', linestyle='-', markersize=5, label="Fast Doubling")
plt.plot(n_values, times_continued_fraction, marker='^', color='g', linestyle='-', markersize=5, label="Continued Fraction")
plt.plot(n_values, times_matrix, marker='d', color='m', linestyle='-', markersize=5, label="Matrix Exponentiation")

plt.xlabel('Nth Fibonacci Term')
plt.ylabel('Time (ms)')
plt.title('Time to Compute Fibonacci Terms Using Different Methods')
plt.legend()
plt.grid(True)
plt.show()
