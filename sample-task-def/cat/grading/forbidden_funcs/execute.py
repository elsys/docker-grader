import shlex


def preprocess(result, state, **kwargs):
    result['stop_on_failure'] = True

    forbidden_funcs = ['printf', 'fgets', 'fopen', 'puts']
    state['forbidden_funcs'] = forbidden_funcs

    result['command'] = 'nm ./cat | grep -E {0!s}'.format(
        shlex.quote('|'.join(forbidden_funcs)))


def postprocess(result, state, rc, stdplex, **kwargs):
    forbidden_funcs_str = ','.join(state['forbidden_funcs'])

    assert rc != 0, "Do not use {0!s}!\n{1!s}".format(
        forbidden_funcs_str, stdplex)

    result['output_msg'] = "Check for {0!s} ok.".format(forbidden_funcs_str)
