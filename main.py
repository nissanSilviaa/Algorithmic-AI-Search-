#Author: Josh Celestino
import sys
from collections import deque
import heapq

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [['-' for _ in range(cols)] for _ in range(rows)]
        self.agent_position = None
        self.goal_positions = []

    def set_agent_position(self, position):
        self.agent_position = position

    def set_goal_positions(self, goals):
        self.goal_positions = goals

    def add_wall(self, x, y, width, height):
        for i in range(y, y + height):
            for j in range(x, x + width):
                if 0 <= i < self.rows and 0 <= j < self.cols:
                    self.grid[i][j] = '#'  # Set '#' for wall cells
                else:
                    print("Wall coordinates out of grid bounds.")

    def print_grid(self):
        for j in range(self.rows):
            for i in range(self.cols):
                if (i, j) == self.agent_position:
                    print('X', end=' ')  # Agent symbol
                elif (i, j) in self.goal_positions:
                    print('O', end=' ')  # Goal Symbol
                else:
                    print(self.grid[j][i], end=' ')  # Print cell
            print()

    def is_valid_move(self, position):
        x, y = position
        return 0 <= x < self.cols and 0 <= y < self.rows and self.grid[y][x] != '#'

    def test_command(self, actions):
        if not all(action in ['up', 'down', 'left', 'right'] for action in actions):
            print("Error: Invalid action. Valid actions are 'up', 'down', 'left', 'right'.")
            return

        x, y = self.agent_position
        for action in actions:
            if action == 'up':
                new_position = (x, y - 1)
            elif action == 'down':
                new_position = (x, y + 1)
            elif action == 'left':
                new_position = (x - 1, y)
            elif action == 'right':
                new_position = (x + 1, y)
            
            if self.is_valid_move(new_position):
                x, y = new_position
                self.agent_position = (x, y)
            else:
                print(f"Goal is unreachable")
                break
        
        print("Path taken:")
        self.print_grid()



def read_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        # Get Rows and Columns
        rows_cols_str = lines[0].strip().split(',')
        rows = int(rows_cols_str[0][1:])
        cols = int(rows_cols_str[1][:-1])

        # Get Agent Pos
        agent_position = lines[1][1:-2].strip('()')
        if agent_position:
            agent_position = tuple(map(int, agent_position.split(',')))
        else:
            print("Error: Agent position is missing or invalid.")
            sys.exit(1)

        goals_line = lines[2][1:-2].strip()
        if '|' in goals_line:  # Multiple goals checker
            goals = ''.join(goals_line.split())  
            goals = goals.replace('(', '').replace(')', '')  # get rid of brackets
            goal_positions = [tuple(map(int, goal.split(','))) for goal in goals.split('|')] #split data from each other using , and |
        else:
            goal_positions = [tuple(map(int, goals_line.replace('(', '').replace(')', '').split(',')))]

        walls = []
        for line in lines[3:]:
            wall_info = tuple(map(int, line.strip().replace('(', '').replace(')', '').split(',')[0:4]))
            walls.append(wall_info)

    return rows, cols, agent_position, goal_positions, walls

def dfs(grid, start, goals):
    stack = [(start, [])]
    visited = set()

    while stack:
        current, actions = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        if current in goals:
            return actions, len(visited)

        x, y = current
        neighbors = [(x, y-1), (x-1, y), (x, y+1), (x+1, y)]
        for neighbor in neighbors:
            if grid.is_valid_move(neighbor):
                stack.append((neighbor, actions + [['up', 'left', 'down', 'right'][neighbors.index(neighbor)]]))

    return None, len(visited)

def bfs(grid, start, goals):
    queue = deque([(start, [])])
    visited = set()

    while queue:
        current, actions = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        if current in goals:
            return actions, len(visited)

        x, y = current
        neighbors = [(x, y-1), (x-1, y), (x, y+1), (x+1, y)]
        for neighbor in neighbors:
            if grid.is_valid_move(neighbor):
                queue.append((neighbor, actions + [['up', 'left', 'down', 'right'][neighbors.index(neighbor)]]))

    return None, len(visited)

