import networkx as nx
import matplotlib.pyplot as plt
import time
import numpy as np
from collections import deque
import os
import matplotlib
import webbrowser
from pathlib import Path
from matplotlib.animation import FuncAnimation, PillowWriter
import subprocess
import shutil

matplotlib.use("Agg")

os.makedirs("graph_visualizations", exist_ok=True)


def open_in_browser(file_path):
    file_uri = Path(file_path).resolve().as_uri()
    preferred_browsers = ["msedge", "chrome", "firefox"]

    for browser in preferred_browsers:
        browser_exe = shutil.which(browser)
        if browser_exe:
            try:
                subprocess.Popen([browser_exe, file_uri])
                return
            except Exception:
                pass

    webbrowser.open_new_tab(file_uri)


def dfs(graph, start, visited=None, path=None, steps=None, step_times=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []
    if steps is None:
        steps = []
    if step_times is None:
        step_times = []

    start_time = time.perf_counter()
    
    visited.add(start)
    path.append(start)

    steps.append(
        {
            "visited": visited.copy(),
            "path": path.copy(),
            "current": start,
            "frontier": [n for n in graph[start] if n not in visited],
        }
    )
    
    step_times.append((time.perf_counter() - start_time) * 1000)

    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited, path, steps, step_times)

    return path, steps, step_times


def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    path = [start]
    steps = []
    step_times = []
    
    start_time = time.perf_counter()
    
    steps.append(
        {
            "visited": visited.copy(),
            "path": path.copy(),
            "current": start,
            "queue": list(queue),
            "frontier": graph[start],
        }
    )
    
    step_times.append((time.perf_counter() - start_time) * 1000)

    while queue:
        start_time = time.perf_counter()
        current = queue.popleft()

        frontier = []
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                path.append(neighbor)
                frontier.append(neighbor)

        if frontier:
            steps.append(
                {
                    "visited": visited.copy(),
                    "path": path.copy(),
                    "current": current,
                    "queue": list(queue),
                    "frontier": frontier,
                }
            )
            
            step_times.append((time.perf_counter() - start_time) * 1000)

    return path, steps, step_times


def measure_performance(graph, start_node, algorithm):
    start_time = time.perf_counter()
    if algorithm == "DFS":
        path, _, _ = dfs(graph, start_node)
    else: 
        path, _, _ = bfs(graph, start_node)
    end_time = time.perf_counter()

    execution_time = (end_time - start_time) * 1000
    memory_usage = len(
        path
    )  

    return {
        "execution_time": execution_time,
        "memory_usage": memory_usage,
        "path_length": len(path),
        "path": path,
    }


def save_algorithm_steps(G, steps, step_times, algorithm, graph_type, directed=False):
    run_dir = f"graph_visualizations/{algorithm}_{graph_type}_steps"
    os.makedirs(run_dir, exist_ok=True)

    if graph_type in ["grid"]:
        pos = {node: node for node in G.nodes()}
    else:
        pos = nx.spring_layout(G, seed=42)

    create_algorithm_gif(
        G,
        pos,
        steps,
        step_times,
        algorithm,
        graph_type,
        run_dir,
        directed=directed,
    )
    print(f"Created GIF animation in {run_dir}/")


def create_algorithm_gif(G, pos, steps, step_times, algorithm, graph_type, run_dir, directed=False):
    gif_file = f"{run_dir}/{algorithm.lower()}_{graph_type}_animation.gif"
    all_nodes = list(G.nodes())

    fig, ax = plt.subplots(figsize=(10, 8))

    def draw_frame(step_idx):
        ax.clear()

        step = steps[step_idx]
        visited = step["visited"]
        current = step["current"]
        frontier = step.get("frontier", [])

        node_colors = []
        node_sizes = []
        for node in all_nodes:
            if node == current:
                node_colors.append("red")
                node_sizes.append(700)
            elif node in frontier:
                node_colors.append("orange")
                node_sizes.append(500)
            elif node in visited:
                node_colors.append("green")
                node_sizes.append(500)
            else:
                node_colors.append("lightgray")
                node_sizes.append(500)

        nx.draw_networkx_edges(G, pos, ax=ax, arrows=directed, alpha=0.3)
        nx.draw_networkx_nodes(
            G,
            pos,
            ax=ax,
            nodelist=all_nodes,
            node_color=node_colors,
            node_size=node_sizes,
        )
        nx.draw_networkx_labels(G, pos, ax=ax)

        queue_str = f"Queue: {step.get('queue', [])}" if algorithm == "BFS" else ""
        step_time = step_times[step_idx]
        ax.set_title(
            f"{algorithm} on {graph_type.title()} Graph - Step {step_idx + 1}/{len(steps)}\n"
            f"{queue_str}\nStep Time: {step_time:.6f} ms"
        )
        ax.axis("off")

    animation = FuncAnimation(fig, draw_frame, frames=len(steps), interval=700, repeat=True)
    animation.save(gif_file, writer=PillowWriter(fps=2))
    plt.close(fig)

    # Open GIF animation automatically with the default system viewer.
    try:
        open_in_browser(gif_file)
    except Exception as exc:
        print(f"Could not auto-open GIF for {gif_file}: {exc}")

    print(f"Created GIF animation at {gif_file}")


