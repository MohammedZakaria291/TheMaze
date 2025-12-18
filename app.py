import streamlit as st
import random
import time
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="حلال المتاهة الذكي", layout="centered")
st.title("🏰 لعبة المتاهة مع خوارزميات البحث")
st.markdown("اختر الخوارزمية وشوف إزاي بتحل المتاهة خطوة بخطوة!")

# توليد متاهة عشوائية
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

# بناء الجيران
def get_neighbors(maze, pos):
    y, x = pos
    neighbors = []
    for dy, dx in [(0,1),(1,0),(0,-1),(-1,0)]:
        ny, nx = y + dy, x + dx
        if 0 <= ny < maze.shape[0] and 0 <= nx < maze.shape[1] and maze[ny, nx] == 0:
            neighbors.append((ny, nx))
    return neighbors

# عرض المتاهة كصورة ملونة
def draw_maze(maze, path=None, visited=None, current=None):
    rgb_array = np.zeros((maze.shape[0], maze.shape[1], 3), dtype=np.uint8)
    
    # ألوان
    wall_color = [50, 50, 50]       # رمادي غامق للحوائط
    path_color = [240, 240, 240]   # أبيض فاتح للممرات
    visited_color = [100, 200, 255] # أزرق فاتح للمزار
    solution_color = [255, 255, 0]  # أصفر للمسار النهائي
    current_color = [255, 0, 0]     # أحمر للموقف الحالي
    start_color = [0, 255, 0]       # أخضر للبداية
    goal_color = [255, 100, 100]    # وردي للهدف
    
    rgb_array[maze == 1] = wall_color
    rgb_array[maze == 0] = path_color
    
    if visited:
        for pos in visited:
            y, x = pos
            rgb_array[y, x] = visited_color
    
    if path:
        for pos in path:
            y, x = pos
            rgb_array[y, x] = solution_color
    
    if current:
        y, x = current
        rgb_array[y, x] = current_color
    
    # تلوين البداية والهدف
    sy, sx = start
    gy, gx = goal
    rgb_array[sy, sx] = start_color
    rgb_array[gy, gx] = goal_color
    
    # تكبير الصورة عشان تبقى واضحة
    zoomed = np.repeat(np.repeat(rgb_array, 30, axis=0), 30, axis=1)
    return zoomed

# الخوارزميات
def bfs_solve(maze, start, goal):
    from collections import deque
    queue = deque([[start]])
    visited = set()
    steps = []
    
    while queue:
        path = queue.popleft()
        current = path[-1]
        
        if current in visited:
            continue
        visited.add(current)
        
        steps.append((path.copy(), visited.copy(), current))
        
        if current == goal:
            return steps
        
        for neighbor in get_neighbors(maze, current):
            if neighbor not in visited:
                queue.append(path + [neighbor])
    return steps

def dfs_solve(maze, start, goal):
    stack = [[start]]
    visited = set()
    steps = []
    
    while stack:
        path = stack.pop()
        current = path[-1]
        
        if current in visited:
            continue
        visited.add(current)
        
        steps.append((path.copy(), visited.copy(), current))
        
        if current == goal:
            return steps
        
        for neighbor in get_neighbors(maze, current):
            if neighbor not in path:
                stack.append(path + [neighbor])
    return steps

def greedy_solve(maze, start, goal):
    def heuristic(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    queue = [[start]]
    visited = set()
    steps = []
    
    while queue:
        queue.sort(key=lambda p: heuristic(p[-1]))
        path = queue.pop(0)
        current = path[-1]
        
        if current in visited:
            continue
        visited.add(current)
        
        steps.append((path.copy(), visited.copy(), current))
        
        if current == goal:
            return steps
        
        for neighbor in get_neighbors(maze, current):
            if neighbor not in path:
                queue.append(path + [neighbor])
    return steps

# الواجهة الرئيسية
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### إعدادات")
    algorithm = st.selectbox(
        "اختر الخوارزمية",
        ["BFS (أقصر مسار مضمون)", "DFS (عمق أولًا)", "Greedy Best-First"]
    )
    
    if st.button("🔄 توليد متاهة جديدة وحلها"):
        st.session_state.maze_generated = True
        st.session_state.steps = None

with col2:
    if 'maze_generated' not in st.session_state:
        st.session_state.maze_generated = True
    
    # توليد المتاهة
    maze, start, goal = generate_maze(12, 10)
    
    # حل حسب الاختيار
    if algorithm == "BFS (أقصر مسار مضمون)":
        steps = bfs_solve(maze, start, goal)
        algo_name = "BFS"
    elif algorithm == "DFS (عمق أولًا)":
        steps = dfs_solve(maze, start, goal)
        algo_name = "DFS"
    else:
        steps = greedy_solve(maze, start, goal)
        algo_name = "Greedy"
    
    placeholder = st.empty()
    status = st.empty()
    
    # عرض الأنيميشن
    with placeholder.container():
        for i, (path, visited, current) in enumerate(steps):
            img = draw_maze(maze, path if current == goal else None, visited, current if current != goal else None)
            st.image(img, use_column_width=True)
            
            if current == goal:
                status.success(f"🎉 تم الحل بـ {algo_name}! عدد الخطوات: {len(path)-1}")
                break
            else:
                status.info(f"خطوة {i+1} - زيارة: {current}")
            
            time.sleep(0.15)
            st.rerun()  # تحديث الصفحة للخطوة التالية

    if current != goal:
        status.error("لم يتم العثور على حل!")

st.markdown("---")
st.caption("متاهة عشوائية تتولد كل مرة • الأخضر = بداية • الوردي = هدف • الأحمر = الحالي • الأصفر = المسار النهائي")
