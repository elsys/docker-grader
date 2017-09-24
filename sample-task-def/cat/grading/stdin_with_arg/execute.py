import shlex


def preprocess(result, state, **kwargs):
    result['command'] = './cat - < {0!s}'.format(shlex.quote('seq_1_255.txt'))


def postprocess(result, rc, stdout, **kwargs):
    assert rc == 0, "Your program must return 0 on success"

    error_msg = "Standart input (with argument -) is not working"
    expected_output = '\n'.join(str(i) for i in range(1, 256)) + '\n'

    assert stdout == expected_output, error_msg

    result['output_msg'] = "Standart input (with argument -) ok."