# Function to compare algorithms for various node sizes
def compare_algorithms_scaled(graph_type, sizes=[50, 100, 200, 500], directed=False):
    results = {
        "DFS": {"execution_time": [], "memory_usage": [], "path_length": []},
        "BFS": {"execution_time": [], "memory_usage": [], "path_length": []},
    }

    for size in sizes:
        # Generate graph based on type and size
        if graph_type == "path":
            G = nx.path_graph(size)
        elif graph_type == "cycle":
            G = nx.cycle_graph(size)
        elif graph_type == "complete":
            G = nx.complete_graph(size)
        elif graph_type == "star":
            G = nx.star_graph(size - 1)  # -1 because star graph adds a central node
        elif graph_type == "bipartite":
            half_size = size // 2
            G = nx.complete_bipartite_graph(half_size, size - half_size)
        elif graph_type == "binary_tree":
            depth = int(np.log2(size + 1))  # Approximate depth for given size
            G = nx.balanced_tree(2, depth)
        elif graph_type == "forest":
            depth = int(np.log2(size // 2 + 1))
            G1 = nx.balanced_tree(2, depth)
            G2 = nx.balanced_tree(2, depth)
            G = nx.disjoint_union(G1, G2)
            # Add an edge between the two trees
            n1 = len(G1)
            G.add_edge(0, n1)
        elif graph_type == "dag":
            G = nx.DiGraph()
            for i in range(size - 1):
                G.add_edge(i, i + 1)
                if i < size - 2:  # Add some branching
                    G.add_edge(i, i + 2)
        elif graph_type == "directed_cycle":
            G = nx.DiGraph()
            for i in range(size - 1):
                G.add_edge(i, i + 1)
            G.add_edge(size - 1, 0)  # Add cycle
            # Add some additional edges
            for i in range(0, size - 2, 2):
                G.add_edge(i, i + 2)
        elif graph_type == "grid":
            grid_size = int(np.sqrt(size))
            G = nx.grid_2d_graph(grid_size, grid_size)
        elif graph_type == "sparse":
            G = nx.gnp_random_graph(size, 0.2, seed=42)
            # Ensure graph is connected
            while not nx.is_connected(G):
                G = nx.gnp_random_graph(size, 0.2, seed=np.random.randint(1000))
        elif graph_type == "dense":
            G = nx.gnp_random_graph(size, 0.7, seed=42)

        # Ensure we have a valid start node
        start_node = list(G.nodes())[0]

        # Convert NetworkX graph to adjacency list representation
        graph_adj_list = {node: list(G.neighbors(node)) for node in G.nodes()}

        # Run DFS and measure performance
        dfs_result = measure_performance(graph_adj_list, start_node, "DFS")
        results["DFS"]["execution_time"].append(dfs_result["execution_time"])
        results["DFS"]["memory_usage"].append(dfs_result["memory_usage"])
        results["DFS"]["path_length"].append(dfs_result["path_length"])

        # Run BFS and measure performance
        bfs_result = measure_performance(graph_adj_list, start_node, "BFS")
        results["BFS"]["execution_time"].append(bfs_result["execution_time"])
        results["BFS"]["memory_usage"].append(bfs_result["memory_usage"])
        results["BFS"]["path_length"].append(bfs_result["path_length"])

        # For the smallest size, save steps as individual images with HTML viewer
        if size == sizes[0]:
            _, dfs_steps, dfs_times = dfs(graph_adj_list, start_node)
            _, bfs_steps, bfs_times = bfs(graph_adj_list, start_node)
            
            print(f"Saving DFS steps for {graph_type} graph...")
            save_algorithm_steps(G, dfs_steps, dfs_times, "DFS", graph_type, directed)
            
            print(f"Saving BFS steps for {graph_type} graph...")
            save_algorithm_steps(G, bfs_steps, bfs_times, "BFS", graph_type, directed)

    # Plot comparison for all sizes
    fig, axs = plt.subplots(3, 1, figsize=(12, 18))

    metrics = ["execution_time", "memory_usage", "path_length"]
    titles = ["Execution Time (ms)", "Memory Usage (nodes)", "Path Length"]

    for i, (metric, title) in enumerate(zip(metrics, titles)):
        axs[i].plot(sizes, results["DFS"][metric], "o-", label="DFS")
        axs[i].plot(sizes, results["BFS"][metric], "s-", label="BFS")
        axs[i].set_title(f"{title} - {graph_type.title()} Graph")
        axs[i].set_xlabel("Number of Nodes")
        axs[i].set_ylabel(title)
        axs[i].legend()
        axs[i].grid(True)

    plt.tight_layout()
    plt.savefig(f"graph_visualizations/comparison_{graph_type}_scaled.png", dpi=300)
    plt.close()

    # Also create a bar chart comparison for all sizes
    fig, axs = plt.subplots(1, len(sizes), figsize=(20, 8))

    for i, size in enumerate(sizes):
        x = np.arange(len(metrics))
        width = 0.35

        dfs_values = [results["DFS"][metric][i] for metric in metrics]
        bfs_values = [results["BFS"][metric][i] for metric in metrics]

        rects1 = axs[i].bar(x - width / 2, dfs_values, width, label="DFS")
        rects2 = axs[i].bar(x + width / 2, bfs_values, width, label="BFS")

        axs[i].set_title(f"{size} Nodes")
        axs[i].set_xticks(x)
        axs[i].set_xticklabels(["Time (ms)", "Memory", "Path Length"], rotation=45)
        axs[i].legend()

        # Add values on top of bars
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                axs[i].annotate(
                    f"{height:.1f}",
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        autolabel(rects1)
        autolabel(rects2)

    plt.suptitle(
        f"DFS vs BFS on {graph_type.title()} Graph - Performance Comparison",
        fontsize=16,
    )
    plt.tight_layout()
    plt.savefig(f"graph_visualizations/bar_comparison_{graph_type}_scaled.png", dpi=300)
    plt.close()

    return results


# Generate different types of graphs and compare algorithms
def generate_and_analyze_graphs():
    graph_types = [
        "path",
        "cycle",
        "complete",
        "star",
        "bipartite",
        "binary_tree",
        "forest",
        "dag",
        "directed_cycle",
        "grid",
        "sparse",
        "dense",
    ]

    directed_types = ["dag", "directed_cycle"]

    # For visualization, we'll use a smaller subset of graph types
    graph_types_to_visualize = ["path", "cycle", "complete", "star", "binary_tree"]
    
    print("Which graph type would you like to visualize?")
    for i, graph_type in enumerate(graph_types_to_visualize):
        print(f"{i+1}. {graph_type}")
    
    try:
        choice = int(input("Enter your choice (1-5), or 0 to analyze all types: "))
        
        if choice == 0:
            results = {}
            for graph_type in graph_types:
                print(f"Analyzing {graph_type} graphs...")
                results[graph_type] = compare_algorithms_scaled(
                    graph_type,
                    sizes=[50, 100, 200, 300],  # Larger default node counts
                    directed=graph_type in directed_types,
                )
        else:
            graph_type = graph_types_to_visualize[choice-1]
            print(f"Analyzing {graph_type} graph with visualization...")
            # Use larger sizes for visualization
            results = {
                graph_type: compare_algorithms_scaled(
                    graph_type, 
                    sizes=[50, 100, 200, 300],  # Larger default node counts
                    directed=graph_type in directed_types
                )
            }
    except (ValueError, IndexError):
        print("Invalid choice. Using 'binary_tree' as default.")
        graph_type = "binary_tree"
        results = {
            graph_type: compare_algorithms_scaled(
                graph_type, 
                sizes=[50, 100, 200, 300],  # Larger default node counts
                directed=False
            )
        }
    
    return results


# Create a summary visualization of all graph types
def create_summary_visualization(results):
    graph_types = list(results.keys())
    if not graph_types:
        print("No results to visualize")
        return
        
    sizes = [50, 100, 200, 300]  # Adjusted for larger default node counts

    # Plot execution time comparison
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for graph_type in graph_types:
        dfs_times = results[graph_type]["DFS"]["execution_time"]
        bfs_times = results[graph_type]["BFS"]["execution_time"]
        
        ax.plot(sizes, dfs_times, 'o-', label=f"DFS - {graph_type}")
        ax.plot(sizes, bfs_times, 's-', label=f"BFS - {graph_type}")
    
    ax.set_xlabel("Number of Nodes")
    ax.set_ylabel("Execution Time (ms)")
    ax.set_title("DFS vs BFS Execution Time")
    ax.legend()
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig("graph_visualizations/execution_time_comparison.png", dpi=300)
    plt.close()


# Main function for visualization without Tkinter
def main():
    print("Graph Algorithm Visualization")
    print("This program will create sequential visualizations of DFS and BFS algorithms")
    print("This version generates GIF animations only")
    
    results = generate_and_analyze_graphs()
    create_summary_visualization(results)
    
    print("Analysis complete! Visualizations saved in the 'graph_visualizations' directory.")
    print("GIF animations are generated for DFS and BFS in each algorithm subdirectory")
    print("Each frame includes timing information with higher precision")


if __name__ == "__main__":
    main()
