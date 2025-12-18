import streamlit as st
import random
import numpy as np
import time

st.set_page_config(page_title="حلال المتاهة الذكي", layout="centered")
st.title("🏰 لعبة المتاهة مع خوارزميات البحث")
st.markdown("اختر الخوارزمية، اضغط تشغيل، واستمتع بالحل التلقائي خطوة بخطوة!")

# توليد متاهة
def generate_maze(width=12, height=10):
    maze = np.ones((height * 2 + 1, width * 2 + 1), dtype=int)
    def carve(x, y):
        maze[y, x] = 0
        dirs = [(0,2),(2,0),(0,-2),(-2,0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width*2 and 1 <= ny < height*2 and maze[ny, nx] == 1:
                maze[y + dy//2, x + dx//2] = 0
                carve(nx, ny)
    carve(1, 1)
    start = (1, 0)
    goal = (height*2 - 1, width*2)
    maze[start] = maze[goal] = 0
    return maze, start, goal

# جيران
def get_neighbors(maze, pos):
    y, x = pos
    dirs = [(0,1),(1,0),(0,-1),(-1,0)]
    return [(y+dy, x+dx) for dy, dx in dirs 
            if 0 <= y+dy < maze.shape[0] and 0 <= x+dx < maze.shape[1] and maze[y+dy, x+dx] == 0]

# رسم المتاهة
def draw_maze(maze, start, goal, path=None, visited=None, current=None):
    rgb = np.zeros((maze.shape[0], maze.shape[1], 3), dtype=np.uint8)
    rgb[maze == 1] = [50, 50, 50]      # حوائط
    rgb[maze == 0] = [240, 240, 240]   # ممرات
    
    if visited:
        for pos in visited:
            rgb[pos] = [100, 200, 255]     # مزار
    
    if path:
        for pos in path:
            rgb[pos] = [255, 255, 0]       # المسار النهائي
    
    if current and current != goal:
        rgb[current] = [255, 0, 0]         # الحالي
    
    rgb[start] = [0, 255, 0]               # بداية
    rgb[goal] = [255, 100, 100]            # هدف
    
    zoomed = np.repeat(np.repeat(rgb, 30, axis=0), 30, axis=1)
    return zoomed

# حل وتخزين الخطوات
def solve_algorithm(maze, start, goal, algo):
    steps = []
    if algo == "BFS":
        from collections import deque
        queue = deque([[start]])
        visited = set([start])
        while queue:
            path = queue.popleft()
            current = path[-1]
            steps.append((path[:], visited.copy(), current))
            if current == goal: return steps
            for neigh in get_neighbors(maze, current):
                if neigh not in visited:
                    visited.add(neigh)
                    queue.append(path + [neigh])
    
    elif algo == "DFS":
        stack = [[start]]
        visited = set([start])
        while stack:
            path = stack.pop()
            current = path[-1]
            steps.append((path[:], visited.copy(), current))
            if current == goal: return steps
            for neigh in get_neighbors(maze, current):
                if neigh not in path:
                    stack.append(path + [neigh])
    
    elif algo == "Greedy":
        def h(p): return abs(p[0]-goal[0]) + abs(p[1]-goal[1])
        queue = [[start]]
        visited = set([start])
        while queue:
            queue.sort(key=lambda p: h(p[-1]))
            path = queue.pop(0)
            current = path[-1]
            steps.append((path[:], visited.copy(), current))
            if current == goal: return steps
            for neigh in get_neighbors(maze, current):
                if neigh not in path:
                    queue.append(path + [neigh])
    return steps

# الواجهة
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### الإعدادات")
    algorithm = st.selectbox("اختر الخوارزمية", 
                             ["BFS (أقصر مسار مضمون)", "DFS (عمق أولًا)", "Greedy Best-First"])
    algo_key = algorithm.split()[0]
    
    if st.button("🔄 توليد متاهة جديدة"):
        st.session_state.clear()
    
    st.markdown("---")
    if st.button("▶️ تشغيل الحل تلقائيًا"):
        st.session_state.playing = True
        st.session_state.step_idx = 0

with col2:
    # توليد المتاهة
    if 'maze' not in st.session_state:
        maze, start, goal = generate_maze(12, 10)
        st.session_state.maze = maze
        st.session_state.start = start
        st.session_state.goal = goal
        st.session_state.steps = None
        st.session_state.playing = False

    maze = st.session_state.maze
    start = st.session_state.start
    goal = st.session_state.goal

    # حل المتاهة مرة واحدة
    if st.session_state.steps is None:
        with st.spinner(f"جاري حساب الحل بـ {algorithm}..."):
            st.session_state.steps = solve_algorithm(maze, start, goal, algo_key)

    steps = st.session_state.steps
    placeholder = st.empty()
    status = st.empty()

    # التشغيل التلقائي
    if st.session_state.get('playing', False):
        if st.session_state.step_idx < len(steps):
            path, visited, current = steps[st.session_state.step_idx]
            
            img = draw_maze(maze, start, goal, path if current == goal else None, visited, current if current != goal else None)
            placeholder.image(img, use_column_width=True)
            
            if current == goal:
                status.success(f"🎉 تم الحل بـ {algorithm}! عدد الخطوات: {len(path)-1}")
                st.session_state.playing = False
            else:
                status.info(f"خطوة {st.session_state.step_idx + 1}/{len(steps)} - زيارة: {current}")
                
                time.sleep(0.15)  # سرعة الأنيميشن (غيرها لو عايز أسرع/أبطأ)
                st.session_state.step_idx += 1
                st.rerun()
        else:
            st.session_state.playing = False
    else:
        # عرض المتاهة الأولية فقط لو مش شغال
        img = draw_maze(maze, start, goal)
        placeholder.image(img, use_column_width=True)
        status.info("اضغط 'تشغيل الحل تلقائيًا' عشان تبدأ الأنيميشن!")

st.markdown("---")
st.caption("🟢 بداية • 🩷 هدف • 🔴 الحالي • 🔵 المزار • 🟡 المسار النهائي • اضغط تشغيل واستمتع!")
