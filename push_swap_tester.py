import subprocess
import random
import os
OK_GREEN = '\033[92m'  # GREEN
FAIL_RED = '\033[91m'  # RED
ENDC = '\033[0m'  # RESET COLOR


params = [
    "",
    " ",
    "   ",
    "-",
    "---",
    "+1+",
    "+++",
    "1+1",
    "1-1",
    "~",
    "a",
    "-a",
    "-2a",
    "-0",
    "?",
    "2147483648",
    "-2147483649",
    "-2147483649123123112",
    "-214748364812123123131312113123123123123123123",
    "-",
    "---",
    "+",
    "+++",
    "~",
    "a",
    "-a",
    "-2a",
    "2147483648",
    "-2147483649",
    "-2147483649123123112",
    "-214748364812123123131312113123123123123123123"
]
norminette_result = subprocess.check_output(["norminette"], universal_newlines=True)

# Split the output into lines
lines = norminette_result.split("\n")

# Initialize normed_files to True
normed_files = True

# Go through each line
for line in lines:
    # If the line does not contain "OK!", print the filename and set normed_files to False
    if "OK!" not in line and line.strip() != "":
        normed_files = False
        filename = line.split(":")[0]
        print(FAIL_RED + filename + " is not normed!" + ENDC)

# If all files are normed, print "Norm OK!"
if normed_files:
    print(OK_GREEN + "Norm OK!" + ENDC)

min_num_params = 1
max_num_params = 500
min_int = -2147483648
max_int = 2147483647

if not os.path.isfile('./push_swap'):
    print(FAIL_RED + "The file 'push_swap' does not exist!" + ENDC)
    exit(1)

if not os.path.isfile('./checker'):
    print(FAIL_RED + "The file 'checker' does not exist!" + ENDC)
    exit(1)

# Generate a random number of calls to make
print(FAIL_RED + 100*'-')
print(FAIL_RED + 'RANDOM TESTS')
print(FAIL_RED + 100*'-')

successful_tests = 0
failed_tests = 0

for _ in range(100):
    # For each call, generate a random number of parameters
    num_params = random.randint(min_num_params, max_num_params)

    # Generate the parameters themselves
    params = [str(random.randint(min_int, max_int)) for _ in range(num_params)]

    # Prepare the command for push_swap
    push_swap_command = ["./push_swap"] + params

    # Run push_swap and get its output
    push_swap_result = subprocess.Popen(push_swap_command, stdout=subprocess.PIPE)

    # Pipe the output of push_swap to checker
    checker_command = ["./checker"] + params
    checker_result = subprocess.Popen(checker_command, stdin=push_swap_result.stdout, stdout=subprocess.PIPE)

    # Ensure that push_swap_result.stdout is closed when checker_result is done with it
    push_swap_result.stdout.close()

    # Get the final output
    output = checker_result.communicate()[0].decode('utf-8').strip()

    # Format and colorize the output
    if output == "OK":
        print(OK_GREEN + 'output: "{}"'.format(output) + ENDC)
    else:
        print(FAIL_RED + 'output: "{}"'.format(output) + ENDC)

    if output == "OK":
        successful_tests += 1
    else:
        failed_tests += 1

print(FAIL_RED + 100*'-')
print(FAIL_RED + 'OTHER TESTS')
print(FAIL_RED + 100*'-')
for param in params:
    # Prepare the command for push_swap
    push_swap_command = ["./push_swap", param]

    # Run push_swap and get its output
    push_swap_result = subprocess.Popen(push_swap_command, stdout=subprocess.PIPE)

    # Pipe the output of push_swap to checker
    checker_command = ["./checker", param]
    checker_result = subprocess.Popen(checker_command, stdin=push_swap_result.stdout, stdout=subprocess.PIPE)

    # Ensure that push_swap_result.stdout is closed when checker_result is done with it
    push_swap_result.stdout.close()

    # Get the final output
    output = checker_result.communicate()[0].decode('utf-8').strip()

    # Format and colorize the output
    if output == "OK":
        print(OK_GREEN + 'output: "{}" | tested with: {}'.format(output, param) + ENDC)
    else:
        print(FAIL_RED + 'output: "{}" | tested with: {}'.format(output, param) + ENDC)

    if output == "OK":
        successful_tests += 1
    else:
        failed_tests += 1

print(OK_GREEN + "Summary:" + ENDC)
print(OK_GREEN + "Successful tests: {} ".format(successful_tests) + ENDC)
if failed_tests > 0:
    print(FAIL_RED + "Failed tests: {} ".format(failed_tests) + ENDC)
else:
    print(OK_GREEN + "Failed tests: {} ".format(failed_tests) + ENDC)