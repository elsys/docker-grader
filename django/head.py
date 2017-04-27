#-----INPUT-TASK-STEP-----
command="gcc -x c " + state
#-----OUTPUT-TASK-STEP-----
state = state
#-----INPUT-TASK-STEP-----
command="bash -c \"nm ./a.out | grep -E 'printf|fgets|fopen|puts'\""
#-----OUTPUT-TASK-STEP-----
if len(stdout.decode("utf8")) > 2:
    exec_next_step = False
    output_msg = "DO NOT USE PRINTF/FGETS/FOPEN/PUTS!"
#-----INPUT-TASK-STEP-----
command = "bash -c 'seq 1 255 > a.txt && ./a.out | head -c 100000'"
state = command
#-----OUTPUT-TASK-STEP-----
try:
    if stdout.decode("utf8") == "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n":
        grade = 50
    else:
        grade = 0
        output_msg = "Check your line ending. You should print a new line character after the last line"
except UnicodeError:
    output_msg = "Strange symbols in output"
#-----INPUT-TASK-STEP-----
command = "bash -c 'seq -s \" \" 1 10 > a.txt && ./a.out | head -c 100000'"
state = command
#-----OUTPUT-TASK-STEP-----
try:
    expected_result = "".join(str(a + 1) + " " for a in range(10))
    if stdout.decode("utf8") == expected_result[:-1] + "\n":
        grade = 50
    else:
        grade = 0
        output_msg = "Make sure you support very long lines!"
except UnicodeError:
	output_msg = "Strange symbols in output"
