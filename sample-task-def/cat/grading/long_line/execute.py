def preprocess(result, state, **kwargs):
    result['command'] = ['./cat', 'long_line_20_25550.txt']


def postprocess(result, rc, stdout, **kwargs):
    assert rc == 0, "Your program must return 0 on success"

    error_msg = "Make sure you support very long lines!"

    expected_output = ''
    for start in range(1,21):
        expected_line = ' '.join(str(i) for i in range(start, 25551))
        expected_output += expected_line + '\n'

    assert stdout == expected_output, error_msg

    result['output_msg'] = "Very long lines OK!"
