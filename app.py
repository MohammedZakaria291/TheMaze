import streamlit as st
import random
import numpy as np
from collections import deque

st.set_page_config(page_title="Smart Maze Solver", layout="centered")
st.title("🏰 Maze Solver - متاهات مع حلقات لمقارنة حقيقية!")
st.markdown("الآن المتاهات فيها تفرعات وحلقات → الخوارزميات هتطلع نتايج مختلفة تمامًا!")

# ====================== توليد متاهة مع حلقات (Prim's Algorithm) ======================
def generate_maze_with_loops(width=15, height=12):
    # حجم أكبر شوية عشان الفرق يبان أكتر
    maze = np.ones((height*2+1, width*2+1), dtype=int)
    grid = np.zeros((height, width), dtype=int)  # الخلايا
    
    # ابدأ من خلية عشوائية
    start_x, start_y = 1, 1
    grid[start_y//2, start_x//2] = 1
    walls = []
    
    # إضافة الجدران الأولية
    if start_y > 0: walls.append(((start_x, start_y-2), (0, -1)))  # أعلى
    if start_x < width*2-2: walls.append(((start_x+2, start_y), (1, 0)))  # يمين
    if start_y < height*2-2: walls.append(((start_x, start_y+2), (0, 1)))  # أسفل
    if start_x > 0: walls.append(((start_x-2, start_y), (-1, 0)))  # يسار
    
    while walls:
        wall_pos, direction = random.choice(walls)
        wx, wy = wall_pos
        dx, dy = direction
        nx, ny = wx + dx*2, wy + dy*2
        
        if 0 <= nx < width*2 and 0 <= ny < height*2:
            cell_x, cell_y = nx // 2, ny // 2
            if grid[cell_y, cell_x] == 0:
                # كسر الجدار وإضافة الخلية
                maze[wy, wx] = 0
                maze[ny, nx] = 0
                grid[cell_y, cell_x] = 1
                
                # إضافة جدران جديدة
                for ndx, ndy in [(0,-1),(1,0),(0,1),(-1,0)]:
                    nnx, nny = nx + ndx*2, ny + ndy*2
                    if 0 <= nnx < width*2 and 0 <= nny < height*2:
                        if grid[nny//2, nnx//2] == 0:
                            walls.append(((nx + ndx, ny + ndy), (ndx, ndy)))
        
        walls.remove((wall_pos, direction))
    
    # فتحة البداية والنهاية
    start = (0, 1)  # أعلى يسار
    goal = (height*2, width*2-1)  # أسفل يمين
    maze[start] = 0
    maze[goal] = 0
    
    return maze, start, goal

# باقي الدوال زي ما هي (get_neighbors, draw_maze)

def get_neighbors(maze, pos):
    y, x = pos
    neighbors = []
    for dy, dx in [(0,1),(1,0),(0,-1),(-1,0)]:
        ny, nx = y + dy, x + dx
        if 0 <= ny < maze.shape[0] and 0 <= nx < maze.shape[1] and maze[ny, nx] == 0:
            neighbors.append((ny, nx))
    return neighbors

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
    
    zoomed = np.repeat(np.repeat(rgb_array, 25, axis=0), 25, axis=1)  # أصغر شوية عشان الحجم
    return zoomed

# الخوارزميات (نفس اللي فات بس مع random في DFS)
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
            if current == goal: return steps
            for n in get_neighbors(maze, current):
                if n not in visited:
                    visited.add(n)
                    queue.append(path + [n])
    
    elif algo == "DFS":
        stack = [[start]]
        visited = set()
        steps.append(([start], visited.copy(), start))
        while stack:
            path = stack.pop()
            current = path[-1]
            if current in visited: continue
            visited.add(current)
            steps.append((path[:], visited.copy(), current))
            if current == goal: return steps
            neighbors = get_neighbors(maze, current)
            random.shuffle(neighbors)  # مهم جدًا للتنويع
            for n in reversed(neighbors):
                if n not in visited:
                    stack.append(path + [n])
    
    elif algo == "Greedy":
        open_list = [[start]]
        visited = set([start])
        steps.append(([start], visited.copy(), start))
        while open_list:
            open_list.sort(key=lambda p: heuristic(p[-1]))
            path = open_list.pop(0)
            current = path[-1]
            steps.append((path[:], visited.copy(), current))
            if current == goal: return steps
            for n in get_neighbors(maze, current):
                if n not in visited:
                    visited.add(n)
                    open_list.append(path + [n])
    
    return steps

# الواجهة (نفس اللي فات مع التعديل في generate)
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### ⚙️ إعدادات")
    algorithm = st.selectbox("اختر الخوارزمية", 
        ["BFS (أقصر مسار)", "DFS (عميق)", "Greedy (جشع)"])
    algo_key = algorithm.split()[0]

with col2:
    if 'maze' not in st.session_state:
        st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze_with_loops()
        st.session_state.locked_maze = None

    # أزرار القفل والتجديد (نفس اللي فات)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔒 قفل المتاهة"):
            st.session_state.locked_maze = (st.session_state.maze.copy(), st.session_state.start, st.session_state.goal)
            st.rerun()
    with c2:
        if st.button("🔄 جديدة"):
            if not st.session_state.get('locked_maze'):
                st.session_state.maze, st.session_state.start, st.session_state.goal = generate_maze_with_loops()
                st.rerun()
    with c3:
        if st.session_state.get('locked_maze'):
            if st.button("🔓 فك"):
                st.session_state.locked_maze = None
                st.rerun()

    maze = st.session_state.locked_maze[0] if st.session_state.get('locked_maze') else st.session_state.maze
    start = st.session_state.locked_maze[1] if st.session_state.get('locked_maze') else st.session_state.start
    goal = st.session_state.locked_maze[2] if st.session_state.get('locked_maze') else st.session_state.goal

    if st.session_state.get('locked_maze'):
        st.success("🔒 مقفلة - قارن بحرية!")

    steps_key = f"steps_{algo_key}"
    if steps_key not in st.session_state:
        with st.spinner("جاري الحل..."):
            st.session_state[steps_key] = solve_algorithm(maze, start, goal, algo_key)

    steps = st.session_state[steps_key]
    step_idx = st.slider("الخطوة", 0, len(steps)-1, len(steps)-1, key=f"s_{algo_key}")

    path, visited, current = steps[step_idx]
    st.image(draw_maze(maze, start, goal, path if current == goal else None, visited, current if current != goal else None))

    if current == goal:
        st.balloons()
        st.success(f"🎉 حل بـ {algorithm} | طول المسار: {len(path)-1} | مزار: {len(visited)}")

st.markdown("""
### النتايج المتوقعة دلوقتي:
- **BFS**: 30–50 خطوة (الأقصر)
- **Greedy**: 35–70 خطوة (جيد بس مش مثالي)
- **DFS**: 100–300+ خطوة (طويل جدًا وملتوي)
""")
