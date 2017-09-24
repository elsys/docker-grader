def preprocess(result, state, **kwargs):
    result['command'] = ['./cat', 'seq_1_255.txt', 'seq_1_255.txt']

def postprocess(result, rc, stdout, **kwargs):
    assert rc == 0, "Your program must return 0 on success"

    error_msg = "Check handling of multiple files. " \
        "You should keep the new line character after the last line"

    expected_output = '\n'.join(str(i) for i in range(1, 256)) + '\n'
    expected_output += expected_output

    assert stdout == expected_output, error_msg

    result['output_msg'] = "Test with multiple files ok."
