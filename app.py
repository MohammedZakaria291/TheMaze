import streamlit as st
import random
import time
from collections import deque

# =====================================
# Generate Maze with Loops
# =====================================
def generate_maze(width=15, height=12):
    """Generate a perfect maze using recursive backtracking, then add random openings to create loops."""
    maze = [[1] * (width * 2 + 1) for _ in range(height * 2 + 1)]
    
    def carve(x, y):
        maze[y][x] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width * 2 and 1 <= ny < height * 2 and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)
    
    carve(1, 1)
    maze[1][0] = 0                          # Entrance (top-left)
    maze[height * 2 - 1][width * 2] = 0      # Exit (bottom-right)
    
    # Key feature: add random wall removals to create multiple paths and loops
    add_random_openings(maze, holes=60)
    
    return maze, (1, 0), (height * 2 - 1, width * 2)

def add_random_openings(maze, holes=60):
    """Randomly remove walls to introduce loops and alternative routes."""
    h, w = len(maze), len(maze[0])
    for _ in range(holes):
        y = random.randint(1, h - 2)
        x = random.randint(1, w - 2)
        if maze[y][x] == 1:  # Only remove actual walls
            maze[y][x] = 0

# =====================================
# Build Graph Representation
# =====================================
def build_graph(maze):
    """Convert the 2D maze into an adjacency list graph."""
    graph = {}
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    h, w = len(maze), len(maze[0])
    for y in range(h):
        for x in range(w):
            if maze[y][x] == 0:  # Passable cell
                graph[(y, x)] = []
                for dy, dx in directions:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and maze[ny][nx] == 0:
                        graph[(y, x)].append((ny, nx))
    return graph

# =====================================
# Heuristic Function (with randomness for variety)
# =====================================
def manhattan(a, b):
    """Manhattan distance with small random noise to break ties differently."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + random.randint(0, 4)

# =====================================
# Text-based Maze Renderer
# =====================================
def render_maze(maze, pos=None, visited=None, path=None):
    """Render the maze as a string using emojis."""
    output = ""
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if pos and (y, x) == pos:
                output += "🧍"      # Current position
            elif path and (y, x) in path:
                output += "🟩"      # Final solution path
            elif visited and (y, x) in visited:
                output += "▫️"      # Explored cell
            elif maze[y][x] == 1:
                output += "⬛"      # Wall
            else:
                output += "⬜"      # Open path
        output += "\n"
    return output

# =====================================
# Search Algorithms (Generator-based for animation)
# =====================================
def bfs_solver(graph, start, goal):
    """Breadth-First Search – guarantees shortest path."""
    queue = deque([[start]])
    visited = set([start])
    yield start, visited.copy(), None
    
    while queue:
        path = queue.popleft()
        node = path[-1]
        yield node, visited.copy(), None
        
        if node == goal:
            yield node, visited.copy(), set(path)
            return
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

def dfs_solver(graph, start, goal):
    """Depth-First Search – often finds long, winding paths."""
    stack = [[start]]
    visited = set()
    yield start, set(), None
    
    while stack:
        path = stack.pop()
        node = path[-1]
        
        if node in visited:
            continue
        
        visited.add(node)
        yield node, visited.copy(), None
        
        if node == goal:
            yield node, visited.copy(), set(path)
            return
        
        # Shuffle neighbors for varied (usually longer) paths
        neighbors = graph[node][:]
        random.shuffle(neighbors)
        
        for neighbor in neighbors:
            if neighbor not in visited:
                stack.append(path + [neighbor])

def greedy_solver(graph, start, goal):
    """Greedy Best-First Search – follows heuristic, fast but not always optimal."""
    open_list = [[start]]
    visited = set([start])
    yield start, visited.copy(), None
    
    while open_list:
        open_list.sort(key=lambda p: manhattan(p[-1], goal))
        path = open_list.pop(0)
        node = path[-1]
        
        yield node, visited.copy(), None
        
        if node == goal:
            yield node, visited.copy(), set(path)
            return
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                open_list.append(path + [neighbor])

# =====================================
# Streamlit User Interface
# =====================================
st.set_page_config(page_title="Maze Solver AI", layout="centered")
st.title("🧠 Maze Solver Visualization")

# Sidebar controls
algo = st.sidebar.selectbox(
    "Select Algorithm",
    ["BFS (Guaranteed Shortest Path)", "DFS (Long & Winding Paths)", "Greedy Best-First (Heuristic)"]
)

speed = st.sidebar.slider("Animation Speed (seconds)", 0.01, 0.5, 0.1, 0.01)

if st.sidebar.button("🔄 Generate New Maze"):
    st.session_state.clear()

# Initialize maze and graph if not present
if "maze" not in st.session_state:
    maze, start, goal = generate_maze()
    st.session_state.maze = maze
    st.session_state.start = start
    st.session_state.goal = goal
    st.session_state.graph = build_graph(maze)

maze = st.session_state.maze
start = st.session_state.start
goal = st.session_state.goal
graph = st.session_state.graph

# Display initial maze
placeholder = st.empty()
placeholder.code(render_maze(maze, pos=start), language=None)

# Solve button
if st.button("▶️ Start Solving"):
    if "BFS" in algo:
        solver = bfs_solver(graph, start, goal)
    elif "DFS" in algo:
        solver = dfs_solver(graph, start, goal)
    else:
        solver = greedy_solver(graph, start, goal)
    
    final_path_len = None
    for pos, visited, path in solver:
        placeholder.code(render_maze(maze, pos, visited, path), language=None)
        time.sleep(speed)
        if path:
            final_path_len = len(path) - 1
    
    if final_path_len is not None:
        st.success(f"🎉 Solved with {algo}!")
        st.markdown(f"**Final Path Length: {final_path_len} steps**")
        st.balloons()
    else:
        st.error("No path found!")

st.caption("⬛ Wall | ⬜ Open | ▫️ Visited | 🟩 Solution Path | 🧍 Current Position")
st.markdown("**Tip:** Generate a few mazes, then compare all three algorithms — DFS will usually produce dramatically longer paths!")
