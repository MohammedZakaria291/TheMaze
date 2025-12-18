import streamlit as st
import random
import numpy as np

st.set_page_config(page_title="حلال المتاهة الذكي", layout="centered")
st.title("🏰 لعبة المتاهة مع خوارزميات البحث")
st.markdown("اختر الخوارزمية، تولد متاهة جديدة، وتحكم في سرعة عرض الحل خطوة بخطوة!")

# توليد متاهة
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

# جيران
def get_neighbors(maze, pos):
    y, x = pos
    neighbors = []
    for dy, dx in [(0,1),(1,0),(0,-1),(-1,0)]:
        ny, nx = y + dy, x + dx
        if 0 <= ny < maze.shape[0] and 0 <= nx < maze.shape[1] and maze[ny, nx] == 0:
            neighbors.append((ny, nx))
    return neighbors

# رسم المتاهة
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

# الخوارزميات (ترجع كل الخطوات)
def solve_algorithm(maze, start, goal, algo):
    steps = []
    if algo == "BFS":
        from collections import deque
        queue = deque([[start]])
        visited = set()
        while queue:
            path = queue.popleft()
            current = path[-1]
            if current in visited: continue
            visited.add(current)
            steps.append((path[:], visited.copy(), current))
            if current == goal: break
            for neighbor in get_neighbors(maze, current):
                if neighbor not in visited:
                    queue.append(path + [neighbor])
    
    elif algo == "DFS":
        stack = [[start]]
        visited = set()
        while stack:
            path = stack.pop()
            current = path[-1]
            if current in visited: continue
            visited.add(current)
            steps.append((path[:], visited.copy(), current))
            if current == goal: break
            for neighbor in get_neighbors(maze, current):
                if neighbor not in path:
                    stack.append(path + [neighbor])
    
    elif algo == "Greedy":
        def heuristic(pos): return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        queue = [[start]]
        visited = set()
        while queue:
            queue.sort(key=lambda p: heuristic(p[-1]))
            path = queue.pop(0)
            current = path[-1]
            if current in visited: continue
            visited.add(current)
            steps.append((path[:], visited.copy(), current))
            if current == goal: break
            for neighbor in get_neighbors(maze, current):
                if neighbor not in path:
                    queue.append(path + [neighbor])
    
    return steps

# الواجهة
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### الإعدادات")
    algorithm = st.selectbox("اختر الخوارزمية", 
                             ["BFS (أقصر مسار مضمون)", "DFS (عمق أولًا)", "Greedy Best-First"])
    algo_key = algorithm.split()[0]
    
    if st.button("🔄 توليد متاهة جديدة"):
        st.session_state.clear()  # مسح الكاش

with col2:
    # توليد أو استرجاع المتاهة
    if 'maze' not in st.session_state:
        st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze(12, 10)
        st.session_state.steps = None
    
    maze = st.session_state.maze
    start = st.session_state.start
    goal = st.session_state.goal
    
    # حساب الخطوات إذا لزم الأمر
    if st.session_state.steps is None:
        with st.spinner(f"جاري حل المتاهة بـ {algorithm}..."):
            st.session_state.steps = solve_algorithm(maze, start, goal, algo_key)
    
    steps = st.session_state.steps
    
    # Slider للتحكم في الخطوات
    step_idx = st.slider("تحكم في خطوة الحل", 0, len(steps)-1, 0, step=1)
    
    path, visited, current = steps[step_idx]
    
    img = draw_maze(maze, start, goal, path if current == goal else None, visited, current if current != goal else None)
    st.image(img, use_column_width=True)
    
    if current == goal:
        st.success(f"🎉 تم الحل بـ {algorithm}! عدد الخطوات: {len(path)-1}")
    else:
        st.info(f"خطوة {step_idx + 1}/{len(steps)} - الموقف الحالي: {current}")

st.markdown("---")
st.caption("🟢 بداية • 🩷 هدف • 🔴 الحالي • 🔵 المزار • 🟡 المسار النهائي • حرك الـ slider عشان تشوف خطوة بخطوة!")
