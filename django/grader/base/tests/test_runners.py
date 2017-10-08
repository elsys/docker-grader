import pytest


from grader.base import rpc
from grader.base.runners import GradingRunner
from grader.base.runners import TestingRunner


@pytest.fixture
def docker_runner(monkeypatch):
    class DockerRunner:
        def __enter__(self, *args, **kwargs):
            pass

        def __exit__(self, *args, **kwargs):
            pass

    monkeypatch.setattr(
        'grader.base.runners.DockerRunner.__enter__', DockerRunner.__enter__)

    monkeypatch.setattr(
        'grader.base.runners.DockerRunner.__exit__', DockerRunner.__exit__)


@pytest.fixture
def docker_container_create(monkeypatch):
    class Container:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

            self.ip_address = '192.168.100.100'

            self.attrs = {
                'NetworkSettings': {
                    'Networks': {
                        'bridge': {
                            'IPAddress': self.ip_address,
                        }
                    }
                }
            }

    def create(*args, **kwargs):
        container = Container(*args, **kwargs)
        create.last_container = container
        return container

    monkeypatch.setattr('grader.base.runners.docker_container_create', create)
    return create


@pytest.fixture
def docker_container_exec(monkeypatch):
    def mock_exec(*args, **kwargs):
        return {'args': args, 'kwargs': kwargs, }

    monkeypatch.setattr('grader.base.runners.docker_container_exec', mock_exec)
    return mock_exec


@pytest.fixture
def xmlrpc_client(monkeypatch):
    class ServerProxy:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def method(self, *args, **kwargs):
            self.call_args = args
            self.call_kwargs = kwargs

    def wait_for_port(host, port):
        wait_for_port.host = host
        wait_for_port.port = port
        return wait_for_port.result

    monkeypatch.setattr(
        'grader.base.runners.xmlrpc.client.ServerProxy', ServerProxy)

    monkeypatch.setattr('grader.base.runners.wait_for_port', wait_for_port)
    wait_for_port.result = True
    return wait_for_port


def test_grading_runner_basic(docker_runner, docker_container_create):
    runner = GradingRunner('test_image')

    docker_create_image, docker_create_command = runner.container.args
    docker_create_kwargs = runner.container.kwargs

    assert docker_create_image == 'test_image'
    assert docker_create_command == ['python', '/grader/rpc.py']
    assert docker_create_kwargs['crippled'] is False
    assert docker_create_kwargs['volumes'] == {
        '/grader/rpc.py': rpc.__file__,
    }


def test_grading_runner_enter_basic(
        docker_runner, docker_container_create, xmlrpc_client):
    runner = GradingRunner('test_image')

    with runner:
        rpc_url = runner.rpc.args[0]

    assert rpc_url == 'http://' + runner.container.ip_address + ':8000/'
    assert xmlrpc_client.host == runner.container.ip_address
    assert xmlrpc_client.port == 8000


def test_grading_runner_enter_no_rpc(
        docker_runner, docker_container_create, xmlrpc_client):
    runner = GradingRunner('test_image')

    xmlrpc_client.result = False

    with pytest.raises(RuntimeError) as excinfo:
        with runner:
            pass  # pragma: no cover

    assert 'server not running' in str(excinfo.value)


def test_grading_runner_rpc_call(
        docker_runner, docker_container_create, xmlrpc_client):
    runner = GradingRunner('test_image')

    with runner:
        runner.rpc_call('method', 'arg1', arg2='val2')
        assert runner.rpc.call_args == ('arg1',)
        assert runner.rpc.call_kwargs == {'arg2': 'val2'}


def test_testing_runner_basic(docker_runner, docker_container_create):
    runner = TestingRunner('test_image', '/host/path')

    docker_create_image, docker_create_command = runner.container.args
    docker_create_kwargs = runner.container.kwargs

    assert runner.input_file_container_path == '/grader/testing/input.file'

    assert docker_create_image == 'test_image'
    assert docker_create_command == ['sleep', 'infinity']
    assert docker_create_kwargs['crippled'] is True
    assert docker_create_kwargs['volumes'] == {
        runner.input_file_container_path: '/host/path',
    }


def test_testing_runner_exec_step(
        docker_runner, docker_container_create, docker_container_exec):
    runner = TestingRunner('test_image', '/host/path')

    with runner:
        result = runner.exec_step('test command')
        assert result['args'][0] == runner.container
        assert result['args'][1] == 'test command'
        assert len(result['kwargs']) == 0
