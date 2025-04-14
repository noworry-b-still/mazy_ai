
# MAZY AI: AI Pathfinding Visualization

## Overview
MAZY AI is an interactive desktop application built with Python and Pygame that generates random mazes and visualizes how different AI search algorithms solve them. Users can watch algorithms race to find solutions or take control and navigate mazes manually. The application provides an engaging educational platform to understand pathfinding techniques in artificial intelligence.

## Features

### Core Features
- **Dynamic Maze Generation**: Creates random mazes using a spanning tree algorithm with adjustable dimensions (5×5 up to 50×50)
- **Multiple Pathfinding Algorithms**:
  - Depth-First Search (DFS)
  - Breadth-First Search (BFS)
  - Uniform-Cost Search (UCS)
  - A* Search with two heuristic options:
    - Standard A* (distance traveled + Manhattan distance to exit)
    - Pure heuristic-based A* (Manhattan distance to exit only)
  - Ant Colony Optimization (ACO) - A nature-inspired probabilistic technique
- **Algorithm Comparison**: Compare all algorithms' performance metrics:
  - Cells explored (efficiency of exploration)
  - Maximum memory usage (space complexity)
  - Path length (solution optimality)
  - Execution time (time complexity)
- **Manual Navigation**: Traverse the maze yourself using W/A/S/D keys or arrow keys
- **Visual Feedback**: Color-coded cells show:
  - Explored paths (blue)
  - Solution path (red)
  - Start/end points (green/red)
- **Adjustable Speed**: Control how quickly algorithms solve the maze

### User Interface
- **Fullscreen Support**: Maximizes your view of complex mazes
- **Responsive Design**: Adapts to different screen sizes
- **Intuitive Controls**: Easy-to-use buttons and dropdown menus
- **Dynamic Scrolling**: Navigate through large mazes with ease
- **Visual Performance Analysis**: Beautiful graphs and charts to compare algorithm efficiency

## Installation

### For Mac Users
1. Download the MAZY AI.app file
2. Drag it to your Applications folder
3. Double-click to run

### For Developers
1. Prerequisites:
   - Python 3.x
   - Pygame

2. Set up:
   ```bash
   # Clone repository
   git clone https://github.com/noworry-b-still/mazy_ai.git
   cd mazy_ai

   # Create a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install pygame
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## How to Use

### Starting a New Maze
- Launch the application
- Use the R: and C: dropdowns to select maze dimensions (Rows and Columns)
- Click "New Maze" to generate a fresh maze

### Watching Algorithms Solve
Click any algorithm button to watch it solve the current maze:
- **Depth-First Search** - Often finds a solution quickly but not necessarily the shortest
- **Breadth-First Search** - Guarantees the shortest path but explores more cells
- **Uniform-Cost Search** - Similar to BFS for uniform-cost mazes
- **A Search - 1*** - Balances path length and heuristic distance
- **A Search - 2*** - Relies purely on distance to exit
- **Ant Colony Opt.** - Uses virtual pheromones to find optimal paths over multiple iterations

### Comparing Algorithm Efficiency
- Click the "Compare Algorithms" button to run all algorithms on the current maze
- View comprehensive statistics including:
  - Number of cells explored by each algorithm
  - Maximum memory usage during execution
  - Final path length (optimality of solution)
  - Execution time for each algorithm
- Visualize the comparison with interactive bar charts
- See rankings of which algorithms perform best for different metrics

### Control the Visualization Speed
- Click "Slower" to reduce the solving speed
- Click "Faster" to increase the solving speed

### Manual Navigation
- Use W/A/S/D keys or arrow keys to move
- Explored paths turn blue
- When you reach the exit, the solution path is highlighted in red

### Interface Controls
- Toggle between fullscreen and windowed mode with the "Windowed" button
- Exit the application with the "Exit" button or press ESC

## Project Structure

- `main.py` - Entry point and main game loop
- `game.py` - Core game logic and algorithm management
- `maze.py` - Maze generation and pathfinding algorithms
- `config.py` - Application settings and constants
- `ui_components.py` - Visual elements and rendering functions
- `dropdown.py` - Custom dropdown menu implementation
- `algorithm_comparison.py` - Algorithm comparison and statistics visualization
- `stats.py` - Statistics collection and performance metrics
- `mazy_ai_logo.icns` - App Logo file for macOS
- `setup.py` - Setup file for generating macOS executable using py2app package
- `.gitignore` - Ignore the unnecessary file for the GitHub repo

## Development
This project is built with modular design principles, making it easy to extend with new algorithms or features. The codebase is structured to separate concerns between UI, game logic, and pathfinding algorithms.

## Copyright
© Dinesh Pandikona. All rights reserved 2025
