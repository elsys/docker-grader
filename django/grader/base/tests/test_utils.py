import time
import socket
from threading import Thread

from collections import OrderedDict

from grader.base.utils import ordered_load
from grader.base.utils import wait_for_port


def test_yaml_order_1():
    raw = """
        a: 1
        b: 2
    """
    doc = ordered_load(raw)
    assert type(doc) == OrderedDict

    first = doc.popitem(last=False)
    assert first == ('a', 1)

    second = doc.popitem(last=False)
    assert second == ('b', 2)


def test_yaml_order_2():
    raw = """
        b: 1
        a: 2
    """
    doc = ordered_load(raw)
    assert type(doc) == OrderedDict

    first = doc.popitem(last=False)
    assert first == ('b', 1)

    second = doc.popitem(last=False)
    assert second == ('a', 2)


def test_wait_for_port_already_opened():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    host, port = s.getsockname()
    s.listen(1)

    assert wait_for_port(host, port, timeout=1)


def test_wait_for_port_closed():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    host, port = s.getsockname()

    assert not wait_for_port(host, port, timeout=1)


def test_wait_for_port_will_open():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    host, port = s.getsockname()

    def later_listen():
        time.sleep(.5)
        s.listen(1)

    thread = Thread(target=later_listen)
    thread.start()
    assert wait_for_port(host, port, timeout=1)
    thread.join()


def test_wait_for_port_will_open_late():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    host, port = s.getsockname()

    def later_listen():
        time.sleep(1)
        s.listen(1)

    thread = Thread(target=later_listen)
    thread.start()
    assert not wait_for_port(host, port, timeout=.5)
    thread.join()
