import shlex


def preprocess(result, filename, **kwargs):
    result['stop_on_failure'] = True
    result['command'] = 'gcc -x c {0!s} -o ./cat && ls ./cat'.format(
        shlex.quote(filename))


def postprocess(result, rc, stdplex, **kwargs):
    assert rc == 0, stdplex

    result['output_msg'] = "Compile OK"
