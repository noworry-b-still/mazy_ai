import pygame


def draw_maze(screen, maze, path=None):
    cell_size = 20
    width, height = len(maze[0]), len(maze)
    screen.fill((255, 255, 255))  # White background

    # Draw maze
    for y in range(height):
        for x in range(width):
            if maze[y][x] == 1:
                pygame.draw.rect(
                    screen,
                    (0, 0, 0),
                    (x * cell_size, y * cell_size, cell_size, cell_size),
                )

    # Draw path if provided
    if path:
        for x, y in path:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (x * cell_size, y * cell_size, cell_size, cell_size),
            )

    pygame.display.flip()