def gbfs(grid, start, goals):
    queue = []
    heapq.heapify(queue)
    heapq.heappush(queue, (heuristic(start, goals[0]), start, []))
    visited = set()

    while queue:
        _, current, actions = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)

        if current in goals:
            return actions, len(visited)

        x, y = current
        neighbors = [(x, y-1), (x-1, y), (x, y+1), (x+1, y)]
        for neighbor in neighbors:
            if grid.is_valid_move(neighbor):
                heapq.heappush(queue, (heuristic(neighbor, goals[0]), neighbor, actions + [['up', 'left', 'down', 'right'][neighbors.index(neighbor)]]))

    return None, len(visited)

def a_star(grid, start, goals):
    queue = []
    heapq.heapify(queue)
    heapq.heappush(queue, (heuristic(start, goals[0]) + 0, start, []))
    visited = set()

    while queue:
        _, current, actions = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)

        if current in goals:
            return actions, len(visited)

        x, y = current
        neighbors = [(x, y-1), (x-1, y), (x, y+1), (x+1, y)]
        for neighbor in neighbors:
            if grid.is_valid_move(neighbor):
                heapq.heappush(queue, (heuristic(neighbor, goals[0]) + len(actions) + 1, neighbor, actions + [['up', 'left', 'down', 'right'][neighbors.index(neighbor)]]))

    return None, len(visited)

def heuristic(current, goal):
    x1, y1 = current
    x2, y2 = goal
    return abs(x1 - x2) + abs(y1 - y2)



def print_actions(actions, filename, method, start, num_nodes):
    print(f"{filename} {method}")
    x, y = start

    #Calculating the end node of the agent
    for action in actions:
        if action == 'up':
            y -= 1
        elif action == 'down':
            y += 1
        elif action == 'left':
            x -= 1
        elif action == 'right':
            x += 1
        goal = x, y

    if goal:
        print(f"{goal} {num_nodes}")
        print("Actions taken:")
        print(actions)
        
    else:
        print(f"No goal is reachable; {num_nodes}")

def print_path(grid, start, actions):
    x, y = start

    #Calculating the end node of the agent
    for action in actions:
        if action == 'up':
            y -= 1
        elif action == 'down':
            y += 1
        elif action == 'left':
            x -= 1
        elif action == 'right':
            x += 1
        grid.grid[y][x] = ' '  # Replace '-' with empty space


    grid.set_agent_position((x, y))  # Set the agent position to the final position
    print("Path taken:")
    grid.print_grid()





if __name__ == "__main__":
    # command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python main.py <filename>.txt <command>")
        sys.exit(1)
    
    filename = sys.argv[1]
    command = sys.argv[2]

    # Read the file
    rows, cols, agent_position, goal_positions, walls = read_file(filename)

    # GRID STUFF
    grid = Grid(rows, cols)
    grid.set_agent_position(agent_position)
    grid.set_goal_positions(goal_positions)

    # Add walls
    for wall in walls:
        grid.add_wall(*wall)

    # Perform the specified command
    if command == "DFS":
        actions, num_nodes = dfs(grid, agent_position, goal_positions)
    elif command == "BFS":
        actions, num_nodes = bfs(grid, agent_position, goal_positions)
    elif command == "GBFS":
        actions, num_nodes = gbfs(grid, agent_position, goal_positions)
    elif command == "AS":
        actions, num_nodes = a_star(grid, agent_position, goal_positions)
    elif command == "test3":
        actions = ['right', 'right', 'right', 'right', 'right'] # Action TESTS
        grid.test_command(actions)
        sys.exit(0)  # Exit after executing the test command
    elif command == "test7":
        actions = ['down', 'right', 'right', 'right', 'right', 'right', 'right', 'right', 'right', 'right', 'right', 'right']  # Action TESTS
        grid.test_command(actions)
        sys.exit(0)  # Exit after executing the test command
    elif command == "overview":
        actions, num_nodes = ["None", 0]
        grid.print_grid()
    else:
        print("Invalid command. Please choose one of: DFS, BFS, GBFS, AS, test(test case ID)")
        sys.exit(1)
        
    if actions is None or actions == "None":
        print("No path found.")
    else:
        print_actions(actions, filename, command, agent_position, num_nodes)
        print_path(grid, agent_position, actions)

    #if actions is None:
    #    print_path(filename, command, "", num_nodes, [], grid)
    #else:
    #    print_path(filename, command, goal_positions[0], num_nodes, actions, grid)

