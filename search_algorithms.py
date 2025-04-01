def dfs(maze, start, goal):
    stack = [(start, [start])]
    visited = set()

    while stack:
        (x, y), path = stack.pop()
        if (x, y) == goal:
            return path
        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Down, Right, Up, Left
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < len(maze[0])
                and 0 <= ny < len(maze)
                and maze[ny][nx] == 0
                and (nx, ny) not in visited
            ):
                stack.append(((nx, ny), path + [(nx, ny)]))
    return None
