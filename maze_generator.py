import random


def generate_maze(width, height):
    # 1 = wall, 0 = path
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve(x, y):
        maze[y][x] = 0  # Mark as path
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]  # Up, Right, Down, Left
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0  # Carve through wall
                carve(nx, ny)

    # Start at (1, 1) to keep outer walls intact
    carve(1, 1)
    maze[1][0] = 0  # Entrance
    maze[height - 2][width - 1] = 0  # Exit
    return maze


# Test it
if __name__ == "__main__":
    maze = generate_maze(21, 21)  # Odd dimensions for proper walls
    for row in maze:
        print("".join("#" if cell == 1 else " " for cell in row))
