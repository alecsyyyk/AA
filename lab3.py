import networkx as nx
import matplotlib.pyplot as plt
import time
import numpy as np
from collections import deque
import os
from matplotlib.lines import Line2D
import matplotlib
import json

matplotlib.use("Agg")

os.makedirs("graph_visualizations", exist_ok=True)


def dfs(graph, start, visited=None, path=None, steps=None, step_times=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []
    if steps is None:
        steps = []
    if step_times is None:
        step_times = []

    start_time = time.time() 
    
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
    
    step_times.append(time.time() - start_time)

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
    
    start_time = time.time() 
    
    steps.append(
        {
            "visited": visited.copy(),
            "path": path.copy(),
            "current": start,
            "queue": list(queue),
            "frontier": graph[start],
        }
    )
    
    step_times.append(time.time() - start_time)

    while queue:
        start_time = time.time()  
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
            
            step_times.append(time.time() - start_time)

    return path, steps, step_times


def measure_performance(graph, start_node, algorithm):
    start_time = time.time()
    if algorithm == "DFS":
        path, _, _ = dfs(graph, start_node)
    else: 
        path, _, _ = bfs(graph, start_node)
    end_time = time.time()

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
    
    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="red",
            markersize=15,
            label="Current Node",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="orange",
            markersize=15,
            label="Frontier Nodes",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="green",
            markersize=15,
            label="Visited Nodes",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="lightgray",
            markersize=15,
            label="Unvisited Nodes",
        ),
    ]
    
    for step_idx, step in enumerate(steps):
        fig, ax = plt.subplots(figsize=(10, 8))
        
        visited = step["visited"]
        current = step["current"]
        frontier = step.get("frontier", [])
        
        nx.draw_networkx_edges(G, pos, ax=ax, arrows=directed, alpha=0.3)
        
        all_nodes = list(G.nodes())
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
        step_time = step_times[step_idx] * 1000  
        
        ax.legend(handles=legend_elements, loc="upper right")
        ax.set_title(
            f"{algorithm} on {graph_type.title()} Graph - Step {step_idx+1}/{len(steps)}\n"
            f"{queue_str}\nStep Time: {step_time:.4f} ms"  
        )
        ax.axis("off")
        
        plt.savefig(f"{run_dir}/step_{step_idx+1:03d}.png", dpi=300)
        plt.close(fig)
    
    print(f"Saved {len(steps)} steps as images in {run_dir}/")
    
    with open(f"{run_dir}/step_times.json", 'w') as f:
        json.dump([round(t * 1000, 4) for t in step_times], f) 
    
    create_html_viewer(run_dir, algorithm, graph_type, len(steps))


def create_html_viewer(image_dir, algorithm, graph_type, num_steps):
    html_file = f"{image_dir}/view_steps.html"
    
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{algorithm} on {graph_type} Graph</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
                text-align: center;
            }}
            .controls {{
                margin: 20px 0;
                display: flex;
                justify-content: center;
                gap: 10px;
                flex-wrap: wrap;
            }}
            button {{
                padding: 10px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #45a049;
            }}
            #resetButton {{
                background-color: #f44336;
            }}
            #resetButton:hover {{
                background-color: #d32f2f;
            }}
            .step-info {{
                margin: 10px 0;
                font-size: 18px;
            }}
            .time-info {{
                margin: 5px 0;
                font-size: 16px;
                color: #666;
            }}
            .meta-info {{
                margin-top: 20px;
                font-size: 12px;
                color: #999;
            }}
            img {{
                max-width: 100%;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <h1>{algorithm} on {graph_type.title()} Graph</h1>
        
        <div class="controls">
            <button onclick="prevStep()">Previous Step</button>
            <button onclick="nextStep()">Next Step</button>
            <button onclick="playAnimation()">Play Animation</button>
            <button onclick="stopAnimation()">Stop</button>
            <button id="resetButton" onclick="resetViewer()">Reset</button>
        </div>
        
        <div class="step-info">
            Step <span id="currentStep">1</span> of {num_steps}
        </div>
        
        <div class="time-info">
            Step Time: <span id="stepTime">loading...</span> ms
        </div>
        
        <div>
            <img id="stepImage" src="step_001.png" alt="Algorithm Step">
        </div>
        
        
        <script>
            let currentStep = 1;
            const totalSteps = {num_steps};
            let animationInterval = null;
            let stepTimes = [];
            
            // Fetch step times from JSON file
            fetch('step_times.json')
                .then(response => response.json())
                .then(data => {{
                    stepTimes = data;
                    document.getElementById('stepTime').textContent = stepTimes[0].toFixed(4);
                }})
                .catch(error => {{
                    console.error('Error loading step times:', error);
                    document.getElementById('stepTime').textContent = 'N/A';
                }});
            
            function updateImage() {{
                const stepStr = currentStep.toString().padStart(3, '0');
                document.getElementById('stepImage').src = `step_${{stepStr}}.png`;
                document.getElementById('currentStep').textContent = currentStep;
                
                // Update step time with 4 decimal places
                if (stepTimes.length > 0) {{
                    document.getElementById('stepTime').textContent = stepTimes[currentStep - 1].toFixed(4);
                }}
            }}
            
            function nextStep() {{
                if (currentStep < totalSteps) {{
                    currentStep++;
                    updateImage();
                }}
            }}
            
            function prevStep() {{
                if (currentStep > 1) {{
                    currentStep--;
                    updateImage();
                }}
            }}
            
            function playAnimation() {{
                if (animationInterval) clearInterval(animationInterval);
                animationInterval = setInterval(() => {{
                    nextStep();
                    if (currentStep === totalSteps) {{
                        stopAnimation();
                    }}
                }}, 1000); // 1 second between steps
            }}
            
            function stopAnimation() {{
                if (animationInterval) {{
                    clearInterval(animationInterval);
                    animationInterval = null;
                }}
            }}
            
            function resetViewer() {{
                stopAnimation();
                currentStep = 1;
                updateImage();
            }}
        </script>
    </body>
    </html>
    """
    
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"Created HTML viewer at {html_file}")
    print(f"Open this file in a web browser to view the algorithm steps interactively")


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
    print("Instead of GIFs, it will generate HTML viewers with step-by-step images")
    
    results = generate_and_analyze_graphs()
    create_summary_visualization(results)
    
    print("Analysis complete! Visualizations saved in the 'graph_visualizations' directory.")
    print("Open the HTML files in each algorithm's subdirectory to view the step-by-step execution")
    print("Each step now includes timing information (with 4 decimal places) and you can use the reset button to start over")


if __name__ == "__main__":
    main()
