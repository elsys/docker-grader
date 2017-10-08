import os.path
import xmlrpc.client

from .utils import wait_for_port
from .docker import docker_container_create
from .docker import docker_container_exec
from .docker import DockerRunner


class GradingRunner(DockerRunner):
    def __init__(self, docker_image):
        super().__init__()

        rpc_host_path = os.path.join(os.path.dirname(__file__), 'rpc.py')
        rpc_container_path = '/grader/rpc.py'

        self.container = docker_container_create(
            docker_image, ['python', rpc_container_path],
            crippled=False, volumes={rpc_container_path: rpc_host_path})

    def __enter__(self):
        result = super().__enter__()

        networks = self.container.attrs['NetworkSettings']['Networks']
        ip_address = networks['bridge']['IPAddress']

        rpc_host, rpc_port = ip_address, 8000
        rpc_url = 'http://{0!s}:{1:d}/'.format(rpc_host, rpc_port)

        self.rpc = xmlrpc.client.ServerProxy(rpc_url)

        if wait_for_port(rpc_host, rpc_port) is not True:
            raise RuntimeError("RPC server not running")

        return result

    def rpc_call(self, func, *args, **kwargs):
        return getattr(self.rpc, func)(*args, **kwargs)


class TestingRunner(DockerRunner):
    def __init__(self, docker_image, input_file_host_path):
        super().__init__()

        input_file_host_path = os.path.abspath(input_file_host_path)
        self.input_file_container_path = '/grader/testing/input.file'

        self.container = docker_container_create(
            docker_image, ['sleep', 'infinity'],
            crippled=True,
            volumes={self.input_file_container_path: input_file_host_path})

    def exec_step(self, command):
        return docker_container_exec(self.container, command)
