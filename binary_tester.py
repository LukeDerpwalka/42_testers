import subprocess
import os
import sys
import time
import shutil
from datetime import datetime


def remove_tester_log_dir():
    try:
        shutil.rmtree('tester_logs')
        print("Successfully removed 'tester_logs' directory and all its contents.")
    except FileNotFoundError:
        print("'tester_logs' directory not found.")
    except Exception as e:
        print(f"Error while deleting 'tester_logs' directory: {e}")


def run_norminette():
    norminette_output, err, returncode, _, _ = run_command(["norminette"])
    norminette_lines = norminette_output.decode('utf-8').split('\n')
    
    if all(line.endswith("OK!") for line in norminette_lines):
        print(f"Norminette passed!")
    else:
        print(f"Norminette failed: {norminette_output.decode('utf-8')}")

def check_tool_exists(tool):
    _, err, returncode, _, _ = run_command(['which', tool])
    if returncode != 0:
        print(f"Error: {tool} not found. Please install it to proceed.")
        sys.exit(1)

def write_output_to_file(command, output):
    """Writes the output of a command to a file."""
    
    # Create a tester_log directory if it doesn't exist
    if not os.path.exists('tester_logs'):
        os.makedirs('tester_logs')
    
    # Get the current datetime to include in the filename
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Generate a filename based on the command, datetime and a timestamp
    file_name = "_".join(command).replace('/', '_') + f"_{current_datetime}_{int(time.time())}.txt"
    
    # Update the path to save inside the tester_log directory
    file_path = os.path.join('tester_logs', file_name)

    with open(file_path, 'w') as f:
        f.write(output.decode('utf-8'))
    return file_path

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    output_filename = write_output_to_file(command, out)
    if err:
        error_filename = write_output_to_file(command + ["_error"], err)
    else:
        error_filename = None
    return out, err, process.returncode, output_filename, error_filename



def get_all_files_in_dir(path='.'):
    """Get a list of all files in the given directory and its sub-directories."""
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames]

def rename_generated_files(initial_files, command, binary_name=None):
    current_files = set(get_all_files_in_dir())
    new_files = current_files - initial_files
    for file in new_files:
        if binary_name and file == binary_name or file.endswith(".o"):
            continue
        new_name = "_".join(command).replace('/', '_') + f"_{os.path.basename(file)}"
        # Update the path to save inside the tester_log directory
        new_path = os.path.join('tester_logs', new_name)
        os.rename(file, new_path)

def summarize_file_types(path='.'):
    """Count and display the number of files of each type in the given directory."""
    # Define file type extensions and their corresponding descriptions
    file_types = {
        '.c': 'C files',
        '.cpp': 'C++ files',
        '.h': 'Header files'
    }
    
    # Initialize counts for each file type
    counts = {file_type: 0 for file_type in file_types}
    other_files = 0
    
    all_files = get_all_files_in_dir(path)
    
    for file in all_files:
        file_ext = os.path.splitext(file)[1]
        if file_ext in counts:
            counts[file_ext] += 1
        else:
            other_files += 1

    # Print the results
    for ext, description in file_types.items():
        print(f"{description}: {counts[ext]}")
    
    print(f"Other files: {other_files}")

def compile_with_make(target, binary_name=None):
    initial_files = set(get_all_files_in_dir())
    out, err, returncode, _, _ = run_command(["make", target])
    if returncode != 0:
        print(f"Failed to compile using 'make {target}': {err.decode('utf-8')}")
        sys.exit(1)
    rename_generated_files(initial_files, ["make", target], binary_name)
    print(out.decode('utf-8'))

def test_with_valgrind(option, binary, params):
    tools = ["memcheck", "helgrind", "drd", "cachegrind"]

    initial_files = set(get_all_files_in_dir())
    print(f"\nTesting option {option} and with valgrind --leak-check=full")
    out, err, returncode, _, _ = run_command(["valgrind", f"--leak-check=full", binary] + params)
    if returncode != 0:
        print(f"Valgrind testing option {option} and leaks failed: {err.decode('utf-8')}")
    rename_generated_files(initial_files, [option, "valgrind", f"--leak-check=full", binary])
    print(out.decode('utf-8'))

    for tool in tools:
        initial_files = set(get_all_files_in_dir())
        print(f"\nTesting with option {option} and valgrind --tool={tool}")
        # Append params when calling the binary
        out, err, returncode, _, _ = run_command(["valgrind", f"--tool={tool}", binary] + params)
        if returncode != 0:
            print(f"Valgrind testing with option {option} and tool {tool} failed: {err.decode('utf-8')}")
        rename_generated_files(initial_files, [option, "valgrind", f"--tool={tool}", binary])
        print(out.decode('utf-8'))

def add_lines_to_makefile():
    with open("Makefile", "r+") as file:
        content = file.read()

        debug_string = "debug: FLAGS += -O0 -g\ndebug: all\n"
        asan_string = "asan: FLAGS += -fsanitize=address\nasan: all\n"
        tsan_string = "tsan: FLAGS += -fsanitize=thread\ntsan: all\n"

        # Check if the strings are already in the content, if not, append them
        if debug_string not in content:
            content += debug_string
        if asan_string not in content:
            content += asan_string
        if tsan_string not in content:
            content += tsan_string

        # Write back to the Makefile
        file.seek(0)
        file.write(content)
        file.truncate()


def remove_lines_from_makefile():
    with open("Makefile", "r+") as file:
        content = file.read()

        debug_string = "debug: FLAGS += -O0 -g\ndebug: all\n"
        asan_string = "asan: FLAGS += -fsanitize=address\nasan: all\n"
        tsan_string = "tsan: FLAGS += -fsanitize=thread\ntsan: all\n"

        # Remove the specified strings if they exist
        content = content.replace(debug_string, "")
        content = content.replace(asan_string, "")
        content = content.replace(tsan_string, "")

        # Write back the updated content to the Makefile
        file.seek(0)
        file.write(content)
        file.truncate()
def main():

    if len(sys.argv) < 2:
        print("Please provide the binary name as the first argument.")
        sys.exit(1)

    binary_name = sys.argv[1]
    params = sys.argv[2:]
    # Ensure necessary tools are installed
    check_tool_exists('valgrind')
    check_tool_exists('norminette')
    check_tool_exists('make')
    remove_tester_log_dir()
    add_lines_to_makefile()
    # Cleanup before starting
    compile_with_make("fclean", binary_name)

    summarize_file_types()
    run_norminette()

    compile_options = ["all", "debug", "asan", "tsan"]

    for option in compile_options:
        compile_with_make("fclean", binary_name)
        print(f"\nCompiling with option: {option}\n")
        compile_with_make(option, binary_name)
        # Check if binary exists and then test with valgrind
        if os.access(binary_name, os.X_OK):
            test_with_valgrind(option, binary_name, params)
        else:
            print(f"Error: Binary '{binary_name}' not found or not executable.")
    remove_lines_from_makefile()
if __name__ == "__main__":
    main()

    
