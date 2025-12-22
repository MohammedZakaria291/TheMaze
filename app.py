import streamlit as st
import random
import time
from collections import deque

# =====================================
# Generate Maze with Loops
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
    maze[1][0] = 0  # Entrance
    maze[height * 2 - 1][width * 2] = 0  # Exit
    
    # أهم جزء: إضافة فتحات عشوائية لخلق حلقات ومسارات متعددة
    add_random_openings(maze, holes=60)
    
    return maze, (1, 0), (height * 2 - 1, width * 2)

def add_random_openings(maze, holes=60):
    h, w = len(maze), len(maze[0])
    for _ in range(holes):
        y = random.randint(1, h - 2)
        x = random.randint(1, w - 2)
        if maze[y][x] == 1:  # فقط جدران
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
# Heuristic (مع random لتنويع Greedy)
# =====================================
def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + random.randint(0, 4)

# =====================================
# Maze Renderer (Text-based)
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
# Solvers (Generator - خطوة بخطوة)
# =====================================
def bfs_solver(graph, start, goal):
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
        
        # ترتيب عشوائي للجيران عشان DFS يسلك طرق مختلفة كل مرة
        neighbors = graph[node][:]
        random.shuffle(neighbors)
        
        for neighbor in neighbors:
            if neighbor not in visited:
                stack.append(path + [neighbor])

def greedy_solver(graph, start, goal):
    open_list = [[start]]
    visited = set([start])
    yield start, visited.copy(), None
    
    while open_list:
        # ترتيب حسب الـ heuristic
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
# Streamlit UI
# =====================================
st.set_page_config(page_title="Maze Solver AI", layout="centered")
st.title("🧠 Maze Solver Visualization - مقارنة حقيقية!")

algo = st.sidebar.selectbox(
    "اختر الخوارزمية",
    ["BFS (أقصر مسار مضمون)", "DFS (مسار طويل ملتوي)", "Greedy (جشع - متوسط)"]
)

speed = st.sidebar.slider("سرعة الأنيميشن (ثواني)", 0.01, 0.5, 0.1)

if st.sidebar.button("🔄 متاهة جديدة"):
    st.session_state.clear()

# Initialize
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
placeholder.code(render_maze(maze, start), language=None)

if st.button("▶️ ابدأ الحل"):
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
    
    if final_path_len:
        st.success(f"🎉 تم الحل بـ {algo}!")
        st.markdown(f"**طول المسار النهائي: {final_path_len} خطوة**")
        st.balloons()
    else:
        st.error("لم يتم العثور على مسار!")

st.caption("⬛ جدار | ⬜ ممر | ▫️ مزار | 🟩 المسار النهائي | 🧍 الموقع الحالي")
st.markdown("**نصيحة:** جرب متاهة جديدة عدة مرات، ثم قارن الثلاث خوارزميات → DFS هيطول جدًا! 🚀")
