import streamlit as st
import random
import numpy as np

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
    start = (1, 0)
    goal = (height * 2 - 1, width * 2)
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
        from collections import deque
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
                if neighbor not in path:
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

# UI
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### Settings")
    algorithm = st.selectbox(
        "Choose Algorithm",
        ["BFS (Guaranteed Shortest Path)", "DFS (Depth First Search)", "Greedy Best-First"]
    )
    algo_key = algorithm.split()[0]
    
    if st.button("🔄 Generate New Maze"):
        st.session_state.clear()

with col2:
    # Generate or load maze
    if 'maze' not in st.session_state:
        st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze(12, 10)
        st.session_state.steps = None
    
    maze = st.session_state.maze
    start = st.session_state.start
    goal = st.session_state.goal
    
    # Solve if needed
    if st.session_state.steps is None:
        with st.spinner(f"Solving maze using {algorithm}..."):
            st.session_state.steps = solve_algorithm(maze, start, goal, algo_key)
    
    steps = st.session_state.steps
    
    # Step slider
    step_idx = st.slider("Control Solution Step", 0, len(steps) - 1, 0, step=1)
    
    path, visited, current = steps[step_idx]
    
    img = draw_maze(
        maze,
        start,
        goal,
        path if current == goal else None,
        visited,
        current if current != goal else None
    )
    
    st.image(img, use_column_width=True)
    
    if current == goal:
        st.success(f"🎉 Maze solved using {algorithm}! Path length: {len(path) - 1}")
    else:
        st.info(f"Step {step_idx + 1}/{len(steps)} - Current position: {current}")

st.markdown("---")
st.caption("🟢 Start • 🩷 Goal • 🔴 Current • 🔵 Visited • 🟡 Final Path • Move the slider to see each step!")
