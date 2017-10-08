import docker as py_docker

import pytest

from grader.base import docker


@pytest.fixture
def docker_client(monkeypatch):
    class Images:
        def build(self, *args, **kwargs):
            self.last_build_args = args
            self.last_build_kwargs = kwargs

    class Containers:
        def __init__(self):
            self.get_result = None

        def create(self, *args, **kwargs):
            self.last_create_args = args
            self.last_create_kwargs = kwargs

            return kwargs

        def get(self, *args, **kwargs):
            self.last_get_args = args
            self.last_get_kwargs = kwargs

            return self.get_result

    class API:
        def exec_create(self, *args, **kwargs):
            self.last_exec_create_args = args
            self.last_exec_create_kwargs = kwargs

            return 'test_exec_id'

        def exec_start(self, *args, **kwargs):
            self.last_exec_start_args = args
            self.last_exec_start_kwargs = kwargs

            return b'stdplex output'

        def exec_inspect(self, *args, **kwargs):
            self.last_exec_inspect_args = args
            self.last_exec_inspect_kwargs = kwargs

            return {'ExitCode': 42}

    class Client:
        images = Images()
        containers = Containers()
        api = API()

    client = Client()
    monkeypatch.setattr('grader.base.docker.client', client)
    return client


@pytest.fixture
def docker_container():
    class Container:
        def __init__(self):
            self.kill_raise = None
            self.start_status = None

            self.status = 'created'
            self.id = 'test_id'

        def start(self):
            if self.start_status:
                self.status = self.start_status
            else:
                self.status = 'running'

        def kill(self):
            self.status = 'deleted'

            if self.kill_raise is not None:
                raise self.kill_raise

    return Container()


def test_docker_image_build(monkeypatch, docker_client):
    labels = {'key1': 'val1'}
    monkeypatch.setattr('grader.base.docker.labels', labels)
    monkeypatch.setattr('grader.base.docker.tag_prefix', 'test_prefix/')

    tag = docker.docker_image_build(
        'test_tag', 'Dockerfile.test', 'path/to/context')

    assert tag == 'test_prefix/test_tag'
    assert docker_client.images.last_build_kwargs['path'] == 'path/to/context'
    assert docker_client.images.last_build_kwargs['tag'] == tag
    assert docker_client.images.last_build_kwargs['rm'] is True
    assert docker_client.images.last_build_kwargs['pull'] is True
    assert docker_client.images.last_build_kwargs['forcerm'] is True
    assert docker_client.images.last_build_kwargs['dockerfile'] == \
        'Dockerfile.test'
    assert docker_client.images.last_build_kwargs['labels'] == labels


def test_docker_container_create_not_crippled(monkeypatch, docker_client):
    labels = {'key1': 'val1'}
    log_config_none = {'key2': 'val2'}
    monkeypatch.setattr('grader.base.docker.labels', labels)
    monkeypatch.setattr('grader.base.docker._log_config_none', log_config_none)

    volumes = {'container/path': 'host/path'}

    kwargs = docker.docker_container_create(
        'test_image', 'test command', crippled=False, volumes=volumes)

    assert len(docker_client.containers.last_create_args) == 0
    assert docker_client.containers.last_create_kwargs == kwargs

    assert kwargs['labels'] == labels
    assert kwargs['image'] == 'test_image'
    assert kwargs['command'] == 'test command'

    assert kwargs['auto_remove'] is True
    assert kwargs['detach'] is True
    assert kwargs['log_config'] == log_config_none
    assert kwargs['oom_kill_disable'] is False
    assert kwargs['oom_score_adj'] == 1000
    assert kwargs['privileged'] is False
    assert kwargs['stdin_open'] is False
    assert kwargs['tty'] is False

    assert kwargs['network_mode'] == 'bridge'

    assert len(kwargs['volumes']) == 1
    assert kwargs['volumes']['host/path']['bind'] == 'container/path'
    assert kwargs['volumes']['host/path']['mode'] == 'ro'


