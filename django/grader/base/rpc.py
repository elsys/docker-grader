import os
import sys
import logging
import importlib

from xmlrpc.server import SimpleXMLRPCServer


logger = logging.getLogger('grader.base.rpc')


def load_module(step_name):
    return importlib.import_module('grading.{0!s}.execute'.format(step_name))


def run_preprocess(step_name, kwargs):
    execute = load_module(step_name)

    result = kwargs.get('result', {})
    kwargs['result'] = result

    result['stop_on_failure'] = False
    result['test_time_limit'] = 1
    result['decode_output_to_ascii'] = True

    execute.preprocess(**kwargs)
    result['state'] = kwargs['state']

    return result


def run_postprocess(step_name, kwargs):
    execute = load_module(step_name)

    result = kwargs.get('result', {})
    kwargs['result'] = result

    result['fail'] = False
    result['grade'] = 100

    try:
        execute.postprocess(**kwargs)
    except AssertionError as e:
        result['fail'] = True
        result['output_msg'] = e.args[0]

    result['state'] = kwargs['state']

    return result


def main():
    sys.path.append(os.path.dirname(__file__))

    server = SimpleXMLRPCServer(('0.0.0.0', 8000), allow_none=True)

    server.register_function(run_preprocess, 'run_preprocess')
    server.register_function(run_postprocess, 'run_postprocess')

    server.serve_forever()


if __name__ == "__main__":
    main()
