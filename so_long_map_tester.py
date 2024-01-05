import os
import subprocess
import shutil

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def clear_terminal():
	if os.name == 'posix':  # For Unix/Linux/Mac
		os.system('clear')
	elif os.name == 'nt':  # For Windows
		os.system('cls')

def color_text(text, color):
	return color + text + RESET

def is_valid_map(map_content):
	valid_cells = {'E', '1', '0', 'C', 'P'}
	
	# Check for rectangular shape
	row_lengths = set(len(line) for line in map_content)
	if len(row_lengths) != 1:
		return False, f"Map is not rectangular. Row lengths: {row_lengths}"

	# Check surrounded by walls
	if not all(cell == '1' for cell in map_content[0] + map_content[-1]) or not all(line[0] == '1' and line[-1] == '1' for line in map_content):
		return False, "Map is not surrounded by walls"

	start = None
	exit = None
	collectibles = []

	# Check for empty lines at the beginning
	empty_lines_beginning = 0
	for line in map_content:
		if line.strip() == "":
			empty_lines_beginning += 1
		else:
			break

	if empty_lines_beginning > 0:
		return False, f"Map has {empty_lines_beginning} empty line(s) at the beginning"

	# Check for empty lines in the middle
	empty_lines_middle = False
	for line in map_content[1:-1]:
		if line.strip() == "":
			empty_lines_middle = True
			break

	if empty_lines_middle:
		return False, "Map has empty line(s) in the middle"

	for i, line in enumerate(map_content):
		for j, cell in enumerate(line):
			if cell not in valid_cells:
				return False, f"Invalid cell '{cell}' found at position ({i}, {j})"
			
			if cell == 'P':
				if start is not None:
					return False, "More than one player ('P')"
				start = (i, j)
			elif cell == 'E':
				if exit is not None:
					return False, "More than one exit ('E')"
				exit = (i, j)
			elif cell == 'C':
				collectibles.append((i, j))

	if start is None:
		return False, "Map missing player's starting position"
	if exit is None:
		return False, "Map missing exit"
	if not collectibles:
		return False, "Map missing collectibles"

	# Check path from start to exit and collectibles
	visited = set()
	stack = [start]

	while stack:
		i, j = stack.pop()
		if (i, j) in visited:
			continue
		visited.add((i, j))

		for x, y in ((i+1, j), (i-1, j), (i, j+1), (i, j-1)):
			if 0 <= x < len(map_content) and 0 <= y < len(map_content[0]) and map_content[x][y] in ('0', 'C', 'E', 'P'):
				stack.append((x, y))

	if exit not in visited:
		return False, "No path from start to exit"
	for c in collectibles:
		if c not in visited:
			return False, f"No path from start to collectible at {c}"

	if map_content[-1].strip() == "":
		return False, "Empty line at the end of the map"

	return True, "Valid map"

print("This script tests the compiled ./so_long binary.")
print("Make sure to compile the ./so_long binary before running this script.")
print("It tests against all maps under the directory /maps.\n")
print("When your so_long opened the game, press 'ESC' to close it and continue with the next map.\n")
# Wait for user to press Enter
# Check if maps directory exists
if not os.path.exists('./maps'):
    print(color_text("No maps folder found", RED))
    exit()  # terminate the script

# Check if there are any .ber files in the maps directory
if not any(fname.endswith('.ber') for fname in os.listdir('./maps')):
    print(color_text("No maps in folder", RED))
    exit()  # terminate the script

# Check if so_long file exists
if not os.path.exists('./so_long'):
    print(color_text("No so_long found, maybe you forgot to make?", RED))
    exit()  # terminate the script
	
input("Press Enter to continue...")

clear_terminal()

root_dir = './maps'
discrepancies = []
ok_files = []
ok_results = []
discrepancy_results = []

check_dir = './check'
os.makedirs(check_dir, exist_ok=True)

if os.path.exists(check_dir):
    for filename in os.listdir(check_dir):
        if filename.endswith(".ber"):
            file_path = os.path.join(check_dir, filename)
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except OSError as e:
                print(f"Error removing {file_path}: {e}")
else:
    print(f"Directory {check_dir} does not exist.")

for dirpath, dirnames, filenames in os.walk(root_dir):
	for file in filenames:
		if file.endswith('.ber'):
			file_path = os.path.join(dirpath, file)
			
			# Validate using our custom function
			with open(file_path, 'r') as f:
				content = [line.strip() for line in f.readlines()]
				is_valid, message = is_valid_map(content)
				if is_valid:
					validator_status = GREEN + "OK" + RESET
					ok_files.append(file_path)
					ok_results.append((file_path, validator_status, validator_status))
				else:
					validator_status = RED + "Error" + RESET
					message = f"Invalid map: {message}"  # Add this line to update the message
			
			# Run ./so_long
			try:
				so_long_output = subprocess.check_output(['./so_long', file_path], stderr=subprocess.STDOUT, universal_newlines=True)
				so_long_status = GREEN + "OK" + RESET
			except subprocess.CalledProcessError as e:
				so_long_status = RED + "Error" + RESET
				so_long_output = e.output  # Capture the error output
			
			# Compare results
			if validator_status == so_long_status:
				combined_status = GREEN + "OK" + RESET
				if ok_results:
					ok_results[-1] = (file_path, validator_status, so_long_status)
			else:
				combined_status = YELLOW + "Warning (Discrepancies)" + RESET
				discrepancies.append((file_path, validator_status, so_long_status, so_long_output, combined_status))
				discrepancy_results.append((file_path, validator_status, so_long_status))

				# Copy the discrepancy map to the 'check' directory
				for file_path, validator_status, so_long_status, so_long_output, _ in discrepancies:
					dest_path = os.path.join(check_dir, os.path.basename(file_path))
					shutil.copy(file_path, dest_path)
					
					with open(dest_path, 'a') as copied_file:
						copied_file.write("\n\nValidator Output:\n")
						copied_file.write(message)
						copied_file.write("\n\nso_long Output:\n")
						copied_file.write(so_long_output)
				
			print(color_text(f" - Check Filename: {file_path} - Validator: {validator_status}, ./so_long: {so_long_status}", combined_status))
			print("Validator Output:\n", message)
			print("so_long Output:\n", so_long_output)

# Display OK Maps
clear_terminal()
print("-"*100)
print("\n")
print("\nSUMMARY:")

# Count OK files and discrepancies
num_ok_files = len(ok_files)
num_discrepancies = len(discrepancy_results)
total_runs = num_ok_files + num_discrepancies

print(f"Total runs: {total_runs}")
print(f"Total OK: {num_ok_files}")
print(f"Total discrepancies: {num_discrepancies}\n")

# Display Discrepancies Maps
if discrepancy_results:
    print("-" * 100)
    print("\nDiscrepancies Maps:")
    for file_path, validator_status, so_long_status in discrepancy_results:
        print(f"Map: {file_path}   validator result: {validator_status}   so_long result: {so_long_status}")

# Display discrepancies summary
if not discrepancies:
    print("-" * 100)
    print("\nNo discrepancies found. Both validation mechanisms are consistent.")
else:
    print("-" * 100)
    print("\nDiscrepancies Summary:")
    for file_path, validator_status, so_long_status, so_long_output, combined_status in discrepancies:
        print(color_text(f"Check Filename: {file_path} - Validator: {validator_status}, ./so_long: {so_long_status}", combined_status))
        print("Validator Output:\n", message)
        print("so_long Output:\n", so_long_output)