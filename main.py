import pygame
from maze_generator import generate_maze
from search_algorithms import dfs
from visualization import draw_maze


def main():
    pygame.init()
    width, height = 21, 21  # Odd numbers for walls
    screen = pygame.display.set_mode((width * 20, height * 20))
    pygame.display.set_caption("Maze Solver")

    # Generate maze
    maze = generate_maze(width, height)
    start, goal = (0, 1), (width - 1, height - 2)  # Entrance and exit

    # Solve with DFS
    path = dfs(maze, start, goal)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_maze(screen, maze, path)

    pygame.quit()


if __name__ == "__main__":
    main()
