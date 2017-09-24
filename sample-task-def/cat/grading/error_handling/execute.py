def preprocess(result, state, **kwargs):
    result['command'] = ['./cat', 'non-existing-file']


def postprocess(result, rc, stderr, **kwargs):
    assert rc != 0, "Your program must return a non-zero exit status on error"

    error_msg = "Fix error handling"

    expected_output = './cat: ' \
        'cannot open \'non-existing-file\' for reading: ' \
        'No such file or directory\n'

    assert stderr == expected_output, error_msg

    result['output_msg'] = "Error handling ok"
