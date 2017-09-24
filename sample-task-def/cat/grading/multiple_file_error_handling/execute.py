def preprocess(result, state, **kwargs):
    result['command'] = ['./cat', 'non-existing-file', 'non-existing-file-2']


def postprocess(result, rc, stderr, **kwargs):
    assert rc != 0, "Your program must return a non-zero exit status on error"

    error_msg = "Fix error handling for multiple files"

    expected_output = './cat: ' \
        'cannot open \'non-existing-file\' for reading: ' \
        'No such file or directory\n' \
        './cat: cannot open \'non-existing-file-2\' for reading: ' \
        'No such file or directory\n'

    assert stderr == expected_output, error_msg

    result['output_msg'] = "Error handling for multiple files ok"
