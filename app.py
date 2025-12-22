import streamlit as st
import random
import numpy as np
from collections import deque

st.set_page_config(page_title="Smart Maze Solver", layout="centered")
st.title("🏰 Maze Solver - خوارزميات البحث المصححة")
st.markdown("قفل المتاهة ثم جرب الخوارزميات الثلاثة وقارن النتايج!")

# ====================== توليد المتاهة ======================
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

# ====================== الجيران ======================
def get_neighbors(maze, pos):
    y, x = pos
    neighbors = []
    for dy, dx in [(0,1),(1,0),(0,-1),(-1,0)]:
        ny, nx = y + dy, x + dx
        if 0 <= ny < maze.shape[0] and 0 <= nx < maze.shape[1] and maze[ny, nx] == 0:
            neighbors.append((ny, nx))
    return neighbors

# ====================== رسم المتاهة ======================
def draw_maze(maze, start, goal, path=None, visited=None, current=None):
    rgb_array = np.zeros((maze.shape[0], maze.shape[1], 3), dtype=np.uint8)
    
    wall_color = [40, 40, 40]
    path_color = [220, 220, 220]
    visited_color = [100, 180, 255]
    solution_color = [255, 255, 0]
    current_color = [255, 0, 0]
    start_color = [0, 255, 0]
    goal_color = [255, 80, 80]
    
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

# ====================== الخوارزميات المصححة ======================
def solve_algorithm(maze, start, goal, algo):
    steps = []
    heuristic = lambda pos: abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    if algo == "BFS":
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
        # DFS تكراري عشان نتجنب recursion limit
        stack = [[start]]
        visited = set()
        steps.append(([start], visited.copy(), start))
        
        while stack:
            path = stack.pop()
            current = path[-1]
            
            if current in visited:
                continue
                
            visited.add(current)
            steps.append((path[:], visited.copy(), current))
            
            if current == goal:
                return steps
                
            # نضيف الجيران بالترتيب العكسي عشان يسلك طرق مختلفة
            neighbors = get_neighbors(maze, current)
            random.shuffle(neighbors)  # اختياري عشان النتايج تختلف أكتر
            for neighbor in reversed(neighbors):  # reversed عشان يشبه recursive DFS
                if neighbor not in visited:
                    stack.append(path + [neighbor])
    
    elif algo == "Greedy":
        open_list = [[start]]  # قائمة المسارات المفتوحة
        visited = set([start])
        steps.append(([start], visited.copy(), start))
        
        while open_list:
            # نرتب حسب الـ heuristic (أقرب للهدف أولاً)
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

# ====================== الواجهة ======================
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### ⚙️ إعدادات")
    algorithm = st.selectbox(
        "اختر الخوارزمية",
        ["BFS (أقصر مسار مضمون)", "DFS (البحث العميق)", "Greedy Best-First (جشع)"]
    )
    algo_key = algorithm.split()[0]

with col2:
    if 'maze' not in st.session_state:
        st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze(12, 10)
        st.session_state.locked_maze = None

    # أزرار التحكم في المتاهة
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔒 قفل المتاهة", use_container_width=True):
            st.session_state.locked_maze = (
                st.session_state.maze.copy(),
                st.session_state.start,
                st.session_state.goal
            )
            st.success("تم قفل المتاهة! غير الخوارزمية بحرية")
            st.rerun()
    with c2:
        if st.button("🔄 متاهة جديدة", use_container_width=True):
            if st.session_state.get('locked_maze') is None:
                st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze(12, 10)
                st.rerun()
            else:
                st.warning("فك القفل أولاً!")
    with c3:
        if st.session_state.get('locked_maze'):
            if st.button("🔓 فك القفل", use_container_width=True):
                st.session_state.locked_maze = None
                st.info("تم فك القفل")
                st.rerun()

    # اختيار المتاهة
    if st.session_state.get('locked_maze'):
        maze, start, goal = st.session_state.locked_maze
        st.success("🔒 تستخدم متاهة مقفلة - مثالية للمقارنة!")
    else:
        maze, start, goal = st.session_state.maze, st.session_state.start, st.session_state.goal

    # حل المتاهة بالخوارزمية المختارة
    steps_key = f"steps_{algo_key}"
    if steps_key not in st.session_state:
        with st.spinner(f"جاري تشغيل {algorithm}..."):
            st.session_state[steps_key] = solve_algorithm(maze, start, goal, algo_key)

    steps = st.session_state[steps_key]
    step_idx = st.slider("الخطوة", 0, len(steps)-1, len(steps)-1, key=f"slider_{algo_key}")

    path, visited, current = steps[step_idx]

    # عرض المتاهة
    img = draw_maze(maze, start, goal,
                    path if current == goal else None,
                    visited,
                    current if current != goal else None)
    st.image(img, use_column_width=True)

    # النتيجة النهائية
    if current == goal:
        path_len = len(path) - 1
        visited_count = len(visited)
        st.success(f"🎉 تم الحل بـ {algorithm}")
        st.markdown(f"""
        **طول المسار:** **{path_len}** خطوة  
        **الخلايا المزارة:** {visited_count}  
        """)
    else:
        st.info(f"الخطوة {step_idx+1}/{len(steps)} | الموضع الحالي: {current}")

st.markdown("---")
st.markdown("""
### توقعات النتايج على نفس المتاهة:
- **BFS** → أقصر مسار (مثال: 25–35 خطوة)
- **Greedy** → مسار جيد لكن أطول شوية (مثال: 35–60 خطوة)
- **DFS** → مسار طويل جدًا (مثال: 80–200+ خطوة)
""")
