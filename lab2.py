import time  # Import the time module for measuring execution time
import matplotlib.pyplot as plt  # Import matplotlib for plotting graphs
import random  # Import random for generating random numbers
import tkinter as tk  # Import tkinter for creating GUI dialogs
from tkinter import simpledialog  # Import simpledialog for user input
import matplotlib  # Import matplotlib for visualization
matplotlib.use('TkAgg')  # Set the backend for matplotlib to TkAgg for GUI compatibility
from sympy import false  # Import false from sympy (unused in this code)

snapshots = []  # Initialize an empty list to store snapshots of arrays during sorting

def captureSnapshot(arr):
    snapshots.append(arr[:])  # Append a copy of the array to the snapshots list

# QuickSort
def partition(array, low, high):
    pivot = array[high]  # Choose the last element as the pivot
    i = low - 1  # Pointer for smaller elements

    for j in range(low, high):
        if array[j] <= pivot:
            i += 1
            array[i], array[j] = array[j], array[i]  # Swap elements if they are smaller than the pivot

    array[i + 1], array[high] = array[high], array[i + 1]  # Place the pivot in its correct position
    return i + 1  # Return the index of the pivot

def quickSort(array, start, end, snap = false):
    if start < end:
        piv = partition(array, start, end)  # Partition the array and get the pivot index
        if (snap) : captureSnapshot(array)  # Capture a snapshot if snap is true
        quickSort(array, start, piv - 1)  # Recursively sort the left part of the array
        quickSort(array, piv + 1, end)  # Recursively sort the right part of the array

# MergeSort
def merge(arr, l, m, r, snap):
    L = arr[l:m + 1]  # Left half of the array
    R = arr[m + 1:r + 1]  # Right half of the array

    i = j = 0  # Initialize pointers for left and right halves
    k = l  # Pointer for the merged array

    while i < len(L) and j < len(R):
        if L[i] <= R[j]:
            arr[k] = L[i]  # Place the smaller element from the left half into the array
            i += 1
        else:
            arr[k] = R[j]  # Place the smaller element from the right half into the array
            j += 1
        k += 1
        if (snap) : captureSnapshot(arr[:])  # Capture a snapshot if snap is true

    while i < len(L):  # Copy remaining elements from the left half
        arr[k] = L[i]
        i += 1
        k += 1
        if (snap): captureSnapshot(arr[:])  # Capture a snapshot if snap is true

    while j < len(R):  # Copy remaining elements from the right half
        arr[k] = R[j]
        j += 1
        k += 1
        if (snap): captureSnapshot(arr[:])  # Capture a snapshot if snap is true

def mergeSort(arr, l, r, snap = false):
    if l < r:
        m = l + (r - l) // 2  # Calculate the middle index
        mergeSort(arr, l, m)  # Recursively sort the left half
        mergeSort(arr, m + 1, r)  # Recursively sort the right half
        merge(arr, l, m, r, snap)  # Merge the sorted halves

# HeapSort
def heapify(arr, n, i, snap):
    largest = i  # Assume the root is the largest
    l = 2 * i + 1  # Left child index
    r = 2 * i + 2  # Right child index

    if l < n and arr[l] > arr[largest]:
        largest = l  # Update largest if the left child is larger

    if r < n and arr[r] > arr[largest]:
        largest = r  # Update largest if the right child is larger

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # Swap the root with the largest child
        if (snap) : captureSnapshot(arr[:])  # Capture a snapshot if snap is true
        heapify(arr, n, largest, snap)  # Recursively heapify the affected subtree

def countingSort(arr):
    max_val = max(arr)  # Find the maximum value in the array
    count = [0] * (max_val + 1)  # Initialize a count array with zeros

    while len(arr) > 0:
        num = arr.pop(0)  # Remove the first element from the array
        count[num] += 1  # Increment the count for that element

    for i in range(len(count)):
        while count[i] > 0:
            arr.append(i)  # Append the element to the array based on its count
            count[i] -= 1  # Decrement the count

def heapSort(arr, snap=false):
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):  # Build a max heap
        heapify(arr, n, i, snap)

    for i in range(n - 1, 0, -1):  # Extract elements one by one
        arr[i], arr[0] = arr[0], arr[i]  # Move the max element to the end
        heapify(arr, i, 0, snap)  # Restore the heap property

