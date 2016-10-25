from tasks import rpc

TEST_INPUT_COMMAND_SOURCE = """
command = "blabla"
state_out = state_in * 15
"""


def test_prepare_input_command():
    result = rpc.prepare_input_command(TEST_INPUT_COMMAND_SOURCE, 1)
    assert result["state"] == 15
    assert result["command"] == "blabla"


TEST_OUTPUT_PARSING_SOURCE = """
output_msg = "blabla"
grade = state_in * status_code
state_out = 2 * grade
exec_next_step = True
"""


def test_parse_output():
    result = rpc.parse_output(TEST_OUTPUT_PARSING_SOURCE, 2, "stdout", "stderr", 15)
    assert result["state"] == 60
    assert result["grade"] == 30
    assert result["output_msg"] == "blabla"
    assert result["exec_next_step"]


TEST_INPUT_NO_STATE = """
command = "blabla"
"""


def test_prepare_input_command_no_state():
    result = rpc.prepare_input_command(TEST_INPUT_NO_STATE, 1)
    assert result["command"] == "blabla"


TEST_OUTPUT_NO_STATE_SOURCE = """
output_msg = "blabla"
grade = state_in * status_code
exec_next_step = True
"""


def test_parse_output_no_state():
    result = rpc.parse_output(TEST_OUTPUT_NO_STATE_SOURCE, 2, "stdout", "stderr", 15)
    assert result["grade"] == 30
    assert result["output_msg"] == "blabla"
    assert result["exec_next_step"]
