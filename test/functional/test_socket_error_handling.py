import socket
import unittest
import libnacl
from multiprocessing import Lock
from threading import Thread
from time import sleep

from splonebox.rpc.connection import Connection


def collect_tests(suite: unittest.TestSuite):
    suite.addTest(SocketErrorHandling("test_connection_closed_by_remote"))


class SocketErrorHandling(unittest.TestCase):
    def test_connection_closed_by_remote(self):
        lo = Lock()

        def test_server():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", 42427))
            lo.release()
            sock.listen()
            lo.acquire()
            sleep(0.1)
            sock.shutdown(socket.SHUT_RDWR)

        lo.acquire()
        t = Thread(target=test_server)
        t.start()

        lo.acquire()
        con = Connection(serverlongtermpk=libnacl.crypto_box_keypair()[0])

        with self.assertRaises(ConnectionResetError):
            con._socket.connect(("127.0.0.1", 42427))
            con._connected = True
            lo.release()
            con._listen(None)
            t.join()