def measure_time(arr):
    methods = ["quickSort", "mergeSort", "heapSort", "countSort"]  # List of sorting methods
    times = {}  # Dictionary to store execution times
    for method in methods:
        arrCopy = arr[:]  # Create a copy of the array
        start = time.perf_counter()  # Start the timer
        if method == "quickSort":
            quickSort(arrCopy, 0, len(arrCopy)-1)  # Perform QuickSort
        elif method == "mergeSort":
            mergeSort(arrCopy, 0, len(arrCopy)-1)  # Perform MergeSort
        elif method == "heapSort":
            heapSort(arrCopy)  # Perform HeapSort
        elif method == "countSort":
            countingSort(arrCopy)  # Perform CountingSort
        times[method] = (time.perf_counter() - start) * 1000  # Calculate and store the time in milliseconds
    return times  # Return the dictionary of execution times

arrays = [
    random.sample(range(0, 1000), 100),  # Generate a random array of 100 elements
    random.sample(range(0, 1000), 1000),  # Generate a random array of 1000 elements
    random.sample(range(0, 10000), 10000),  # Generate a random array of 10000 elements
    random.sample(range(0, 100000), 100000),  # Generate a random array of 100000 elements
    random.sample(range(0, 500000), 500000)  # Generate a random array of 500000 elements
]

# Array names for printing purposes
array_names = ["100 Elements", "1K Elements", "10K Elements", "100K Elements", "500K Elements"]

# Print the header
print(f"{'Elements':<15}{'QuickSort (ms)':<20}{'MergeSort (ms)':<20}{'HeapSort (ms)':<20}{'CountingSort (ms)'}")

quick_sort_times = []  # List to store QuickSort execution times
merge_sort_times = []  # List to store MergeSort execution times
heap_sort_times = []  # List to store HeapSort execution times
counting_sort_times = []  # List to store CountingSort execution times

# Measure time for each array and print the results
for i, arr in enumerate(arrays):
    times = measure_time(arr)  # Measure execution times for the current array
    print(f"{array_names[i]:<15}{times['quickSort']:<20.4f}{times['mergeSort']:<20.4f}{times['heapSort']:<20.4f}{times['countSort']:<.4f}")
    quick_sort_times.append(times["quickSort"])  # Append QuickSort time to the list
    merge_sort_times.append(times["mergeSort"])  # Append MergeSort time to the list
    heap_sort_times.append(times["heapSort"])  # Append HeapSort time to the list
    counting_sort_times.append(times["countSort"])  # Append CountingSort time to the list

# Plotting
x_values = [100, 1000, 10000, 100000, 500000]  # X-axis values (number of elements)
plt.figure(figsize=(10, 6))  # Create a figure for the plot
plt.plot(x_values, quick_sort_times, marker='o', linestyle='-', label="QuickSort")  # Plot QuickSort times
plt.plot(x_values, merge_sort_times, marker='s', linestyle='-', label="MergeSort")  # Plot MergeSort times
plt.plot(x_values, heap_sort_times, marker='^', linestyle='-', label="HeapSort")  # Plot HeapSort times
plt.plot(x_values, counting_sort_times, marker='d', linestyle='-', label="CountingSort")  # Plot CountingSort times

# Labels and title
plt.xlabel("Number of Elements")  # Label for the X-axis
plt.ylabel("Time (ms)")  # Label for the Y-axis
plt.title("Sorting Algorithm Efficiency")  # Title of the plot
plt.xscale("log")  # Use a logarithmic scale for the X-axis
plt.yscale("log")  # Use a logarithmic scale for the Y-axis
plt.legend()  # Display the legend
plt.grid(True, which="both", linestyle="--", linewidth=0.5)  # Add a grid to the plot

# Show plot
plt.show()  # Display the plot

# Sorting visualization

def visualize_quick_sort(arr):
    plt.figure(figsize=(10, 6))  # Create a figure for QuickSort visualization
    quick_sort_display(arr)  # Call the QuickSort display function
    plt.show()  # Display the visualization

def visualize_merge_sort(arr):
    plt.figure(figsize=(10, 6))  # Create a figure for MergeSort visualization
    merge_sort_display(arr)  # Call the MergeSort display function
    plt.show()  # Display the visualization

def visualize_heap_sort(arr):
    plt.figure(figsize=(10, 6))  # Create a figure for HeapSort visualization
    heap_sort_display(arr)  # Call the HeapSort display function
    plt.show()  # Display the visualization

def visualize_counting_sort(arr):
    counting_sort_display(arr)  # Call the CountingSort display function
    plt.show()  # Display the visualization

# Sorting functions without snapshots