def test_docker_container_create_crippled(monkeypatch, docker_client):
    labels = {'key1': 'val1'}
    log_config_none = {'key2': 'val2'}
    monkeypatch.setattr('grader.base.docker.labels', labels)
    monkeypatch.setattr('grader.base.docker._log_config_none', log_config_none)

    volumes = {'container/path': 'host/path'}

    kwargs = docker.docker_container_create(
        'test_image', 'test command', crippled=True, volumes=volumes)

    assert len(docker_client.containers.last_create_args) == 0
    assert docker_client.containers.last_create_kwargs == kwargs

    assert kwargs['labels'] == labels
    assert kwargs['image'] == 'test_image'
    assert kwargs['command'] == 'test command'

    assert kwargs['auto_remove'] is True
    assert kwargs['detach'] is True
    assert kwargs['log_config'] == log_config_none
    assert kwargs['oom_kill_disable'] is False
    assert kwargs['oom_score_adj'] == 1000
    assert kwargs['privileged'] is False
    assert kwargs['stdin_open'] is False
    assert kwargs['tty'] is False

    assert kwargs['mem_limit'] == '100m'
    assert kwargs['mem_swappiness'] == 0
    assert kwargs['memswap_limit'] == '100m'
    assert kwargs['kernel_memory'] == '50m'
    assert kwargs['network_disabled'] is True
    assert kwargs['network_mode'] == 'none'
    assert kwargs['pids_limit'] == 100
    assert kwargs['shm_size'] == '100M'

    assert len(kwargs['volumes']) == 1
    assert kwargs['volumes']['host/path']['bind'] == 'container/path'
    assert kwargs['volumes']['host/path']['mode'] == 'ro'


def test_docker_container_exec(docker_client, docker_container):
    rc, stdout, stderr, stdplex = docker.docker_container_exec(
        docker_container, 'test command')

    create_args = docker_client.api.last_exec_create_args
    create_kwargs = docker_client.api.last_exec_create_kwargs
    assert create_args == (docker_container.id, 'test command')
    assert create_kwargs == {
        'stdout': True,
        'stderr': True,
        'stdin': False,
        'tty': False,
        'privileged': False,
    }

    start_args = docker_client.api.last_exec_start_args
    start_kwargs = docker_client.api.last_exec_start_kwargs
    assert start_args == ('test_exec_id',)
    assert start_kwargs == {
        'detach': False,
        'tty': False,
        'stream': False,
        'socket': False,
    }

    inspect_args = docker_client.api.last_exec_inspect_args
    inspect_kwargs = docker_client.api.last_exec_inspect_kwargs
    assert inspect_args == ('test_exec_id',)
    assert len(inspect_kwargs) == 0

    assert rc == 42
    assert stdout == stderr
    assert stderr == stdplex
    assert stdplex == b'stdplex output'


def test_docker_runner(docker_client, docker_container):
    runner = docker.DockerRunner()
    runner.container = docker_container
    docker_client.containers.get_result = docker_container

    assert runner.container.status == 'created'

    with runner:
        assert runner.container.status == 'running'

    assert runner.container.status == 'deleted'


def test_docker_runner_raise(docker_client, docker_container):
    runner = docker.DockerRunner()
    runner.container = docker_container
    docker_client.containers.get_result = docker_container

    assert runner.container.status == 'created'

    try:
        with runner:
            assert runner.container.status == 'running'
            raise
    except:
        pass

    assert runner.container.status == 'deleted'


def test_docker_runner_kill_not_found(docker_client, docker_container):
    runner = docker.DockerRunner()
    runner.container = docker_container
    docker_client.containers.get_result = docker_container
    docker_container.kill_raise = py_docker.errors.NotFound('not found')

    assert runner.container.status == 'created'

    with runner:
        assert runner.container.status == 'running'

    assert runner.container.status == 'deleted'


def test_docker_runner_not_running(docker_client, docker_container):
    runner = docker.DockerRunner()
    runner.container = docker_container
    docker_client.containers.get_result = docker_container
    docker_container.start_status = 'created'

    assert runner.container.status == 'created'

    with pytest.raises(RuntimeError) as excinfo:
        with runner:
            pass  # pragma: no cover

    assert 'container not running' in str(excinfo.value)
