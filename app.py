import streamlit as st
import random
import numpy as np
from collections import deque

st.set_page_config(page_title="Smart Maze Solver", layout="centered")
st.title("🏰 Maze Solver with Search Algorithms")
st.markdown("Choose an algorithm, LOCK the maze, and compare results!")

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

# ==================== الخوارزميات المُصححة ====================
def solve_algorithm(maze, start, goal, algo):
    steps = []
    
    if algo == "BFS":
        # BFS: يضمن أقصر مسار، visited عادي
        queue = deque([[start]])
        visited = set([start])
        steps.append(([start], visited.copy(), start))
        
        while queue:
            path = queue.popleft()
            current = path[-1]
            
            steps.append((path[:], visited.copy(), current))
            if current == goal:
                return steps
                
            for neighbor in get_neighbors(maze, current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
    
    elif algo == "DFS":
        # DFS: يروح عميق، ما يزورش نفس الخلية مرتين
        def dfs_recursive(current_path, visited):
            current = current_path[-1]
            steps.append((current_path[:], visited.copy(), current))
            
            if current == goal:
                return True
                
            for neighbor in get_neighbors(maze, current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    if dfs_recursive(current_path + [neighbor], visited.copy()):
                        return True
                    visited.remove(neighbor)  # Backtrack
            return False
        
        visited = set([start])
        dfs_recursive([start], visited)
    
    elif algo == "Greedy":
        # Greedy: يختار أقرب للهدف، بس مش مضمون
        def heuristic(pos):
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
        open_list = [[start]]
        visited = set([start])
        steps.append(([start], visited.copy(), start))
        
        while open_list:
            # أصغر heuristic
            open_list.sort(key=lambda p: heuristic(p[-1]))
            path = open_list.pop(0)
            current = path[-1]
            
            steps.append((path[:], visited.copy(), current))
            if current == goal:
                return steps
            
            for neighbor in get_neighbors(maze, current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    open_list.append(path + [neighbor])
    
    return steps

# UI
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### ⚙️ Settings")
    algorithm = st.selectbox(
        "Choose Algorithm",
        ["BFS (Guaranteed Shortest Path)", "DFS (Depth First Search)", "Greedy Best-First"]
    )
    algo_key = algorithm.split()[0]

with col2:
    # Initialize
    if 'maze' not in st.session_state:
        st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze(12, 10)
        st.session_state.locked_maze = None

    # Maze control buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔒 Lock Current Maze", use_container_width=True):
            st.session_state.locked_maze = (
                st.session_state.maze.copy(),
                st.session_state.start,
                st.session_state.goal
            )
            st.rerun()
    
    with col_btn2:
        if st.button("🔄 New Maze", use_container_width=True):
            if st.session_state.get('locked_maze') is None:
                st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze(12, 10)
                st.session_state.locked_maze = None
                st.rerun()
            else:
                st.error("🔒 Unlock first!")

    if st.session_state.get('locked_maze') is not None:
        if st.button("🔓 Unlock", use_container_width=True):
            st.session_state.locked_maze = None
            st.rerun()

    # Use locked maze or current
    if st.session_state.get('locked_maze') is not None:
        maze, start, goal = st.session_state.locked_maze
        st.success("🔒 Locked maze active!")
    else:
        maze, start, goal = st.session_state.maze, st.session_state.start, st.session_state.goal

    # Solve for this algorithm
    steps_key = f"steps_{algo_key}"
    if steps_key not in st.session_state:
        with st.spinner(f"Running {algorithm}..."):
            st.session_state[steps_key] = solve_algorithm(maze, start, goal, algo_key)

    steps = st.session_state[steps_key]
    step_idx = st.slider("Step", 0, len(steps)-1, 0, key=f"slider_{algo_key}")

    path, visited, current = steps[step_idx]
    
    # Draw
    img = draw_maze(
        maze, start, goal,
        path if current == goal else None,
        visited,
        current if current != goal else None
    )
    st.image(img, use_column_width=True)

    # Results
    if current == goal:
        path_length = len(path) - 1
        st.balloons()
        st.markdown(f"""
        <div style='background-color: #d4edda; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745;'>
            <h3>🎉 {algorithm} Success!</h3>
            <p><strong>Path length:</strong> <span style='font-size: 24px; color: #28a745;'>{path_length} steps</span></p>
            <p><strong>Cells visited:</strong> {len(visited)}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Step {step_idx+1}/{len(steps)} | Position: {current}")

st.markdown("---")
st.markdown("""
| Algorithm | Expected Path Length | Behavior |
|-----------|---------------------|----------|
| 🟢 **BFS** | **Shortest** (25-35) | Explores level by level |
| 🔵 **DFS** | **Long** (50-150+) | Goes deep first |
| 🟡 **Greedy** | **Medium** (30-50) | Greedy heuristic |
""")