def quick_sort_display(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1  # Set the high index if not provided
    if low < high:
        pivot = partition(arr, low, high)  # Partition the array
        plt.clf()  # Clear the current figure
        plt.bar(range(len(arr)), arr, color='blue')  # Plot the array as a bar chart
        plt.pause(0.01)  # Pause to visualize the step
        quick_sort_display(arr, low, pivot - 1)  # Recursively sort the left part
        quick_sort_display(arr, pivot + 1, high)  # Recursively sort the right part

def partition(array, low, high):
    pivot = array[high]  # Choose the last element as the pivot
    i = low - 1  # Pointer for smaller elements
    for j in range(low, high):
        if array[j] <= pivot:
            i += 1
            array[i], array[j] = array[j], array[i]  # Swap elements
    array[i + 1], array[high] = array[high], array[i + 1]  # Place the pivot correctly
    return i + 1  # Return the pivot index

def merge_sort_display(arr, l=0, r=None):
    if r is None:
        r = len(arr) - 1  # Set the right index if not provided
    if l < r:
        m = (l + r) // 2  # Calculate the middle index
        merge_sort_display(arr, l, m)  # Recursively sort the left half
        merge_sort_display(arr, m + 1, r)  # Recursively sort the right half
        merge(arr, l, m, r)  # Merge the sorted halves
        plt.clf()  # Clear the current figure
        plt.bar(range(len(arr)), arr, color='blue')  # Plot the array as a bar chart
        plt.pause(0.01)  # Pause to visualize the step

def merge(arr, l, m, r):
    left = arr[l:m + 1]  # Left half of the array
    right = arr[m + 1:r + 1]  # Right half of the array
    i = j = 0  # Initialize pointers for left and right halves
    k = l  # Pointer for the merged array
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            arr[k] = left[i]  # Place the smaller element from the left half
            i += 1
        else:
            arr[k] = right[j]  # Place the smaller element from the right half
            j += 1
        k += 1
    while i < len(left):
        arr[k] = left[i]  # Copy remaining elements from the left half
        i += 1
        k += 1
    while j < len(right):
        arr[k] = right[j]  # Copy remaining elements from the right half
        j += 1
        k += 1

def heap_sort_display(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):  # Build a max heap
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):  # Extract elements one by one
        arr[i], arr[0] = arr[0], arr[i]  # Move the max element to the end
        plt.clf()  # Clear the current figure
        plt.bar(range(len(arr)), arr, color='blue')  # Plot the array as a bar chart
        plt.pause(0.01)  # Pause to visualize the step
        heapify(arr, i, 0)  # Restore the heap property

def heapify(arr, n, i):
    largest = i  # Assume the root is the largest
    left = 2 * i + 1  # Left child index
    right = 2 * i + 2  # Right child index
    if left < n and arr[left] > arr[largest]:
        largest = left  # Update largest if the left child is larger
    if right < n and arr[right] > arr[largest]:
        largest = right  # Update largest if the right child is larger
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]  # Swap the root with the largest child
        heapify(arr, n, largest)  # Recursively heapify the affected subtree

def counting_sort_display(arr):
    max_val = max(arr)  # Find the maximum value in the array
    count = [0] * (max_val + 1)  # Initialize a count array with zeros

    for num in arr:
        count[num] += 1  # Count the occurrences of each element

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))  # Create a figure with two subplots

    index = 0
    for i in range(len(count)):
        while count[i] > 0:
            arr[index] = i  # Place the element in the sorted array
            index += 1
            count[i] -= 1  # Decrement the count

            axes[0].cla()  # Clear the first subplot
            axes[0].bar(range(len(arr)), arr, color='blue')  # Plot the sorted array
            axes[0].set_title("Sorted Array")  # Set the title for the first subplot

            axes[1].cla()  # Clear the second subplot
            axes[1].bar(range(len(count)), count, color='red')  # Plot the count array
            axes[1].set_title("Count Array")  # Set the title for the second subplot

            plt.pause(0.01)  # Pause to visualize the step

# Prompt for sorting visualization

def select_sorting():
    root = tk.Tk()  # Create a Tkinter root window
    root.withdraw()  # Hide the root window

    while True:
        sort_choice = simpledialog.askstring("Sorting Visualization",
                                             "Choose a sorting algorithm: Quick, Merge, Heap, Counting or type 'exit' to quit")

        if not sort_choice or sort_choice.lower() == "exit":
            break  # Exit the loop if the user types 'exit'

        arr = [random.randint(0,200) for _ in range(200)]  # Generate a random array of 200 elements

        if sort_choice.lower() == "quick":
            visualize_quick_sort(arr)  # Visualize QuickSort
        elif sort_choice.lower() == "merge":
            visualize_merge_sort(arr)  # Visualize MergeSort
        elif sort_choice.lower() == "heap":
            visualize_heap_sort(arr)  # Visualize HeapSort
        elif sort_choice.lower() == "counting":
            visualize_counting_sort(arr)  # Visualize CountingSort
        else:
            print("Invalid selection.")  # Print an error message for invalid input

# Run visualization selection
select_sorting()  # Call the function to start the sorting visualization