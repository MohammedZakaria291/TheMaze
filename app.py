import streamlit as st
import random
import time
from collections import deque

# =====================================
# Generate Maze
# =====================================
def generate_maze(width=15, height=12):
    maze = [[1] * (width * 2 + 1) for _ in range(height * 2 + 1)]

    def carve(x, y):
        maze[y][x] = 0
        dirs = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width * 2 and 1 <= ny < height * 2 and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)

    carve(1, 1)

    maze[1][0] = 0
    maze[height * 2 - 1][width * 2] = 0

    add_random_openings(maze, holes=60)

    return maze, (1, 0), (height * 2 - 1, width * 2)


def add_random_openings(maze, holes=60):
    h, w = len(maze), len(maze[0])
    for _ in range(holes):
        y = random.randint(1, h - 2)
        x = random.randint(1, w - 2)
        maze[y][x] = 0


# =====================================
# Build Graph
# =====================================
def build_graph(maze):
    graph = {}
    dirs = [(0,1), (1,0), (0,-1), (-1,0)]
    h, w = len(maze), len(maze[0])

    for y in range(h):
        for x in range(w):
            if maze[y][x] == 0:
                graph[(y,x)] = []
                for dy, dx in dirs:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and maze[ny][nx] == 0:
                        graph[(y,x)].append((ny,nx))
    return graph


# =====================================
# Heuristic
# =====================================
def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + random.randint(0, 3)


# =====================================
# Maze Renderer
# =====================================
def render_maze(maze, pos=None, visited=None, path=None):
    s = ""
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if pos and (y,x) == pos:
                s += "🧍"
            elif path and (y,x) in path:
                s += "🟩"
            elif visited and (y,x) in visited:
                s += "▫️"
            elif maze[y][x] == 1:
                s += "⬛"
            else:
                s += "⬜"
        s += "\n"
    return s


# =====================================
# Solvers (Generator style)
# =====================================
def bfs_solver(graph, start, goal):
    queue = deque([[start]])
    visited = set()

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node in visited:
            continue
        visited.add(node)

        yield node, visited, None

        if node == goal:
            yield node, visited, set(path)
            return

        for n in graph[node]:
            if n not in visited:
                queue.append(path + [n])


def dfs_solver(graph, start, goal):
    stack = [[start]]
    visited = set()

    while stack:
        path = stack.pop()
        node = path[-1]

        if node in visited:
            continue
        visited.add(node)

        yield node, visited, None

        if node == goal:
            yield node, visited, set(path)
            return

        for n in graph[node]:
            if n not in path:
                stack.append(path + [n])


def greedy_solver(graph, start, goal):
    queue = [[start]]
    visited = set()

    while queue:
        queue.sort(key=lambda p: manhattan(p[-1], goal))
        path = queue.pop(0)
        node = path[-1]

        if node in visited:
            continue
        visited.add(node)

        yield node, visited, None

        if node == goal:
            yield node, visited, set(path)
            return

        for n in graph[node]:
            if n not in path:
                queue.append(path + [n])


# =====================================
# Streamlit UI
# =====================================
st.set_page_config(page_title="Maze Solver AI", layout="centered")
st.title("🧠 Maze Solver Visualization")

algo = st.sidebar.selectbox(
    "Choose Algorithm",
    ["BFS (Optimal)", "DFS (Bad paths)", "Greedy (Heuristic)"]
)

speed = st.sidebar.slider("Animation Speed", 0.01, 0.5, 0.15)

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

placeholder = st.empty()

if st.button("▶ Solve"):
    if algo.startswith("BFS"):
        solver = bfs_solver(graph, start, goal)
    elif algo.startswith("DFS"):
        solver = dfs_solver(graph, start, goal)
    else:
        solver = greedy_solver(graph, start, goal)

    for pos, visited, path in solver:
        placeholder.text(render_maze(maze, pos, visited, path))
        time.sleep(speed)

st.caption("⬛ Wall | ⬜ Path | ▫️ Visited | 🟩 Final Path | 🧍 Player")
