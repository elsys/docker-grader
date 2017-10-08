import pytest

from grader.base import rpc


@pytest.fixture
def import_module(monkeypatch):
    class Execute:
        def __init__(self, *args, **kwargs):
            self.init_args = args
            self.init_kwargs = kwargs

        def preprocess(self, *args, **kwargs):
            self.preprocess_args = args
            self.preprocess_kwargs = kwargs

        def postprocess(self, *args, **kwargs):
            self.postprocess_args = args
            self.postprocess_kwargs = kwargs

            if import_module.postprocess_assert is True:
                assert not True, "Assert happened!"

    def import_module(*args, **kwargs):
        module = Execute(*args, **kwargs)
        import_module.last_module = module
        return module

    import_module.postprocess_assert = False

    monkeypatch.setattr(
        'grader.base.rpc.importlib.import_module', import_module)

    return import_module


@pytest.fixture
def xmlrpc_server(monkeypatch):
    class SimpleXMLRPCServer:
        def __init__(self, *args, **kwargs):
            SimpleXMLRPCServer.last_server = self

            self.init_args = args
            self.init_kwargs = kwargs
            self.registered_functions = {}

        def register_function(self, func, name):
            self.registered_functions[name] = func

        def serve_forever(self):
            pass

    monkeypatch.setattr(
        'grader.base.rpc.SimpleXMLRPCServer', SimpleXMLRPCServer)

    return SimpleXMLRPCServer


def test_load_module(import_module):
    module = rpc.load_module('test_step')

    assert module.init_args == ('grading.test_step.execute',)


def test_run_preprocess(import_module):
    state = {'key10': 'val10'}
    result = rpc.run_preprocess('test_step', {'key1': 'val1', 'state': state})

    module = import_module.last_module
    assert module.init_args == ('grading.test_step.execute',)

    assert module.preprocess_args == tuple()
    assert module.preprocess_kwargs == {
        'key1': 'val1',
        'state': state,
        'result': result,
    }

    assert result == {
        'stop_on_failure': False,
        'test_time_limit': 1,
        'decode_output_to_ascii': True,
        'state': state,
    }


def test_run_postprocess(import_module):
    state = {'key10': 'val10'}
    result = rpc.run_postprocess('test_step', {'key1': 'val1', 'state': state})

    module = import_module.last_module
    assert module.init_args == ('grading.test_step.execute',)

    assert module.postprocess_args == tuple()
    assert module.postprocess_kwargs == {
        'key1': 'val1',
        'state': state,
        'result': result,
    }

    assert result == {
        'fail': False,
        'grade': 100,
        'state': state,
    }


def test_run_postprocess_assert(import_module):
    import_module.postprocess_assert = True

    state = {'key10': 'val10'}
    result = rpc.run_postprocess('test_step', {'key1': 'val1', 'state': state})

    module = import_module.last_module
    assert module.init_args == ('grading.test_step.execute',)

    assert module.postprocess_args == tuple()
    assert module.postprocess_kwargs == {
        'key1': 'val1',
        'state': state,
        'result': result,
    }

    assert result['fail'] is True
    assert result['grade'] == 100
    assert result['state'] == state
    assert "Assert happened!" in result['output_msg']


def test_main(xmlrpc_server):
    rpc.main()
    server = xmlrpc_server.last_server

    assert server.init_args == (('0.0.0.0', 8000),)
    assert server.init_kwargs == {'allow_none': True}
    assert server.registered_functions == {
        'run_preprocess': rpc.run_preprocess,
        'run_postprocess': rpc.run_postprocess,
    }
