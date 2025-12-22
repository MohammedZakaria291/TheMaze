import streamlit as st
import random
import numpy as np
from collections import deque

st.set_page_config(page_title="Smart Maze Solver", layout="centered")
st.title("🏰 Maze Solver with Search Algorithms")
st.markdown("Choose an algorithm, generate a new maze, and control the solution step by step!")

# Generate Maze
def generate_maze(width=12, height=10):
    maze = np.ones((height * 2 + 1, width * 2 + 1), dtype=int)
   
    def carve(x, y):
        maze[y, x] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width * 2 and 1 <= ny < height * 2 and maze[ny, nx] == 1:
                maze[y + dy//2, x + dx//2] = 0
                carve(nx, ny)
   
    carve(1, 1)
    start = (1, 0)  # Top entrance
    goal = (height * 2 - 1, width * 2)  # Bottom-right exit
    maze[start] = 0
    maze[goal] = 0
    return maze, start, goal

# Get neighbors
def get_neighbors(maze, pos):
    y, x = pos
    neighbors = []
    for dy, dx in [(0,1),(1,0),(0,-1),(-1,0)]:
        ny, nx = y + dy, x + dx
        if 0 <= ny < maze.shape[0] and 0 <= nx < maze.shape[1] and maze[ny, nx] == 0:
            neighbors.append((ny, nx))
    return neighbors

# Draw maze
def draw_maze(maze, start, goal, path=None, visited=None, current=None):
    rgb_array = np.zeros((maze.shape[0], maze.shape[1], 3), dtype=np.uint8)
   
    wall_color = [50, 50, 50]
    path_color = [240, 240, 240]
    visited_color = [100, 200, 255]
    solution_color = [255, 255, 0]
    current_color = [255, 0, 0]
    start_color = [0, 255, 0]
    goal_color = [255, 100, 100]
   
    rgb_array[maze == 1] = wall_color
    rgb_array[maze == 0] = path_color
   
    if visited:
        for pos in visited:
            rgb_array[pos] = visited_color
   
    if path:
        for pos in path:
            rgb_array[pos] = solution_color
   
    if current and current != goal:
        rgb_array[current] = current_color
   
    rgb_array[start] = start_color
    rgb_array[goal] = goal_color
   
    zoomed = np.repeat(np.repeat(rgb_array, 30, axis=0), 30, axis=1)
    return zoomed

# Algorithms (return all steps)
def solve_algorithm(maze, start, goal, algo):
    steps = []
    if algo == "BFS":
        queue = deque([[start]])
        visited = set()
        while queue:
            path = queue.popleft()
            current = path[-1]
            if current in visited:
                continue
            visited.add(current)
            steps.append((path[:], visited.copy(), current))
            if current == goal:
                break
            for neighbor in get_neighbors(maze, current):
                if neighbor not in visited:
                    queue.append(path + [neighbor])
   
    elif algo == "DFS":
        stack = [[start]]
        visited = set()
        while stack:
            path = stack.pop()
            current = path[-1]
            if current in visited:
                continue
            visited.add(current)
            steps.append((path[:], visited.copy(), current))
            if current == goal:
                break
            for neighbor in get_neighbors(maze, current):
                if neighbor not in path:  # Avoid immediate backtracking
                    stack.append(path + [neighbor])
   
    elif algo == "Greedy":
        def heuristic(pos):
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
       
        queue = [[start]]
        visited = set()
        while queue:
            queue.sort(key=lambda p: heuristic(p[-1]))
            path = queue.pop(0)
            current = path[-1]
            if current in visited:
                continue
            visited.add(current)
            steps.append((path[:], visited.copy(), current))
            if current == goal:
                break
            for neighbor in get_neighbors(maze, current):
                if neighbor not in path:
                    queue.append(path + [neighbor])
   
    return steps

# ==================== UI ====================
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### Settings")
    algorithm = st.selectbox(
        "Choose Algorithm",
        ["BFS (Guaranteed Shortest Path)", "DFS (Depth First Search)", "Greedy Best-First"]
    )
    algo_key = algorithm.split()[0]

with col2:
    # Initialize session state
    if 'maze' not in st.session_state:
        st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze(12, 10)
        st.session_state.locked_maze = None
        st.session_state.current_algo = None

    # Buttons for maze control
    col_lock, col_new = st.columns([1, 1])
    
    with col_lock:
        if st.button("🔒 Lock Current Maze"):
            st.session_state.locked_maze = (
                st.session_state.maze.copy(),
                st.session_state.start,
                st.session_state.goal
            )
            st.success("✅ Maze locked! Now you can safely switch algorithms.")

    with col_new:
        if st.button("🔄 Generate New Maze"):
            if st.session_state.get('locked_maze') is None:
                new_maze, new_start, new_goal = generate_maze(12, 10)
                st.session_state.maze = new_maze
                st.session_state.start = new_start
                st.session_state.goal = new_goal
                st.session_state.current_algo = None  # Force re-solve
                st.rerun()
            else:
                st.warning("🔒 Maze is locked! Unlock first to generate a new one.")

    # Unlock button
    if st.session_state.get('locked_maze') is not None:
        if st.button("🔓 Unlock Maze"):
            st.session_state.locked_maze = None
            st.info("🔓 Maze unlocked. You can now generate new mazes.")

    # Determine which maze to use
    if st.session_state.get('locked_maze') is not None:
        maze = st.session_state.locked_maze[0]
        start = st.session_state.locked_maze[1]
        goal = st.session_state.locked_maze[2]
        st.info("🔒 Using locked maze")
    else:
        maze = st.session_state.maze
        start = st.session_state.start
        goal = st.session_state.goal

    # Solve with current algorithm
    steps_key = f"steps_{algo_key}"
    slider_key = f"slider_{algo_key}"

    if (st.session_state.get(steps_key) is None or 
        st.session_state.get('current_algo') != algo_key):
        with st.spinner(f"Solving with {algorithm}..."):
            st.session_state[steps_key] = solve_algorithm(maze, start, goal, algo_key)
            st.session_state.current_algo = algo_key

    steps = st.session_state[steps_key]

    # Step slider
    step_idx = st.slider(
        "Control Solution Step",
        0, len(steps) - 1, 0,
        key=slider_key
    )

    path, visited, current = steps[step_idx]

    img = draw_maze(
        maze, start, goal,
        path if current == goal else None,
        visited,
        current if current != goal else None
    )

    st.image(img, use_column_width=True)

    if current == goal:
        st.success(f"🎉 Solved with {algorithm}! Path length: {len(path) - 1} steps")
    else:
        st.info(f"Step {step_idx + 1}/{len(steps)} → Current: {current}")

st.markdown("---")
st.caption("🟢 Start • 🩷 Goal • 🔴 Current • 🔵 Visited • 🟡 Final Path • Use Lock to compare algorithms on the same maze!")
