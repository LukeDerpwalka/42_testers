import random
import os
from collections import deque

# 1. Generate Random Map
def generate_random_map(width, height):
    map_data = [['1' for _ in range(width)] for _ in range(height)]
    for i in range(1, height-1):
        for j in range(1, width-1):
            map_data[i][j] = random.choice(['0', '1', 'C'])
    
    start_i, start_j = random.randint(1, height-2), random.randint(1, width-2)
    map_data[start_i][start_j] = 'P'
    
    exit_i, exit_j = random.randint(1, height-2), random.randint(1, width-2)
    while (exit_i, exit_j) == (start_i, start_j):
        exit_i, exit_j = random.randint(1, height-2), random.randint(1, width-2)
    map_data[exit_i][exit_j] = 'E'
    
    collect_i, collect_j = random.randint(1, height-2), random.randint(1, width-2)
    while (collect_i, collect_j) in [(start_i, start_j), (exit_i, exit_j)]:
        collect_i, collect_j = random.randint(1, height-2), random.randint(1, width-2)
    map_data[collect_i][collect_j] = 'C'

    return [''.join(row) for row in map_data]


# 2. Validate Map
def flood_fill(map_data, start):
    visited = set()
    queue = deque([start])
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    while queue:
        i, j = queue.popleft()
        if (i, j) in visited:
            continue
        visited.add((i, j))

        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < len(map_data) and 0 <= nj < len(map_data[0]) and map_data[ni][nj] != '1':
                queue.append((ni, nj))
    return visited

def validate_map(map_data):
    # Check walls
    if not all(cell == '1' for row in map_data for cell in [row[0], row[-1]]):
        return False, "Map is not surrounded by walls."
    if not all(cell == '1' for cell in map_data[0] + map_data[-1]):
        return False, "Map is not surrounded by walls."
    
    # Check for required elements
    if sum(row.count('P') for row in map_data) != 1 or sum(row.count('E') for row in map_data) != 1 or sum(row.count('C') for row in map_data) < 1:
        return False, "Map missing required elements."
    
    # Flood fill to check paths
    start_i, start_j = next((i, j) for i, row in enumerate(map_data) for j, cell in enumerate(row) if cell == 'P')
    visited = flood_fill(map_data, (start_i, start_j))

    all_collectibles_and_exit = [(i, j) for i, row in enumerate(map_data) for j, cell in enumerate(row) if cell in ['C', 'E']]
    for pos in all_collectibles_and_exit:
        if pos not in visited:
            return False, f"No path to {map_data[pos[0]][pos[1]]} at ({pos[0]}, {pos[1]})"
    return True, "Map is valid."

# 3. Execute so_long and Check
def execute_so_long(map_data):
    with open("temp.ber", "w") as f:
        for row in map_data:
            f.write(row + "\n")
    result = os.system('./so_long temp.ber')
    os.remove('temp.ber')
    return result

def main():
    map_data = generate_random_map(10, 10)
    print("\nGenerated Map:")
    for row in map_data:
        print(row)

    valid, reason = validate_map(map_data)
    print(f"\nValidation Result: {reason}")

    result = execute_so_long(map_data)
    print(f"\n./so_long Execution Result: {'Success' if result == 0 else 'Failed'}")

if __name__ == "__main__":
    main()
