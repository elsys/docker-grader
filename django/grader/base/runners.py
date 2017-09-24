import os.path
import xmlrpc.client

from .utils import wait_for_port
from .docker import client as docker_client
from .docker import DockerRunner



class GradingRunner(DockerRunner):
    def __init__(self, docker_image):
        super().__init__()

        rpc_host_path = os.path.join(os.path.dirname(__file__), 'rpc.py')
        rpc_container_path = '/grader/rpc.py'

        volumes = {
            rpc_host_path: {
                'bind': rpc_container_path,
                'mode': 'ro',
            }
        }

        self.container = docker_client.containers.create(
            image=docker_image,
            command=['python', rpc_container_path],
#            auto_remove=True,
            detach=True,
            network_mode='bridge',
            oom_kill_disable=False,
            oom_score_adj=1000,
            privileged=False,
            stdin_open=False,
            tty=False,
            volumes=volumes)

    def __enter__(self):
        result = super().__enter__()

        networks = self.container.attrs['NetworkSettings']['Networks']
        ip_address = networks['bridge']['IPAddress']

        rpc_host, rpc_port = ip_address, 8000
        rpc_url = 'http://{0!s}:{1:d}/'.format(rpc_host, rpc_port)

        self.rpc = xmlrpc.client.ServerProxy(rpc_url)

        assert wait_for_port(rpc_host, rpc_port), "RPC server not running"

        return result

    def rpc_call(self, func, *args, **kwargs):
        return getattr(self.rpc, func)(*args, **kwargs)



class TestingRunner(DockerRunner):
    def __init__(self, docker_image, input_file_host_path):
        super().__init__()

        input_file_host_path = os.path.abspath(input_file_host_path)
        self.input_file_container_path = '/grader/testing/input.file'

        log_config_none = {
            'type': None,
            'config': {},
        }

        volumes = {
            input_file_host_path: {
                'bind': self.input_file_container_path,
                'mode': 'ro',
            }
        }

        self.container = docker_client.containers.create(
            image=docker_image,
            command=['sleep', 'infinity'],
            auto_remove=True,
            detach=True,
            log_config=log_config_none,
            mem_limit='100m',
            mem_swappiness=0,
            memswap_limit='100m',
            kernel_memory='50m',
            network_disabled=True,
            network_mode='none',
            oom_kill_disable=False,
            oom_score_adj=1000,
            pids_limit=100,
            privileged=False,
            shm_size='100M',
            stdin_open=False,
            tty=False,
            volumes=volumes)

    def exec_step(self, command):
        docker_exec_id = docker_client.api.exec_create(
            self.container.id,
            command,
            stdout=True,
            stderr=True,
            stdin=False,
            tty=False,
            privileged=False)

        stdplex = docker_client.api.exec_start(
            docker_exec_id,
            detach=False,
            tty=False,
            stream=False,
            socket=False)

        docker_exec_result = docker_client.api.exec_inspect(docker_exec_id)
        rc = docker_exec_result['ExitCode']

        stdout = stderr = stdplex
        return rc, stdout, stderr, stdplex
