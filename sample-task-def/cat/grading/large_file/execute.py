def preprocess(result, state, **kwargs):
    result['command'] = ['./cat', 'seq_1_255000.txt', 'seq_1_255000.txt']


def postprocess(result, rc, stdout, **kwargs):
    assert rc == 0, "Your program must return 0 on success"

    error_msg = "Check handling of large files."

    expected_output = '\n'.join(str(i) for i in range(1, 255001)) + '\n'
    expected_output += expected_output

    assert stdout == expected_output, error_msg

    result['output_msg'] = "Large files ok."
